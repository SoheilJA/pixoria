/* کنترل‌های صدا (SND) — از مرجع؛ پیش‌فرض خاموش */
import { $, $$, store } from "./utils.js";
import { Sound, SOUND_KEY } from "./sound.js";
import { toast } from "./toast.js";

export function syncSoundBtns() {
  const p = String(Sound.on);
  $$(".btn-sound").forEach((b) => b.setAttribute("aria-pressed", p));
}

export function toggleSound() {
  Sound.on = !Sound.on;
  store.set(SOUND_KEY, Sound.on ? "1" : "0");
  syncSoundBtns();
  if (Sound.on) {
    Sound.ensure();
    Sound.ok();
    toast("صدا روشن شد — صدای تایپ و بازی فعال است.");
  }
}

export function initSound() {
  Sound.on = store.get(SOUND_KEY) === "1";
  syncSoundBtns();
  $$(".btn-sound").forEach((b) =>
    b.addEventListener("click", () => toggleSound()),
  );
}

/* مود بیزینس/بازی — از لندینگ ۵؛ بیزینس = خوانایی بالاتر روی پس‌زمینه */
const MODE_KEY = "pixoria_mode";

export function applyMode(biz) {
  document.documentElement.classList.toggle("biz", biz);
  store.set(MODE_KEY, biz ? "biz" : "game");
  const b = $("#btnMode");
  if (b) b.setAttribute("aria-pressed", String(biz));
}

export function initMode() {
  const saved = store.get(MODE_KEY);
  const biz = saved ? saved === "biz" : true; /* پیش‌فرض: بیزینس (خوانا) */
  applyMode(biz);
  const b = $("#btnMode");
  if (b) b.addEventListener("click", () => applyMode(!document.documentElement.classList.contains("biz")));
}
