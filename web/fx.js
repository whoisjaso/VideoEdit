// Feel: sounds + haptics + confetti. Every sound is synthesized here (no samples), so it ships with
// the open-source app. Haptics: navigator.vibrate on Android/Chrome; on iOS Safari (18+), toggling a
// hidden <input type=checkbox switch> fires the system haptic, the only web haptic iOS exposes.
const store = {
  get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } },
};

let ctx = null;
const audio = () => {
  if (!store.get("sound", true)) return null;
  try {
    ctx = ctx || new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === "suspended") ctx.resume();
    return ctx;
  } catch { return null; }
};

function tone(freq, start, dur, { type = "sine", gain = 0.18, slide = 0 } = {}) {
  const a = audio();
  if (!a) return;
  const t0 = a.currentTime + start;
  const o = a.createOscillator();
  const g = a.createGain();
  o.type = type;
  o.frequency.setValueAtTime(freq, t0);
  if (slide) o.frequency.exponentialRampToValueAtTime(freq * slide, t0 + dur);
  g.gain.setValueAtTime(0.0001, t0);
  g.gain.exponentialRampToValueAtTime(gain, t0 + 0.012);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  o.connect(g).connect(a.destination);
  o.start(t0);
  o.stop(t0 + dur + 0.02);
}

let iosSwitch = null;
function buzz(pattern) {
  if (!store.get("haptics", true)) return;
  if (navigator.vibrate) { navigator.vibrate(pattern); return; }
  if (!iosSwitch) {
    const label = document.createElement("label");
    label.style.cssText = "position:fixed;opacity:0;pointer-events:none;width:1px;height:1px;overflow:hidden";
    label.innerHTML = '<input type="checkbox" switch>';
    document.body.appendChild(label);
    iosSwitch = label;
  }
  const pulses = Array.isArray(pattern) ? Math.ceil(pattern.length / 2) : 1;
  for (let i = 0; i < pulses; i++) setTimeout(() => iosSwitch.click(), i * 70);
}

export const fx = {
  tap() { tone(520, 0, 0.05, { type: "triangle", gain: 0.06 }); buzz(6); },
  select() { tone(660, 0, 0.07, { type: "triangle", gain: 0.1 }); tone(990, 0.04, 0.09, { gain: 0.06 }); buzz(10); },
  success() {   // bright two-step "that's right"
    tone(784, 0, 0.12, { type: "triangle", gain: 0.16 });
    tone(1175, 0.09, 0.22, { type: "triangle", gain: 0.16 });
    tone(2350, 0.1, 0.18, { gain: 0.03 });
    buzz([12, 50, 18]);
  },
  error() { tone(330, 0, 0.16, { type: "square", gain: 0.05, slide: 0.8 }); tone(247, 0.12, 0.22, { type: "square", gain: 0.05 }); buzz([30, 40, 30]); },
  celebrate() {  // rising arpeggio + sparkle
    [523, 659, 784, 1047, 1319].forEach((f, i) => tone(f, i * 0.075, 0.28, { type: "triangle", gain: 0.13 }));
    [2093, 2637, 3136].forEach((f, i) => tone(f, 0.4 + i * 0.06, 0.25, { gain: 0.035 }));
    buzz([15, 40, 15, 40, 60]);
    confetti();
  },
  whoosh() { tone(220, 0, 0.25, { type: "sawtooth", gain: 0.025, slide: 3 }); },
  get sound() { return store.get("sound", true); },
  set sound(v) { store.set("sound", v); },
  get haptics() { return store.get("haptics", true); },
  set haptics(v) { store.set("haptics", v); },
};

export function confetti(n = 90) {
  const box = document.createElement("div");
  box.className = "confetti";
  const colors = ["#58cc02", "#1cb0f6", "#ffc800", "#ff4b4b", "#ce82ff", "#ff9600"];
  for (let i = 0; i < n; i++) {
    const p = document.createElement("i");
    p.style.left = `${Math.random() * 100}%`;
    p.style.background = colors[i % colors.length];
    p.style.setProperty("--dx", `${(Math.random() - 0.5) * 240}px`);
    p.style.setProperty("--rot", `${Math.random() * 900 - 450}deg`);
    p.style.animationDelay = `${Math.random() * 0.35}s`;
    p.style.animationDuration = `${1.4 + Math.random() * 1.1}s`;
    if (i % 3 === 0) p.style.borderRadius = "50%";
    box.appendChild(p);
  }
  document.body.appendChild(box);
  setTimeout(() => box.remove(), 3000);
}

// Kai, the Kairos mascot: a clapperboard with a face. Moods: happy, think, wow.
export function kai(mood = "happy", cls = "") {
  const mouth = {
    happy: '<path d="M40 66 Q50 76 60 66" stroke="#4b3a00" stroke-width="4" fill="none" stroke-linecap="round"/>',
    think: '<path d="M43 69 H57" stroke="#4b3a00" stroke-width="4" stroke-linecap="round"/>',
    wow: '<ellipse cx="50" cy="69" rx="6" ry="7" fill="#4b3a00"/>',
  }[mood] || "";
  const look = mood === "think" ? 3 : 0;
  return `<svg class="kai ${cls}" viewBox="0 0 100 100" aria-hidden="true">
    <ellipse cx="50" cy="95" rx="28" ry="4" fill="rgba(0,0,0,.08)"/>
    <rect x="16" y="30" width="68" height="60" rx="18" fill="#e7a601"/>
    <rect x="16" y="26" width="68" height="58" rx="18" fill="#ffc800"/>
    <g transform="rotate(-12 18 24)">
      <rect x="14" y="10" width="72" height="16" rx="6" fill="#4b4b4b"/>
      <path d="M24 10 l10 16 M42 10 l10 16 M60 10 l10 16" stroke="#fff" stroke-width="6"/>
    </g>
    <g class="blink">
      <ellipse cx="37" cy="51" rx="9" ry="10" fill="#fff"/><ellipse cx="63" cy="51" rx="9" ry="10" fill="#fff"/>
      <circle cx="${39 + look}" cy="${53 - look}" r="5" fill="#3c3c3c"/><circle cx="${65 + look}" cy="${53 - look}" r="5" fill="#3c3c3c"/>
      <circle cx="${41 + look}" cy="${51 - look}" r="1.6" fill="#fff"/><circle cx="${67 + look}" cy="${51 - look}" r="1.6" fill="#fff"/>
    </g>
    <circle cx="27" cy="64" r="4" fill="#ff9600" opacity=".45"/><circle cx="73" cy="64" r="4" fill="#ff9600" opacity=".45"/>
    ${mouth}
  </svg>`;
}
