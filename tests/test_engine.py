"""Engine tests. Run: python -m unittest discover -s tests   (needs ffmpeg; ~1 minute)"""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="kairos-test-"))
os.environ["KAIROS_DATA"] = str(TMP / "data")
os.environ.pop("ANTHROPIC_API_KEY", None)          # tests exercise the offline path

from kairos import autoedit, export, grade, learn, media, moments, project, render, styles  # noqa: E402
from kairos.timeline import Keyframe, Segment, Timeline  # noqa: E402

SCRIPT = ("nobody tells you the truth about money . you think discipline is the problem . the real problem is you "
          "never decided . i made seven thousand dollars in one week . stop waiting for permission that's bullshit . "
          "purpose comes first then the money follows .").split()


def fake_words(total: float) -> list[dict]:
    words, t = [], 0.3
    while t < total - 1:
        for w in SCRIPT:
            if w == ".":
                t += 0.9
                continue
            d = 0.2 + 0.03 * len(w)
            words.append({"word": w, "start": round(t, 2), "end": round(t + d, 2), "conf": 0.95})
            t += d + 0.06
            if t > total - 1:
                break
        t += 1.8
    return words


def make_video(path: Path, seconds: int = 40, size: str = "1280x720") -> Path:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=s={size}:r=30:d={seconds}",
                    "-f", "lavfi", "-i", f"aevalsrc='0.3*sin(2*PI*220*t)*gt(mod(t\\,9)\\,2)':s=48000:d={seconds}",
                    "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", str(path)], check=True)
    return path


class Units(unittest.TestCase):
    def test_money_phrase(self):
        m = autoedit.money_phrase
        self.assertEqual(m("seven thousand dollars in".split()), "$7,000")
        self.assertEqual(m("a hundred grand".split()), "$100,000")
        self.assertEqual(m("two hundred fifty thousand dollars".split()), "$250,000")
        self.assertIsNone(m("one week".split()))

    def test_timeline_clock(self):
        tl = Timeline(segments=[Segment(src_in=10, src_out=12), Segment(src_in=20, src_out=21, speed=0.5)])
        self.assertAlmostEqual(tl.duration, 4.0)
        self.assertAlmostEqual(tl.src_to_out(20.5), 3.0)
        self.assertIsNone(tl.src_to_out(15))
        self.assertAlmostEqual(tl.out_to_src(1.0), 11.0)
        self.assertEqual(json.loads(tl.model_dump_json())["schema"], "kairos.timeline/1")

    def test_keep_spans_respect_pauses(self):
        w = [{"word": "a", "start": 0, "end": 0.5}, {"word": "b", "start": 1.0, "end": 1.5}, {"word": "c", "start": 5.0, "end": 5.5}]
        spans = autoedit._keep_spans(w, 0, 6, gap_max=1.4, gap_keep=0.75)
        self.assertEqual(len(spans), 2)                       # 0.5s pause kept, 3.5s dead air cut
        self.assertAlmostEqual(spans[1][0] - spans[0][1], 3.5 - 0.75, places=2)

    def test_zoom_expression_evaluates(self):
        e = render.zoom_expr([Keyframe(t=0, value=1), Keyframe(t=1, value=1.2, ease="overshoot"), Keyframe(t=2, value=1.2, ease="hold")])
        self.assertIn("if(lt(t,1.0000)", e)

    def test_heuristic_moments(self):
        ms = moments.heuristic(fake_words(120), 3, 20, 40)
        self.assertTrue(1 <= len(ms) <= 3)
        for a, b in zip(ms, ms[1:]):
            self.assertTrue(a["end"] <= b["start"] or b["end"] <= a["start"])

    def test_learning_is_bounded(self):
        for _ in range(30):
            learn.feedback("jason", 6, ["More zooms", "Bigger captions"], "", {"id": "x"})
        s = styles.get("jason")
        self.assertGreaterEqual(s["zoom"]["every"], 2.5)
        self.assertLessEqual(s["caption"]["size"], 130)
        (TMP / "data" / "styles" / "jason.json").unlink()


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = make_video(TMP / "talk.mp4")
        cls.p = project.create(cls.src, "talk", {"count": 1, "length": "short", "style": "jason"})
        (project.pdir(cls.p["id"]) / "words.json").write_text(json.dumps(fake_words(40)))
        project.run_pipeline(cls.p["id"])
        cls.p = project.load(cls.p["id"])

    def test_pipeline_ready(self):
        self.assertEqual(self.p["status"], "ready", self.p.get("trace"))
        self.assertEqual(len(self.p["clips"]), 1)

    def test_render_is_vertical_and_loud_enough(self):
        cid = self.p["clips"][0]
        out = project.render_clip(self.p["id"], cid, preview=True)
        info = media.probe(out)
        self.assertEqual((info["width"], info["height"]), (540, 960))
        tl = project.get_clip(self.p["id"], cid)
        self.assertAlmostEqual(info["duration"], tl.duration, delta=0.15)

    def test_clip_has_the_recipe(self):
        tl = project.get_clip(self.p["id"], self.p["clips"][0])
        names = {c.name for c in tl.sfx}
        self.assertIn("deep_bass", names)                     # hook impact
        self.assertIn("whoosh", names)                        # every zoom gets a whoosh
        self.assertTrue(any(g.kind == "title" for g in tl.graphics))
        self.assertTrue(any(w.color != "white" for c in tl.captions for w in c.words))

    def test_exports(self):
        tl = project.get_clip(self.p["id"], self.p["clips"][0])
        doc = export.fcpxml7(tl, self.src, self.p["info"])
        from xml.dom import minidom
        minidom.parseString(doc)
        self.assertIn("-->", export.srt(tl))

    def test_every_look_renders(self):
        for look in grade.catalog():
            out = TMP / f"look_{look['id'].replace(':', '_')}.jpg"
            grade.still(self.src, 2, look["id"], 1.0, out, width=120)
            self.assertTrue(out.exists(), look["id"])


if __name__ == "__main__":
    unittest.main()
