/* منوی پاپ‌آپ موبایل — از مرجع (role=dialog، ↑↓ Enter Esc، focus trap) */
import { $, $$, G, RM, Sound, scrollToId } from "./utils.js";

const Menu = { open: false, idx: 0, items: [] };

function openMenu() {
  Menu.open = true;
  Menu.idx = 0;
  const ov = $("#menuOverlay");
  ov.classList.add("open");
  ov.setAttribute("aria-hidden", "false");
  Menu.items = $$("#menuList .menu-item");
  Menu.items.forEach((it, i) => it.classList.toggle("sel", i === 0));
  $("#menuClose").focus();
  Sound.ok();
}

function closeMenu() {
  Menu.open = false;
  const ov = $("#menuOverlay");
  ov.classList.remove("open");
  ov.setAttribute("aria-hidden", "true");
  $("#btnMenu").focus();
  Sound.blip();
}

function activate(it) {
  closeMenu();
  const go = it.dataset.target;
  setTimeout(() => {
    if (go && go.startsWith("#")) scrollToId(go.slice(1));
    else if (go) window.location.href = go;
  }, 60);
}

export function initMenu() {
  const btn = $("#btnMenu"),
    ov = $("#menuOverlay");
  if (!btn || !ov) return;
  btn.addEventListener("click", openMenu);
  $("#menuClose").addEventListener("click", closeMenu);
  ov.addEventListener("click", (e) => {
    if (e.target === e.currentTarget) closeMenu();
  });
  Menu.items = $$("#menuList .menu-item");
  Menu.items.forEach((it, i) => {
    it.addEventListener("click", () => activate(it));
    it.addEventListener("mouseenter", () => {
      Menu.idx = i;
      Menu.items.forEach((x, j) => x.classList.toggle("sel", i === j));
    });
  });
  document.addEventListener("keydown", (e) => {
    if (!Menu.open) return;
    if (e.key === "Escape") {
      e.preventDefault();
      closeMenu();
    } else if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      Menu.idx =
        (Menu.idx + (e.key === "ArrowDown" ? 1 : -1) + Menu.items.length) %
        Menu.items.length;
      Menu.items.forEach((x, j) => x.classList.toggle("sel", j === Menu.idx));
      Menu.items[Menu.idx].focus();
      Sound.blip();
    } else if (e.key === "Enter") {
      const it = Menu.items[Menu.idx];
      if (it) activate(it);
    }
  });
}

export { Menu, openMenu, closeMenu };
