#!/usr/bin/env node
/**
 * scripts/build_brand.js — build the Pixoria brand option set (T57).
 *
 * Six space / solar-system-themed logo concepts under static/brand/option-N-x/:
 *   logo-mark.svg        the mark alone, in gold (for dark backgrounds)
 *   logo-mono-light.svg  monochrome cream (for ink backgrounds)
 *   logo-mono-dark.svg   monochrome ink (for cream backgrounds)
 *   logo-full.svg        mark + Persian wordmark «پیکسوریا»
 *   favicon.svg          a chunky 16px-safe icon variant
 *   favicon-16.png, favicon-32.png, apple-touch-icon.png (180),
 *   icon-192.png, icon-512.png
 *
 * Wordmarks are real SVG PATHS traced from the self-hosted fonts (no font
 * dependency at runtime):
 *   Persian «پیکسوریا» — Vazirmatn. Arabic joining needs complex-text
 *   shaping, which neither opentype.js nor Node has built in, so the shaped
 *   string comes from the project's existing arabic_reshaper + python-bidi
 *   stack (the same shaping scripts/build_pixel_wordmark.py uses) via a
 *   one-shot child process. The outlines themselves are opentype.js.
 *   Latin "PIXORIA" — Space Grotesk (plain ASCII, no shaping).
 *
 * woff2 is decompressed to TTF with wawoff2 (opentype.js needs TTF), and the
 * PNGs are rasterized with sharp. All devDependencies — nothing here ships to
 * the browser.
 *
 * Usage:  node scripts/build_brand.js
 */

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const opentype = require("opentype.js");
const wawoff2 = require("wawoff2");
const sharp = require("sharp");

const BASE = path.resolve(__dirname, "..");
const OUT = path.join(BASE, "static", "brand");

/* ---------------------------------------------------------------- palette */

const INK = "#0a0a0c";
const CREAM = "#f5f3ee";

const PALETTES = {
  // gold full-colour mark (dark backgrounds)
  gold: { main: "#c9a15a", accent: "#e8c47a", shade: "#8f6b2c", bg: INK },
  // single-colour variants — `bg` is the assumed page background, used for
  // negative-space details (the rocket's porthole) so the shape never closes up
  light: { main: CREAM, accent: CREAM, shade: CREAM, bg: INK },
  dark: { main: INK, accent: INK, shade: INK, bg: CREAM },
};

/* ---------------------------------------------------------------- helpers */

/** A four-pointed star (concave sides) as one path, centred at (cx, cy). */
function star4(cx, cy, R, r) {
  const pts = [
    [0, -R],
    [r, -r],
    [R, 0],
    [r, r],
    [0, R],
    [-r, r],
    [-R, 0],
    [-r, -r],
  ];
  return (
    "M" +
    pts
      .map(([dx, dy]) => `${(cx + dx).toFixed(1)} ${(cy + dy).toFixed(1)}`)
      .join(" L") +
    " Z"
  );
}

/** opentype.js path commands → an SVG `d` string. */
function cmdsToD(cmds) {
  return cmds
    .map((c) => {
      if (c.type === "Z") return "Z";
      if (c.type === "Q") return `Q${c.x1} ${c.y1} ${c.x} ${c.y}`;
      if (c.type === "C") return `C${c.x1} ${c.y1} ${c.x2} ${c.y2} ${c.x} ${c.y}`;
      return `${c.type}${c.x} ${c.y}`;
    })
    .join(" ");
}

/**
 * Lay `text` out as a single SVG path starting at (x, baseline), one glyph
 * after another. Returns the joined `d` and the total advance width.
 */
function textToPath(font, text, x, y, size, spacing = 0) {
  const scale = size / font.unitsPerEm;
  let cursor = x;
  let d = "";
  for (const ch of text) {
    const glyph = font.charToGlyph(ch);
    d += cmdsToD(glyph.getPath(cursor, y, size).commands) + " ";
    cursor += glyph.advanceWidth * scale + spacing;
  }
  return { d, advance: cursor - x };
}

