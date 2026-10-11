// Kairos web app. No build step: plain ES modules, one screen at a time.
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const store = {
  get(k, d = null) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } },
  del(k) { try { localStorage.removeItem(k); } catch { /* */ } },
};

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
  plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
  spark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 17l.8 2.2L22 20l-2.2.8L19 23l-.8-2.2L16 20l2.2-.8z"/></svg>',
  film: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="3" width="18" height="18" rx="4"/><path d="M7 3v18M17 3v18M3 8h4M3 16h4M17 8h4M17 16h4"/></svg>',
  books: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 19V5a2 2 0 012-2h3v18H6a2 2 0 01-2-2zM9 3h4v18H9zM15 4l4 1-3 16-4-1z"/></svg>',
  gear: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 00.3 1.8l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.8-.3 1.7 1.7 0 00-1 1.5V21a2 2 0 11-4 0v-.1a1.7 1.7 0 00-1.1-1.5 1.7 1.7 0 00-1.8.3l-.1.1a2 2 0 11-2.8-2.8l.1-.1a1.7 1.7 0 00.3-1.8 1.7 1.7 0 00-1.5-1H3a2 2 0 110-4h.1a1.7 1.7 0 001.5-1.1 1.7 1.7 0 00-.3-1.8l-.1-.1a2 2 0 112.8-2.8l.1.1a1.7 1.7 0 001.8.3H9a1.7 1.7 0 001-1.5V3a2 2 0 114 0v.1a1.7 1.7 0 001 1.5 1.7 1.7 0 001.8-.3l.1-.1a2 2 0 112.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.8V9a1.7 1.7 0 001.5 1H21a2 2 0 110 4h-.1a1.7 1.7 0 00-1.5 1z"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
  redo: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11a8 8 0 10-2.3 5.7"/><path d="M20 4v7h-7"/></svg>',
  look: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="9" cy="10" r="5.5"/><circle cx="15" cy="10" r="5.5"/><circle cx="12" cy="15" r="5.5"/></svg>',
  play: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15l13-7.5z"/></svg>',
  stop: '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>',
  mic: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0014 0M12 18v3"/></svg>',
  upload: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4M7 9l5-5 5 5M4 20h16"/></svg>',
};

// ---------- toast ----------
let toastT;
function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastT);
  toastT = setTimeout(() => t.classList.remove("show"), 2600);
}

// ---------- router with spring page transitions ----------
const routes = [];
const route = (re, fn) => routes.push([re, fn]);
let current = null;
let depth = 0;
let leaving = null;

async function go(hash, { replace = false } = {}) {
  if (replace) history.replaceState(null, "", hash); else history.pushState(null, "", hash);
  await render(1);
}
window.addEventListener("popstate", () => render(-1));

async function render(dir = 1) {
  const h = location.hash || "#/";
  if (leaving) leaving();
  $$(".sheet, .scrim").forEach((x) => x.remove());   // a new screen never inherits an open sheet
  for (const [re, fn] of routes) {
    const m = h.match(re);
    if (!m) continue;
    const page = document.createElement("section");
    page.className = "page";
    const stage = $("#stage");
    $("#barRight").innerHTML = "";
    $("#barTitle").textContent = "";
    const back = $("#back");
    back.hidden = h === "#/";
    back.onclick = () => (history.length > 1 ? history.back() : go("#/"));
    leaving = null;
    await fn(page, ...m.slice(1));
    const old = current;
    stage.appendChild(page);
    current = page;
    window.scrollTo({ top: 0 });
    const x = 40 * dir;
    page.animate([{ transform: `translateX(${x}px)`, opacity: 0 }, { transform: "none", opacity: 1 }], { duration: 480, easing: "cubic-bezier(.2,.9,.2,1)" });
    if (old) {
      old.style.pointerEvents = "none";
      old.animate([{ transform: "none", opacity: 1 }, { transform: `translateX(${-x}px)`, opacity: 0 }], { duration: 300, easing: "ease-in", fill: "forwards" }).finished.then(() => old.remove());
    }
    depth += dir;
    return;
  }
  go("#/", { replace: true });
}

