"""The EditGraph: Premiere's sequence model, stripped to what an agent needs.

A Premiere sequence is tracks of clips with in/out points, effects, keyframes, titles,
audio and markers. Kairos keeps exactly that, as plain JSON an agent can read and patch:

    Timeline
      segments  -> V1/A1: ordered source ranges (in/out, speed, crop, zoom keyframes)
      captions  -> the caption track (word-timed pages, keyword colors)
      graphics  -> V2+: titles, pop-ups, CTA, Blender renders, images
      sfx       -> A2+: sound cues on the output clock
      markers   -> notes for people and agents

Every time in captions/graphics/sfx/markers is on the OUTPUT clock (seconds into the clip).
Segments map output time back to the source.
"""
from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


SCHEMA = "kairos.timeline/1"     # versioned, diff-friendly JSON (an idea borrowed from EffectCraft's .ecproj)

Ease = Literal["linear", "ease", "ease_in", "ease_out", "hold", "overshoot"]


class Keyframe(BaseModel):
    """After Effects keyframe semantics: `ease` is the interpolation INTO this keyframe
    (hold on the previous keyframe freezes the value until this one)."""
    t: float                      # seconds from the start of the segment's output
    value: float
    ease: Ease = "ease"


class Shake(BaseModel):
    """A decaying camera shake, like AE's wiggle() expression, for impact beats."""
    t: float                      # seconds from the start of the segment's output
    dur: float = 0.35
    amp: float = 14               # pixels at 1080 wide


class Segment(BaseModel):
    src_in: float
    src_out: float
    speed: float = 1.0            # 0.5 = slow-mo (the curse-word punchline)
    pitch_drop: bool = False      # slow-mo with the octave drop (Jason's rule)
    crop_x: float = 0.5           # 0..1 horizontal centre of the 9:16 window in a wide source
    zoom: list[Keyframe] = Field(default_factory=list)   # scale over time, 1.0 = no zoom
    shake: list[Shake] = Field(default_factory=list)
    tag: str = ""                 # section name: hook, cold_open, body, payoff, cta

    @property
    def out_dur(self) -> float:
        return (self.src_out - self.src_in) / self.speed


class Word(BaseModel):
    t0: float
    t1: float
    w: str
    color: Literal["white", "gold", "green", "red"] = "white"


class Caption(BaseModel):
    start: float
    end: float
    words: list[Word]
    hidden: bool = False          # a title/graphic already says these words

    @property
    def text(self) -> str:
        return " ".join(w.w for w in self.words)


class Graphic(BaseModel):
    id: str = Field(default_factory=lambda: new_id("g"))
    kind: Literal["title", "popup", "counter", "cta", "image", "blender", "lower_third"]
    start: float
    end: float
    text: str = ""
    sub: str = ""
    color: Literal["white", "gold", "green", "red"] = "gold"
    position: Literal["top", "center", "bottom", "behind"] = "top"
    asset: str = ""               # image / rendered overlay path for image|blender
    params: dict = Field(default_factory=dict)


class SfxCue(BaseModel):
    t: float
    name: str                     # library key, e.g. "whoosh", "ios/ios_tink"
    gain: float = 0.8
    why: str = ""                 # the playbook rule that placed it


class Marker(BaseModel):
    t: float
    note: str


class Timeline(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)
    schema_: str = Field(default=SCHEMA, alias="schema")
    id: str = Field(default_factory=lambda: new_id("clip"))
    title: str = ""
    hook: str = ""
    why: str = ""                 # why this moment was chosen
    score: float = 0.0            # predicted strength 0..10
    style: str = "jason"
    width: int = 1080
    height: int = 1920
    fps: int = 30
    grade: str = "moody"          # a look id from grade.catalog(): moody, teal_orange, lut:<file>, custom:<name>
    grade_intensity: float = 1.0  # 0..1.5
    segments: list[Segment] = Field(default_factory=list)
    captions: list[Caption] = Field(default_factory=list)
    graphics: list[Graphic] = Field(default_factory=list)
    sfx: list[SfxCue] = Field(default_factory=list)
    markers: list[Marker] = Field(default_factory=list)
    version: int = 1
    moment: dict = Field(default_factory=dict)      # the source moment, so a redo can rebuild it
    check_words: list[dict] = Field(default_factory=list)   # low-confidence words to confirm before posting
    feedback: list[dict] = Field(default_factory=list)

    @property
    def duration(self) -> float:
        return sum(s.out_dur for s in self.segments)

    def src_to_out(self, t_src: float) -> float | None:
        """Where a source timestamp lands in the clip (None if it was cut)."""
        acc = 0.0
        for s in self.segments:
            if s.src_in - 1e-6 <= t_src <= s.src_out + 1e-6:
                return acc + (t_src - s.src_in) / s.speed
            acc += s.out_dur
        return None

    def out_to_src(self, t_out: float) -> float | None:
        acc = 0.0
        for s in self.segments:
            if t_out <= acc + s.out_dur + 1e-6:
                return s.src_in + (t_out - acc) * s.speed
            acc += s.out_dur
        return None

    def summary(self) -> dict:
        return {
            "id": self.id, "title": self.title, "hook": self.hook, "why": self.why,
            "score": round(self.score, 1), "duration": round(self.duration, 2),
            "segments": len(self.segments), "captions": len(self.captions),
            "graphics": len(self.graphics), "sfx": len(self.sfx), "version": self.version,
            "check_words": self.check_words,
        }
