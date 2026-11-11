"""Narration script as recorded. One entry per spoken line: (id, text, gap_after_s).

gap_after: 0.42 = sentence gap inside a paragraph, 0.75 = paragraph break,
1.25 = a marked pause ( · ) from the brief. Lists get their own entries so the
pauses between items are deliberate instead of whatever the voice engine picks.
Bracketed on-screen cards are not here; they live in src/film.py.

Three lines differ from the brief's script. Each is tagged CHANGED and listed in
REPORT.md with the before/after and the reason (the lens: no invented numbers,
and a model is called a model).
"""
S, P, B = 0.36, 0.62, 1.0    # sentence gap, paragraph gap, marked pause ( · )

LINES = [
 # --- hook, spoken (the silent type hook plays before this) ---
 ("hook1", "Your brain is racist.", 0.55),
 ("hook2", "So is mine.", 0.70),
 ("hook3", "And before you close this, hear the second half: it's not because either of us chose it.", B),

 # --- one job ---
 ("job1", "Here's the thing nobody says out loud.", S),
 ("job2", "Your brain has one job.", 0.55),
 ("job3", "Not to be fair.", 0.38),
 ("job4", "Not to be moral.", 0.38),
 ("job5", "Not to be a good person.", 0.55),
 ("job6", "One job: keep you alive long enough to do it again tomorrow.", P),

 # --- pattern-match ---
 ("pat1", "To do that job, it can't think. Thinking is slow.", S),
 ("pat2", "So it pattern-matches.", S),
 ("pat3", "It takes everything it has ever seen and builds a script:", 0.30),
 ("pat4", "when I see this, expect that.", S),
 ("pat5", "And it runs that script before you've finished seeing the thing.", B),

 # --- cultivation ---
 ("cul1", "So where did the script come from?", P),
 ("cul2", "You didn't write it. You absorbed it.", S),
 ("cul3", "Every movie, every show, every song, every clip on your feed since you were four years old.", S),
 ("cul4", "Researchers have a name for this: cultivation.", S),
 ("cul5", "The more you watch, the more the world on the screen becomes the world you expect off it.", P),
 ("cul6", "And the screen has been very consistent.", 0.9),

 # --- the three characters (hard cuts) ---
 ("chA1", "The robber.", 0.40), ("chA2", "The dealer.", 0.40), ("chA3", "The gangster with the baby momma.", 0.85),
 ("chB1", "The cartel.", 0.40), ("chB2", "Seven kids.", 0.40), ("chB3", "Here illegally.", 0.85),
 ("chC1", "Corporate.", 0.40), ("chC2", "Divorced.", 0.40), ("chC3", "Nine to five.", 0.40), ("chC4", "Figurehead.", B),

 # --- the IAT ---
 ("iat1", "Say that's not you. Say you don't believe any of that.", S),
 ("iat2", "You might be right. You don't.", 0.45),
 ("iat3", "Your brain does.", P),
 ("iat4", "There's a test for it, the implicit association test, millions of people have taken it,", 0.25),
 # CHANGED: was "most people's brains, including people of every race, pair ...". Nosek et al. 2007: Black
 # participants show no implicit preference on average, so the claim is split into two true sentences.
 ("iat5", "and most people's brains pair the same faces with the same words faster than the others.", S),
 ("iat5b", "And it shows up in people of every race.", S),
 ("iat6", "Not because they decided to.", 0.40),
 ("iat7", "Because the script was already there.", B),

 # --- the street, pass one ---
 ("st1", "Here's what that looks like.", P),
 ("st2", "It's night. You're walking.", S),
 ("st3", "You've got your phone, your watch, your keys.", S),
 ("st4", "Someone's walking toward you.", 0.55),
 ("st5", "Tank top.", 0.42), ("st6", "Pants low.", 0.42), ("st7", "Black.", P),
 ("st8", "You don't think, that man will rob me. You're not that person.", 0.50),
 ("st9", "You just...", 0.55),
 ("st10", "cross the street.", 1.0),
 ("st11", "Your brain ran the script and moved your feet before your conscience got a vote.", B),

 # --- the street, pass two ---
 ("sx1", "Now run it again.", 0.50),
 ("sx2", "Same street. Same night.", S),
 ("sx3", "A man in a suit.", 0.42), ("sx4", "Clean shaven.", 0.42), ("sx5", "White.", P),
 ("sx6", "You don't cross.", B),

 ("ch1", "Was the first man dangerous? You have no idea. He was walking home.", S),
 ("ch2", "Was the second man safe? You have no idea either.", S),
 ("ch3", "Your brain didn't check. It never checks.", S),
 ("ch4", "Checking is slow, and slow is how animals die.", S),
 ("ch5", "It saw the pattern from the movies and it acted.", P),
 ("ch6", "That's the whole mechanism.", 0.50),
 ("ch7", "Not hate.", 0.50),
 ("ch8", "Prediction.", B),

 # --- two heads ---
 ("two1", "Now here's where it gets dangerous.", S),
 ("two2", "Because the script doesn't run in one head.", 0.50),
 ("two3", "It runs in both.", B),

 # --- the traffic stop ---
 ("ts1", "A police officer pulls a car over.", S),
 ("ts2", "Loud music. White tank top. The car smells like weed.", P),
 ("ts3", "The officer's brain runs its script before he's out of the cruiser.", 0.50),
 ("ts4", "Gangster.", 0.42), ("ts5", "Gangster means gun.", 0.42), ("ts6", "Gun means I might not go home.", P),
 ("ts7", "His hand is already on his belt and his voice is already sharp and he doesn't know he did either one.", B),
 ("ts8", "The driver's brain runs its script before the window's down.", 0.50),
 ("ts9", "Cop.", 0.42), ("ts10", "Cop means this is how people like me die.", 0.42),
 ("ts11", "He's going to escalate.", 0.42), ("ts12", "Don't give him control.", P),
 ("ts13", "His shoulders are up, his answers are short, his hands are moving when they should be still, and he doesn't know he did any of that either.", B),
 ("ts14", "Two men. Neither one has done anything.", S),
 ("ts15", "Both of them are now acting exactly like the other one's script said they would.", P),
 ("ts16", "The officer sees the short answers and the moving hands:", 0.30), ("ts17", "see, suspicious.", S),
 ("ts18", "The driver sees the sharp voice and the hand on the belt:", 0.30), ("ts19", "see, he's about to do it.", P),
 ("ts20", "Each one is proving the other one's movie right.", 0.50),
 ("ts21", "In real time.", 0.42), ("ts22", "With their bodies.", B),

 ("news1", "That is the thing we keep watching on the news and calling a few bad people.", S),
 ("news2", "It's two scripts, installed by the same screens, colliding in a parking lot.", B),

 # --- the other direction ---
 ("od1", "And it runs the other direction too.", 0.50),
 ("od2", "Quieter.", B),
 ("od3", "Because your brain isn't just watching other people.", S),
 ("od4", "It's watching you, trying to figure out who you are and how someone like you is supposed to act.", P),
 ("od5", "So a Black kid grows up watching the screen.", S),
 ("od6", "What does the screen show him that looks like him?", 0.60),
 ("od7", "The rapper.", 0.40), ("od8", "The athlete.", 0.40), ("od9", "The dealer.", 0.40), ("od10", "The one in the cell.", P),
 ("od11", "And the part of his brain whose job is to figure out, how am I supposed to be, takes notes.", S),
 ("od12", "Not, I want to be that.", 0.40),
 ("od13", "Just: that's what we are.", S),
 ("od14", "And it starts, quietly, acting it out.", S),
 ("od15", "The walk. The voice. The things you don't try because people like you don't do that.", P),
 ("od16", "And every time he acts it out, his brain goes:", 0.30),
 ("od17", "see? Told you. That's us.", P),
 ("od18", "Repetition becomes identity.", 0.55),
 ("od19", "Identity becomes a life.", B),
 ("od20", "Same for the Mexican kid who's only ever seen himself on screen as the cartel's nephew.", S),
 ("od21", "Same for the white kid who's only ever seen himself as the guy in the cubicle with the divorce.", S),
 ("od22", "The screen hands everyone a character.", 0.50),
 ("od23", "The brain, trying to help, learns the lines.", B),

 # --- the switch ---
 ("sw1", "And then we switch.", B),
 ("sw2", "You know the voice.", S),
 ("sw3", "The one you use in the interview. On the sales call. In the meeting with the people who don't look like you.", S),
 ("sw4", "A little higher. A little more careful. The words you'd never use at home.", P),
 ("sw5", "Code-switching.", 0.42), ("sw6", "Corporate voice.", 0.42), ("sw7", "Being professional.", P),
 ("sw8", "That's not fake, exactly.", S),
 ("sw9", "That's your brain, having read the room's script about people like you, trying to not match it.", S),
 ("sw10", "You're performing against the character they expect, so you don't trigger their script.", S),
 ("sw11", "And it costs something. Every time.", S),
 ("sw12", "It's exhausting to be two people.", 0.50),
 ("sw13", "And the second one is never quite you.", B),

 # --- whose fault ---
 ("wf1", "So.", 0.50),
 ("wf2", "Whose fault is this?", B),
 ("wf3", "Not yours, that it's there.", 0.55),
 ("wf4", "You didn't write it.", S),
 # CHANGED: "ten thousand hours" -> "thousands of hours" (no named study behind the number)
 ("wf5", "It was written into you by thousands of hours of screens before you were old enough to say no.", B),

 # --- the observer ---
 ("ob1", "But here's the part that matters.", S),
 ("ob2", "There's a piece of you that can watch the script run.", S),
 ("ob3", "The part that noticed, just now, that you'd cross the street.", S),
 ("ob4", "The part that hears the corporate voice come out of your mouth and goes, that's not me.", P),
 ("ob5", "Call it the observer.", 0.55),
 ("ob6", "It's the only part of you that was never on the screen.", B),

 # --- the half-second ---
 # CHANGED: added "Here's a model of it." and "about" (the timing is a model, not a measurement)
 ("hs0", "Here's a model of it.", 0.50),
 ("hs1", "The script runs in about a quarter of a second.", S),
 ("hs2", "The observer catches it in the half-second after.", P),
 ("hs3", "That half-second is the only place freedom has ever lived.", B),

 # --- the new script ---
 ("ns1", "You can't delete the script. Nobody can.", S),
 ("ns2", "But every time you catch it, every time you notice the feet moving or the voice changing or the shoulders going up, and you decide anyway,", 0.35),
 ("ns3", "you write one line of a new one.", P),
 ("ns4", "Do that enough times, and the brain, which only ever wanted to keep you alive, starts running the new script instead.", 4.6),   # the silent hook card returns in this gap

 # --- close (the hook card returns, silent, before this line) ---
 ("cl1", "Now you know whose job it is to do something about that.", 1.4),
]
