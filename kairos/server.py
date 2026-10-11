"""HTTP API + the web app. Run: python -m kairos serve  (http://localhost:8787)

Big files never pass through a chat window: the browser uploads in resumable 8 MB chunks
straight to this server (an hour of 4K is fine), or you paste a link / a local path.
"""
from __future__ import annotations

import json
import re
import shutil
import threading
import uuid
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from . import __version__, blender, brain, config, export, grade, learn, project, prompts, sfx, styles, transcribe
from .config import LIBRARY, ROOT, UPLOADS, WEB

JOBS: dict[str, dict] = {}       # "pid/cid" -> {"state": "rendering"|"ready"|"error", ...}


def ok(data, status: int = 200) -> JSONResponse:
    return JSONResponse(data, status_code=status)


def err(msg: str, status: int = 400) -> JSONResponse:
    return JSONResponse({"error": msg}, status_code=status)


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._ -]", "_", Path(name).name)[:120] or "file"


# ---------- status / settings ----------
async def status(_: Request):
    return ok({"version": __version__, "claude": brain.status(), "transcribers": transcribe.available(),
               "blender": blender.available(), "scoreboard": learn.scoreboard(), "chunk_mb": config.settings()["chunk_mb"]})


async def settings(req: Request):
    if req.method == "POST":
        body = await req.json()
        s = config.save_settings(body)
        brain.reset()
    else:
        s = config.settings()
    s = dict(s)
    if s.get("anthropic_api_key"):
        s["anthropic_api_key"] = "saved"
    return ok(s)


# ---------- resumable chunked upload ----------
async def upload_init(req: Request):
    b = await req.json()
    uid = "u_" + uuid.uuid4().hex[:12]
    d = UPLOADS / uid
    d.mkdir()
    (d / "meta.json").write_text(json.dumps({"name": safe_name(b.get("name", "video.mp4")), "size": int(b.get("size", 0))}))
    (d / "data").touch()
    return ok({"id": uid, "received": 0, "chunk": config.settings()["chunk_mb"] * 1024 * 1024})


async def upload_chunk(req: Request):
    uid = req.path_params["uid"]
    d = UPLOADS / uid
    if not (d / "meta.json").exists() or not re.fullmatch(r"u_[0-9a-f]{12}", uid):
        return err("unknown upload", 404)
    f = d / "data"
    if req.method == "GET":
        return ok({"received": f.stat().st_size})
    offset = int(req.query_params.get("offset", "0"))
    have = f.stat().st_size
    if offset != have:                      # client resumes from what we actually have
        return ok({"received": have, "resync": True})
    with f.open("ab") as fh:
        async for part in req.stream():
            fh.write(part)
    return ok({"received": f.stat().st_size})


async def upload_complete(req: Request):
    uid = req.path_params["uid"]
    d = UPLOADS / uid
    meta = json.loads((d / "meta.json").read_text())
    body = await req.json() if (await req.body()) else {}
    f = d / "data"
    if meta["size"] and f.stat().st_size != meta["size"]:
        return err(f"upload incomplete: {f.stat().st_size} of {meta['size']} bytes", 409)
    named = d / meta["name"]
    f.rename(named)
    p = project.create(named, Path(meta["name"]).stem, body.get("brief", {}), move=True)
    shutil.rmtree(d, ignore_errors=True)
    return ok(p)


async def import_source(req: Request):
    """Paste a link or a path: no upload at all. Links use yt-dlp when installed, else a direct download."""
    import asyncio
    b = await req.json()
    return await asyncio.to_thread(_import, b)


def _import(b: dict):
    src = (b.get("url") or b.get("path") or "").strip()
    if not src:
        return err("give a url or a path")
    if not src.startswith(("http://", "https://")):
        p = Path(src).expanduser()
        if not p.is_file():
            return err("file not found on this machine", 404)
        return ok(project.create(p, p.stem, b.get("brief", {}), move=False))
    d = UPLOADS / ("u_" + uuid.uuid4().hex[:12])
    d.mkdir()
    ytdlp = shutil.which("yt-dlp")
    if ytdlp:
        import subprocess
        r = subprocess.run([ytdlp, "-f", "mp4/bestvideo*+bestaudio/best", "--merge-output-format", "mp4",
                            "-o", str(d / "%(title).80s.%(ext)s"), src], capture_output=True, text=True, timeout=3600)
        files = list(d.glob("*.mp4"))
        if r.returncode or not files:
            return err("could not download that link: " + r.stderr[-300:])
        target = files[0]
    else:
        import httpx
        target = d / safe_name(src.split("?")[0].rsplit("/", 1)[-1] or "video.mp4")
        with httpx.stream("GET", src, follow_redirects=True, timeout=60) as r:
            if r.status_code != 200:
                return err(f"download failed ({r.status_code})")
            with target.open("wb") as fh:
                for chunk in r.iter_bytes(1 << 20):
                    fh.write(chunk)
    p = project.create(target, target.stem, b.get("brief", {}), move=True)
    shutil.rmtree(d, ignore_errors=True)
    return ok(p)


