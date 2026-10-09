// Ep05 engraving cutaways. Frames are 60 fps, local to each insert: f = (episode frame - insert start) * 2.
// Every time below comes from his words in captions.json (see make_scenes notes in the journal).
const W = (t, w) => ({ t, w });
window.SCENES = {
  // "I'm so perspicacious." Galileo: the device falls from the sun along its rays and lands on his eye (insight).
  persp: {
    len: 134,
    shots: [{ img: "galileo", from: 0, to: 134, x: 560, y: 800, w: 1500, fx: 0.355, fy: 0.43, z0: 1.0, z1: 1.09 }],
    dot: [
      { f: 0, shot: "galileo", fx: 0.48, fy: 0.15 },
      { f: 42, shot: "galileo", fx: 0.355, fy: 0.43, dur: 30, r: 74 },
    ],
    lines: [
      { words: [W(4, "I’m"), W(14, "so")], out: 32, y: 1430, size: 124 },
      { words: [W(42, "perspicacious.")], out: 1e9, y: 1430, size: 118 },
    ],
    defs: [{ t: 58, out: 1e9, y: 1610, text: "having a ready insight into things" }],
  },
  // "I'm so indefatigable." Goltzius' Great Hercules: the device drops onto his heart.
  indef: {
    len: 128,
    shots: [{ img: "hercules", from: 0, to: 128, x: 540, y: 760, w: 1400, fx: 0.42, fy: 0.33, z0: 1.06, z1: 1.0 }],
    dot: [
      { f: 0, shot: "hercules", fx: 0.47, fy: 0.03, from: [600, -40], dur: 6 },
      { f: 36, shot: "hercules", fx: 0.42, fy: 0.33, dur: 28, r: 78 },
    ],
    lines: [
      { words: [W(4, "I’m"), W(14, "so")], out: 28, y: 1430, size: 124 },
      { words: [W(36, "indefatigable.")], out: 1e9, y: 1430, size: 118 },
    ],
    defs: [{ t: 52, out: 1e9, y: 1610, text: "persisting tirelessly" }],
  },
  // "because my belief on who I am is so fucking high." Napoleon crossing the Alps: the device climbs boot, heart, hat.
  high: {
    len: 340,
    shots: [{ img: "napoleon", from: 0, to: 340, x: 540, y: 820, w: 1320, fx: 0.46, fy: 0.36, z0: 1.12, z1: 1.0 }],
    dot: [
      { f: 30, shot: "napoleon", fx: 0.40, fy: 0.49, from: [540, 1980], dur: 30, r: 62 },
      { f: 160, shot: "napoleon", fx: 0.46, fy: 0.36, dur: 34, r: 70 },
      { f: 314, shot: "napoleon", fx: 0.42, fy: 0.135, dur: 40, r: 96 },
    ],
    lines: [
      { words: [W(4, "because"), W(30, "my"), W(52, "belief")], out: 104, y: 1430, size: 124 },
      { words: [W(116, "on"), W(128, "who"), W(144, "I"), W(160, "am")], out: 206, y: 1430, size: 124 },
      { words: [W(216, "is"), W(266, "so"), W(288, "fucking"), W(314, "high.")], out: 1e9, y: 1430, size: 112 },
    ],
  },
  // "he is chosen by God himself, like handpicked from God himself, Yahweh Yeshua HaMashiach."
  // Polidoro's Creation of Adam: the device lands on God's fingertip, passes to Adam's hand, rises to God's face;
  // match cut on God's head into Preti's Moses, where God descends: the three names, one at a time.
  chosen: {
    len: 432,
    shots: [
      { img: "adam", from: 0, to: 300, x: 300, y: 860, w: 2900, fx: 0.375, fy: 0.375, z0: 1.0, z1: 1.22 },
      { img: "moses", from: 300, to: 432, x: 540, y: 600, w: 2600, fx: 0.42, fy: 0.31, z0: 1.0, z1: 1.08, match: { shot: "adam", fx: 0.515, fy: 0.08, f: 300 } },
    ],
    dot: [
      { f: 28, shot: "adam", fx: 0.385, fy: 0.365, from: [540, -40], dur: 26, r: 66 },
      { f: 184, shot: "adam", fx: 0.335, fy: 0.395, dur: 30, r: 60 },
      { f: 240, shot: "adam", fx: 0.515, fy: 0.08, dur: 34, r: 84 },
      { f: 334, shot: "moses", fx: 0.42, fy: 0.31, dur: 30, r: 92 },
    ],
    lines: [
      { words: [W(4, "he"), W(16, "is"), W(28, "chosen")], out: 72, y: 1430, size: 124 },
      { words: [W(80, "by"), W(94, "God"), W(122, "himself,")], out: 132, y: 1430, size: 124 },
      { words: [W(134, "like"), W(184, "handpicked")], out: 212, y: 1430, size: 118 },
      { words: [W(218, "from"), W(240, "God"), W(274, "himself,")], out: 326, y: 1430, size: 124 },
      { words: [W(334, "Yahweh.")], out: 348, y: 1430, size: 132 },
      { words: [W(354, "Yeshua.")], out: 376, y: 1430, size: 132 },
      { words: [W(382, "HaMashiach.")], out: 1e9, y: 1430, size: 124 },
    ],
  },
};
