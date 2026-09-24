/* توست — از مرجع */
import { $ } from "./utils.js";

let toastTimer = null;
export function toast(msg) {
  const t = $("#toast"),
    tx = $("#toastText");
  if (!t || !tx) return;
  tx.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), 3600);
}
