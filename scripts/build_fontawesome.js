/**
 * Build the local Font Awesome (Free) webfont assets.
 *
 * Replaces the old Lucide sprite pipeline. Outputs (all under static/):
 *   fontawesome/css/all.min.css   FA CSS, trimmed so only woff2 font sources
 *                                 remain (the project ships woff2 only, like
 *                                 its other fonts — keeps the repo small).
 *   fontawesome/webfonts/*.woff2  the four woff2 files the CSS references.
 *   fontawesome/icons.json        {solid, regular, brands} name lists — the
 *                                 authoritative free-per-style icon sets, read
 *                                 by apps/core/icon_utils.py for validation.
 *   admin/js/fa_icons.js          window.__FA_ICONS for the admin icon picker.
 *
 * The per-style sets come from the package's own svgs/ directories: an icon
 * name is only "solid"/"regular"/"brands" if that folder ships its glyph.
 *
 * Usage:  node scripts/build_fontawesome.js
 */
const fs = require("fs");
const path = require("path");

const PKG = path.join(__dirname, "..", "node_modules", "@fortawesome", "fontawesome-free");
const STATIC = path.join(__dirname, "..", "static");
const OUT_CSS_DIR = path.join(STATIC, "fontawesome", "css");
const OUT_WF_DIR = path.join(STATIC, "fontawesome", "webfonts");
const OUT_ICONS_JSON = path.join(STATIC, "fontawesome", "icons.json");
const OUT_PICKER_JS = path.join(STATIC, "admin", "js", "fa_icons.js");

function readNames(dir) {
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".svg"))
    .map((f) => f.slice(0, -4))
    .sort((a, b) => a.localeCompare(b));
}

// ---- static validation of the Lucide → Font Awesome migration table ----
// The table lives in apps/core/icon_utils.py (LUCIDE_TO_FA). Every target name
// must exist in the free font, otherwise an admin-edited or template icon would
// silently render nothing. Also checks the literal {% icon "..." %} call sites
// in templates, so a renamed icon is caught at build time, not on the site.
function readLucideToFa() {
  const src = fs.readFileSync(
    path.join(__dirname, "..", "apps", "core", "icon_utils.py"),
    "utf8",
  );
  const start = src.indexOf("LUCIDE_TO_FA = {");
  const end = src.indexOf("\n}", start);
  const body = src.slice(start, end);
  const entries = [...body.matchAll(/"([a-z0-9-]+)":\s*"([a-z0-9-]+)"/g)];
  return entries.map((m) => [m[1], m[2]]);
}

function validateIconNames(styles) {
  const known = new Set([...styles.solid, ...styles.regular, ...styles.brands]);
  const problems = [];

  for (const [from, to] of readLucideToFa()) {
    if (!known.has(to)) {
      problems.push(`LUCIDE_TO_FA: "${from}" → "${to}" is not a free FA icon`);
    }
  }

  const tmplDir = path.join(__dirname, "..", "templates");
  const walk = (dir) =>
    fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
      const p = path.join(dir, e.name);
      return e.isDirectory() ? walk(p) : [p];
    });
  const mapping = new Map(readLucideToFa());
  for (const file of walk(tmplDir)) {
    if (!file.endsWith(".html")) continue;
    const src = fs.readFileSync(file, "utf8");
    for (const m of src.matchAll(/\{%\s*icon\s+"([a-z0-9-]+)"/g)) {
      const name = mapping.get(m[1]) || m[1];
      if (!known.has(name)) {
        problems.push(
          `${path.relative(tmplDir, file)}: icon "${m[1]}" has no free FA equivalent`,
        );
      }
    }
  }

  if (problems.length) {
    console.error("fontawesome: icon name validation FAILED");
    for (const p of problems) console.error("  " + p);
    process.exit(1);
  }
  return problems.length;
}

function main() {
  const styles = {
    solid: readNames(path.join(PKG, "svgs", "solid")),
    regular: readNames(path.join(PKG, "svgs", "regular")),
    brands: readNames(path.join(PKG, "svgs", "brands")),
  };
  const total = styles.solid.length + styles.regular.length + styles.brands.length;
  validateIconNames(styles);

  // ---- copy + trim the CSS (drop the woff/truetype sources) ----
  const cssDir = path.join(PKG, "css");
  let css = fs.readFileSync(path.join(cssDir, "all.min.css"), "utf8");
  // 'src:url(../webfonts/fa-solid-900.woff2) format("woff2"),url(...) format("woff"),url(...) format("truetype")'
  // → keep only the woff2 clause of every @font-face.
  let dropped = 0;
  css = css.replace(/url\(\.\.\/webfonts\/([a-z0-9-]+)\.(woff|ttf)\) format\("(woff|truetype)"\),?/g, (m) => {
    dropped += 1;
    return "";
  });
  // sweep leftovers: a trailing comma at the end of a src list, or a comma
  // that ended up directly before the closing brace after the removals.
  css = css.replace(/,\s*,/g, ",").replace(/src:\s*,/g, "src:").replace(/,\}/g, "}");

  fs.mkdirSync(OUT_CSS_DIR, { recursive: true });
  fs.writeFileSync(path.join(OUT_CSS_DIR, "all.min.css"), css, "utf8");

  // ---- copy the woff2 files the CSS actually references ----
  fs.mkdirSync(OUT_WF_DIR, { recursive: true });
  const woff2 = ["fa-brands-400.woff2", "fa-regular-400.woff2", "fa-solid-900.woff2", "fa-v4compatibility.woff2"];
  for (const f of woff2) {
    fs.copyFileSync(path.join(PKG, "webfonts", f), path.join(OUT_WF_DIR, f));
  }

  // ---- machine-readable icon lists ----
  const data = {
    version: require(path.join(PKG, "package.json")).version,
    styles,
  };
  fs.mkdirSync(path.dirname(OUT_ICONS_JSON), { recursive: true });
  fs.writeFileSync(OUT_ICONS_JSON, JSON.stringify(data, null, 0), "utf8");

  fs.mkdirSync(path.dirname(OUT_PICKER_JS), { recursive: true });
  fs.writeFileSync(
    OUT_PICKER_JS,
    `/* Generated by scripts/build_fontawesome.js — do not edit.\n` +
      ` * window.__FA_ICONS = { solid: [...], regular: [...], brands: [...] }\n` +
      ` * Free Font Awesome ${data.version} icon names per style.\n` +
      ` */\n` +
      `window.__FA_ICONS = ${JSON.stringify(styles)};\n`,
    "utf8"
  );

  console.log(
    `fontawesome: ${total} free icons ` +
      `(solid ${styles.solid.length}, regular ${styles.regular.length}, ` +
      `brands ${styles.brands.length}); dropped ${dropped} non-woff2 sources`
  );
}

main();