// ---------- status ----------
let STATUS = null;
async function status() {
  STATUS = await api("/api/status").catch(() => null);
  return STATUS;
}

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
            await sleep(800 * 2 ** tries);  // network blip: back off and resume from the server's byte count
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
  const C = 2 * Math.PI * 10;
  el.innerHTML = `<div class="upchip"><span id="upTxt"></span><svg viewBox="0 0 26 26"><circle class="trk" cx="13" cy="13" r="10"/><circle class="val" cx="13" cy="13" r="10" stroke-dasharray="${C}" stroke-dashoffset="${C}"/></svg></div>`;
  const off = upload.on((u) => {
    if (!u.file && !u.url && !u.path) { el.innerHTML = ""; return; }
    const v = $(".val", el), t = $("#upTxt", el);
    if (!v) return;
    v.style.strokeDashoffset = C * (1 - u.pct);
    t.textContent = u.error ? "Upload paused" : u.done ? "Uploaded" : u.file ? `${Math.round(u.pct * 100)}%` : "Link ready";
  });
  leaving = off;
}

// ---------- the new-clips Q&A ----------
const brief = { count: 5, length: "medium", style: "jason", look: "", about: "", rules: "" };
const Q = ["video", "about", "count", "length", "style", "look", "rules", "ready"];

function shell(page, i, title, sub, body, { next = "Continue", skip = false, nextDisabled = false } = {}) {
  page.classList.add("center");
  page.innerHTML = `
    <div class="dots">${Q.map((_, k) => `<i class="${k === i ? "on" : k < i ? "done" : ""}"></i>`).join("")}</div>
    <h1>${title}</h1>${sub ? `<p class="sub">${sub}</p>` : ""}
    <div class="body">${body}</div>
    <div class="dock"><div class="inner">
      <button class="btn" id="next" ${nextDisabled ? "disabled" : ""}>${next}</button>
      ${skip ? `<button class="btn ghost" id="skip">Skip</button>` : ""}
    </div></div>`;
  upChip($("#barRight"));
  const n = Q[i + 1];
  $("#next", page).onclick = () => go(`#/new/${n}`);
  if (skip) $("#skip", page).onclick = () => go(`#/new/${n}`);
}

function choices(page, key, opts) {
  $$(".choice", page).forEach((b) => {
    b.onclick = () => {
      brief[key] = isNaN(+b.dataset.v) ? b.dataset.v : +b.dataset.v;
      $$(".choice", page).forEach((x) => x.classList.toggle("on", x === b));
      navigator.vibrate?.(8);
      if (opts?.auto) setTimeout(() => $("#next", page).click(), 260);
    };
  });
}

route(/^#\/new\/video$/, async (page) => {
  const has = upload.file || upload.url || upload.path;
  shell(page, 0, "Drop your video.", "Any length. An hour-long podcast is fine. It uploads while you answer the next questions.",
    `<label class="drop ${has ? "has" : ""}" id="drop">
        <input type="file" accept="video/*" hidden id="file">
        <div class="plus">${has ? I.check : I.plus}</div>
        <div class="t">${has ? esc(upload.file?.name || upload.url || upload.path) : "Choose a video"}</div>
        <div class="d">${has ? "Tap to pick a different one" : "or drag it here"}</div>
     </label>
     <div class="or">OR PASTE A LINK</div>
     <input class="field" id="link" placeholder="YouTube, Drive or a file path" value="${esc(upload.url || upload.path || "")}">`,
    { nextDisabled: !has });
  const drop = $("#drop", page), file = $("#file", page), next = $("#next", page);
  const pick = (f) => { if (!f) return; upload.start(f); next.disabled = false; setTimeout(() => go("#/new/about"), 200); };
  file.onchange = () => pick(file.files[0]);
  ["dragenter", "dragover"].forEach((e) => drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.add("hover"); }));
  ["dragleave", "drop"].forEach((e) => drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.remove("hover"); }));
  drop.addEventListener("drop", (ev) => pick(ev.dataTransfer.files[0]));
  $("#link", page).oninput = (e) => {
    const v = e.target.value.trim();
    upload.reset();
    if (/^https?:\/\//.test(v)) upload.url = v; else if (v) upload.path = v;
    upload.emit();
    next.disabled = !v;
  };
});

route(/^#\/new\/about$/, async (page) => {
  shell(page, 1, "What's it about?", "A sentence is plenty. It helps me find the moments that matter to you.",
    `<textarea class="field" id="about" placeholder="e.g. Podcast about discipline and money. Find the boldest takes.">${esc(brief.about)}</textarea>`, { skip: true });
  $("#about", page).oninput = (e) => (brief.about = e.target.value);
});

route(/^#\/new\/count$/, async (page) => {
  shell(page, 2, "How many clips?", "",
    `<div class="choices two">${[3, 5, 8, 10].map((n) => `<button class="choice ${brief.count === n ? "on" : ""}" data-v="${n}"><span class="big">${n}</span><span class="t">clips</span><span class="check"></span></button>`).join("")}</div>`);
  choices(page, "count", { auto: true });
});

