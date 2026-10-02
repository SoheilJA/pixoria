/**
 * Build a single local SVG sprite from lucide-static icons.
 * Output: static/icons/lucide.sprite.svg  (one <symbol> per icon)
 * Usage: node scripts/build_icon_sprite.js
 */
const fs = require("fs");
const path = require("path");

const SRC = path.join(__dirname, "..", "node_modules", "lucide-static", "icons");
const OUT_DIR = path.join(__dirname, "..", "static", "icons");
const OUT = path.join(OUT_DIR, "lucide.sprite.svg");

function stripComments(svg) {
  return svg.replace(/<!--[\s\S]*?-->/g, "");
}

function build() {
  if (!fs.existsSync(SRC)) {
    console.error("lucide-static not installed — run `npm install lucide-static`");
    process.exit(1);
  }
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const files = fs.readdirSync(SRC).filter((f) => f.endsWith(".svg")).sort();
  const symbols = [];
  let kept = 0;

  for (const file of files) {
    const name = path.basename(file, ".svg");
    const raw = stripComments(fs.readFileSync(path.join(SRC, file), "utf8")).trim();
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
  console.log(`sprite: ${kept} icons -> ${path.relative(process.cwd(), OUT)} (${kb} KB)`);
}

build();
