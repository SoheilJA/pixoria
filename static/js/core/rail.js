/* ریل چپ + بیپ (همراه) — از مرجع */
import { $, $$, G, RM, Sound, toast } from "./utils.js";

const BUDDY_PHRASES = [
  "بیپ!",
  "همین‌جا هستم",
  "مسیر رو دوست داری؟",
  "یک قدم دیگر...",
  "نزدیک شدی!",
  "کارت خوبه!",
];

let buddyClicks = 0,
  buddyTimer = null;

export function updateRail(p) {
  const usable = Math.max(0, window.innerHeight - 192 - 46);
  const y = 96 + p * usable;
  const b = $("#railBuddy");
  if (b) b.style.transform = `translateY(${y}px)`;
  $$(".rail-dot").forEach((d, i) =>
    d.classList.toggle("on", p * 100 >= (i + 1) * 10),
  );
  const alt = $("#railAlt");
  if (alt) alt.textContent = "ALT " + String(Math.round(p * 100)).padStart(2, "0") + "%";
}

export function buddySay(txt) {
  const s = $("#buddySay");
  if (!s) return;
  s.textContent = txt;
  s.classList.add("show");
  clearTimeout(buddySay._t);
  buddySay._t = setTimeout(() => s.classList.remove("show"), 1500);
}

export function initRail() {
  const track = $("#railTrack");
  if (!track) return;
  for (let i = 0; i < 9; i++) {
    const d = document.createElement("span");
    d.className = "rail-dot";
    d.style.top = 10 * (i + 1) + "%";
    track.appendChild(d);
  }
  const b = $("#railBuddy");
  b.addEventListener("click", () => {
    Sound.blip();
    if (G && !RM)
      G.fromTo(
        "#railBuddy .b-in",
        { y: 0 },
        { y: -12, duration: 0.09, ease: "none", yoyo: true, repeat: 1 },
      );
    buddyClicks++;
    clearTimeout(buddyTimer);
    buddyTimer = setTimeout(() => (buddyClicks = 0), 1500);
    if (buddyClicks >= 10) {
      buddyClicks = 0;
      Sound.jingle();
      toast("کد مخفی همکار: BUDDY-10 — نمونه/DEMO، تخفیف واقعی نیست.");
      buddySay("قلبم رو بردی!");
    } else buddySay(BUDDY_PHRASES[(buddyClicks - 1) % BUDDY_PHRASES.length]);
  });
}