route(/^#\/new\/length$/, async (page) => {
  const L = [["short", "Short", "15–30 seconds. Fast, punchy."], ["medium", "Medium", "30–60 seconds. The sweet spot."], ["long", "Long", "60–90 seconds. Full stories."]];
  shell(page, 3, "How long each?", "",
    `<div class="choices">${L.map(([v, t, d]) => `<button class="choice ${brief.length === v ? "on" : ""}" data-v="${v}"><div><div class="t">${t}</div><div class="d">${d}</div></div><span class="check"></span></button>`).join("")}</div>`);
  choices(page, "length", { auto: true });
});

route(/^#\/new\/style$/, async (page) => {
  const styles = await api("/api/styles").catch(() => []);
  shell(page, 4, "Pick your style.", "Your style learns from every score you give it.",
    `<div class="choices">${styles.map((s) => `<button class="choice ${brief.style === s.id ? "on" : ""}" data-v="${esc(s.id)}"><div><div class="t">${esc(s.name)}</div><div class="d">${esc(s.blurb)}${s.learned ? ` · learned from ${s.learned} edits` : ""}</div></div><span class="check"></span></button>`).join("")}</div>`);
  choices(page, "style", { auto: true });
});

route(/^#\/new\/look$/, async (page) => {
  const looks = (await api("/api/looks").catch(() => [])).filter((l) => l.kind !== "custom" || true);
  shell(page, 5, "Pick a look.", "The color grade. You can change it on any clip later.",
    `<div class="looks">${[{ id: "", label: "Style default" }, ...looks].map((l) => `<button class="look ${brief.look === l.id ? "on" : ""}" data-v="${esc(l.id)}"><div class="im" style="background:${swatch(l.id)}"></div>${esc(l.label)}</button>`).join("")}</div>`,
    { skip: true });
  $$(".look", page).forEach((b) => (b.onclick = () => { brief.look = b.dataset.v; $$(".look", page).forEach((x) => x.classList.toggle("on", x === b)); }));
});

function swatch(id) {
  const m = { "": "linear-gradient(160deg,#2a2a2e,#0b0b0f)", none: "linear-gradient(160deg,#7aa6d8,#d8a86a)", natural: "linear-gradient(160deg,#8fb3d9,#e0b27a)",
    moody: "linear-gradient(160deg,#3c4450,#15181d)", moody_gold: "linear-gradient(160deg,#3a3d42 55%,#FFD24A)", teal_orange: "linear-gradient(160deg,#1f5a66,#e08a3c)",
    warm_film: "linear-gradient(160deg,#a9825a,#3b2a1e)", cool_clean: "linear-gradient(160deg,#cfe2f5,#6f8fb0)", punchy: "linear-gradient(160deg,#ff5d73,#ffc21a)",
    golden_hour: "linear-gradient(160deg,#ffb347,#8a4b1f)", noir: "linear-gradient(160deg,#d9d9d9,#111)", faded: "linear-gradient(160deg,#9aa0a8,#5b5f66)" };
  return m[id] || "linear-gradient(160deg,#666,#222)";
}

route(/^#\/new\/rules$/, async (page) => {
  shell(page, 6, "Anything I should always or never do?", "Say it how you'd say it. I'll remember it for this batch.",
    `<textarea class="field" id="rules" placeholder="e.g. Never cut my pauses. Always end on the strongest line.">${esc(brief.rules)}</textarea>`, { skip: true });
  $("#rules", page).oninput = (e) => (brief.rules = e.target.value);
});