/** Ink bounding box of textToPath's output (used to centre the wordmark). */
function textBBox(font, text, x, y, size, spacing = 0) {
  const scale = size / font.unitsPerEm;
  let cursor = x;
  let bb = null;
  for (const ch of text) {
    const glyph = font.charToGlyph(ch);
    const b = glyph.getPath(cursor, y, size).getBoundingBox();
    if (!bb) bb = { x1: b.x1, y1: b.y1, x2: b.x2, y2: b.y2 };
    else {
      bb.x1 = Math.min(bb.x1, b.x1);
      bb.y1 = Math.min(bb.y1, b.y1);
      bb.x2 = Math.max(bb.x2, b.x2);
      bb.y2 = Math.max(bb.y2, b.y2);
    }
    cursor += glyph.advanceWidth * scale + spacing;
  }
  return bb;
}

function svgShell(viewBox, body, label, width, height) {
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" ` +
    `viewBox="${viewBox}" role="img" aria-label="${label}"><title>${label}</title>${body}</svg>`
  );
}

/* ---------------------------------------------------------------- concepts */

const CST = [
  [15, 50],
  [25, 39],
  [34, 29],
  [42, 20],
  [50, 12],
];

const CONCEPTS = [
  {
    id: "option-1-orbit",
    fa: "مدار",
    latin: "Orbit",
    blurb: "سیارهٔ طلایی با حلقهٔ اریب و ماهِ روی حلقه — همان امbleم امروزی سایت.",
    mark: (p) =>
      `<ellipse cx="32" cy="32" rx="27" ry="10.5" transform="rotate(-20 32 32)" fill="none" stroke="${p.main}" stroke-width="3.2" opacity="0.55"/>` +
      `<circle cx="32" cy="32" r="13.5" fill="${p.main}"/>` +
      `<circle cx="57.4" cy="22.8" r="3.4" fill="${p.accent}"/>`,
    icon: (p) =>
      `<ellipse cx="32" cy="32" rx="26" ry="11" transform="rotate(-20 32 32)" fill="none" stroke="${p.main}" stroke-width="6.5"/>` +
      `<circle cx="32" cy="32" r="15" fill="${p.main}"/>` +
      `<circle cx="56" cy="23.5" r="5.5" fill="${p.accent}"/>`,
  },
  {
    id: "option-2-eclipse",
    fa: "کسوف",
    latin: "Eclipse",
    blurb: "حلقهٔ درخشان خورشیدگرفتگی با مهرهٔ الماسِ در مرکز.",
    mark: (p) =>
      `<path fill-rule="evenodd" fill="${p.main}" d="M32 5a27 27 0 1 1 0 54 27 27 0 1 1 0-54Zm0 9.5a17.5 17.5 0 1 1 0 35 17.5 17.5 0 1 1 0-35Z"/>` +
      `<path fill="${p.accent}" d="${star4(41, 22, 5.5, 2.2)}"/>`,
    icon: (p) =>
      `<path fill-rule="evenodd" fill="${p.main}" d="M32 4a28 28 0 1 1 0 56 28 28 0 1 1 0-56Zm0 14a14 14 0 1 1 0 28 14 14 0 1 1 0-28Z"/>` +
      `<path fill="${p.accent}" d="${star4(40, 22, 5, 2)}"/>`,
  },
  {
    id: "option-3-comet",
    fa: "دنباله‌دار",
    latin: "Comet",
    blurb: "هستهٔ درخشان با دو دمِّ نوری که در حرکت پشت سرش می‌آیند.",
    mark: (p) =>
      `<path d="M31 33C40 42 49 49 57 55" fill="none" stroke="${p.main}" stroke-width="6.5" stroke-linecap="round" opacity="0.9"/>` +
      `<path d="M28 29C37 37 45 43 52 48" fill="none" stroke="${p.accent}" stroke-width="3.2" stroke-linecap="round" opacity="0.6"/>` +
      `<circle cx="23" cy="23" r="9.5" fill="${p.main}"/>` +
      `<circle cx="26.5" cy="19.5" r="2.2" fill="${p.accent}" opacity="0.75"/>`,
    icon: (p) =>
      `<path d="M30 30C40 40 49 48 56 54" fill="none" stroke="${p.main}" stroke-width="13" stroke-linecap="round"/>` +
      `<circle cx="21" cy="21" r="14" fill="${p.main}"/>`,
  },
  {
    id: "option-4-constellation",
    fa: "صورت فلکی",
    latin: "Constellation",
    blurb: "ستاره‌هایی که با خطوط نازک به هم وصل‌اند — مسیرِ صعود به سوی ستارهٔ بزرگ.",
    mark: (p) => {
      const lines = CST.slice(0, -1)
        .map((a, i) =>
          `<line x1="${a[0]}" y1="${a[1]}" x2="${CST[i + 1][0]}" y2="${CST[i + 1][1]}" stroke="${p.main}" stroke-width="1.8" opacity="0.7"/>`
        )
        .join("");
      const dots = CST.slice(0, -1)
        .map((c) => `<circle cx="${c[0]}" cy="${c[1]}" r="2.6" fill="${p.main}"/>`)
        .join("");
      return lines + dots + `<path fill="${p.accent}" d="${star4(50, 12, 6.5, 2.6)}"/>`;
    },
    icon: (p) => {
      // Favicon-thick: at 16px a 4.5-unit stroke is sub-pixel, so the lines,
      // dots and star are all bulked up to keep the constellation readable.
      const lines = CST.slice(0, -1)
        .map((a, i) =>
          `<line x1="${a[0]}" y1="${a[1]}" x2="${CST[i + 1][0]}" y2="${CST[i + 1][1]}" stroke="${p.main}" stroke-width="8" opacity="0.95" stroke-linecap="round"/>`
        )
        .join("");
      const dots = CST.slice(0, -1)
        .map((c) => `<circle cx="${c[0]}" cy="${c[1]}" r="7.5" fill="${p.main}"/>`)
        .join("");
      return lines + dots + `<path fill="${p.accent}" d="${star4(50, 12, 11, 4.4)}"/>`;
    },
  },
  {
    id: "option-5-rocket",
    fa: "موشک",
    latin: "Rocket",
    blurb: "موشکِ صعودکننده با باله‌ها، پنجرهٔ گرد و شعلهٔ طلایی.",
    mark: (p) =>
      `<path fill="${p.main}" d="M24 20L32 7L40 20V47a8 8 0 0 1-16 0Z"/>` +
      `<path fill="${p.shade}" d="M24 32L14.5 49h9.5Z"/>` +
      `<path fill="${p.shade}" d="M40 32L49.5 49h-9.5Z"/>` +
      `<circle cx="32" cy="27" r="5.5" fill="${p.bg}"/>` +
      `<path fill="${p.accent}" d="M26 48L32 60L38 48Z"/>`,
    icon: (p) =>
      // Wider than the mark: a narrow rocket body vanishes at 16px.
      `<path fill="${p.main}" d="M21 21L32 7L43 21V45a11 11 0 0 1-22 0Z"/>` +
      `<path fill="${p.shade}" d="M21 32L10 51h11Z"/>` +
      `<path fill="${p.shade}" d="M43 32L54 51H43Z"/>` +
      `<circle cx="32" cy="26" r="7.5" fill="${p.bg}"/>` +
      `<path fill="${p.accent}" d="M24 46L32 62L40 46Z"/>`,
  },
  {
    id: "option-6-crescent",
    fa: "هلال",
    latin: "Crescent",
    blurb: "ماهِ نو با ستارهٔ همراه — برشی از یک دایره با قانون fill-rule.",
    mark: (p) =>
      `<path fill-rule="evenodd" fill="${p.main}" d="M33 12a20 20 0 1 1 0 40 20 20 0 1 1 0-40Zm7.5 8.5a11.5 11.5 0 1 1 0 23 11.5 11.5 0 1 1 0-23Z"/>` +
      `<path fill="${p.accent}" d="${star4(14, 50, 5, 2)}"/>`,
    icon: (p) =>
      `<path fill-rule="evenodd" fill="${p.main}" d="M33 11a21 21 0 1 1 0 42 21 21 0 1 1 0-42Zm8 9a12 12 0 1 1 0 24 12 12 0 1 1 0-24Z"/>` +
      `<path fill="${p.accent}" d="${star4(14, 50, 6, 2.4)}"/>`,
  },
];

