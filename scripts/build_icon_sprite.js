/**
 * Build the local Lucide SVG sprites from the pinned `lucide-static` package.
 *
 * Outputs (all under static/):
 *   icons/lucide.sprite.svg      PUBLIC sprite — only the icons the site
 *                                actually uses (templates + admin icon fields),
 *                                so the public payload stays small.
 *   icons/lucide.full.sprite.svg ADMIN-ONLY sprite — every icon in the package,
 *                                used only by the icon picker widget in the
 *                                admin.
 *   admin/js/lucide_full_icons.js `window.__LUCIDE_FULL_ICONS` /
 *                                `__LUCIDE_PUBLIC_ICONS` name lists for the
 *                                picker (search grid + "not in the public
 *                                sprite yet" warning).
 *
 * Usage:
 *   node scripts/build_icon_sprite.js [--extra path/to/icons.json]
 *
 * `--extra` merges a JSON array of extra icon names (from the DB, passed by
 * `python manage.py sync_icons`) into the PUBLIC sprite's "needed" set.
 *
 * Brand glyphs (instagram, linkedin, figma) ship inside lucide-static itself
 * now, so no separate brand source tree is merged anymore — every name maps to
 * exactly one symbol (duplicate ids in a sprite break `<use>`).
 */
const fs = require("fs");
const path = require("path");

const SRC = path.join(__dirname, "..", "node_modules", "lucide-static", "icons");
const OUT_DIR = path.join(__dirname, "..", "static", "icons");
const OUT_PUBLIC = path.join(OUT_DIR, "lucide.sprite.svg");
const OUT_FULL = path.join(OUT_DIR, "lucide.full.sprite.svg");
const OUT_NAMES = path.join(
  __dirname,
  "..",
  "static",
  "admin",
  "js",
  "lucide_full_icons.js",
);

function stripComments(svg) {
  return svg.replace(/<!--[\s\S]*?-->/g, "");
}

/** اسپریت عمومی: فقط آیکون‌های استفاده‌شده در قالب‌ها/ادمین + پارامتر --extra */
function collectNeeded(extraNames) {
  const names = new Set(extraNames || []);
  const scan = (dir, re) => {
    if (!fs.existsSync(dir)) return;
    for (const file of fs.readdirSync(dir)) {
      const full = path.join(dir, file);
      const stat = fs.statSync(full);
      if (stat.isDirectory()) scan(full, re);
      else if (/\.(html|md|py|js)$/.test(file)) {
        const text = fs.readFileSync(full, "utf8");
        let m;
        while ((m = re.exec(text))) names.add(m[1]);
      }
    }
  };
  scan(path.join(__dirname, "..", "templates"), /\{%\s*icon\s+"([^"]+)"/g);
  scan(path.join(__dirname, "..", "new"), /data-lucide="([^"]+)"/g);
  scan(path.join(__dirname, "..", "apps"), /icon\s*=\s*"([^"]+)"/g);
  // Always keep the fallback icon so models/admin never render empty.
  names.add("sparkles");
  return names;
}

/** فهرست همهٔ فایل‌های svg قابل دسترس */
function allIconFiles() {
  return fs.readdirSync(SRC).filter((f) => f.endsWith(".svg")).sort();
}

function symbolFor(file) {
  const name = path.basename(file, ".svg");
  const raw = stripComments(fs.readFileSync(path.join(SRC, file), "utf8")).trim();
  const inner = raw
    .replace(/^<svg[^>]*>/, "")
    .replace(/<\/svg>\s*$/, "")
    .trim();
  return `<symbol id="i-${name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${inner}</symbol>`;
}

function writeSprite(outPath, symbols) {
  const sprite =
    `<!-- Pixoria local Lucide icon sprite — generated from lucide-static v1.49.0 (ISC). Do not edit by hand. -->\n` +
    `<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">${symbols.join(
      "",
    )}</svg>`;
  fs.writeFileSync(outPath, sprite);
  return Math.round((fs.statSync(outPath).size / 1024) * 10) / 10;
}

function build() {
  if (!fs.existsSync(SRC)) {
    console.error("lucide-static not installed — run `npm install lucide-static`");
    process.exit(1);
  }

  // --extra: JSON array of names from the DB (sync_icons)
  let extraNames = null;
  const extraIdx = process.argv.indexOf("--extra");
  if (extraIdx !== -1) {
    try {
      extraNames = JSON.parse(fs.readFileSync(process.argv[extraIdx + 1], "utf8"));
    } catch (err) {
      console.error(`--extra: cannot read/parse file (${err.message})`);
      process.exit(1);
    }
  }

  fs.mkdirSync(OUT_DIR, { recursive: true });

  const needed = collectNeeded(extraNames);
  const files = allIconFiles();

  const publicSymbols = [];
  const fullSymbols = [];
  let kept = 0;
  for (const file of files) {
    const name = path.basename(file, ".svg");
    fullSymbols.push(symbolFor(file));
    if (needed.has(name)) {
      publicSymbols.push(symbolFor(file));
      kept++;
    }
  }

  const publicKb = writeSprite(OUT_PUBLIC, publicSymbols);
  const fullKb = writeSprite(OUT_FULL, fullSymbols);

  // فهرست نام‌ها برای پیکر آیکون ادمین
  const publicNames = publicSymbols
    .map((s) => s.match(/id="i-([^"]+)"/)[1])
    .sort();
  const fullNames = fullSymbols.map((s) => s.match(/id="i-([^"]+)"/)[1]).sort();
  fs.mkdirSync(path.dirname(OUT_NAMES), { recursive: true });
  fs.writeFileSync(
    OUT_NAMES,
    `/* Generated by scripts/build_icon_sprite.js — do not edit by hand.\n   Name lists for the admin icon picker (T55): the full Lucide set for the\n   search grid, and the public sprite set for the "not synced yet" warning. */\n` +
      `window.__LUCIDE_FULL_ICONS = ${JSON.stringify(fullNames)};\n` +
      `window.__LUCIDE_PUBLIC_ICONS = ${JSON.stringify(publicNames)};\n`,
  );

  const rel = (p) => path.relative(process.cwd(), p);
  console.log(
    `public sprite: ${kept} icons -> ${rel(OUT_PUBLIC)} (${publicKb} KB)`,
  );
  console.log(
    `admin sprite : ${fullNames.length} icons -> ${rel(OUT_FULL)} (${fullKb} KB)`,
  );
  console.log(`picker lists -> ${rel(OUT_NAMES)}`);
}

build();
