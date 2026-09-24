import { $, $$, store, RM, escapeHtml } from '../core/utils.js';
import { Sound } from '../core/sound.js';
import { toast } from '../core/toast.js';
import { Menu } from '../core/menu.js';
import Pac from './pac.js';
import Tank from './tank.js';
import Tetris from './tetris.js';
import LDB from '../leaderboard.js';

let lbData = { pac: [], tank: [], tetris: [] };

async function refreshLB() {
  for (const k of Object.keys(lbData)) lbData[k] = await LDB.getTop(k);
}
function qualifies(k, s) {
  const b = lbData[k] || [];
  return b.length < 5 || s > b[b.length - 1].s;
}
async function addRecord(k, n, s) {
  const rank = await LDB.submit({ gameId: k, nickname: n, score: s });
  lbData[k] = await LDB.getTop(k);
  return rank;
}
function topEntry(k) {
  return (lbData[k] || [])[0];
}
function renderLB() {
  const key = Arcade.cur;
  $("#lbGame").textContent = Arcade.META[key].lb;
  $("#lbList").innerHTML = (lbData[key] || [])
    .map(
      (e, i) =>
        `<li><span class="lb-rank r${i + 1}">${i + 1}</span><span class="lb-n">${escapeHtml(e.n)}${e.demo ? ' <span class="k-tag">نمونه</span>' : ""}</span><span class="lb-s">${e.s}</span></li>`,
    )
    .join("");
}
function renderHelp() {
  $("#helpBody").innerHTML = Arcade.HELP[Arcade.cur]
    .map((h) => `<span>${h}</span>`)
    .join("");
}
const Arcade = {
  cur: "pac",
  games: { pac: Pac, tank: Tank, tetris: Tetris },
  state: "boot",
  visible: false,
  last: 0,
  held: { u: 0, d: 0, l: 0, r: 0 },
  cv: null,
  ctx: null,
  META: {
    pac: {
title: "PAC-CORRIDOR",
name: "پک‌کریدور",
lb: "PAC-CORRIDOR",
desc: "همه‌ی نقطه‌ها را بخور و از دو روحِ شکارچی فرار کن.",
helpShort: "کلیدهای جهت یا دی‌پد · ۳ جان · هر نقطه ۱۰ امتیاز",
    },
    tank: {
title: "TANK BATTLE",
name: "نبرد تانک",
lb: "TANK-BATTLE",
desc: "تانک‌های دشمن را یکی‌یکی از پا درآور؛ موج‌ها سخت‌تر و شلوغ‌تر می‌شوند.",
helpShort: "جهت‌ها برای حرکت · Space یا A برای شلیک",
    },
    tetris: {
title: "BLOCKFALL",
name: "بلوک‌فال",
lb: "BLOCKFALL",
desc: "خط‌ها را بچین و پاک کن؛ هر سطح، سریع‌تر از قبل.",
helpShort: "→ ← حرکت · ↑ چرخش · Space سقوط فوری",
    },
  },
  CODES: { pac: "PAC", tank: "TNK", tetris: "BLK" },
  HELP: {
    pac: [
"حرکت: <b>کلیدهای جهت</b>، دی‌پد یا کشیدن انگشت",
"هدف: خوردنِ <b>همه‌ی نقطه‌های</b> راهرو",
"خطر: دو <b>روح شکارچی</b> با هوشِ تعقیب",
"جان: <b>۳</b> — گرفته شدی، برمی‌گردی اول مسیر",
"هر نقطه: <b>۱۰ امتیاز</b> · پاک‌کردن کامل = برد",
    ],
    tank: [
"حرکت و نشانه‌گیری: <b>کلیدهای جهت</b> یا دی‌پد",
"شلیک: <b>Space</b> یا دکمه‌ی <b>A</b>",
"آجرها <b>خراب می‌شوند</b>؛ فولاد نه",
"هر تانک دشمن: <b>۵۰ امتیاز</b> · پاک‌کردن موج: <b>۱۰۰</b>",
"موج‌های بعدی <b>سریع‌تر و پرتعدادترند</b>",
    ],
    tetris: [
"حرکت: <b>→ ←</b> یا دی‌پد (نگه‌داشتن = تکرار)",
"چرخش: <b>↑</b> یا دکمه‌ی <b>A</b>",
"سقوط نرم: <b>↓</b> · سقوط فوری: <b>Space</b> یا <b>B</b>",
"هر خط: <b>۱۰۰×</b> سطح · چهار خط با هم: <b>۸۰۰×</b> سطح",
"هر ۸ خط، یک سطح بالاتر و سریع‌تر",
    ],
  },

  init() {
    this.cv = $("#gameCanvas");
    this.ctx = this.cv.getContext("2d");
    this.cv.style.touchAction = "none";
    
    /* کارتریج‌ها */
    $$(".cart-chip").forEach((ch) =>
ch.addEventListener("click", () => this.switchGame(ch.dataset.g)),
    );
    /* دی‌پد */
    $$("#gDpad button").forEach((b) => {
const d = b.dataset.d;
b.addEventListener("pointerdown", (e) => {
  e.preventDefault();
  this.held[d] = 1;
  this.press(d);
});
const off = () => {
  this.held[d] = 0;
};
["pointerup", "pointerleave", "pointercancel"].forEach((ev) =>
  b.addEventListener(ev, off),
);
    });
    $("#gA").addEventListener("pointerdown", (e) => {
e.preventDefault();
this.press("A");
    });
    $("#gB").addEventListener("pointerdown", (e) => {
e.preventDefault();
this.press("B");
    });
    $("#gStart").addEventListener("pointerdown", (e) => {
e.preventDefault();
this.press("START");
    });
    /* اکشن‌های اورلی LCD */
    $("#lcdOv").addEventListener("click", (e) => {
const b = e.target.closest("[data-act]");
if (!b) return;
const a = b.dataset.act;
if (a === "start" || a === "retry") this.start();
else if (a === "resume") this.resume();
else if (a === "boot") this.showBoot();
    });
    $("#lcdOv").addEventListener("submit", (e) => {
e.preventDefault();
this.submitEntry(e.target);
    });
    /* سوایپ و تاپ روی LCD (موبایل) */
    let sx = 0,
sy = 0,
sw = false,
mv = 0;
    this.cv.addEventListener("pointerdown", (e) => {
sw = true;
mv = 0;
sx = e.clientX;
sy = e.clientY;
e.preventDefault();
    });
    this.cv.addEventListener("pointermove", (e) => {
if (!sw) return;
const dx = e.clientX - sx,
  dy = e.clientY - sy;
mv += Math.abs(dx) + Math.abs(dy);
if (Math.abs(dx) > 26 || Math.abs(dy) > 26) {
  this.press(
    Math.abs(dx) > Math.abs(dy)
? dx > 0
  ? "r"
  : "l"
: dy > 0
  ? "d"
  : "u",
  );
  sx = e.clientX;
  sy = e.clientY;
}
    });
    ["pointerup", "pointercancel"].forEach((ev) =>
this.cv.addEventListener(ev, () => {
  if (sw && mv < 12) this.press("A");
  sw = false;
}),
    );
    /* توقف هنگام خروج از دید یا مخفی‌شدن تب */
    new IntersectionObserver(
(en) => {
  this.visible = en[0].isIntersecting;
  if (!this.visible && this.state === "play") this.pause();
},
{ threshold: 0.15 },
    ).observe($("#arcade"));
    document.addEventListener("visibilitychange", () => {
if (document.hidden && this.state === "play") this.pause();
    });
    this.refreshLB().then(renderLB);
    renderLB();
    renderHelp();
    this.showBoot();
    this.last = performance.now();
    requestAnimationFrame((n) => this.loop(n));
  },

  initKeys() {
    const isTyping = (t) =>
t &&
(t.tagName === "INPUT" ||
  t.tagName === "TEXTAREA" ||
  t.tagName === "SELECT");
    /* حالت armed: کلیدها فقط بعد از کلیک/فوکوس روی کنسول گرفته می‌شوند؛ Esc آزاد می‌کند */
    const box = $("#arcade");
    if (box) {
      box.addEventListener("pointerdown", () => this.arm());
      box.addEventListener("focusin", () => this.arm());
    }
    window.addEventListener("keydown", (e) => {
if (isTyping(e.target) || !this.visible || Menu.open) return;
if (document.querySelector(".modal-root.open")) return;
if (e.key === "Escape") {
  e.preventDefault();
  if (this.armed) this.disarm();
  else this.press("B");
  return;
}
if (!this.armed) return;
const k = e.key;
const map = {
  ArrowUp: "u",
  ArrowDown: "d",
  ArrowLeft: "l",
  ArrowRight: "r",
};
if (map[k]) {
  e.preventDefault();
  this.held[map[k]] = 1;
  if (!e.repeat) this.press(map[k]);
} else if (k === " ") {
  e.preventDefault();
  if (!e.repeat) this.press("FIRE");
} else if (k === "Enter") {
  e.preventDefault();
  if (!e.repeat) this.press("START");
}
    });
    window.addEventListener("keyup", (e) => {
const map = {
  ArrowUp: "u",
  ArrowDown: "d",
  ArrowLeft: "l",
  ArrowRight: "r",
};
if (map[e.key]) this.held[map[e.key]] = 0;
    });
  },

  ovHTML(html) {
    const o = $("#lcdOv");
    o.innerHTML = html;
    o.classList.add("show");
  },
  ovHide() {
    const o = $("#lcdOv");
    o.classList.remove("show");
    o.innerHTML = "";
  },
  clearHeld() {
    this.held = { u: 0, d: 0, l: 0, r: 0 };
  },

  armed: false,
  arm() {
    if (this.armed) return;
    this.armed = true;
    const b = $("#arcade");
    if (b) b.classList.add("armed");
    const h = $("#armedHint");
    if (h) h.classList.add("on");
  },
  disarm() {
    this.armed = false;
    this.clearHeld();
    if (this.state === "play") this.pause();
    const b = $("#arcade");
    if (b) b.classList.remove("armed");
    const h = $("#armedHint");
    if (h) h.classList.remove("on");
  },

  switchGame(g) {
    if (!this.games[g]) return;
    Sound.blip();
    if (g !== this.cur) {
this.cur = g;
$$(".cart-chip").forEach((c) => {
  const on = c.dataset.g === g;
  c.classList.toggle("on", on);
  c.setAttribute("aria-selected", String(on));
});
renderLB();
renderHelp();
    }
    this.showBoot();
  },

  showBoot() {
    const m = this.META[this.cur];
    this.state = "boot";
    this.clearHeld();
    this.games[this.cur].reset(true);
    this.ovHTML(`<div>
<p class="ov-title">${m.title}</p>
<p class="ov-sub">${m.desc}</p>
<p class="ov-sub dim">${m.helpShort}</p>
<div class="ov-row"><button class="ov-btn" data-act="start">شروع بازی</button></div>
<p class="ov-sub dim" style="margin-top:10px">Enter یا A برای شروع · START برای مکث</p>
<p class="ov-sub dim" style="margin-top:6px">برای فعال‌شدن کنترل کیبورد روی کنسول کلیک کن — Esc برای خروج.</p>
    </div>`);
  },

  start() {
    if (this.state === "play") return;
    this.games[this.cur].reset(true);
    this.clearHeld();
    this.state = "play";
    this.ovHide();
    Sound.ok();
  },
  resume() {
    if (this.state !== "pause") return;
    this.state = "play";
    this.ovHide();
    Sound.blip();
  },
  pause() {
    if (this.state !== "play") return;
    this.state = "pause";
    this.clearHeld();
    this.ovHTML(`<div>
<p class="ov-title warn">PAUSED</p>
<div class="ov-row">
  <button class="ov-btn" data-act="resume">ادامه</button>
  <button class="ov-btn ghost" data-act="boot">منوی بازی</button>
</div>
<p class="ov-sub dim" style="margin-top:8px">START برای ادامه</p>
    </div>`);
    Sound.blip();
  },

  press(b) {
    if (this.state === "boot") {
if (b === "A" || b === "FIRE" || b === "START") this.start();
return;
    }
    if (this.state === "pause") {
if (b === "START" || b === "A" || b === "FIRE") this.resume();
else if (b === "B") this.showBoot();
return;
    }
    if (this.state !== "play") return;
    if (b === "START") {
this.pause();
return;
    }
    const g = this.games[this.cur];
    if (g.press) g.press(b);
  },

  gameEnd(res) {
    if (this.state !== "play") return;
    this.state = "over";
    this.clearHeld();
    const key = this.cur,
g = this.games[key],
meta = this.META[key];
    const score = g.score || 0;
    if (res && res.win) Sound.jingle();
    else Sound.boom();
    const extra =
res && res.win && res.time
  ? ` — زمان: ${res.time.toFixed(1)} ثانیه`
  : "";
    if (score > 0 && qualifies(key, score)) {
this.state = "entry";
this.ovHTML(`<div>
  <p class="ov-title">NEW RECORD!</p>
  <p class="ov-sub">امتیاز: ${score}${extra}</p>
  <p class="ov-sub dim">تو جزو پنج نفر اول ${meta.name} هستی. اسمت را بنویس. کدها فعلاً نمونه/DEMO هستند.</p>
  <form class="ov-form" data-entry>
    <input maxlength="12" placeholder="اسمت" value="${escapeHtml(LDB.myName())}" autocomplete="off">
    <button class="ov-btn" type="submit">ثبت رکورد</button>
  </form>
</div>`);
setTimeout(() => {
  const i = $("#lcdOv input");
  if (i) i.focus();
}, 60);
    } else {
const top = topEntry(key);
this.ovHTML(`<div>
  <p class="ov-title warn">${res && res.win ? "CORRIDOR CLEAR!" : "GAME OVER"}</p>
  <p class="ov-sub">امتیاز: ${score}${extra}</p>
  <p class="ov-sub dim">رکورد فعلی: ${top ? escapeHtml(top.n) + " — " + top.s : "—"}</p>
  <div class="ov-row">
    <button class="ov-btn" data-act="retry">دوباره</button>
    <button class="ov-btn ghost" data-act="boot">منوی بازی</button>
  </div>
</div>`);
    }
  },

  submitEntry(form) {
    if (this.state !== "entry" || !form.closest("#lcdOv")) return;
    const inp = form.querySelector("input");
    const name = ((inp && inp.value.trim()) || "بی‌نام").slice(0, 12);
    const key = this.cur;
    const score = this.games[key].score || 0;
    const rank = addRecord(key, name, score);
    LDB.saveName(name);
    renderLB();
    const code = this.CODES[key] + "-" + rank;
    this.state = "registered";
    Sound.jingle();
    this.ovHTML(`<div>
<p class="ov-title">REGISTERED!</p>
<p class="ov-sub">رتبه‌ی ${rank} در ${this.META[key].name} — ${escapeHtml(name)}</p>
<p class="ov-sub dim">کد تخفیف تو: <b dir="ltr" style="display:inline-block">${code}</b><br>در فرم تماس یا ایمیل یادت نرود.</p>
<div class="ov-row">
  <button class="ov-btn" data-act="retry">دوباره بازی</button>
  <button class="ov-btn ghost" data-act="boot">منوی بازی</button>
</div>
    </div>`);
    toast("رکورد ثبت شد! کد تخفیف: " + code);
  },

  loop(now) {
    requestAnimationFrame((n) => this.loop(n));
    if (document.hidden || !this.visible) {
this.last = now;
return;
    }
    const dt = Math.min(0.05, (now - this.last) / 1000);
    this.last = now;
    if (this.state === "play") this.games[this.cur].update(dt);
    this.games[this.cur].draw(this.ctx, now);
  },
};

export default Arcade;