/* ---------------------------------------------------------------- fonts */

const PY_SHAPER =
  "import sys; sys.stdout.reconfigure(encoding='utf-8')\n" +
  "import arabic_reshaper\n" +
  "from bidi.algorithm import get_display\n" +
  "sys.stdout.write(get_display(arabic_reshaper.reshape(sys.argv[1])))";

const pythonBin =
  process.platform === "win32" ? "venv/Scripts/python.exe" : "venv/bin/python";

function shapePersian(text) {
  return execFileSync(pythonBin, ["-c", PY_SHAPER, text], {
    encoding: "utf-8",
    cwd: BASE,
  });
}

async function loadFont(rel, probe = "M") {
  const u8 = await wawoff2.decompress(fs.readFileSync(path.join(BASE, rel)));
  const ab = u8.buffer.slice(u8.byteOffset, u8.byteOffset + u8.byteLength);
  const font = opentype.parse(ab);
  // Abort loudly rather than emit .notdef boxes.
  if (font.charToGlyph(probe).name === ".notdef") throw new Error(`could not read font ${rel}`);
  return font;
}

/* ---------------------------------------------------------------- output */

function write(rel, content) {
  const full = path.join(OUT, rel);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  fs.writeFileSync(full, content, "utf-8");
  console.log(`  ${rel}  (${Buffer.byteLength(content)} B)`);
}

