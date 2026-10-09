/**
 * Pixoria admin icon picker (T55) — vanilla JS, no dependencies.
 *
 * Wired by IconPickerWidget (apps/core/icon_utils.py). Each picker root is a
 *   <div class="icon-picker" data-icon-picker data-ip-sprite="…">
 * with an input (data-ip-input), a preview button (data-ip-preview), warning /
 * error lines and a popup (data-ip-popup) holding a search box and a grid.
 *
 * Icon names come from window.__LUCIDE_FULL_ICONS (every Lucide icon — the
 * admin-only sprite) and window.__LUCIDE_PUBLIC_ICONS (the small sprite the
 * public site ships). Picking an icon that is not in the public set yet shows
 * the «sync_icons» warning; `python manage.py sync_icons` then publishes it.
 */
(function () {
  "use strict";

  var FULL = window.__LUCIDE_FULL_ICONS || [];
  var PUBLIC = {};
  (window.__LUCIDE_PUBLIC_ICONS || []).forEach(function (n) {
    PUBLIC[n] = true;
  });
  var MAX_ITEMS = 240;

  var SVGNS = "http://www.w3.org/2000/svg";
  var XLINKNS = "http://www.w3.org/1999/xlink";

  function svgFor(root, name) {
    var svg = document.createElementNS(SVGNS, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("fill", "none");
    svg.setAttribute("stroke", "currentColor");
    svg.setAttribute("stroke-width", "2");
    svg.setAttribute("stroke-linecap", "round");
    svg.setAttribute("stroke-linejoin", "round");
    svg.setAttribute("aria-hidden", "true");
    var use = document.createElementNS(SVGNS, "use");
    var url = root.dataset.ipSprite + "#i-" + name;
    use.setAttribute("href", url);
    use.setAttributeNS(XLINKNS, "xlink:href", url);
    svg.appendChild(use);
    return svg;
  }

  function matches(name, query) {
    if (!query) return true;
    // جستجوی ساده: هر کلمهٔ جستجو باید در نام آیکون باشد
    return query
      .toLowerCase()
      .split(/\s+/)
      .every(function (part) {
        return name.indexOf(part) !== -1;
      });
  }

  function init(root) {
    var input = root.querySelector("[data-ip-input]");
    var previewBtn = root.querySelector("[data-ip-preview]");
    var popup = root.querySelector("[data-ip-popup]");
    var search = root.querySelector("[data-ip-search]");
    var grid = root.querySelector("[data-ip-grid]");
    var count = root.querySelector("[data-ip-count]");
    var warn = root.querySelector("[data-ip-warn]");
    var error = root.querySelector("[data-ip-error]");
    if (!input || !previewBtn || !popup) return;

    var open = false;
    var names = [];

    /* ---- وضعیتِ فیلد: پیش‌نمایش + هشدارها ---- */
    function syncState() {
      var value = input.value.trim();
      previewBtn.textContent = "";
      if (value && FULL.indexOf(value) !== -1) {
        previewBtn.appendChild(svgFor(root, value));
        previewBtn.classList.remove("ip-empty");
      } else {
        previewBtn.textContent = "—";
        previewBtn.classList.add("ip-empty");
      }
      warn.hidden = !(
        value &&
        FULL.indexOf(value) !== -1 &&
        !PUBLIC[value]
      );
      error.hidden = !(value && FULL.indexOf(value) === -1);
    }

    /* ---- رندرِ جدولِ آیکون‌ها ---- */
    function renderGrid() {
      var query = search.value.trim();
      grid.textContent = "";
      names = [];
      var shown = 0;
      for (var i = 0; i < FULL.length && shown < MAX_ITEMS; i++) {
        var name = FULL[i];
        if (!matches(name, query)) continue;
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "ip-item";
        btn.dataset.name = name;
        btn.title = name;
        btn.appendChild(svgFor(root, name));
        grid.appendChild(btn);
        names.push(name);
        shown++;
      }
      var total = FULL.filter(function (n) {
        return matches(n, query);
      }).length;
      count.textContent =
        shown < total
          ? shown + " از " + total + " آیکون — جستجو را دقیق‌تر کنید"
          : total + " آیکون";
    }

    function openPopup() {
      if (open) return;
      open = true;
      popup.hidden = false;
      search.value = "";
      renderGrid();
      search.focus();
      document.addEventListener("mousedown", onOutside);
    }

    function closePopup() {
      if (!open) return;
      open = false;
      popup.hidden = true;
      document.removeEventListener("mousedown", onOutside);
    }

    function onOutside(e) {
      if (!root.contains(e.target)) closePopup();
    }

    function select(name) {
      input.value = name;
      syncState();
      closePopup();
      input.focus();
    }

    previewBtn.addEventListener("click", function () {
      if (open) closePopup();
      else openPopup();
    });

    search.addEventListener("input", renderGrid);

    search.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        closePopup();
        input.focus();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        var first = grid.querySelector(".ip-item");
        if (first) first.focus();
      }
    });

    grid.addEventListener("click", function (e) {
      var btn = e.target.closest(".ip-item");
      if (btn) select(btn.dataset.name);
    });

    grid.addEventListener("keydown", function (e) {
      var items = [].slice.call(grid.querySelectorAll(".ip-item"));
      var idx = items.indexOf(document.activeElement);
      if (e.key === "ArrowRight" || e.key === "ArrowDown") {
        e.preventDefault();
        items[Math.min(items.length - 1, idx + 1)].focus();
      } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        e.preventDefault();
        if (idx <= 0) search.focus();
        else items[idx - 1].focus();
      } else if (e.key === "Escape") {
        closePopup();
        input.focus();
      }
    });

    input.addEventListener("input", syncState);
    input.addEventListener("blur", function () {
      // هشدارها فقط بعد از ترکِ فیلد محو می‌شوند تا حین تایپ مزاحم نباشند
      syncState();
    });

    root.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && open) {
        closePopup();
        input.focus();
      }
    });

    syncState();
  }

  document.querySelectorAll("[data-icon-picker]").forEach(init);
})();
