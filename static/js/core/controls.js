/* مود بیزینس/بازی — از لندینگ ۵؛ بیزینس = خوانایی بالاتر روی پس‌زمینه */
import { store } from "./utils.js";

const MODE_KEY = "pixoria_mode";

export function applyMode(biz) {
  document.documentElement.classList.toggle("biz", biz);
  store.set(MODE_KEY, biz ? "biz" : "game");
  const b = document.querySelector("#btnMode");
  if (b) b.setAttribute("aria-pressed", String(biz));
}

export function initMode() {
  const saved = store.get(MODE_KEY);
  const biz = saved ? saved === "biz" : true; /* پیش‌فرض: بیزینس (خوانا) */
  applyMode(biz);
  const b = document.querySelector("#btnMode");
  if (b)
    b.addEventListener("click", () =>
      applyMode(!document.documentElement.classList.contains("biz")),
    );
}
