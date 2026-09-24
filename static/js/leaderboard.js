/* لایه‌ی رکورد — اینترفیس عمومی getTop/submit
   آداپتور فعلی: localStorage + داده‌ی نمونه‌ی مرجع (برچسب «نمونه/DEMO»).
   CONFIG.API_BASE پر شود → همان متدها با fetch + CSRF جنگو به API وصل می‌شوند. */
import { store, escapeHtml } from "./core/utils.js";
import { toast } from "./core/toast.js";

export const CONFIG = {
  API_BASE: "", /* مثلا "/api/leaderboard" — خالی = حالت لوکال/نمونه */
};

const SEEDS = {
  pac: [
    ["آرش", 480],
    ["نگار", 390],
    ["سام", 300],
    ["مینا", 220],
    ["کیان", 140],
  ],
  tank: [
    ["بردیا", 1250],
    ["سارا", 900],
    ["امیر", 650],
    ["لیلا", 400],
    ["پویا", 200],
  ],
  tetris: [
    ["الهام", 7600],
    ["راستی", 5100],
    ["کاوه", 3400],
    ["درسا", 1800],
    ["یاسر", 900],
  ],
};

const data = { pac: [], tank: [], tetris: [] };

function loadLocal() {
  for (const k of Object.keys(data)) {
    let arr = null;
    try {
      arr = JSON.parse(store.get("lr_lb_" + k) || "null");
    } catch (e) {}
    if (!Array.isArray(arr) || !arr.length)
      arr = SEEDS[k].map(([n, s]) => ({ n, s, demo: true }));
    data[k] = arr.slice(0, 5);
  }
}

function saveLocal(k) {
  try {
    store.set("lr_lb_" + k, JSON.stringify(data[k]));
  } catch (e) {}
}

function csrf() {
  const m = document.cookie.match(/(^|;\s*)csrftoken=([^;]*)/);
  return m ? decodeURIComponent(m[2]) : "";
}

export const Leaderboard = {
  async getTop(gameId) {
    if (CONFIG.API_BASE) {
      try {
        const r = await fetch(`${CONFIG.API_BASE}/${gameId}/`, {
          headers: { Accept: "application/json" },
        });
        if (r.ok) {
          const j = await r.json();
          return (j.results || j).slice(0, 5);
        }
      } catch (e) {}
    }
    loadLocal();
    return data[gameId] || [];
  },

  async submit({ gameId, nickname, score, contact }) {
    nickname = String(nickname || "").trim().slice(0, 20);
    score = Math.max(0, Math.round(Number(score) || 0));
    if (!nickname || !data.hasOwnProperty(gameId)) return null;
    if (CONFIG.API_BASE) {
      try {
        const r = await fetch(`${CONFIG.API_BASE}/${gameId}/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrf(),
          },
          body: JSON.stringify({ nickname, score, contact }),
        });
        if (r.ok) {
          const j = await r.json();
          return j.rank ?? null;
        }
      } catch (e) {}
      toast("ثبت رکورد آنلاین ناموفق بود — به‌صورت نمونه ذخیره شد.");
    }
    loadLocal();
    const b = data[gameId];
    b.push({ n: nickname, s: score, demo: false });
    b.sort((a, x) => x.s - a.s);
    data[gameId] = b.slice(0, 5);
    saveLocal(gameId);
    for (let i = 0; i < data[gameId].length; i++)
      if (data[gameId][i].n === nickname && data[gameId][i].s === score)
        return i + 1;
    return null;
  },

  myName() {
    return store.get("lr_name") || "";
  },
  saveName(n) {
    store.set("lr_name", String(n || "").trim().slice(0, 20));
  },
  isDemo() {
    return !CONFIG.API_BASE;
  },
  rowHtml(entry) {
    const tag = entry.demo
      ? ' <span class="k-tag">نمونه</span>'
      : "";
    return `${escapeHtml(entry.n)} — ${entry.s}${tag}`;
  },
};

export default Leaderboard;
