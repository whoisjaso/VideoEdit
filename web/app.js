// Kairos web app. No build step. Design language: Duolingo (see docs/DESIGN.md).
import { fx, kai } from "/web/fx.js";

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const store = {
  get(k, d = null) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } },
  del(k) { try { localStorage.removeItem(k); } catch { /* */ } },
};
const pick = (a) => a[Math.floor(Math.random() * a.length)];
const PRAISE = ["Nice!", "Great pick!", "Love it!", "Perfect!", "Locked in!"];

async function api(path, opts = {}) {
  const init = { ...opts };
  if (opts.json !== undefined) {
    init.method = init.method || "POST";
    init.headers = { "Content-Type": "application/json" };
    init.body = JSON.stringify(opts.json);
  }
  const r = await fetch(path, init);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || `Request failed (${r.status})`);
  return data;
}

const I = {
  x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>',
  plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
  spark: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l2.2 6.3L20.5 10l-6.3 2.2L12 18.5l-2.2-6.3L3.5 10l6.3-1.7z"/></svg>',
  film: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M5 3h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2zm1 3v2h2V6H6zm0 5v2h2v-2H6zm0 5v2h2v-2H6zm10-10v2h2V6h-2zm0 5v2h2v-2h-2zm0 5v2h2v-2h-2z"/></svg>',
  books: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 4a2 2 0 012-2h3v20H6a2 2 0 01-2-2V4zm6-2h4v20h-4V2zm6.2 1.1l3.9 1-4.3 17-3.9-1z"/></svg>',
  brain: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 2a3 3 0 00-3 3 3 3 0 00-2.6 4.5A3.5 3.5 0 004 16a3 3 0 003 4 2 2 0 002 2h2V2H9zm6 0h-2v20h2a2 2 0 002-2 3 3 0 003-4 3.5 3.5 0 00.6-6.5A3 3 0 0018 5a3 3 0 00-3-3z"/></svg>',
  gear: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M19.4 13a7.5 7.5 0 000-2l2-1.6-2-3.4-2.4 1a7.6 7.6 0 00-1.7-1L15 3.5h-4l-.4 2.5a7.6 7.6 0 00-1.7 1l-2.4-1-2 3.4L6.6 11a7.5 7.5 0 000 2l-2 1.6 2 3.4 2.4-1a7.6 7.6 0 001.7 1l.4 2.5h4l.4-2.5a7.6 7.6 0 001.7-1l2.4 1 2-3.4-2.1-1.6zM13 15.5a3.5 3.5 0 110-7 3.5 3.5 0 010 7z"/></svg>',
  fire: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2s5 4.5 5 10a5 5 0 01-10 0c0-2 1-3.5 1-3.5S9 11 11 11c0-4 1-9 1-9z"/></svg>',
  gem: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 3h10l4 6-9 12L3 9z"/></svg>',
  bolt: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13 2L4 14h6l-1 8 9-12h-6z"/></svg>',
  redo: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11a8 8 0 10-2.3 5.7"/><path d="M20 4v7h-7"/></svg>',
  look: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"><circle cx="9" cy="10" r="5.5"/><circle cx="15" cy="10" r="5.5"/><circle cx="12" cy="15" r="5.5"/></svg>',
  play: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15l13-7.5z"/></svg>',
  stop: '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>',
  mic: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0014 0M12 18v3"/></svg>',
  upload: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4M7 9l5-5 5 5M4 20h16"/></svg>',
  ear: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a7 7 0 00-7 7h3a4 4 0 118 0c0 2-1.4 3-2.5 4S11 15.2 11 17a2 2 0 01-4 0H4a5 5 0 0010 0c0-.8.5-1.4 1.6-2.4C17 13.4 19 11.7 19 9a7 7 0 00-7-7z"/></svg>',
  scissors: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M8.5 7.5L20 18M8.5 16.5L20 6"/></svg>',
  eye: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 5C6 5 2 12 2 12s4 7 10 7 10-7 10-7-4-7-10-7zm0 11a4 4 0 110-8 4 4 0 010 8z"/></svg>',
  star: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3 6.5 7 .8-5.2 4.8 1.5 7L12 17.6 5.7 21l1.5-7L2 9.3l7-.8z"/></svg>',
  clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
};

// every chunky button gives a tap sound + haptic
document.addEventListener("pointerdown", (e) => { if (e.target.closest(".btn,.icon-btn,.tile,.seg button,.chip,.score button,.play")) fx.tap(); });

let toastT;
function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastT);
  toastT = setTimeout(() => t.classList.remove("show"), 2600);
}

// ---------- router ----------
const routes = [];
const route = (re, fn) => routes.push([re, fn]);
let current = null;
let leaving = null;

async function go(hash, { replace = false } = {}) {
  if (replace) history.replaceState(null, "", hash); else history.pushState(null, "", hash);
  await render(1);
}
window.addEventListener("popstate", () => render(-1));

function header({ progress = null, title = "", back = true, close = false } = {}) {
  const bar = $(".bar");
  bar.innerHTML = `
    <button class="back" id="back" ${back ? "" : "hidden"} aria-label="${close ? "Close" : "Back"}">${close ? I.x : I.back}</button>
    ${progress !== null ? `<div class="prog"><i style="width:${Math.max(4, progress * 100)}%"></i></div>` : `<div class="mid">${esc(title)}</div>`}
    <div class="right" id="barRight"></div>`;
  $("#back").onclick = () => (close ? go("#/") : history.length > 1 ? history.back() : go("#/"));
}

async function render(dir = 1) {
  const h = location.hash || "#/";
  if (leaving) leaving();
  leaving = null;
  $$(".sheet, .scrim").forEach((x) => x.remove());   // a new screen never inherits an open sheet
  for (const [re, fn] of routes) {
    const m = h.match(re);
    if (!m) continue;
    const page = document.createElement("section");
    page.className = "page";
    header({ back: h !== "#/" });
    await fn(page, ...m.slice(1));
    const old = current;
    $("#stage").appendChild(page);
    current = page;
    window.scrollTo({ top: 0 });
    page.animate([{ transform: `translateX(${32 * dir}px)`, opacity: 0 }, { transform: "none", opacity: 1 }], { duration: 380, easing: "cubic-bezier(.2,.9,.2,1)" });
    if (old) {
      old.style.pointerEvents = "none";
      old.animate([{ opacity: 1 }, { opacity: 0, transform: `translateX(${-32 * dir}px)` }], { duration: 220, easing: "ease-in", fill: "forwards" }).finished.then(() => old.remove());
    }
    return;
  }
  go("#/", { replace: true });
}

