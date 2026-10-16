/**
 * فرمِ تطبیقیِ «نظر مشتری»: فقط فیلدهای مربوط به نوعِ انتخاب‌شده (متن/ویدیو/صوت)
 * نمایش داده می‌شوند. وانیلا جاوااسکریپت — بدون jQuery یا کتابخانه.
 *
 * روی صفحهٔ اختصاصی، فیلدست‌ها کلاس kind-* دارند و کلشان مخفی می‌شود؛ روی
 * اینلاین‌های جدولی فیلدست نیستند، بنابراین ردیفِ هر فیلد را جداگانه مخفی
 * می‌کنیم. هر دو حالت با شناسه‌های «id_kind» و «id_<prefix>-kind» کار می‌کنند.
 */
(function () {
  "use strict";

  // فیلدهایی که فقط به یک نوع تعلق دارند.
  const KIND_FIELDS = {
    text: ["text"],
    video: ["video_file", "video_url", "video_poster", "video_duration"],
    audio: ["audio_file", "audio_url", "audio_title", "audio_project", "audio_duration"],
  };
  const KIND_CLASS = { text: "kind-text", video: "kind-video", audio: "kind-audio" };
  const SUFFIX = "-kind";

  function syncKind(select) {
    if (!select || !KIND_CLASS[select.value]) return;
    const prefix = select.id.slice(0, -SUFFIX.length); // "id" یا "id_testimonials-0"

    // فیلدست‌های اختصاصی (صفحهٔ کامل)
    document
      .querySelectorAll("fieldset.kind-text, fieldset.kind-video, fieldset.kind-audio")
      .forEach(function (fs) {
        fs.style.display = fs.classList.contains(KIND_CLASS[select.value]) ? "" : "none";
      });

    // ردیف‌های جداگانه (اینلاین‌ها)
    Object.keys(KIND_FIELDS).forEach(function (kind) {
      const show = kind === select.value;
      KIND_FIELDS[kind].forEach(function (field) {
        const el = document.getElementById(prefix + "-" + field);
        if (!el) return;
        const row = el.closest(".form-row");
        if (row) row.style.display = show ? "" : "none";
      });
    });
  }

  function wire(select) {
    if (!select || select.dataset.kindWired) return;
    select.dataset.kindWired = "1";
    select.addEventListener("change", function () {
      syncKind(select);
    });
    syncKind(select);
  }

  function init(root) {
    (root || document)
      .querySelectorAll("select[id$='" + SUFFIX + "']")
      .forEach(wire);
  }

  document.addEventListener("DOMContentLoaded", function () {
    init(document);
  });

  // اینلاین‌هایی که داینامیک اضافه می‌شوند.
  document.addEventListener("formset:added", function (e) {
    if (e.target) init(e.target);
  });
})();