route(/^#\/new\/ready$/, async (page) => {
  const L = { short: "15–30s", medium: "30–60s", long: "60–90s" };
  shell(page, 7, "Ready.", "Here's the plan.",
    `<div class="list">
      <div class="item"><div class="grow"><div class="t">${esc(upload.file?.name || upload.url || upload.path || "No video yet")}</div><div class="d" id="upLine">Video</div></div></div>
      <div class="item"><div class="grow"><div class="t">${brief.count} clips · ${L[brief.length]}</div><div class="d">Clips</div></div></div>
      <div class="item"><div class="grow"><div class="t">${esc(brief.style)}${brief.look ? ` · ${esc(brief.look)}` : ""}</div><div class="d">Style and look</div></div></div>
      ${brief.about ? `<div class="item"><div class="grow"><div class="t">${esc(brief.about)}</div><div class="d">About</div></div></div>` : ""}
    </div>`, { next: `${I.spark} Make my clips` });
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
        btn.innerHTML = '<span class="spinner" style="border-color:rgba(127,127,127,.3);border-top-color:currentColor;width:22px;height:22px;margin:0"></span> Finishing upload…';
        while (!upload.done) { if (upload.error) throw new Error(upload.error); await sleep(400); }
        p = await api(`/api/uploads/${upload.id}/complete`, { json: { brief: b } });
      } else {
        btn.innerHTML = "Fetching your video…";
        p = await api("/api/import", { json: { url: upload.url, path: upload.path, brief: b } });
      }
      if (brief.look) store.set(`look:${p.id}`, brief.look);
      await api(`/api/projects/${p.id}/start`, { json: {} });
      upload.reset();
      go(`#/p/${p.id}`, { replace: true });
    } catch (e) {
      toast(e.message);
      btn.disabled = false;
      btn.innerHTML = `${I.spark} Try again`;
    }
  };
});

// ---------- project: processing -> clips ----------
const STEP_LABELS = { probe: "Reading your video", listen: "Listening", moments: "Finding the best moments", edit: "Editing", render: "Rendering previews" };

route(/^#\/p\/([\w]+)$/, async (page, pid) => {
  page.classList.add("wide");
  let alive = true;
  leaving = () => (alive = false);
  let p = await api(`/api/projects/${pid}`);
  $("#barTitle").textContent = p.name;
  const drawProgress = () => {
    const C = 2 * Math.PI * 92;
    const steps = p.progress.steps;
    const cur = steps.indexOf(p.progress.step);
    page.innerHTML = `<div style="max-width:520px;margin:0 auto">
      <p class="kicker">${p.status === "error" ? "Something went wrong" : "Working on it"}</p>
      <h1>${p.status === "error" ? "Let's try that again." : esc(STEP_LABELS[p.progress.step] || "Getting started")}.</h1>
      <p class="sub">${p.status === "error" ? esc(p.error) : "You can leave this page. Your clips keep cooking."}</p>
      <div class="ring"><svg viewBox="0 0 200 200"><circle class="trk" cx="100" cy="100" r="92"/><circle class="val" cx="100" cy="100" r="92" stroke-dasharray="${C}" stroke-dashoffset="${C * (1 - (p.progress.pct || 0))}"/></svg><div class="pct">${Math.round((p.progress.pct || 0) * 100)}%</div></div>
      <div class="steps">${steps.map((s, k) => `<div class="step ${k < cur || p.progress.step === "done" ? "done" : k === cur ? "now" : ""}"><span class="dot"></span>${STEP_LABELS[s]}${k === cur && p.progress.note ? `<span class="note">${esc(p.progress.note)}</span>` : ""}</div>`).join("")}</div>
      ${p.status === "error" ? `<div class="stack" style="margin-top:20px"><button class="btn" id="retry">Try again</button></div>` : ""}
    </div>`;
    const r = $("#retry", page);
    if (r) r.onclick = async () => { await api(`/api/projects/${pid}/start`, { json: {} }); poll(); };
  };
  const poll = async () => {
    while (alive) {
      p = await api(`/api/projects/${pid}`).catch(() => p);
      if (p.status === "ready") { drawClips(page, p); return; }
      // patch the ring in place for smooth motion
      if (!$(".ring", page) || p.status === "error") drawProgress();
      else {
        const C = 2 * Math.PI * 92;
        $(".ring .val", page).style.strokeDashoffset = C * (1 - (p.progress.pct || 0));
        $(".ring .pct", page).textContent = `${Math.round((p.progress.pct || 0) * 100)}%`;
        const steps = p.progress.steps, cur = steps.indexOf(p.progress.step);
        $$(".step", page).forEach((el, k) => { el.className = `step ${k < cur ? "done" : k === cur ? "now" : ""}`; });
        $("h1", page).textContent = `${STEP_LABELS[p.progress.step] || "Getting started"}.`;
      }
      if (p.status === "error") return;
      await sleep(1500);
    }
  };
  if (p.status === "ready") drawClips(page, p); else { drawProgress(); poll(); }
  // keep busy clips fresh
  (async () => {
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
        if (c && c.job !== "working") replaceClip(el, pid, c);
      }
    }
  })();
});