let STATUS = null;
const status = async () => (STATUS = await api("/api/status").catch(() => null));

// ---------- resumable chunked upload (no 30 MB limit) ----------
const upload = {
  file: null, id: null, sent: 0, size: 0, done: false, error: null, listeners: new Set(), url: null, path: null,
  on(fn) { this.listeners.add(fn); fn(this); return () => this.listeners.delete(fn); },
  emit() { this.listeners.forEach((fn) => fn(this)); },
  reset() { Object.assign(this, { file: null, id: null, sent: 0, size: 0, done: false, error: null, url: null, path: null }); this.emit(); },
  async start(file) {
    this.reset();
    this.file = file; this.size = file.size;
    const key = `up:${file.name}:${file.size}:${file.lastModified}`;
    let saved = store.get(key);
    try {
      if (saved) {
        const s = await api(`/api/uploads/${saved.id}`).catch(() => null);
        if (s) { this.id = saved.id; this.sent = s.received; } else saved = null;
      }
      if (!saved) {
        const r = await api("/api/uploads", { json: { name: file.name, size: file.size } });
        this.id = r.id; this.sent = 0;
        store.set(key, { id: r.id });
      }
      const chunk = (STATUS?.chunk_mb || 8) * 1024 * 1024;
      this.emit();
      while (this.sent < this.size) {
        const blob = file.slice(this.sent, Math.min(this.size, this.sent + chunk));
        let tries = 0;
        for (;;) {
          try {
            const r = await fetch(`/api/uploads/${this.id}?offset=${this.sent}`, { method: "PUT", body: blob });
            const j = await r.json();
            if (!r.ok) throw new Error(j.error || "upload failed");
            this.sent = j.received;
            break;
          } catch (e) {
            if (++tries > 5) throw e;
            await sleep(800 * 2 ** tries);   // network blip: back off, resume from the server's byte count
            const s = await api(`/api/uploads/${this.id}`).catch(() => null);
            if (s) this.sent = s.received;
          }
        }
        this.emit();
      }
      this.done = true;
      store.del(key);
      this.emit();
    } catch (e) {
      this.error = e.message; this.emit();
    }
  },
  get pct() { return this.size ? this.sent / this.size : this.done ? 1 : 0; },
};

function upChip(el) {
  if (!el) return () => {};
  const C = 2 * Math.PI * 10;
  el.innerHTML = `<div class="upchip"><span id="upTxt"></span><svg viewBox="0 0 26 26"><circle class="trk" cx="13" cy="13" r="10"/><circle class="val" cx="13" cy="13" r="10" stroke-dasharray="${C}" stroke-dashoffset="${C}"/></svg></div>`;
  return upload.on((u) => {
    const v = $(".val", el), t = $("#upTxt", el);
    if (!v) return;
    el.style.visibility = u.file || u.url || u.path ? "visible" : "hidden";
    v.style.strokeDashoffset = C * (1 - u.pct);
    t.textContent = u.error ? "Paused" : u.done ? "" : u.file ? `${Math.round(u.pct * 100)}%` : "";
  });
}

// ---------- the new-clips flow: one question per screen ----------
const brief = { count: 5, length: "medium", style: "jason", look: "", about: "", rules: "" };
const Q = ["video", "about", "count", "length", "style", "look", "rules", "ready"];

function lesson(page, i, { say, mood = "happy", body, next = "Continue", skip = false, nextDisabled = false, answered = false }) {
  header({ progress: i / (Q.length - 1), close: true });
  const off = upChip($("#barRight"));
  page.innerHTML = `
    <div class="ask">${kai(mood, "bob")}<div class="bubble">${say}</div></div>
    <div class="body">${body}</div>
    <div class="dock ${answered ? "good" : ""}"><div class="inner">
      <div class="msg"><span class="ok">${I.check}</span><span id="praise">${pick(PRAISE)}</span></div>
      <button class="btn" id="next" ${nextDisabled ? "disabled" : ""}>${next}</button>
      ${skip ? `<button class="btn ghost" id="skip">Skip</button>` : ""}
    </div></div>`;
  const n = Q[i + 1];
  $("#next", page).onclick = () => { fx.whoosh(); go(`#/new/${n}`); };
  if (skip) $("#skip", page).onclick = () => go(`#/new/${n}`);
  const keys = (e) => {   // Duolingo-style keyboard: 1-9 picks, Enter continues
    if (e.target.matches("textarea,input")) return;
    if (/^[1-9]$/.test(e.key)) $$(".choice,.look", page)[+e.key - 1]?.click();
    if (e.key === "Enter" && !$("#next", page).disabled) $("#next", page).click();
  };
  addEventListener("keydown", keys);
  leaving = () => { off(); removeEventListener("keydown", keys); };
}

function answered(page) {
  const d = $(".dock", page);
  $("#praise", page).textContent = pick(PRAISE);
  d.classList.remove("good");
  void d.offsetWidth;
  d.classList.add("good");
  $("#next", page).disabled = false;
  fx.success();
}

function choices(page, key) {
  $$(".choice", page).forEach((b) => {
    b.onclick = () => {
      brief[key] = isNaN(+b.dataset.v) ? b.dataset.v : +b.dataset.v;
      $$(".choice", page).forEach((x) => x.classList.toggle("on", x === b));
      answered(page);
    };
  });
}

