/**
 * Build a single local SVG sprite from lucide-static icons.
 * Output: static/icons/lucide.sprite.svg  (one <symbol> per icon)
 * Usage: node scripts/build_icon_sprite.js
 *
 * Only icons referenced by the frontend (via grep for `data-lucide`/`{% icon %}`)
 * are included so the sprite stays small. Pass `--all` to emit every icon.
 *
 * A few brand glyphs (instagram, linkedin, figma) are not part of the
 * lucide-static npm package; their SVG sources live in scripts/brand-icons/
 * and are merged in here.
 */
const fs = require("fs");
const path = require("path");

const SRC = path.join(__dirname, "..", "node_modules", "lucide-static", "icons");
const EXTRA = path.join(__dirname, "brand-icons");
const OUT_DIR = path.join(__dirname, "..", "static", "icons");
const OUT = path.join(OUT_DIR, "lucide.sprite.svg");
const ALL = process.argv.includes("--all");

function stripComments(svg) {
  return svg.replace(/<!--[\s\S]*?-->/g, "");
}

function collectNeeded() {
  // Scan every Django template for {% icon "name" %} plus the v2 prototype
  // pages in new/ for data-lucide="name", and admin icon fields.
  const names = new Set();
  const scan = (globDir, re) => {
    if (!fs.existsSync(globDir)) return;
    for (const file of fs.readdirSync(globDir)) {
      const full = path.join(globDir, file);
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

function build() {
  if (!fs.existsSync(SRC)) {
    console.error("lucide-static not installed — run `npm install lucide-static`");
    process.exit(1);
  }
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const needed = ALL ? null : collectNeeded();
  const files = fs.readdirSync(SRC).filter((f) => f.endsWith(".svg")).sort();
  if (fs.existsSync(EXTRA)) {
    // brand icons missing from the npm package
    files.push(...fs.readdirSync(EXTRA).filter((f) => f.endsWith(".svg")).sort());
  }
  const symbols = [];
  let kept = 0;
  let skipped = 0;

  for (const file of files) {
    const name = path.basename(file, ".svg");
    if (needed && !needed.has(name)) {
      skipped++;
      continue;
    }
    const dir = fs.existsSync(path.join(SRC, file)) ? SRC : EXTRA;
    const raw = stripComments(fs.readFileSync(path.join(dir, file), "utf8")).trim();
    // Extract the inner content of the <svg> element
    const inner = raw.replace(/^<svg[^>]*>/, "").replace(/<\/svg>\s*$/, "").trim();
    symbols.push(
      `<symbol id="i-${name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${inner}</symbol>`
    );
    kept++;
  }

  const sprite =
    `<!-- Pixoria local Lucide icon sprite — generated from lucide-static v1.49.0 (ISC). Do not edit by hand. -->\n` +
    `<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">${symbols.join("")}</svg>`;

  fs.writeFileSync(OUT, sprite);
  const kb = Math.round((fs.statSync(OUT).size / 1024) * 10) / 10;
  console.log(
    `sprite: ${kept} icons -> ${path.relative(process.cwd(), OUT)} (${kb} KB)` +
      (skipped ? `, skipped ${skipped} unused` : "")
  );
}

build();