function clipCard(pid, c) {
  return `<article class="clip" data-id="${c.id}" data-busy="${c.job === "working" ? 1 : 0}">
    <div class="vid">
      ${c.video ? `<video src="${c.video}" playsinline controls preload="metadata"></video>` : ""}
      <span class="badge ${c.score >= 8 ? "gold" : ""}">${c.score.toFixed(1)}</span>
      ${c.job === "working" ? `<div class="busy"><div class="spinner"></div>${esc(c.busy || "Updating…")}</div>` : ""}
    </div>
    <div class="meta"><div class="ttl">${esc(c.title || "Clip")}</div><div class="why">${Math.round(c.duration)}s · ${esc(c.why)}</div></div>
    <div class="acts">
      <button data-a="tweak">${I.redo}Adjust</button>
      <button data-a="look">${I.look}Look</button>
      <button data-a="keep" class="keep">${I.check}Keep</button>
    </div>
  </article>`;
}

function wireClip(el, pid, c) {
  $$("[data-a]", el).forEach((b) => (b.onclick = () => ({ tweak: tweakSheet, look: lookSheet, keep: keepSheet })[b.dataset.a](pid, c, el)));
}

function replaceClip(el, pid, c) {
  const tmp = document.createElement("div");
  tmp.innerHTML = clipCard(pid, c);
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
  page.innerHTML = `<p class="kicker">${p.clips_view.length} clips · ${engine}</p><h1>Your clips.</h1>
    <p class="sub">Tap <b>Adjust</b> to tell me what to change. Every note makes the next edit better.</p>
    <div class="feed">${p.clips_view.map((c) => clipCard(p.id, c)).join("")}</div>`;
  $$(".clip", page).forEach((el, k) => { el.style.animationDelay = `${k * 70}ms`; wireClip(el, p.id, p.clips_view[k]); });
}