route(/^#\/new\/video$/, async (page) => {
  const has = upload.file || upload.url || upload.path;
  lesson(page, 0, {
    say: "Drop your video. Any length. An hour-long podcast is fine!",
    body: `<label class="drop ${has ? "has" : ""}" id="drop">
        <input type="file" accept="video/*" hidden id="file">
        <div class="plus">${has ? I.check : I.plus}</div>
        <div class="t">${has ? esc(upload.file?.name || upload.url || upload.path) : "Choose a video"}</div>
        <div class="d">${has ? "Tap to pick a different one" : "or drag it here"}</div>
      </label>
      <div class="or">OR PASTE A LINK</div>
      <input class="field" id="link" placeholder="YouTube, Drive or a file path" value="${esc(upload.url || upload.path || "")}">`,
    nextDisabled: !has, answered: !!has,
  });
  const drop = $("#drop", page), file = $("#file", page);
  const choose = (f) => {
    if (!f) return;
    upload.start(f);
    drop.classList.add("has");
    $(".plus", drop).innerHTML = I.check;
    $(".t", drop).textContent = f.name;
    $(".d", drop).textContent = "Uploading while you answer the next questions";
    answered(page);
  };
  file.onchange = () => choose(file.files[0]);
  ["dragenter", "dragover"].forEach((e) => drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.add("hover"); }));
  ["dragleave", "drop"].forEach((e) => drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.remove("hover"); }));
  drop.addEventListener("drop", (ev) => choose(ev.dataTransfer.files[0]));
  $("#link", page).onchange = (e) => {
    const v = e.target.value.trim();
    upload.reset();
    if (/^https?:\/\//.test(v)) upload.url = v; else if (v) upload.path = v;
    upload.emit();
    if (v) answered(page);
  };
});

route(/^#\/new\/about$/, async (page) => {
  lesson(page, 1, {
    say: "What's it about? One sentence helps me find what matters to you.",
    mood: "think",
    body: `<textarea class="field" id="about" placeholder="Podcast about discipline and money. Find the boldest takes.">${esc(brief.about)}</textarea>`,
    skip: true,
  });
  $("#about", page).oninput = (e) => (brief.about = e.target.value);
});

route(/^#\/new\/count$/, async (page) => {
  lesson(page, 2, {
    say: "How many clips should I make?",
    body: `<div class="choices two">${[3, 5, 8, 10].map((n, k) => `<button class="choice ${brief.count === n ? "on" : ""}" data-v="${n}"><span class="key">${k + 1}</span><span class="big">${n}</span><span class="t">clips</span></button>`).join("")}</div>`,
    answered: true,
  });
  choices(page, "count");
});

route(/^#\/new\/length$/, async (page) => {
  const L = [["short", "Short", "15–30 seconds. Fast and punchy."], ["medium", "Medium", "30–60 seconds. The sweet spot."], ["long", "Long", "60–90 seconds. Full stories."]];
  lesson(page, 3, {
    say: "How long should each clip be?",
    body: `<div class="choices">${L.map(([v, t, d], k) => `<button class="choice ${brief.length === v ? "on" : ""}" data-v="${v}"><span class="key">${k + 1}</span><div><div class="t">${t}</div><div class="d">${d}</div></div></button>`).join("")}</div>`,
    answered: true,
  });
  choices(page, "length");
});

route(/^#\/new\/style$/, async (page) => {
  const styles = await api("/api/styles").catch(() => []);
  lesson(page, 4, {
    say: "Pick your style. It learns from every score you give me.",
    body: `<div class="choices">${styles.map((s, k) => `<button class="choice ${brief.style === s.id ? "on" : ""}" data-v="${esc(s.id)}"><span class="key">${k + 1}</span><div><div class="t">${esc(s.name)}</div><div class="d">${esc(s.blurb)}${s.learned ? ` · trained on ${s.learned} edits` : ""}</div></div></button>`).join("")}</div>`,
    answered: true,
  });
  choices(page, "style");
});

function swatch(id) {
  const m = { "": "linear-gradient(160deg,#4b4b4b,#131f24)", none: "linear-gradient(160deg,#84d8ff,#ffc800)", natural: "linear-gradient(160deg,#8fb3d9,#e0b27a)",
    moody: "linear-gradient(160deg,#52656d,#131f24)", moody_gold: "linear-gradient(160deg,#37464f 55%,#ffc800)", teal_orange: "linear-gradient(160deg,#007c8f,#ff9600)",
    warm_film: "linear-gradient(160deg,#e7a601,#4b3a00)", cool_clean: "linear-gradient(160deg,#ddf4ff,#1899d6)", punchy: "linear-gradient(160deg,#ff4b4b,#ffc800)",
    golden_hour: "linear-gradient(160deg,#ffb100,#ff9600)", noir: "linear-gradient(160deg,#e5e5e5,#131f24)", faded: "linear-gradient(160deg,#afafaf,#52656d)" };
  return m[id] || "linear-gradient(160deg,#afafaf,#4b4b4b)";
}

route(/^#\/new\/look$/, async (page) => {
  const looks = await api("/api/looks").catch(() => []);
  lesson(page, 5, {
    say: "Pick a look. That's the color grade. You can change it on any clip later.",
    body: `<div class="looks">${[{ id: "", label: "Style default" }, ...looks].map((l) => `<button class="look ${brief.look === l.id ? "on" : ""}" data-v="${esc(l.id)}"><div class="im" style="background:${swatch(l.id)}"></div>${esc(l.label)}</button>`).join("")}</div>`,
    answered: true,
  });
  $$(".look", page).forEach((b) => (b.onclick = () => { brief.look = b.dataset.v; $$(".look", page).forEach((x) => x.classList.toggle("on", x === b)); answered(page); }));
});

route(/^#\/new\/rules$/, async (page) => {
  lesson(page, 6, {
    say: "Anything I should always or never do? Say it how you'd say it.",
    mood: "think",
    body: `<textarea class="field" id="rules" placeholder="Never cut my pauses. Always end on the strongest line.">${esc(brief.rules)}</textarea>`,
    skip: true,
  });
  $("#rules", page).oninput = (e) => (brief.rules = e.target.value);
});

