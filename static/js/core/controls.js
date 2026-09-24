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