# ---------- projects ----------
async def projects(_: Request):
    return ok(project.list_projects())


def _project_view(pid: str) -> dict:
    p = project.load(pid)
    p.pop("trace", None)
    clips = []
    for cid in p.get("clips", []):
        try:
            tl = project.get_clip(pid, cid)
        except FileNotFoundError:
            continue
        r = project.latest_render(pid, cid)
        clips.append({**tl.summary(), "grade": tl.grade, "grade_intensity": tl.grade_intensity,
                      "video": f"/api/projects/{pid}/clips/{cid}/video?v={tl.version}" if r else None,
                      "poster": f"/api/projects/{pid}/clips/{cid}/poster?v={tl.version}" if r else None,
                      "final": bool(r and not r.stem.endswith("_preview")),
                      "job": JOBS.get(f"{pid}/{cid}", {}).get("state")})
    p["clips_view"] = clips
    p["claude"] = brain.status()
    return p


async def project_get(req: Request):
    pid = req.path_params["pid"]
    if not (project.pdir(pid) / "project.json").exists():
        return err("no such project", 404)
    if req.method == "DELETE":
        shutil.rmtree(project.pdir(pid))
        return ok({"deleted": pid})
    return ok(_project_view(pid))


async def project_brief(req: Request):
    return ok(project.set_brief(req.path_params["pid"], await req.json()))


async def project_start(req: Request):
    pid = req.path_params["pid"]
    if project.load(pid)["status"] == "working":
        return ok({"started": False})
    project.start(pid)
    return ok({"started": True})


async def project_thumb(req: Request):
    f = project.pdir(req.path_params["pid"]) / "thumb.jpg"
    return FileResponse(f) if f.exists() else Response(status_code=404)


async def transcript(req: Request):
    from .transcribe import sentences
    return ok(sentences(project.get_words(req.path_params["pid"])))


# ---------- clips ----------
def _bg(key: str, fn, *args):
    JOBS[key] = {"state": "working"}

    def run():
        try:
            fn(*args)
            JOBS[key] = {"state": "ready"}
        except Exception as e:
            JOBS[key] = {"state": "error", "error": str(e)}
    threading.Thread(target=run, daemon=True).start()


async def clip(req: Request):
    pid, cid = req.path_params["pid"], req.path_params["cid"]
    if req.method == "PUT":                  # agents and power users patch the EditGraph directly
        from .timeline import Timeline
        tl = Timeline.model_validate(await req.json())
        tl.id = cid
        project.save_clip(pid, tl)
        _bg(f"{pid}/{cid}", project.render_clip, pid, cid, True)
        return ok(tl.summary())
    return ok(json.loads(project.get_clip(pid, cid).model_dump_json()))


async def clip_video(req: Request):
    r = project.latest_render(req.path_params["pid"], req.path_params["cid"])
    return FileResponse(r, media_type="video/mp4") if r else Response(status_code=404)


async def clip_poster(req: Request):
    """A still from the latest render, so the card shows the clip (and the hook title) before play."""
    import asyncio
    from . import media
    pid, cid = req.path_params["pid"], req.path_params["cid"]
    r = project.latest_render(pid, cid)
    if not r:
        return Response(status_code=404)
    f = r.with_suffix(".poster.jpg")
    if not f.exists() or f.stat().st_mtime < r.stat().st_mtime:
        await asyncio.to_thread(media.thumbnail, r, f, 0.6, 540)
    return FileResponse(f, media_type="image/jpeg")