async function pngFrom(svgBody, size, rel) {
  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 64 64">` +
    svgBody +
    `</svg>`;
  await sharp(Buffer.from(svg)).png().toFile(path.join(OUT, rel));
  console.log(`  ${rel}  (${size}×${size})`);
}

/** The full lockup: mark on the right (RTL), Persian wordmark to its left. */
function fullLogoSvg(concept, fontFa, visual) {
  const SIZE = 34;
  const probe = textToPath(fontFa, visual, 0, 0, SIZE);
  const bb = textBBox(fontFa, visual, 0, 0, SIZE);
  const baseline = 32 - (bb.y1 + bb.y2) / 2; // ink vertically centred on the mark
  const padL = 6;
  const word = textToPath(fontFa, visual, padL, baseline, SIZE);
  const gap = 18;
  const w = padL + word.advance + gap + 64;

  const gid = `grad-${concept.id}`;
  const defs =
    `<defs><linearGradient id="${gid}" x1="1" y1="0" x2="0" y2="0">` +
    `<stop offset="0" stop-color="#e8c47a"/>` +
    `<stop offset="0.55" stop-color="#c9a15a"/>` +
    `<stop offset="1" stop-color="#8f6b2c"/></linearGradient></defs>`;
  const body =
    defs +
    `<path fill="url(#${gid})" d="${word.d}"/>` +
    `<g transform="translate(${padL + word.advance + gap}, 0)">${concept.mark(PALETTES.gold)}</g>`;
  return svgShell(`0 0 ${w.toFixed(1)} 64`, body, "پیکسوریا", Math.round(w), 64);
}

async function build() {
  console.log("loading fonts (woff2 → ttf → opentype.js)…");
  // "ی" is present in the arabic subset, "M" is not.
  const fontFa = await loadFont("static/fonts/vazirmatn-600-arabic.woff2", "ی");
  const fontLa = await loadFont("static/fonts/space-grotesk-500-latin.woff2");

  const visual = shapePersian("پیکسوریا");
  const notdef = [...visual].some((ch) => fontFa.charToGlyph(ch).name === ".notdef");
  if (notdef) throw new Error("the Vazirmatn arabic subset lacks a shaped glyph");
  console.log(`wordmark «پیکسوریا» shaped → ${visual.length} glyphs`);

  const latinWm = textToPath(fontLa, "PIXORIA", 0, 0, 22, 2.4);

  for (const c of CONCEPTS) {
    console.log(`\n${c.id} — ${c.fa}`);
    write(`${c.id}/logo-mark.svg`, svgShell("0 0 64 64", c.mark(PALETTES.gold), "پیکسوریا", 64, 64));
    write(`${c.id}/logo-mono-light.svg`, svgShell("0 0 64 64", c.mark(PALETTES.light), "پیکسوریا", 64, 64));
    write(`${c.id}/logo-mono-dark.svg`, svgShell("0 0 64 64", c.mark(PALETTES.dark), "پیکسوریا", 64, 64));
    write(`${c.id}/logo-full.svg`, fullLogoSvg(c, fontFa, visual));
    write(`${c.id}/favicon.svg`, svgShell("0 0 64 64", c.icon(PALETTES.gold), "پیکسوریا", 64, 64));

    // PNGs: the chunky icon scaled into the maskable safe zone on an ink tile.
    const pad = 0.74;
    const t = (1 - pad) * 32;
    const tile = `<rect width="64" height="64" fill="${INK}"/>` +
      `<g transform="translate(${t} ${t}) scale(${pad})">${c.icon(PALETTES.gold)}</g>`;
    await pngFrom(tile, 16, `${c.id}/favicon-16.png`);
    await pngFrom(tile, 32, `${c.id}/favicon-32.png`);
    await pngFrom(tile, 180, `${c.id}/apple-touch-icon.png`);
    await pngFrom(tile, 192, `${c.id}/icon-192.png`);
    await pngFrom(tile, 512, `${c.id}/icon-512.png`);
  }

  write("README.md", readme(visual, latinWm.advance));
  write("index.html", previewSheet());
  console.log("\nDone → static/brand/");
}