// ---------- bottom sheets ----------
function sheet(html) {
  const scrim = document.createElement("div");
  scrim.className = "scrim";
  const sh = document.createElement("div");
  sh.className = "sheet";
  sh.innerHTML = `<div class="grab"></div><button class="x" aria-label="Close">&times;</button>${html}`;
  document.body.append(scrim, sh);
  requestAnimationFrame(() => { scrim.classList.add("show"); sh.classList.add("show"); });
  const close = () => { scrim.classList.remove("show"); sh.classList.remove("show"); setTimeout(() => { scrim.remove(); sh.remove(); }, 450); };
  scrim.onclick = close;
  $(".x", sh).onclick = close;
  const onKey = (e) => { if (e.key === "Escape") { close(); removeEventListener("keydown", onKey); } };
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
    <div class="kicker">Quick fixes</div>
    <div class="chips">${CHIPS.map((x) => `<button class="chip">${x}</button>`).join("")}</div>
    <div class="row" style="align-items:flex-start">
      <textarea class="field" id="note" style="min-height:110px" placeholder="Or just say it: “the hook is weak, open on the money line”"></textarea>
    </div>
    <div class="stack" style="margin-top:16px">
      <button class="btn" id="redo">${I.redo} Re-edit it</button>
      <button class="btn ghost" id="justscore">Just save my score</button>
    </div>`);
  $$(".score button", sh).forEach((b) => (b.onclick = () => { st.score = +b.dataset.s; $$(".score button", sh).forEach((x) => x.classList.toggle("on", x === b)); navigator.vibrate?.(6); }));
  $$(".chip", sh).forEach((b) => (b.onclick = () => { b.classList.toggle("on"); st.chips[b.classList.contains("on") ? "add" : "delete"](b.textContent); }));
  const send = async (redo) => {
    const note = $("#note", sh).value;
    if (!st.score && !st.chips.size && !note.trim()) return toast("Tap a score or a quick fix first");
    close();
    const r = await api(`/api/projects/${pid}/clips/${c.id}/feedback`, { json: { score: st.score, chips: [...st.chips], note, redo } }).catch((e) => toast(e.message));
    if (r) toast(r.lesson ? `Learned: ${r.lesson}` : redo ? "Re-editing with your notes" : "Saved");
    if (redo) replaceClip(el, pid, { ...c, job: "working", busy: "Re-editing with your notes…" });
  };
  $("#redo", sh).onclick = () => send(true);
  $("#justscore", sh).onclick = () => send(false);
}

async function lookSheet(pid, c, el) {
  const looks = await api("/api/looks");
  let pick = c.grade, k = c.grade_intensity ?? 1;
  const { el: sh, close } = sheet(`
    <h2>Pick a look.</h2><p class="muted" style="margin-top:-4px">Shown on your footage.</p>
    <div class="looks">${looks.map((l) => `<button class="look ${l.id === pick ? "on" : ""}" data-v="${esc(l.id)}"><div class="im"><img loading="lazy" src="/api/projects/${pid}/look/${encodeURIComponent(l.id)}?i=1" alt=""></div>${esc(l.label)}</button>`).join("")}</div>
    <div class="kicker">Strength</div>
    <input type="range" min="0" max="1.5" step="0.05" value="${k}" id="k">
    <div class="stack" style="margin-top:14px">
      <button class="btn" id="apply">Apply look</button>
      <label class="btn ghost" style="cursor:pointer">${I.upload} Match a reference photo<input type="file" accept="image/*" hidden id="ref"></label>
    </div>`);
  $$(".look", sh).forEach((b) => (b.onclick = () => { pick = b.dataset.v; $$(".look", sh).forEach((x) => x.classList.toggle("on", x === b)); }));
  $("#k", sh).oninput = (e) => (k = +e.target.value);
  $("#apply", sh).onclick = async () => {
    close();
    await api(`/api/projects/${pid}/clips/${c.id}/grade`, { json: { look: pick, intensity: k } }).catch((e) => toast(e.message));
    replaceClip(el, pid, { ...c, job: "working", busy: "Grading…", grade: pick, grade_intensity: k });
  };
  $("#ref", sh).onchange = async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    toast("Matching colors…");
    const r = await fetch(`/api/looks/match?pid=${pid}&name=${encodeURIComponent(f.name.replace(/\.\w+$/, ""))}`, { method: "POST", body: f }).then((x) => x.json());
    close();
    await api(`/api/projects/${pid}/clips/${c.id}/grade`, { json: { look: r.look, intensity: 1 } });
    replaceClip(el, pid, { ...c, job: "working" });
    toast("Matched. Re-rendering with your reference look");
  };
}

function keepSheet(pid, c) {
  const base = `/api/projects/${pid}/clips/${c.id}`;
  const { el: sh } = sheet(`
    <h2>Keep this one.</h2><p class="muted" style="margin-top:-4px">Full quality, 1080×1920, ready to post.</p>
    <div class="stack">
      <button class="btn" id="final">${c.final ? "Download MP4" : "Render full quality"}</button>
      <a class="btn secondary" href="${base}/download?kind=xml">Open in Premiere Pro (XML)</a>
      <a class="btn secondary" href="${base}/download?kind=srt">Captions (SRT)</a>
      <a class="btn ghost" href="${base}/download?kind=json">Timeline (for agents)</a>
    </div>`);
  const b = $("#final", sh);
  b.onclick = async () => {
    if (c.final) { location.href = `${base}/download?kind=mp4`; return; }
    b.disabled = true;
    b.innerHTML = '<span class="spinner" style="border-color:rgba(127,127,127,.3);border-top-color:currentColor;width:22px;height:22px;margin:0"></span> Rendering…';
    await api(`${base}/export`, { json: {} });
    for (;;) {
      await sleep(2000);
      const p = await api(`/api/projects/${pid}`);
      const cc = p.clips_view.find((x) => x.id === c.id);
      if (cc.job === "error") { toast("Render failed"); b.disabled = false; return; }
      if (cc.job !== "working" && cc.final) { c.final = true; b.disabled = false; b.textContent = "Download MP4"; location.href = `${base}/download?kind=mp4`; return; }
    }
  };
}

// ---------- home ----------
route(/^#\/$/, async (page) => {
  page.classList.add("center");
  const s = await status();
  const projects = await api("/api/projects").catch(() => []);
  $("#barTitle").textContent = "";
  $("#barRight").innerHTML = `<button class="icon-btn" aria-label="Settings" id="gear">${I.gear}</button>`;
  $("#gear").onclick = () => go("#/settings");
  const sb = s?.scoreboard;
  page.innerHTML = `
    <p class="kicker">${s?.claude?.connected ? '<span class="pill good">Claude connected</span>' : '<span class="pill warn">Offline editor</span>'}${sb?.average ? ` <span class="pill">avg score ${sb.average}</span>` : ""}</p>
    <h1>Long videos in.<br>Clips that hit, out.</h1>
    <p class="sub">Drop a podcast, a vlog or a talk. I find the moments, cut them in your style, and learn from every note.</p>
    <button class="btn accent" id="new">${I.plus} New clips</button>
    <div class="tiles">
      <button class="tile" data-go="#/projects"><span class="ic">${I.film}</span><span><div class="t">My projects</div><div class="d">${projects.length} so far</div></span></button>
      <button class="tile" data-go="#/idea"><span class="ic">${I.spark}</span><span><div class="t">Idea → Prompt</div><div class="d">Say it messy</div></span></button>
      <button class="tile" data-go="#/library"><span class="ic">${I.books}</span><span><div class="t">Library</div><div class="d">Sounds, looks, refs</div></span></button>
      <button class="tile" data-go="#/learning"><span class="ic">${I.redo}</span><span><div class="t">What I've learned</div><div class="d">${sb?.edits_scored || 0} scored edits</div></span></button>
    </div>`;
  $("#new", page).onclick = () => go("#/new/video");
  $$("[data-go]", page).forEach((b) => (b.onclick = () => go(b.dataset.go)));
});

route(/^#\/projects$/, async (page) => {
  $("#barTitle").textContent = "Projects";
  const ps = await api("/api/projects");
  page.innerHTML = `<h1>Projects.</h1>${ps.length ? `<div class="list">${ps.map((p) => `
    <a class="item" href="#/p/${p.id}" style="text-decoration:none"><img class="th" src="/api/projects/${p.id}/thumb" alt="" onerror="this.style.visibility='hidden'">
      <div class="grow"><div class="t">${esc(p.name)}</div><div class="d">${p.info ? `${Math.round(p.info.duration / 60)} min · ` : ""}${(p.clips || []).length} clips</div></div>
      <span class="pill ${p.status === "ready" ? "good" : p.status === "error" ? "" : "warn"}">${esc(p.status)}</span></a>`).join("")}</div>`
    : `<div class="empty"><div class="t">Nothing yet</div>Your first video is one tap away.</div><button class="btn" onclick="location.hash='#/new/video'">New clips</button>`}`;
});

// ---------- idea -> prompt ----------
route(/^#\/idea$/, async (page) => {
  $("#barTitle").textContent = "Idea → Prompt";
  let target = "video";
  page.innerHTML = `<h1>Say it messy.</h1><p class="sub">Ramble. I'll turn it into a clear vision and a prompt you can use.</p>
    <div class="seg" id="tg">${[["video", "Video"], ["image", "Image"], ["edit", "Edit"], ["script", "Script"]].map(([v, t]) => `<button data-v="${v}" class="${v === target ? "on" : ""}">${t}</button>`).join("")}</div>
    <textarea class="field" id="messy" placeholder="so like, I want to talk about how discipline isn't the problem…"></textarea>
    <div class="stack" style="margin-top:12px">
      <button class="btn secondary mic" id="mic">${I.mic} Talk instead</button>
      <button class="btn" id="go">${I.spark} Make it clear</button>
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
    if (!text) return toast("Say something first");
    const b = $("#go", page);
    b.disabled = true; b.innerHTML = '<span class="spinner" style="border-color:rgba(127,127,127,.3);border-top-color:currentColor;width:22px;height:22px;margin:0"></span> Thinking…';
    try {
      const r = await api("/api/prompts/enhance", { json: { text, target } });
      $("#out", page).innerHTML = `
        <div class="card"><div class="lbl">The vision</div><p>${esc(r.vision)}</p></div>
        <div class="card"><div class="lbl">Hooks</div><ol>${r.hook_options.map((h) => `<li>${esc(h)}</li>`).join("")}</ol></div>
        <div class="card"><div class="lbl">Beats</div><ol>${r.beats.map((h) => `<li>${esc(h)}</li>`).join("")}</ol></div>
        <div class="card"><div class="lbl">Your prompt</div><p id="pr">${esc(r.prompt)}</p></div>
        <div class="stack"><button class="btn" id="copy">Copy prompt</button><button class="btn secondary" id="save">Save to library</button></div>
        ${r.engine === "offline" ? `<p class="muted small" style="text-align:center">Offline mode. Connect Claude in Settings for much sharper results.</p>` : ""}`;
      $("#copy", page).onclick = () => navigator.clipboard.writeText(r.prompt).then(() => toast("Copied"));
      $("#save", page).onclick = () => api("/api/prompts", { json: { kind: target === "image" ? "image" : "idea", title: r.title, text: r.prompt } }).then(() => toast("Saved to library"));
      $("#out", page).scrollIntoView({ behavior: "smooth" });
    } catch (e) { toast(e.message); }
    b.disabled = false; b.innerHTML = `${I.spark} Make it clear`;
  };
});

