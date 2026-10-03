"""Generate the Pixoria pixel wordmark, compact mark and favicon set.

Everything is derived from the self-hosted Vazirmatn font (SIL OFL) — the Persian
word «پیکسوریا» is rendered as a *joined* word, pixelated onto a coarse grid and
emitted as crisp square pixels, so the logo is a real pixel-grid SVG (no external
assets, no CDN).

Persian joining needs complex text shaping, which PIL cannot do without
libraqm (not available here). `arabic_reshaper` converts the word to Unicode
presentation forms (ﭖ ﯿ ﮐ …) so the letters connect without a shaper, and
`python-bidi` flips the result into visual order for PIL's left-to-right
renderer. Never split the word into per-letter elements and never apply
letter-spacing — both break Arabic-script joining.

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

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "static" / "brand"
FONT = BASE / "static" / "fonts" / "vazirmatn-600-arabic.woff2"

TEXT = "پیکسوریا"
ACCENT_LETTER = "ک"

INK = "#eaf2e8"  # --color-ink (used for preview renders)
LIME = "#c8ff3d"  # --color-lime (accent letter + favicon pixels)
NIGHT = "#04070a"  # --color-night (favicon background)

RENDER_SIZE = 700          # font px used for the source raster (then pixelated)
WORDMARK_ROWS = 14         # pixel rows of the full wordmark
MARK_ROWS = 12             # pixel rows of the compact «پ» mark
THRESHOLD = 100            # alpha coverage that keeps a pixel cell "on"


def _shape(text):
    """Joined Persian text in visual (left-to-right) order for PIL."""
    return get_display(arabic_reshaper.reshape(text))


def render_grid(text, rows, accent_letter=None):
    """Rasterize `text` as a joined word and pixelate it to `rows` rows.

    Returns (grid, accent_span) where accent_span = (x0, x1) column range of the
    `accent_letter` in the grid (or None when it is not requested / absent), so a
    single letter can be recoloured without splitting the word.
    """
    display = _shape(text)
    font = ImageFont.truetype(str(FONT), RENDER_SIZE)
    ascent, descent = font.getmetrics()
    cap = ascent + descent

    line_w = int(font.getlength(display)) + 8
    img = Image.new("L", (line_w, cap), 0)
    draw = ImageDraw.Draw(img)
    draw.text((4, 0), display, font=font, fill=255)

    # Pixelate the ink itself (not the whole line box) so the pixel size is
    # measured on the glyph height — otherwise descender/dot headroom shrinks
    # the wordmark to a few rows.
    ink_l, ink_t, ink_r, ink_b = img.getbbox()
    ink_w, ink_h = ink_r - ink_l, ink_b - ink_t
    ps = max(2, round(ink_h / rows))
    gw, gh = max(1, ink_w // ps), max(1, ink_h // ps)
    small = img.crop((ink_l, ink_t, ink_r, ink_b)).resize((gw, gh), Image.BOX)
    grid = [[small.getpixel((cx, cy)) >= THRESHOLD for cx in range(gw)] for cy in range(gh)]

    accent_span = None
    if accent_letter and accent_letter in text:
        # The accent is one codepoint of the shaped word; locate its visual
        # index, then measure its column span from the ink of the prefixes
        # around it (PIL lays presentation forms out strictly left-to-right).
        shaped = arabic_reshaper.reshape(text)
        logical_idx = text.index(accent_letter)
        visual_idx = len(display) - 1 - logical_idx
        left = draw.textlength(display[:visual_idx], font=font)
        right = left + draw.textlength(display[visual_idx : visual_idx + 1], font=font)
        x0 = max(0, int((max(left, ink_l) - ink_l) // ps))
        x1 = max(x0 + 1, min(gw, int((right - ink_l) // ps) + 1))
        accent_span = (x0, x1)
    return grid, accent_span



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
    print(f"Pixelating «{TEXT}» (joined Persian word)")
    grid, accent = render_grid(TEXT, WORDMARK_ROWS, accent_letter=ACCENT_LETTER)
    print(f"  grid {len(grid[0])}x{len(grid)}  accent «{ACCENT_LETTER}» cols {accent}")

    def color_of_full(x, y):
        return LIME if accent and accent[0] <= x < accent[1] else "currentColor"

    write("wordmark-full.svg", grid_to_svg(grid, color_of_full, TEXT))
    # Monochrome variant inherits its colour from CSS (`currentColor`).
    write("wordmark-mono.svg", grid_to_svg(grid, lambda x, y: "currentColor", TEXT))

    mark, _ = render_grid("پ", MARK_ROWS)
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