route(/^#\/new\/ready$/, async (page) => {
  const L = { short: "15–30s", medium: "30–60s", long: "60–90s" };
  lesson(page, 7, {
    say: "Ready! Here's the plan.",
    mood: "wow",
    body: `<div class="list">
      <div class="item"><div class="grow"><div class="t">${esc(upload.file?.name || upload.url || upload.path || "No video yet")}</div><div class="d" id="upLine">Video</div></div></div>
      <div class="item"><div class="grow"><div class="t">${brief.count} clips · ${L[brief.length]}</div><div class="d">Clips</div></div></div>
      <div class="item"><div class="grow"><div class="t">${esc(brief.style)}${brief.look ? ` · ${esc(brief.look)}` : ""}</div><div class="d">Style and look</div></div></div>
      ${brief.about ? `<div class="item"><div class="grow"><div class="t">${esc(brief.about)}</div><div class="d">About</div></div></div>` : ""}
    </div>`,
    next: "Make my clips",
  });
  const btn = $("#next", page);
  const off = upload.on((u) => {
    const line = $("#upLine", page);
    if (line && u.file) line.textContent = u.error ? `Upload paused: ${u.error}` : u.done ? "Uploaded" : `Uploading ${Math.round(u.pct * 100)}%`;
  });
  const prev = leaving;
  leaving = () => { off(); prev?.(); };
  btn.disabled = !(upload.file || upload.url || upload.path);
  btn.onclick = async () => {
    btn.disabled = true;
    try {
      let p;
      const b = { count: brief.count, length: brief.length, style: brief.style, about: brief.about, rules: brief.rules };
      if (upload.file) {
        btn.textContent = "Finishing upload…";
        while (!upload.done) { if (upload.error) throw new Error(upload.error); await sleep(400); }
        p = await api(`/api/uploads/${upload.id}/complete`, { json: { brief: b } });
      } else {
        btn.textContent = "Fetching your video…";
        p = await api("/api/import", { json: { url: upload.url, path: upload.path, brief: b } });
      }
      if (brief.look) store.set(`look:${p.id}`, brief.look);
      await api(`/api/projects/${p.id}/start`, { json: {} });
      upload.reset();
      go(`#/p/${p.id}`, { replace: true });
    } catch (e) {
      fx.error();
      toast(e.message);
      btn.disabled = false;
      btn.textContent = "Try again";
    }
  };
});

// ---------- project: path of steps -> celebration -> clips ----------
const STEPS = { probe: ["Reading", I.eye], listen: ["Listening", I.ear], moments: ["Finding moments", I.star], edit: ["Cutting", I.scissors], render: ["Rendering", I.film] };
const SAY = { probe: "Opening your video…", listen: "Listening to every word. Long videos take a minute.", moments: "Hunting for the moments that hit…", edit: "Cutting, captioning, adding sounds…", render: "Almost there. Rendering your clips!" };

route(/^#\/p\/([\w]+)$/, async (page, pid) => {
  page.classList.add("wide");
  let alive = true;
  leaving = () => (alive = false);
  let p = await api(`/api/projects/${pid}`);
  header({ title: p.name });
  const drawProgress = () => {
    const steps = p.progress.steps, cur = steps.indexOf(p.progress.step);
    const err = p.status === "error";
    page.innerHTML = `<div style="max-width:520px;margin:0 auto">
      <div class="ask">${kai(err ? "think" : "happy", "bob")}<div class="bubble" id="say">${err ? `Oops. ${esc(p.error)}` : esc(SAY[p.progress.step] || "Getting started…")}</div></div>
      <div class="bigprog"><i id="bp" style="width:${Math.max(3, (p.progress.pct || 0) * 100)}%"></i></div>
      <p class="muted small" style="text-align:right;margin:4px 0 10px" id="pct">${Math.round((p.progress.pct || 0) * 100)}%</p>
      <div class="path">${steps.map((s, k) => `<div class="node ${k < cur || p.progress.step === "done" ? "done" : k === cur ? "now" : ""}">${k < cur ? I.check : STEPS[s][1]}<span class="lbl">${STEPS[s][0]}</span></div>`).join("")}</div>
      <p class="muted small" style="text-align:center;margin-top:26px">You can leave this page. Your clips keep cooking.</p>
      ${err ? `<div class="stack" style="margin-top:16px"><button class="btn" id="retry">Try again</button></div>` : ""}
    </div>`;
    const r = $("#retry", page);
    if (r) r.onclick = async () => { await api(`/api/projects/${pid}/start`, { json: {} }); p.status = "working"; drawProgress(); poll(); };
  };
  let lastStep = null;
  const poll = async () => {
    while (alive) {
      p = await api(`/api/projects/${pid}`).catch(() => p);
      if (p.status === "ready") { celebrate(page, p); return; }
      if (p.status === "error" || !$(".bigprog", page)) drawProgress();
      else {
        $("#bp", page).style.width = `${Math.max(3, (p.progress.pct || 0) * 100)}%`;
        $("#pct", page).textContent = `${Math.round((p.progress.pct || 0) * 100)}%`;
        if (p.progress.step !== lastStep) { drawProgress(); if (lastStep) fx.select(); }
      }
      lastStep = p.progress.step;
      if (p.status === "error") { fx.error(); return; }
      await sleep(1500);
    }
  };
  if (p.status === "ready") drawClips(page, p); else { drawProgress(); poll(); }
  (async () => {   // keep re-editing clips fresh
    while (alive) {
      await sleep(2000);
      if (p.status !== "ready") continue;
      const busy = $$(".clip[data-busy='1']", page);
      if (!busy.length) continue;
      const q = await api(`/api/projects/${pid}`).catch(() => null);
      if (!q) continue;
      p = q;
      for (const el of busy) {
        const c = q.clips_view.find((x) => x.id === el.dataset.id);
        if (c && c.job !== "working") { replaceClip(el, pid, c); fx.success(); }
      }
    }
  })();
});

function celebrate(page, p) {
  const mins = Math.max(1, Math.round((p.info?.duration || 0) / 60));
  const best = Math.max(0, ...p.clips_view.map((c) => c.score));
  page.innerHTML = `<div style="max-width:480px;margin:0 auto;text-align:center;padding-top:20px">
    ${kai("wow", "bob").replace('class="kai', 'style="width:170px;height:170px" class="kai')}
    <h1 style="color:var(--bee)">Your clips are ready!</h1>
    <div class="stats">
      <div class="stat" style="--c:var(--bee)"><div class="h">Clips</div><div class="v">${I.film}${p.clips_view.length}</div></div>
      <div class="stat" style="--c:var(--macaw);animation-delay:.1s"><div class="h">Minutes read</div><div class="v">${I.clock}${mins}</div></div>
      <div class="stat" style="--c:var(--owl);animation-delay:.2s"><div class="h">Top score</div><div class="v">${I.star}${best.toFixed(1)}</div></div>
    </div>
    <div class="dock"><div class="inner"><button class="btn" id="see">See my clips</button></div></div>
  </div>`;
  fx.celebrate();
  $("#see", page).onclick = () => drawClips(page, p);
}