def _rebuild(pid: str, cid: str, style_name: str):
    old = project.get_clip(pid, cid)
    p = project.load(pid)
    from . import autoedit
    tl = autoedit.build(str(project.pdir(pid) / p["source"]), p["info"], project.get_words(pid), project.get_speech(pid),
                        old.moment, styles.get(style_name), style_name)
    tl.id, tl.version, tl.feedback = old.id, old.version, old.feedback
    project.save_clip(pid, tl)
    project.render_clip(pid, cid, preview=True)


async def clip_feedback(req: Request):
    pid, cid = req.path_params["pid"], req.path_params["cid"]
    b = await req.json()
    tl = project.get_clip(pid, cid)
    entry = learn.feedback(tl.style, b.get("score"), b.get("chips", []), b.get("note", ""), tl.summary())
    tl.feedback.append({k: entry[k] for k in ("score", "chips", "note", "lesson")})
    project.save_clip(pid, tl, bump=False)
    if b.get("redo", True):
        _bg(f"{pid}/{cid}", _rebuild, pid, cid, tl.style)
    return ok(entry)


async def clip_grade(req: Request):
    pid, cid = req.path_params["pid"], req.path_params["cid"]
    b = await req.json()
    tl = project.get_clip(pid, cid)
    tl.grade = b.get("look", tl.grade)
    tl.grade_intensity = float(b.get("intensity", tl.grade_intensity))
    project.save_clip(pid, tl)
    _bg(f"{pid}/{cid}", project.render_clip, pid, cid, True)
    return ok(tl.summary())


async def clip_export(req: Request):
    pid, cid = req.path_params["pid"], req.path_params["cid"]
    _bg(f"{pid}/{cid}", project.render_clip, pid, cid, False)
    return ok({"rendering": True})


async def clip_download(req: Request):
    pid, cid = req.path_params["pid"], req.path_params["cid"]
    kind = req.query_params.get("kind", "mp4")
    tl = project.get_clip(pid, cid)
    stem = re.sub(r"[^a-z0-9]+", "-", (tl.title or cid).lower()).strip("-")[:40] or cid
    if kind == "mp4":
        r = project.latest_render(pid, cid)
        return FileResponse(r, filename=f"{stem}.mp4") if r else err("not rendered yet", 404)
    if kind == "srt":
        return PlainTextResponse(export.srt(tl), headers={"Content-Disposition": f'attachment; filename="{stem}.srt"'})
    if kind == "xml":
        p = project.load(pid)
        return Response(export.fcpxml7(tl, project.pdir(pid) / p["source"], p["info"]), media_type="application/xml",
                        headers={"Content-Disposition": f'attachment; filename="{stem}-premiere.xml"'})
    return Response(tl.model_dump_json(indent=1), media_type="application/json",
                    headers={"Content-Disposition": f'attachment; filename="{stem}.timeline.json"'})


# ---------- looks ----------
async def looks(_: Request):
    return ok(grade.catalog())


async def look_still(req: Request):
    pid = req.path_params["pid"]
    look = req.path_params["look"]
    k = float(req.query_params.get("i", "1"))
    p = project.load(pid)
    cache = project.pdir(pid) / "looks"
    cache.mkdir(exist_ok=True)
    f = cache / f"{safe_name(look)}_{k:.2f}.jpg"
    if not f.exists():
        import asyncio
        at = float(req.query_params.get("t", min(5.0, p.get("info", {}).get("duration", 2) / 3)))
        await asyncio.to_thread(grade.still, project.pdir(pid) / p["source"], at, look, k, f)
    return FileResponse(f, media_type="image/jpeg")


async def look_match(req: Request):
    """Body = a reference image. Builds a custom look matched to it."""
    pid = req.query_params["pid"]
    name = req.query_params.get("name", "My match")
    ref = LIBRARY / "references" / f"match_{uuid.uuid4().hex[:6]}.jpg"
    ref.write_bytes(await req.body())
    p = project.load(pid)
    look = grade.match(ref, project.pdir(pid) / p["source"], min(5.0, p["info"]["duration"] / 3), name)
    return ok({"look": look})


# ---------- library ----------
async def library_sfx(_: Request):
    return ok(sfx.catalog())


async def library_sfx_audio(req: Request):
    f = sfx.resolve(req.path_params["key"])
    return FileResponse(f) if f else Response(status_code=404)