function readme(wordmarkAdvance, latinAdvance) {
  const rows = CONCEPTS.map((c, i) =>
    `| ${i + 1} | [${c.id}]( ${c.id}/) | «${c.fa}» / ${c.latin} | ${c.blurb} |`
  ).join("\n");

  return `# پیکسوریا — مجموعهٔ لوگو و فاوآیکون

شش مفهوم لوگو با تم فضایی/سامانهٔ خورشیدی برای «پیکسوریا / Pixoria»، با
پالتِ سایت: طلایی \`#c9a15a\` / \`#e8c47a\` / \`#8f6b2c\`، جوهر \`#0a0a0c\`،
کرم \`#f5f3ee\` و سلطنتی \`#2e63ff\`.

هر گزینه یک پوشهٔ مستقل در \`static/brand/\` است:

| # | پوشه | نام | ایده |
|---|---|---|---|
${rows}

## فایل‌های هر گزینه

- \`logo-mark.svg\` — نشان به‌تنهایی، طلایی (روی پس‌زمینهٔ تیره)
- \`logo-mono-light.svg\` — تک‌رنگِ کرم (روی جوهر)
- \`logo-mono-dark.svg\` — تک‌رنگِ جوهر (روی کرم)
- \`logo-full.svg\` — نشان + واژه‌ markِ فارسی «پیکسوریا»
- \`favicon.svg\` — نسخهٔ ضخیم‌شده برای خواندن در ۱۶–۳۲ پیکسل
- \`favicon-16.png\`، \`favicon-32.png\`، \`apple-touch-icon.png\` (۱۸۰)،
  \`icon-192.png\`، \`icon-512.png\` — روی کاشیِ جوهر، با حاشیهٔ امنِ maskable

## نکات طراحی

- واژه‌مارک‌ها **مسیرِ واقعی SVG** هستند، نه متن: حروف از فونت‌های
  self-hosted پروژه (Vazirmatn برای فارسی، Space Grotesk برای لاتین)
  توسط \`scripts/build_brand.js\* استخراج شده‌اند. در زمان اجرا هیچ
  فونتی نیاز نیست.
- شکل‌دهی فارسی (اتصال حروف + ترتیب بصری RTL) توسط همین استکِ موجود
  پروژه انجام می‌شود (\`arabic_reshaper\` + \`python-bidi\`، مثل
  \`scripts/build_pixel_wordmark.py\`)؛ خود مسیرها با opentype.js از روی
  فونت گرفته می‌شوند.
- نشان‌ها کاملاً تخت (flat) و ساده‌اند تا در ۱۶ پیکسل هم خوب بخوانند؛
  \`favicon.svg\` نسخهٔ ضخیم‌شدهٔ هر نشان است.
- روی پس‌زمینهٔ روشن از \`logo-mono-dark.svg\` و روی تیره از
  \`logo-mono-light.svg\` استفاده کنید.

## بازسازی

\`\`\`bash
node scripts/build_brand.js
\`\`\`

وابستگی‌های توسعه (در \`package.json\`، devDependencies): \`opentype.js\`،
\`sharp\`، \`wawoff2\`. چیزی از این اسکریپت در زمان اجرا لود نمی‌شود.

## انتخاب و فعال‌سازی

هنوز هیچ‌کدام روی سایت فعال نیست؛ انتخاب از طریق \`SiteSettings\` در
مدیریت و سیم‌کشی در قالب‌ها انجام می‌شود (T58). پیش‌نمایشِ کنارهمِ همهٔ
گزینه‌ها روی پس‌زمینهٔ تیره و روشن: [\`index.html\`](index.html) (محلی).

> نکته: فایل‌های ریشهٔ \`static/brand/\` (مثل \`favicon.ico\`،
> \`wordmark-full.svg\` و PNGها) هنوز مجموعهٔ پیکسلیِ v1 هستند تا T58
> انتخاب جدید را سیم‌کشی کند؛ این اسکریپت آن‌ها را دست نمی‌زند.
`;
}

