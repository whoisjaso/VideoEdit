"""Chapter II (Caesar) settings. Used by parse/voice/build_scene/world_scene/metfind when CH=caesar.
Chapter I keeps its tables inside each script; anything not set here falls back to them."""
SCRIPT = "../scripts/02-caesar.md"
SCENES = "scenes_caesar.json"
LABEL = "Plutarch's Lives  ·  Caesar"
SUB = "Chapter II  ·  Caesar"
PROOF = None            # chapter I re-used a separately built proof for scene 4; chapter II renders every scene
PLACE = {0: "Spain  ·  61 BC", 1: "Chaeronea  ·  c. AD 100", 2: "Rome  ·  82 BC", 3: "The Aegean  ·  75 BC", 4: "The Alps  ·  61 BC",
 5: "Gaul  ·  58–50 BC", 6: "Alesia  ·  52 BC", 7: "The Rubicon  ·  49 BC", 8: "The Aous  ·  48 BC", 9: "Alexandria  ·  48 BC",
 10: "Zela  ·  47 BC", 11: "Rome  ·  44 BC", 12: "Rome, the Lupercalia  ·  44 BC", 13: "Rome  ·  14 March, 44 BC",
 14: "Rome  ·  the Ides of March, 44 BC", 15: "The Curia of Pompey  ·  44 BC", 16: "Rome  ·  44 BC", 17: "", 18: "Plutarch's Lives"}
HEROES = {0: ["I have done nothing great.", "You'll be him."], 1: ["Watch the choices."],
 2: ["What do you do?", "There are many Mariuses in this boy.", "I don't bend."],
 3: ["Ask for fifty.", "who are we, here?", "We are Caesar."], 4: ["I would rather be first here than second in Rome."],
 5: ["He made war his medicine.", "we don't use excuses."], 6: ["He doesn't say a word."],
 7: ["What do you do?", "Let the die be cast.", "What's your Rubicon?"], 8: ["You're carrying Caesar, and Caesar's luck.", "It doesn't move oceans."],
 9: ["And Caesar weeps.", "Remember his name."], 10: ["Veni, vidi, vici."], 11: ["Remember that you are Caesar."],
 12: ["It just stops listening to them."], 13: ["A sudden one."], 14: ["What do you do?", "Unread.", "it makes you deaf."],
 15: ["The statue of Pompey."], 16: ["the name, and the envy that came with it."], 17: ["Decide who you are before the room does.", "Sleep well."],
 18: ["It's an investment.", "who are we, here?", "it's rented.", "Only in front of God, and yourself.", "We know how this is done.", "As them."]}
DUSTS = {0, 4, 7}
KEY = {"caesar", "rubicon", "pirates", "crown", "note", "brutus", "pompey", "ides", "luck", "river", "storm", "medicine", "excuse", "excuses",
       "sulla", "alexander", "warning", "deaf", "comparison", "scoreboard", "fifty", "village", "rome"}
ICON_EXTRA = [("crown", r"^(diadem|dictator)$"), ("scroll", r"^(note|notes|poems|speeches|list)$"), ("drop", r"^(sea|storm|waves|ocean|oceans)$"),
              ("sword", r"^(blades|daggers|pirates|soldiers)$"), ("eye", r"^(seer)$")]