// ---------- library ----------
route(/^#\/library(?:\/(\w+))?$/, async (page, tab = "sounds") => {
  $("#barTitle").textContent = "Library";
  page.innerHTML = `<h1>Library.</h1>
    <div class="seg">${[["sounds", "Sounds"], ["looks", "Looks"], ["refs", "References"], ["prompts", "Prompts"]].map(([v, t]) => `<button class="${v === tab ? "on" : ""}" onclick="location.replace('#/library/${v}')">${t}</button>`).join("")}</div>
    <div id="lib"></div>`;
  const lib = $("#lib", page);
  const uploader = (kind, label, accept) => `<label class="btn secondary" style="margin-bottom:14px;cursor:pointer">${I.upload} ${label}<input type="file" hidden accept="${accept}" data-kind="${kind}"></label>`;
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
    lib.innerHTML = uploader("lut", "Add a LUT (.cube)", ".cube") + `<div class="list">${l.map((x) => `<div class="item"><div class="play" style="background:${swatch(x.id)}"></div><div class="grow"><div class="t">${esc(x.label)}</div><div class="d">${esc(x.about)}</div></div><span class="pill">${x.kind}</span></div>`).join("")}</div>`;
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
    toast(r.ok ? "Added" : (await r.json()).error);
    render(0);
  }));
});