function clipCard(c) {
  return `<article class="clip" data-id="${c.id}" data-busy="${c.job === "working" ? 1 : 0}">
    <div class="vid">
      ${c.video ? `<video src="${c.video}" playsinline controls preload="metadata"></video>` : ""}
      <span class="badge ${c.score >= 8 ? "gold" : ""}">${I.star}${c.score.toFixed(1)}</span>
      ${c.job === "working" ? `<div class="busy"><div class="spinner"></div>${esc(c.busy || "Updating…")}</div>` : ""}
    </div>
    <div class="meta"><div class="ttl">${esc(c.title || "Clip")}</div><div class="why">${Math.round(c.duration)}s · ${esc(c.why)}</div>
      ${c.check_words?.length ? `<div class="check" title="${esc(c.check_words.map((w) => `${w.t}s: “${w.context}”`).join("\n"))}">${c.check_words.length} word${c.check_words.length > 1 ? "s" : ""} to check: ${c.check_words.slice(0, 3).map((w) => `<b>${esc(w.word)}</b>`).join(", ")}</div>` : ""}</div>
    <div class="acts">
      <button class="btn white" data-a="tweak">${I.redo}Adjust</button>
      <button class="btn blue" data-a="look">${I.look}Look</button>
      <button class="btn" data-a="keep">${I.check}Keep</button>
    </div>
  </article>`;
}

function wireClip(el, pid, c) {
  $$("[data-a]", el).forEach((b) => (b.onclick = () => ({ tweak: tweakSheet, look: lookSheet, keep: keepSheet })[b.dataset.a](pid, c, el)));
}

function replaceClip(el, pid, c) {
  const tmp = document.createElement("div");
  tmp.innerHTML = clipCard(c);
  const n = tmp.firstElementChild;
  el.replaceWith(n);
  wireClip(n, pid, c);
}

function drawClips(page, p) {
  const look = store.get(`look:${p.id}`);
  if (look) {   // apply the look picked in the Q&A once
    store.del(`look:${p.id}`);
    p.clips_view.forEach((c) => api(`/api/projects/${p.id}/clips/${c.id}/grade`, { json: { look } }));
    p.clips_view.forEach((c) => { c.job = "working"; c.busy = "Applying your look…"; });
  }
  const engine = p.engine?.moments === "claude" ? "Picked by Claude" : p.engine?.moments === "energy" ? "Picked by speech energy (no transcript)" : "Picked by the built-in editor";
  page.innerHTML = `<p class="kicker">${p.clips_view.length} clips · ${engine}</p><h1>Your clips</h1>
    <p class="sub">Tap <b>Adjust</b> to tell me what to change. Every note trains your style.</p>
    <div class="feed">${p.clips_view.map((c) => clipCard(c)).join("")}</div>`;
  $$(".clip", page).forEach((el, k) => { el.style.animationDelay = `${k * 80}ms`; wireClip(el, p.id, p.clips_view[k]); });
}

// ---------- bottom sheets ----------
function sheet(html) {
  const scrim = document.createElement("div");
  scrim.className = "scrim";
  const sh = document.createElement("div");
  sh.className = "sheet";
  sh.innerHTML = `<button class="x" aria-label="Close">&times;</button>${html}`;
  document.body.append(scrim, sh);
  requestAnimationFrame(() => { scrim.classList.add("show"); sh.classList.add("show"); });
  const onKey = (e) => { if (e.key === "Escape") close(); };
  const close = () => { removeEventListener("keydown", onKey); scrim.classList.remove("show"); sh.classList.remove("show"); setTimeout(() => { scrim.remove(); sh.remove(); }, 450); };
  scrim.onclick = close;
  $(".x", sh).onclick = close;
  addEventListener("keydown", onKey);
  let y0 = null;
  sh.addEventListener("touchstart", (e) => (y0 = sh.scrollTop === 0 ? e.touches[0].clientY : null));
  sh.addEventListener("touchend", (e) => { if (y0 !== null && e.changedTouches[0].clientY - y0 > 90) close(); });
  return { el: sh, close };
}

const CHIPS = ["More zooms", "Fewer zooms", "Bigger captions", "Smaller captions", "More gold words", "Less gold", "Fewer sounds",
  "Louder sounds", "Tighter cuts", "Keep more pauses", "Hit the hook harder", "Darker look", "Lighter look"];

function tweakSheet(pid, c, el) {
  const st = { score: null, chips: new Set() };
  const { el: sh, close } = sheet(`
    <h2>How did it hit?</h2>
    <div class="score">${[...Array(10)].map((_, i) => `<button data-s="${i + 1}">${i + 1}</button>`).join("")}</div>
    <div class="lbl2">Quick fixes</div>
    <div class="chips">${CHIPS.map((x) => `<button class="chip">${x}</button>`).join("")}</div>
    <textarea class="field" id="note" style="min-height:100px" placeholder="Or just say it: “the hook is weak, open on the money line”"></textarea>
    <div class="stack" style="margin-top:16px">
      <button class="btn" id="redo">Re-edit it</button>
      <button class="btn white" id="justscore">Just save my score</button>
    </div>`);
  $$(".score button", sh).forEach((b) => (b.onclick = () => { st.score = +b.dataset.s; $$(".score button", sh).forEach((x) => x.classList.toggle("on", x === b)); fx.select(); }));
  $$(".chip", sh).forEach((b) => (b.onclick = () => { b.classList.toggle("on"); st.chips[b.classList.contains("on") ? "add" : "delete"](b.textContent); fx.select(); }));
  const send = async (redo) => {
    const note = $("#note", sh).value;
    if (!st.score && !st.chips.size && !note.trim()) { fx.error(); return toast("Tap a score or a quick fix first"); }
    close();
    const r = await api(`/api/projects/${pid}/clips/${c.id}/feedback`, { json: { score: st.score, chips: [...st.chips], note, redo } }).catch((e) => toast(e.message));
    if (r) { fx.success(); toast(r.lesson ? `Learned: ${r.lesson}` : `+${st.score ? 15 : 10} XP · style trained`); }
    if (redo) replaceClip(el, pid, { ...c, job: "working", busy: "Re-editing with your notes…" });
  };
  $("#redo", sh).onclick = () => send(true);
  $("#justscore", sh).onclick = () => send(false);
}