async def library_upload(req: Request):
    """PUT raw bytes. kind: sfx | reference | lut | avatar."""
    kind = req.path_params["kind"]
    name = safe_name(req.query_params.get("name", "file"))
    dest = {"sfx": LIBRARY / "sfx" / name, "reference": LIBRARY / "references" / name,
            "lut": LIBRARY / "luts" / name, "avatar": LIBRARY / "avatar.png"}.get(kind)
    if dest is None:
        return err("unknown kind")
    if kind == "lut" and dest.suffix.lower() != ".cube":
        return err("LUTs must be .cube files")
    with dest.open("wb") as fh:
        async for part in req.stream():
            fh.write(part)
    meta = LIBRARY / "references.json"
    if kind == "reference":
        refs = json.loads(meta.read_text()) if meta.exists() else []
        refs.insert(0, {"file": name, "note": req.query_params.get("note", ""), "tags": req.query_params.get("tags", "")})
        meta.write_text(json.dumps(refs, indent=2))
    return ok({"saved": name, "kind": kind})


async def library_refs(_: Request):
    meta = LIBRARY / "references.json"
    return ok(json.loads(meta.read_text()) if meta.exists() else [])


async def library_ref_file(req: Request):
    f = LIBRARY / "references" / safe_name(req.path_params["name"])
    return FileResponse(f) if f.exists() else Response(status_code=404)


async def prompt_list(req: Request):
    if req.method == "POST":
        b = await req.json()
        return ok(prompts.add(b.get("kind", "idea"), b.get("title", "Untitled"), b.get("text", "")))
    return ok(prompts.library(req.query_params.get("kind")))


async def prompt_delete(req: Request):
    prompts.remove(req.path_params["id"])
    return ok({"deleted": True})


async def prompt_enhance(req: Request):
    b = await req.json()
    import asyncio
    res = await asyncio.to_thread(prompts.enhance, b.get("text", ""), b.get("target", "video"), b.get("style", "jason"))
    return ok(res)


async def style_list(_: Request):
    return ok(styles.list_styles())


async def journal(_: Request):
    return ok({"entries": learn.journal(), "scoreboard": learn.scoreboard()})


async def index(_: Request):
    return FileResponse(WEB / "index.html")


P = "/api/projects/{pid}"
C = P + "/clips/{cid}"
routes = [
    Route("/", index),
    Route("/api/status", status),
    Route("/api/settings", settings, methods=["GET", "POST"]),
    Route("/api/uploads", upload_init, methods=["POST"]),
    Route("/api/uploads/{uid}", upload_chunk, methods=["GET", "PUT"]),
    Route("/api/uploads/{uid}/complete", upload_complete, methods=["POST"]),
    Route("/api/import", import_source, methods=["POST"]),
    Route("/api/projects", projects),
    Route(P, project_get, methods=["GET", "DELETE"]),
    Route(P + "/brief", project_brief, methods=["POST"]),
    Route(P + "/start", project_start, methods=["POST"]),
    Route(P + "/thumb", project_thumb),
    Route(P + "/transcript", transcript),
    Route(P + "/look/{look}", look_still),
    Route(C, clip, methods=["GET", "PUT"]),
    Route(C + "/video", clip_video),
    Route(C + "/poster", clip_poster),
    Route(C + "/feedback", clip_feedback, methods=["POST"]),
    Route(C + "/grade", clip_grade, methods=["POST"]),
    Route(C + "/export", clip_export, methods=["POST"]),
    Route(C + "/download", clip_download),
    Route("/api/looks", looks),
    Route("/api/looks/match", look_match, methods=["POST"]),
    Route("/api/library/sfx", library_sfx),
    Route("/api/library/sfx/{key:path}", library_sfx_audio),
    Route("/api/library/references", library_refs),
    Route("/api/library/references/{name}", library_ref_file),
    Route("/api/library/{kind}", library_upload, methods=["PUT"]),
    Route("/api/prompts", prompt_list, methods=["GET", "POST"]),
    Route("/api/prompts/enhance", prompt_enhance, methods=["POST"]),
    Route("/api/prompts/{id}", prompt_delete, methods=["DELETE"]),
    Route("/api/styles", style_list),
    Route("/api/journal", journal),
    Mount("/web", StaticFiles(directory=str(WEB)), name="web"),
    Mount("/site", StaticFiles(directory=str(ROOT / "site"), html=True), name="site"),   # the landing page
]

app = Starlette(routes=routes)


def serve(host: str = "127.0.0.1", port: int = 8787) -> None:
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="warning")