function previewSheet() {
  const card = (c, i) => {
    const tiles = (dark) => {
      const mark = dark
        ? `<div class="tile"><img src="${c.id}/logo-full.svg" alt="logo-full" style="height:54px"><div class="lbl">logo-full</div></div>
           <div class="tile"><img src="${c.id}/logo-mark.svg" alt="mark" style="height:42px"><div class="lbl">mark</div></div>
           <div class="tile"><img src="${c.id}/logo-mono-light.svg" alt="mono-light" style="height:42px"><div class="lbl">mono-light</div></div>`
        : `<div class="tile"><img src="${c.id}/logo-mono-dark.svg" alt="mono-dark" style="height:42px"><div class="lbl">mono-dark</div></div>
           <div class="tile"><img src="${c.id}/logo-mark.svg" alt="mark" style="height:42px"><div class="lbl">mark</div></div>`;
      return `${mark}
      <div class="row tight">
        <div class="tile sq"><img src="${c.id}/favicon-16.png" alt="16" style="width:32px;image-rendering:pixelated"><div class="lbl">۱۶</div></div>
        <div class="tile sq"><img src="${c.id}/favicon-32.png" alt="32" style="width:40px"><div class="lbl">۳۲</div></div>
        <div class="tile sq"><img src="${c.id}/icon-192.png" alt="192" style="width:56px"><div class="lbl">۱۹۲</div></div>
      </div>`;
    };
    return `<div class="card">
      <h2>${["۱", "۲", "۳", "۴", "۵", "۶"][i]} · ${c.fa}</h2>
      <div class="latin">${c.id}</div>
      <p class="blurb">${c.blurb}</p>
      <div class="row">${tiles(true)}</div>
    </div>`;
  };

  return `<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>پیکسوریا — مجموعهٔ لوگو</title>
<style>
  :root { --gold:#c9a15a; --ink:#0a0a0c; --cream:#f5f3ee; --cream2:#efece5; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { font-family:system-ui,"Segoe UI",Tahoma,sans-serif; background:var(--ink); color:var(--cream); }
  .sheet { padding:3rem clamp(1rem,5vw,4rem); }
  .sheet.light { background:var(--cream2); color:var(--ink); }
  h1 { font-size:clamp(1.4rem,3.5vw,2.2rem); }
  .sub { opacity:.6; margin-top:.4rem; font-size:.9rem; }
  .grid { display:grid; gap:1.25rem; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); margin-top:2.25rem; }
  .card { border:1px solid rgba(201,161,90,.3); border-radius:1.25rem; padding:1.4rem; background:rgba(255,255,255,.03); }
  .light .card { background:rgba(10,10,12,.03); border-color:rgba(143,107,44,.35); }
  .card h2 { font-size:1.05rem; }
  .latin { font-family:ui-monospace,monospace; font-size:.72rem; opacity:.5; letter-spacing:.08em; margin-top:.15rem; }
  .blurb { font-size:.82rem; opacity:.7; margin-top:.5rem; line-height:1.7; }
  .row { display:flex; align-items:center; gap:.9rem; flex-wrap:wrap; margin-top:1rem; }
  .row.tight { gap:.5rem; margin-top:.75rem; }
  .tile { border-radius:.9rem; padding:.65rem .9rem; background:var(--ink); display:grid; place-items:center; min-height:64px; }
  .light .tile { background:var(--cream); }
  .tile.sq { padding:.5rem; }
  .lbl { font-size:.62rem; opacity:.5; margin-top:.3rem; }
  .rule { height:1px; background:linear-gradient(90deg,transparent,var(--gold),transparent); border:0; }
</style>
</head>
<body>
  <section class="sheet">
    <h1>مجموعهٔ لوگوی پیکسوریا</h1>
    <p class="sub">شش مفهوم با تم فضایی — روی پس‌زمینهٔ تیره · پیش‌نمایش محلی (static/brand/index.html)</p>
    <div class="grid">${CONCEPTS.map(card).join("")}</div>
  </section>
  <hr class="rule">
  <section class="sheet light">
    <h1>روی پس‌زمینهٔ روشن</h1>
    <p class="sub">نسخهٔ تک‌رنگِ جوهر (logo-mono-dark) + فاوآیکون‌ها</p>
    <div class="grid">${CONCEPTS.map((c) => card(c, -1)).join("")}</div>
  </section>
</body>
</html>`;
}

build().catch((e) => {
  console.error(e);
  process.exit(1);
});
