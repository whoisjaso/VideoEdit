"""Kairos CLI.

  python -m kairos serve [--host 0.0.0.0] [--port 8787]   web app + API
  python -m kairos mcp                                    MCP server (stdio) for Claude / agents
  python -m kairos run VIDEO [--count 5] [--length medium] [--style jason] [--about "..."]
  python -m kairos status
"""
from __future__ import annotations

import argparse
import json


def main() -> None:
    ap = argparse.ArgumentParser(prog="kairos")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("serve")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8787)
    sub.add_parser("mcp")
    r = sub.add_parser("run", help="long video in, edited clips out")
    r.add_argument("video")
    r.add_argument("--count", type=int, default=5)
    r.add_argument("--length", choices=["short", "medium", "long"], default="medium")
    r.add_argument("--style", default="jason")
    r.add_argument("--about", default="")
    r.add_argument("--final", action="store_true", help="also render 1080x1920 finals")
    sub.add_parser("status")
    a = ap.parse_args()

    if a.cmd == "serve":
        from .server import serve
        print(f"Kairos on http://{a.host}:{a.port}")
        serve(a.host, a.port)
    elif a.cmd == "mcp":
        from .mcp_server import main as mcp_main
        mcp_main()
    elif a.cmd == "status":
        from . import blender, brain, transcribe
        print(json.dumps({"claude": brain.status(), "transcribers": transcribe.available(),
                          "blender": blender.available()}, indent=2))
    elif a.cmd == "run":
        from . import project
        p = project.create(a.video, brief={"count": a.count, "length": a.length, "style": a.style, "about": a.about})
        print("project", p["id"])
        project.run_pipeline(p["id"])
        p = project.load(p["id"])
        if p["status"] != "ready":
            raise SystemExit(f"failed: {p.get('error')}")
        for cid in p["clips"]:
            out = project.render_clip(p["id"], cid, preview=False) if a.final else project.latest_render(p["id"], cid)
            tl = project.get_clip(p["id"], cid)
            print(f"{tl.score:>4}  {tl.duration:5.1f}s  {tl.title[:40]:<40}  {out}")


if __name__ == "__main__":
    main()