HICON = {"remember that you are caesar.": "laurel", "veni, vidi, vici.": "laurel", "we are caesar.": "laurel", "you'll be him.": "laurel"}
# the ball goes dark when ego wins: from the unread note through the death; it returns for "Only the name"
DARK = {14: "Unread.", 15: None}
WORLD = {
 0: dict(music=[("dvorak_lento.ogg", 0, -15, None)], beds=[("fire_rumble.wav", -40, 0, None, None)]),
 1: dict(music=[("haydn_lark_adagio.ogg", 0, -15, None)], beds=[("market.wav", -40, -0.2, None, None)]),
 2: dict(music=[("coriolan.ogg", 0, -14, None)], beds=[("wind_prairie.wav", -40, 0, "fever", None)], hits=[("steps.mp3", 0, 4, "soldiers", -18, 0.3)]),
 3: dict(music=[("brahms2_ii.ogg", 0, -15, None)], beds=[("river_gentle.wav", -32, 0.2, None, None), ("fire_crackle.wav", -36, -0.2, "Now", None)],
         hits=[("laugh_group.wav", 1, 4, "laugh", -18, -0.3), ("men_drunk_laugh.wav", 0, 5, "charming", -20, 0.2)]),
 4: dict(music=[("mendel_scottish_i.ogg", 0, -15, None)], beds=[("wind_prairie.wav", -36, 0, None, None)], hits=[("eagle.wav", 2, 5, "Alps", -24, 0.4)]),
 5: dict(music=[("eroica_i.ogg", 0, -15, None)], beds=[("wind_prairie.wav", -38, 0, None, None)],
         hits=[("walk_dirt.wav", 0, 5, "marches", -22, -0.2), ("gallop_dirt.wav", 0, 5, "horseback", -20, 0.2)]),
 6: dict(music=[("brahms4_i.ogg", 0, -16, None)], beds=[("men_murmur.wav", -34, 0, None, None)], hits=[("hoof_clatter.mp3", 0, 4, "rides", -16, -0.3)]),
 7: dict(music=[("brahms_tragic.ogg", 0, -15, None)], beds=[("river_gentle.wav", -30, 0.2, "Rubicon", None), ("stallion_snore.wav", -38, -0.3, "edge", None)],
         hits=[("big_snort.wav", 0, 3, "edge", -20, -0.3)]),
 8: dict(music=[("brahms1_intro.ogg", 0, -15, None)], beds=[("river_rapids.wav", -26, 0, "storm", None), ("thunder_roll.wav", -30, 0, "storm", None)],
         hits=[("thunder_clap.wav", 0, 7, "crash", -14, 0.2)]),
 9: dict(music=[("dvorak_dumka.ogg", 0, -15, None)], beds=[("palace_murmur.wav", -36, 0, "Egypt", None)]),
 10: dict(music=[("mendel_italian_ii.ogg", 0, -15, None)], beds=[], hits=[("men_cheer.wav", 0, 5, "conquered", -20, 0)]),
 11: dict(music=[("brahms4_ii.ogg", 0, -15, None)], beds=[("court_murmur.wav", -34, 0, None, None)]),
 12: dict(music=[("brahms2_ii.ogg", 0, -16, None)], beds=[("party_crowd.wav", -30, 0, None, "stands")],
          hits=[("men_cheer.wav", 0, 5, "roars", -16, 0), ("men_cheer.wav", 1, 5, "cheers", -18, 0)]),
 13: dict(music=[("beet_q6_adagio.ogg", 0, -15, None)], beds=[("fire_crackle.wav", -38, 0, "dinner", None)]),
 14: dict(music=[("brahms_tragic.ogg", 0, -15, None)], beds=[("market.wav", -32, 0, "streets", "seer")]),
 15: dict(music=[("eroica_funebre.ogg", 0, -14, None)], beds=[("court_murmur.wav", -34, 0, None, "signal")],
          hits=[("sword_draw.wav", 0, 2.5, "blade", -12, 0.2), ("horrified.wav", 0, 6, "strikes", -16, 0)]),
 16: dict(music=[("grieg_ase.ogg", 0, -15, None)], beds=[("fire_rumble.wav", -34, 0, "pyre", None)], hits=[("swords_crowd.wav", 0, 6, "torches", -24, 0)]),
 17: dict(music=[("brahms3_iii.ogg", 0, -15, None)], beds=[]),
}
Q = {
 0: ["Julius Caesar", "Alexander the Great", "reading scroll", "Caesar weeping"],
 1: ["Plutarch", "Cicero", "Roman orator", "Roman street"],
 2: ["Sulla", "proscription Rome", "Marius", "Roman soldiers torches"],
 3: ["pirates", "Caesar pirates", "ancient galley", "pirate ship", "captive ship sea"],
 4: ["mountain village", "Alps village", "Julius Caesar", "Alexander the Great portrait"],
 5: ["Gauls", "Roman army march", "Roman legion", "Gallic war", "Roman soldiers camp"],
 6: ["Vercingetorix", "Alesia", "surrender chief", "Gallic warrior"],
 7: ["Rubicon", "Caesar crossing Rubicon", "river bridge night", "Roman cavalry"],
 8: ["storm at sea", "boat storm", "Caesar boat", "shipwreck"],
 9: ["Pompey", "death of Pompey", "Caesar Egypt", "Cleopatra Caesar", "signet ring"],
 10: ["Cato", "death of Cato", "Roman triumph", "triumph of Caesar"],
 11: ["Roman senate", "Caesar dictator", "Roman forum", "Caesar portrait"],
 12: ["Mark Antony", "Lupercalia", "crown laurel", "Caesar crown"],
 13: ["Roman banquet", "soothsayer", "Roman dinner", "Ides of March"],
 14: ["Calpurnia", "Calpurnia dream", "Caesar senate", "Roman crowd street"],
 15: ["death of Caesar", "assassination of Caesar", "Brutus", "Pompey statue", "Caesar murder"],
 16: ["Caesar funeral", "Antony oration", "comet", "Brutus ghost"],
 17: ["Julius Caesar portrait", "candle", "Caesar coin", "Roman coin"],
}