async function lookSheet(pid, c, el) {
  const looks = await api("/api/looks");
  let choice = c.grade, k = c.grade_intensity ?? 1;
  const { el: sh, close } = sheet(`
    <h2>Pick a look</h2><p class="muted" style="margin-top:-6px">Shown on your footage.</p>
    <div class="looks">${looks.map((l) => `<button class="look ${l.id === choice ? "on" : ""}" data-v="${esc(l.id)}"><div class="im"><img loading="lazy" src="/api/projects/${pid}/look/${encodeURIComponent(l.id)}?i=1" alt=""></div>${esc(l.label)}</button>`).join("")}</div>
    <div class="lbl2">Strength</div>
    <input type="range" min="0" max="1.5" step="0.05" value="${k}" id="k">
    <div class="stack" style="margin-top:14px">
      <button class="btn" id="apply">Apply look</button>
      <label class="btn white" style="cursor:pointer">${I.upload} Match a reference photo<input type="file" accept="image/*" hidden id="ref"></label>
    </div>`);
  $$(".look", sh).forEach((b) => (b.onclick = () => { choice = b.dataset.v; $$(".look", sh).forEach((x) => x.classList.toggle("on", x === b)); fx.select(); }));
  $("#k", sh).oninput = (e) => (k = +e.target.value);
  $("#apply", sh).onclick = async () => {
    close();
    await api(`/api/projects/${pid}/clips/${c.id}/grade`, { json: { look: choice, intensity: k } }).catch((e) => toast(e.message));
    replaceClip(el, pid, { ...c, job: "working", busy: "Grading…", grade: choice, grade_intensity: k });
  };
  $("#ref", sh).onchange = async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    toast("Matching colors…");
    const r = await fetch(`/api/looks/match?pid=${pid}&name=${encodeURIComponent(f.name.replace(/\.\w+$/, ""))}`, { method: "POST", body: f }).then((x) => x.json());
    close();
    await api(`/api/projects/${pid}/clips/${c.id}/grade`, { json: { look: r.look, intensity: 1 } });
    replaceClip(el, pid, { ...c, job: "working", busy: "Grading to your reference…" });
  };
}

function keepSheet(pid, c) {
  const base = `/api/projects/${pid}/clips/${c.id}`;
  const { el: sh } = sheet(`
    <h2>Keep this one</h2><p class="muted" style="margin-top:-6px">Full quality, 1080×1920, ready to post.</p>
    <div class="stack">
      <button class="btn" id="final">${c.final ? "Download MP4" : "Render full quality"}</button>
      <a class="btn white" href="${base}/download?kind=xml">Open in Premiere Pro</a>
      <a class="btn white" href="${base}/download?kind=srt">Captions (SRT)</a>
      <a class="btn ghost" href="${base}/download?kind=json">Timeline for agents</a>
    </div>`);
  const b = $("#final", sh);
  b.onclick = async () => {
    if (c.final) { location.href = `${base}/download?kind=mp4`; return; }
    b.disabled = true;
    b.textContent = "Rendering…";
    await api(`${base}/export`, { json: {} });
    for (;;) {
      await sleep(2000);
      const p = await api(`/api/projects/${pid}`);
      const cc = p.clips_view.find((x) => x.id === c.id);
      if (cc.job === "error") { fx.error(); toast("Render failed"); b.disabled = false; b.textContent = "Try again"; return; }
      if (cc.job !== "working" && cc.final) { c.final = true; b.disabled = false; b.textContent = "Download MP4"; fx.celebrate(); location.href = `${base}/download?kind=mp4`; return; }
    }
  };
}

// ---------- home ----------
route(/^#\/$/, async (page) => {
  const s = await status();
  const projects = await api("/api/projects").catch(() => []);
  const sb = s?.scoreboard || {};
  const bar = $(".bar");
  bar.innerHTML = `<div class="hud" style="flex:1;justify-content:flex-start;margin:0">
      <span class="h fire" title="Days in a row you trained your style">${I.fire}${sb.streak || 0}</span>
      <span class="h xp" title="Style XP">${I.gem}${sb.xp || 0}</span>
      <span class="h ${s?.claude?.connected ? "ai" : "off"}" title="${s?.claude?.connected ? "Claude connected" : "Offline editor"}">${I.bolt}${s?.claude?.connected ? "AI" : "Off"}</span>
    </div><button class="icon-btn" aria-label="Settings" id="gear">${I.gear}</button>`;
  $("#gear").onclick = () => go("#/settings");
  const greet = sb.trained_today ? "You trained your style today. Keep it going!" : sb.streak ? `Your ${sb.streak}-day streak is waiting. Score a clip today!` : "Ready to find your best moments?";
  page.innerHTML = `
    <div class="hero">${kai("happy", "bob")}<div class="bubble" style="display:inline-block;margin:0 0 22px">${greet}</div></div>
    <h1 style="text-align:center">Long videos in.<br>Clips that hit, out.</h1>
    <p class="sub" style="text-align:center">Drop a podcast, a vlog or a talk. I find the moments, cut them in your style, and learn from every note.</p>
    <button class="btn" id="new">${I.plus} New clips</button>
    <div class="tiles">
      <button class="tile" data-go="#/projects"><span class="ic" style="background:var(--macaw)">${I.film}</span><span><div class="t">My projects</div><div class="d">${projects.length} so far</div></span></button>
      <button class="tile" data-go="#/idea"><span class="ic" style="background:var(--beetle)">${I.spark}</span><span><div class="t">Idea → Prompt</div><div class="d">Say it messy</div></span></button>
      <button class="tile" data-go="#/library"><span class="ic" style="background:var(--fox)">${I.books}</span><span><div class="t">Library</div><div class="d">Sounds, looks, refs</div></span></button>
      <button class="tile" data-go="#/learning"><span class="ic" style="background:var(--owl)">${I.brain}</span><span><div class="t">What I've learned</div><div class="d">${sb.edits_scored || 0} scored edits</div></span></button>
    </div>`;
  $("#new", page).onclick = () => go("#/new/video");
  $$("[data-go]", page).forEach((b) => (b.onclick = () => go(b.dataset.go)));
});

