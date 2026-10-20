// فیگورهای @lucasmarkes/hairline — وندورِ لوکال (static/js/vendor/hairline.js)
// مونتِ اعلامی: کافی است المانی با data-hl="<نامِ فیگور>" در DOM باشد.
// گزینه‌ها: data-hl-intensity="0..1" (پیش‌فرضِ هر فیگور)
// سازگار با hx-boost: کلِ body هر بار سواپ میشود؛ این ماژول بعد از هر
// htmx:afterSettle دوباره سکن میگیرد و هاستهای تازه را مونت میکند —
// خودِ ماژولِ ESM فقط یک بار fetch میشود (کشِ import).
const boot = document.querySelector("script[data-hl-lib]");
const LIB_URL = boot ? boot.dataset.hlLib : null;

let libPromise = null;

const loadLib = () => (libPromise ||= import(LIB_URL));

async function mountFigure(host) {
  if (host.dataset.hlMounted) return;
  host.dataset.hlMounted = "1";
  try {
    const figs = await loadLib();
    const draw = figs[host.dataset.hl];
    if (typeof draw !== "function") return;
    const opts = { play: true };
    const intensity = parseFloat(host.dataset.hlIntensity);
    if (!Number.isNaN(intensity)) opts.intensity = intensity;
    host._hairline = draw(host, opts);
  } catch {
    // شبکه یا کتابخانه در دسترس نیست — فریمِ بافتدارِ خالی میماند
    host.classList.add("hl-broken");
    delete host.dataset.hlMounted;
  }
}

// از بین بردنِ امنِ یک فیگور و آزادسازیِ هاست جهتِ مونتِ دوباره
function unmountFigure(host) {
  const fig = host._hairline;
  if (fig && typeof fig.destroy === "function") {
    try { fig.destroy(); } catch { /* هرگز مسدود نمیکند */ }
  }
  delete host._hairline;
  delete host.dataset.hlMounted;
}

function scanFigures() {
  if (!LIB_URL) return;
  // حرکت کمتر / ری‌دیوس: بی‌تحرک بماند
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  document.querySelectorAll("[data-hl]").forEach(mountFigure);
}

document.addEventListener("DOMContentLoaded", () => scanFigures());
document.addEventListener("htmx:afterSettle", () => scanFigures());

// کتابخانه اندازهٔ SVG را فقط در لحظهٔ مونت میگیرد (ResizeObserver ندارد)؛
// پس با تغییرِ اندازهٔ صفحه همهٔ فیگورها را از نو مونت میکنیم.
let resizeTimer = null;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    document.querySelectorAll("[data-hl]").forEach(unmountFigure);
    scanFigures();
  }, 250);
});
