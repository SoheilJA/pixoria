"""Generate the Pixoria pixel wordmark, compact mark and favicon set.

Everything is derived from the self-hosted Vazirmatn font (SIL OFL) — the Persian
word «پیکسوریا» is rendered, pixelated onto a coarse grid and emitted as crisp
square pixels, so the logo is a real pixel-grid SVG (no external assets, no CDN).

Outputs (static/brand/):
  wordmark-full.svg        «پیکسوریا» — ink white + lime accent on the «ک»
  wordmark-mono-white.svg  monochrome white
  wordmark-mono-lime.svg   monochrome lime
  mark-compact.svg         pixel «پ» mark (favicons / app icon)
  favicon-16/32/48/192/512.png, apple-touch-icon.png, favicon.ico, favicon.svg
  site.webmanifest

Usage:  python scripts/build_pixel_wordmark.py
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "static" / "brand"
FONT = BASE / "static" / "fonts" / "vazirmatn-600-arabic.woff2"

TEXT = "پیکسوریا"
# Without libraqm the renderer cannot join/shape Arabic, so letters are laid out
# individually in visual (left-to-right) order; isolated letterforms are a
# deliberate pixel-font look.
ACCENT_LETTER = "ک"

INK = "#eaf2e8"  # --color-ink (used for preview renders)
LIME = "#c8ff3d"  # --color-lime (accent letter + favicon pixels)
NIGHT = "#04070a"  # --color-night (favicon background)

RENDER_SIZE = 700          # font px used for the source raster (then pixelated)
WORDMARK_ROWS = 14         # pixel rows of the full wordmark
MARK_ROWS = 12             # pixel rows of the compact «پ» mark
TRACKING_RATIO = 0.06      # gap between letters, as a fraction of the cap height
THRESHOLD = 100            # alpha coverage that keeps a pixel cell "on"


def render_grid(letters, rows, tracking_ratio=TRACKING_RATIO):
    """Rasterize `letters` (list of single chars) and pixelate to `rows` rows.

    Returns (grid, letter_spans) where letter_spans[i] = (x0, x1) column range of
    the i-th letter in the grid, so a single letter can be recoloured.
    """
    font = ImageFont.truetype(str(FONT), RENDER_SIZE)
    ascent, descent = font.getmetrics()
    cap = ascent + descent

    # Measure each letter and lay them out left-to-right with even tracking.
    widths = []
    tracking = round(cap * tracking_ratio)
    x = tracking
    for ch in letters:
        l, t, r, b = font.getbbox(ch)
        widths.append((r - l, l, t, r, b))
        x += (r - l) + tracking

    img = Image.new("L", (x, cap), 0)
    draw = ImageDraw.Draw(img)
    cursor = tracking
    for ch, (w, l, t, r, b) in zip(letters, widths):
        draw.text((cursor - l, -t), ch, fill=255, font=font)
        cursor += w + tracking

    # Pixelate the ink itself (not the whole line box) so the pixel size is
    # measured on the glyph height — otherwise descender/dot headroom shrinks
    # the wordmark to a few rows.
    ink_l, ink_t, ink_r, ink_b = img.getbbox()
    ink_w, ink_h = ink_r - ink_l, ink_b - ink_t
    ps = max(2, round(ink_h / rows))
    gw, gh = max(1, ink_w // ps), max(1, ink_h // ps)
    small = img.crop((ink_l, ink_t, ink_r, ink_b)).resize((gw, gh), Image.BOX)
    grid = [[small.getpixel((cx, cy)) >= THRESHOLD for cx in range(gw)] for cy in range(gh)]

    spans = []
    cursor = tracking
    for (w, l, t, r, b) in widths:
        spans.append(((cursor - ink_l) // ps, (cursor + w - ink_l) // ps))
        cursor += w + tracking
    return grid, spans


def runs(grid, color_of):
    """Collapse each row into horizontal runs of equal colour → (x, y, w, color)."""
    out = []
    for y, row in enumerate(grid):
        cx = 0
        while cx < len(row):
            if not row[cx]:
                cx += 1
                continue
            color = color_of(cx, y)
            w = 1
            while cx + w < len(row) and row[cx + w] and color_of(cx + w, y) == color:
                w += 1
            out.append((cx, y, w, color))
            cx += w
    return out


def grid_to_svg(grid, color_of, label, extra_attrs=""):
    w, h = len(grid[0]), len(grid)
    by_color = {}
    for x, y, rw, color in runs(grid, color_of):
        by_color.setdefault(color, []).append(f'<rect x="{x}" y="{y}" width="{rw}" height="1"/>')
    # "currentColor" resolves from CSS so the wordmark can be re-tinted per context.
    groups = "".join(
        f'<g fill="{"currentColor" if c == "currentColor" else c}">{"".join(rects)}</g>'
        for c, rects in by_color.items()
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'shape-rendering="crispEdges" role="img" aria-label="{label}"{extra_attrs}>'
        f"<title>{label}</title>{groups}</svg>"
    )


def write(name, content):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"  {name}  ({len(content):,} B)")


def grid_to_png(grid, size, color, bg=None, radius_ratio=0.0):
    """Rasterize a pixel grid to a PNG icon; `bg` None → transparent."""
    gw, gh = len(grid[0]), len(grid)
    scale = max(1, int(size / max(gw, gh) * 0.72))
    px = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rgb = tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))
    for y in range(gh):
        for x in range(gw):
            if not grid[y][x]:
                continue
            x0 = (size - gw * scale) // 2 + x * scale
            y0 = (size - gh * scale) // 2 + y * scale
            ImageDraw.Draw(px).rectangle([x0, y0, x0 + scale - 1, y0 + scale - 1], fill=rgb + (255,))
    if bg:
        bg_rgb = tuple(int(bg[i : i + 2], 16) for i in (1, 3, 5))
        base = Image.new("RGBA", (size, size), bg_rgb + (255,))
        if radius_ratio:
            mask = Image.new("L", (size, size), 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                [0, 0, size - 1, size - 1], radius=size * radius_ratio, fill=255
            )
            base.paste(px, mask=mask)
            return base
        return Image.alpha_composite(base, px)
    return px


def build():
    letters = list(reversed(TEXT))  # visual LTR order (RTL word)
    print(f"Pixelating «{TEXT}» → letters {letters}")

    grid, spans = render_grid(letters, WORDMARK_ROWS)
    accent_idx = letters.index(ACCENT_LETTER)
    a0, a1 = spans[accent_idx]
    print(f"  grid {len(grid[0])}x{len(grid)}  accent «{ACCENT_LETTER}» cols {a0}–{a1}")

    def color_of_full(x, y):
        return LIME if a0 <= x < a1 else "currentColor"

    write("wordmark-full.svg", grid_to_svg(grid, color_of_full, TEXT))
    # Monochrome variant inherits its colour from CSS (`currentColor`).
    write("wordmark-mono.svg", grid_to_svg(grid, lambda x, y: "currentColor", TEXT))

    mark, _ = render_grid(["پ"], MARK_ROWS, tracking_ratio=0.0)
    write("mark-compact.svg", grid_to_svg(mark, lambda x, y: "currentColor", "پیکسوریا"))

    # Favicon set — Google requires a multiple of 48x48 for rich results.
    for size in (16, 32, 48, 192, 512):
        icon = grid_to_png(mark, size, LIME, bg=NIGHT, radius_ratio=0.18)
        icon.save(OUT / f"favicon-{size}.png")
        print(f"  favicon-{size}.png")
    grid_to_png(mark, 180, LIME, bg=NIGHT).save(OUT / "apple-touch-icon.png")
    print("  apple-touch-icon.png")

    ico = grid_to_png(mark, 48, LIME, bg=NIGHT, radius_ratio=0.18)
    ico.save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print("  favicon.ico")

    write("favicon.svg", grid_to_svg(mark, lambda x, y: LIME, "پیکسوریا"))

    manifest = {
        "name": "پیکسوریا",
        "short_name": "پیکسوریا",
        "description": "استودیو طراحی و توسعهٔ محصولات دیجیتال پیکسوریا",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": NIGHT,
        "theme_color": NIGHT,
        "lang": "fa",
        "dir": "rtl",
        "icons": [
            {"src": "favicon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "favicon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "favicon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    write("site.webmanifest", json.dumps(manifest, ensure_ascii=False, indent=2))
    print("Done →", OUT.relative_to(BASE))


if __name__ == "__main__":
    build()