route(/^#\/projects$/, async (page) => {
  header({ title: "Projects" });
  const ps = await api("/api/projects");
  page.innerHTML = `<h1>Projects</h1>${ps.length ? `<div class="list">${ps.map((p) => `
    <a class="item" href="#/p/${p.id}"><img class="th" src="/api/projects/${p.id}/thumb" alt="" onerror="this.style.visibility='hidden'">
      <div class="grow"><div class="t">${esc(p.name)}</div><div class="d">${p.info ? `${Math.max(1, Math.round(p.info.duration / 60))} min · ` : ""}${(p.clips || []).length} clips</div></div>
      <span class="pill ${p.status === "ready" ? "good" : p.status === "error" ? "" : "warn"}">${esc(p.status)}</span></a>`).join("")}</div>`
    : `<div class="empty">${kai("think")}<div class="t">Nothing yet</div>Your first video is one tap away.</div><button class="btn" onclick="location.hash='#/new/video'">New clips</button>`}`;
});

// ---------- idea -> prompt ----------
route(/^#\/idea$/, async (page) => {
  header({ title: "Idea → Prompt" });
  let target = "video";
  page.innerHTML = `<div class="ask">${kai("think", "bob")}<div class="bubble">Say it messy. Ramble! I'll turn it into a clear vision and a prompt.</div></div>
    <div class="seg" id="tg">${[["video", "Video"], ["image", "Image"], ["edit", "Edit"], ["script", "Script"]].map(([v, t]) => `<button data-v="${v}" class="${v === target ? "on" : ""}">${t}</button>`).join("")}</div>
    <textarea class="field" id="messy" placeholder="so like, I want to talk about how discipline isn't the problem…"></textarea>
    <div class="stack" style="margin-top:14px">
      <button class="btn white mic" id="mic">${I.mic} Talk instead</button>
      <button class="btn" id="go">Make it clear</button>
    </div><div id="out" style="margin-top:22px"></div>`;
  $$("#tg button", page).forEach((b) => (b.onclick = () => { target = b.dataset.v; $$("#tg button", page).forEach((x) => x.classList.toggle("on", x === b)); }));
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const mic = $("#mic", page);
  if (!SR) mic.remove();
  else {
    let rec = null;
    mic.onclick = () => {
      if (rec) { rec.stop(); return; }
      rec = new SR(); rec.continuous = true; rec.interimResults = true;
      const base = $("#messy", page).value;
      rec.onresult = (e) => { $("#messy", page).value = base + " " + [...e.results].map((r) => r[0].transcript).join(" "); };
      rec.onend = () => { rec = null; mic.classList.remove("on"); mic.innerHTML = `${I.mic} Talk instead`; };
      rec.start(); mic.classList.add("on"); mic.innerHTML = `${I.stop} Stop`;
    };
  }
  $("#go", page).onclick = async () => {
    const text = $("#messy", page).value.trim();
    if (!text) { fx.error(); return toast("Say something first"); }
    const b = $("#go", page);
    b.disabled = true; b.textContent = "Thinking…";
    try {
      const r = await api("/api/prompts/enhance", { json: { text, target } });
      fx.success();
      $("#out", page).innerHTML = `
        <div class="card"><div class="lbl">The vision</div><p>${esc(r.vision)}</p></div>
        <div class="card"><div class="lbl">Hooks</div><ol>${r.hook_options.map((h) => `<li>${esc(h)}</li>`).join("")}</ol></div>
        <div class="card"><div class="lbl">Beats</div><ol>${r.beats.map((h) => `<li>${esc(h)}</li>`).join("")}</ol></div>
        <div class="card"><div class="lbl">Your prompt</div><p>${esc(r.prompt)}</p></div>
        <div class="stack"><button class="btn blue" id="copy">Copy prompt</button><button class="btn white" id="save">Save to library</button></div>
        ${r.engine === "offline" ? `<p class="muted small" style="text-align:center">Offline mode. Connect Claude in Settings for much sharper results.</p>` : ""}`;
      $("#copy", page).onclick = () => navigator.clipboard.writeText(r.prompt).then(() => toast("Copied!"));
      $("#save", page).onclick = () => api("/api/prompts", { json: { kind: target === "image" ? "image" : "idea", title: r.title, text: r.prompt } }).then(() => { fx.success(); toast("Saved to library"); });
      $("#out", page).scrollIntoView({ behavior: "smooth" });
    } catch (e) { fx.error(); toast(e.message); }
    b.disabled = false; b.textContent = "Make it clear";
  };
});

// ---------- library ----------
route(/^#\/library(?:\/(\w+))?$/, async (page, tab = "sounds") => {
  header({ title: "Library" });
  page.innerHTML = `<h1>Library</h1>
    <div class="seg">${[["sounds", "Sounds"], ["looks", "Looks"], ["refs", "Refs"], ["prompts", "Prompts"]].map(([v, t]) => `<button class="${v === tab ? "on" : ""}" onclick="location.replace('#/library/${v}')">${t}</button>`).join("")}</div>
    <div id="lib"></div>`;
  const lib = $("#lib", page);
  const uploader = (kind, label, accept) => `<label class="btn white" style="margin-bottom:16px;cursor:pointer">${I.upload} ${label}<input type="file" hidden accept="${accept}" data-kind="${kind}"></label>`;
  if (tab === "sounds") {
    const s = await api("/api/library/sfx");
    lib.innerHTML = uploader("sfx", "Add a sound", "audio/*") + `<div class="list">${s.map((x) => `
      <div class="item"><button class="play" data-k="${esc(x.key)}">${I.play}</button><div class="grow"><div class="t">${esc(x.key)}</div><div class="d">${esc(x.job || x.pack)}</div></div></div>`).join("")}</div>`;
    let audio = null, btn = null;
    $$(".play", lib).forEach((b) => (b.onclick = () => {
      if (audio) { audio.pause(); btn.classList.remove("on"); btn.innerHTML = I.play; if (btn === b) { audio = null; return; } }
      audio = new Audio(`/api/library/sfx/${b.dataset.k}`); btn = b; audio.play(); b.classList.add("on"); b.innerHTML = I.stop;
      audio.onended = () => { b.classList.remove("on"); b.innerHTML = I.play; audio = null; };
    }));
  } else if (tab === "looks") {
    const l = await api("/api/looks");
    lib.innerHTML = uploader("lut", "Add a LUT (.cube)", ".cube") + `<div class="list">${l.map((x) => `<div class="item"><div class="play" style="background:${swatch(x.id)};box-shadow:none"></div><div class="grow"><div class="t">${esc(x.label)}</div><div class="d">${esc(x.about)}</div></div><span class="pill">${x.kind}</span></div>`).join("")}</div>`;
  } else if (tab === "refs") {
    const r = await api("/api/library/references");
    lib.innerHTML = uploader("reference", "Add a reference video or image", "video/*,image/*") + uploader("avatar", "Set my follow-card photo", "image/*")
      + (r.length ? `<div class="list">${r.map((x) => `<div class="item"><div class="grow"><div class="t">${esc(x.file)}</div><div class="d">${esc(x.note || "Reference")}</div></div></div>`).join("")}</div>`
        : `<div class="empty"><div class="t">No references yet</div>Add reels you want me to study.</div>`);
  } else {
    const ps = await api("/api/prompts");
    lib.innerHTML = `<div class="list">${ps.map((x) => `<div class="item"><div class="grow"><div class="t">${esc(x.title)}</div><div class="d">${esc(x.text.slice(0, 140))}</div></div><span class="pill">${esc(x.kind)}</span></div>`).join("")}</div>`;
  }
  $$("input[type=file]", lib).forEach((inp) => (inp.onchange = async () => {
    const f = inp.files[0];
    if (!f) return;
    toast("Uploading…");
    const r = await fetch(`/api/library/${inp.dataset.kind}?name=${encodeURIComponent(f.name)}`, { method: "PUT", body: f });
    if (r.ok) { fx.success(); toast("Added!"); } else { fx.error(); toast((await r.json()).error); }
    render(0);
  }));
});