// ---------- learning ----------
route(/^#\/learning$/, async (page) => {
  $("#barTitle").textContent = "Learning";
  const j = await api("/api/journal");
  const sb = j.scoreboard;
  page.innerHTML = `<h1>What I've learned.</h1>
    <p class="sub">${sb.edits_scored ? `${sb.edits_scored} scored edits · average ${sb.average} · best ${sb.best}` : "Score a clip and I start learning your taste."}</p>
    ${j.entries.length ? `<div class="list">${j.entries.map((e) => `<div class="item"><div class="grow"><div class="t">${e.lesson ? esc(e.lesson) : esc((e.chips || []).join(", ") || "Score saved")}</div>
      <div class="d">${e.changes.map((c) => `${esc(c.param)} ${c.from} → ${c.to}`).join(" · ") || esc(e.clip?.title || "")}</div></div>${e.score ? `<span class="pill ${e.score >= 8 ? "good" : ""}">${e.score}/10</span>` : ""}</div>`).join("")}</div>` : ""}`;
});

// ---------- settings ----------
route(/^#\/settings$/, async (page) => {
  $("#barTitle").textContent = "Settings";
  const s = await status();
  const cfg = await api("/api/settings");
  page.innerHTML = `<h1>Settings.</h1>
    <div class="card"><div class="lbl">Claude</div>
      <p class="muted" style="margin-bottom:12px">${s.claude.connected ? "Connected. Claude picks moments, writes hooks and learns from your notes." : esc(s.claude.error || "Not connected. Everything still works with the built-in editor.")}</p>
      <input class="field" type="password" id="key" placeholder="${cfg.anthropic_api_key ? "Key saved. Paste to replace" : "Paste your Anthropic API key"}">
      <div style="height:10px"></div><button class="btn" id="save">Save</button></div>
    <div class="card"><div class="lbl">Engine</div>
      <div class="list" style="box-shadow:none">
        <div class="item"><div class="grow"><div class="t">Transcription</div><div class="d">${s.transcribers.length ? esc(s.transcribers.join(", ")) : "None installed: clips are found by speech energy. Install faster-whisper for word captions."}</div></div></div>
        <div class="item"><div class="grow"><div class="t">Blender (3D graphics)</div><div class="d">${s.blender ? "Ready" : "Not installed. Optional."}</div></div></div>
        <div class="item"><div class="grow"><div class="t">Model</div><div class="d">${esc(cfg.model)}</div></div></div>
      </div></div>
    <div class="card"><div class="lbl">Appearance</div><div class="seg" id="theme">${["auto", "light", "dark"].map((t) => `<button data-t="${t}" class="${(store.get("theme") || "auto") === t ? "on" : ""}">${t[0].toUpperCase() + t.slice(1)}</button>`).join("")}</div></div>`;
  $("#save", page).onclick = async () => {
    const k = $("#key", page).value.trim();
    await api("/api/settings", { json: k ? { anthropic_api_key: k } : {} });
    toast("Saved");
    render(0);
  };
  $$("#theme button", page).forEach((b) => (b.onclick = () => { store.set("theme", b.dataset.t); applyTheme(); $$("#theme button", page).forEach((x) => x.classList.toggle("on", x === b)); }));
});

function applyTheme() {
  const t = store.get("theme") || "auto";
  if (t === "auto") document.documentElement.removeAttribute("data-theme"); else document.documentElement.dataset.theme = t;
}

applyTheme();
status().finally(() => render(1));