// ---------- learning ----------
route(/^#\/learning$/, async (page) => {
  header({ title: "Learning" });
  const j = await api("/api/journal");
  const sb = j.scoreboard;
  page.innerHTML = `<h1>What I've learned</h1>
    <div class="stats">
      <div class="stat" style="--c:var(--fox)"><div class="h">Streak</div><div class="v">${I.fire}${sb.streak}</div></div>
      <div class="stat" style="--c:var(--bee);animation-delay:.08s"><div class="h">Style XP</div><div class="v">${I.gem}${sb.xp}</div></div>
      <div class="stat" style="--c:var(--owl);animation-delay:.16s"><div class="h">Avg score</div><div class="v">${I.star}${sb.average ?? "–"}</div></div>
    </div>
    ${j.entries.length ? `<div class="list">${j.entries.map((e) => `<div class="item"><div class="grow"><div class="t">${e.lesson ? esc(e.lesson) : esc((e.chips || []).join(", ") || "Score saved")}</div>
      <div class="d">${e.changes.map((c) => `${esc(c.param)} ${c.from} → ${c.to}`).join(" · ") || esc(e.clip?.title || "")}</div></div>${e.score ? `<span class="pill ${e.score >= 8 ? "good" : ""}">${e.score}/10</span>` : ""}</div>`).join("")}</div>`
      : `<div class="empty">${kai("think")}<div class="t">Nothing yet</div>Score a clip and I start learning your taste.</div>`}`;
});

// ---------- settings ----------
route(/^#\/settings$/, async (page) => {
  header({ title: "Settings" });
  const s = await status();
  const cfg = await api("/api/settings");
  const toggle = (id, label, on) => `<div class="item"><div class="grow"><div class="t">${label}</div></div><div class="seg" style="margin:0;width:150px" id="${id}"><button data-v="1" class="${on ? "on" : ""}">On</button><button data-v="0" class="${on ? "" : "on"}">Off</button></div></div>`;
  page.innerHTML = `<h1>Settings</h1>
    <div class="card"><div class="lbl">Claude</div>
      <p class="muted" style="margin-bottom:12px">${s.claude.connected ? "Connected. Claude picks moments, writes hooks and learns from your notes." : esc(s.claude.error || "Not connected. Everything still works with the built-in editor.")}</p>
      <input class="field" type="password" id="key" placeholder="${cfg.anthropic_api_key ? "Key saved. Paste to replace" : "Paste your Anthropic API key"}">
      <div style="height:12px"></div><button class="btn" id="save">Save</button></div>
    <div class="card"><div class="lbl">Feel</div><div class="list">${toggle("snd", "Sounds", fx.sound)}${toggle("hap", "Haptics", fx.haptics)}</div></div>
    <div class="card"><div class="lbl">Engine</div><div class="list">
        <div class="item"><div class="grow"><div class="t">Transcription</div><div class="d">${s.transcribers.length ? esc(s.transcribers.join(", ")) : "None installed: pip install faster-whisper for word captions."}</div></div></div>
        <div class="item"><div class="grow"><div class="t">Blender (3D graphics)</div><div class="d">${s.blender ? "Ready" : "Not installed. Optional."}</div></div></div>
        <div class="item"><div class="grow"><div class="t">Model</div><div class="d">${esc(cfg.model)}</div></div></div>
      </div></div>
    <div class="card"><div class="lbl">Appearance</div><div class="seg" id="theme" style="margin:0">${["auto", "light", "dark"].map((t) => `<button data-t="${t}" class="${(store.get("theme") || "auto") === t ? "on" : ""}">${t}</button>`).join("")}</div></div>`;
  $("#save", page).onclick = async () => {
    const k = $("#key", page).value.trim();
    await api("/api/settings", { json: k ? { anthropic_api_key: k } : {} });
    fx.success(); toast("Saved");
    render(0);
  };
  const wire = (id, set) => $$(`#${id} button`, page).forEach((b) => (b.onclick = () => { set(b.dataset.v === "1"); $$(`#${id} button`, page).forEach((x) => x.classList.toggle("on", x === b)); fx.select(); }));
  wire("snd", (v) => (fx.sound = v));
  wire("hap", (v) => (fx.haptics = v));
  $$("#theme button", page).forEach((b) => (b.onclick = () => { store.set("theme", b.dataset.t); applyTheme(); $$("#theme button", page).forEach((x) => x.classList.toggle("on", x === b)); }));
});

function applyTheme() {
  const t = store.get("theme") || "auto";
  if (t === "auto") document.documentElement.removeAttribute("data-theme"); else document.documentElement.dataset.theme = t;
}

applyTheme();
status().finally(() => render(1));
