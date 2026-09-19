"""Let's Connect links: a pixel icon, a label and a stepped underline, one SVG per link.

Each link is its own image so the README can wrap it in a normal <a> (SVG-internal links are not
clickable on GitHub). The two links are separated by a shared, theme-neutral vertical divider.
Everything is measured with the same text metrics as the cards, so labels never clip.
"""
from __future__ import annotations

from config import Config
from svg_helpers import esc, svg_doc
from text_metrics import TextMetrics

# Pixel icons on a cell grid; "X" is filled, "." is transparent.
ICONS = {
    "linkedin": [
        ".XXXXXXXXXX.",
        "XXXXXXXXXXXX",
        "XXXXXXXXXXXX",
        "XXX.XXXXXXXX",
        "XXXXXXXXXXXX",
        "XXX.X...XXXX",
        "XXX.X.XX.XXX",
        "XXX.X.XX.XXX",
        "XXX.X.XX.XXX",
        "XXX.X.XX.XXX",
        "XXXXXXXXXXXX",
        ".XXXXXXXXXX.",
    ],
    "mail": [
        "XXXXXXXXXXXXXX",
        "XX..........XX",
        "X.X........X.X",
        "X..X......X..X",
        "X...X....X...X",
        "X....X..X....X",
        "X.....XX.....X",
        "X............X",
        "X............X",
        "XXXXXXXXXXXXXX",
    ],
}


def _runs(grid: list[str]):
    for r, row in enumerate(grid):
        c = 0
        while c < len(row):
            if row[c] == "X":
                s = c
                while c < len(row) and row[c] == "X":
                    c += 1
                yield r, s, c - s
            else:
                c += 1


def _icon(grid: list[str], x: float, y: float, cell: float, color: str) -> str:
    rects = "".join(f'<rect x="{x + s * cell:g}" y="{y + r * cell:g}" width="{n * cell:g}" height="{cell:g}"/>'
                    for r, s, n in _runs(grid))
    return f'<g fill="{color}" shape-rendering="crispEdges">{rects}</g>'


def render_link(cfg: Config, metrics: TextMetrics, theme: str, link: dict, mode: str) -> str:
    spec = cfg.tokens["connect"][mode]
    color = cfg.tokens["connect"]["colors"][theme][link["id"]]
    grid = ICONS[link["icon"]]
    H, pad, cell = spec["height"], spec["pad"], spec["cell"]
    ih, iw = len(grid) * cell, len(grid[0]) * cell
    fs = spec["label_size"]
    text_w = metrics.width(link["label"], fs, "600")
    tx = pad + iw + spec["icon_gap"]
    base = H / 2 + fs * 0.32                    # optical vertical centre of the label
    uy = round(base + spec["underline_gap"])
    line_end = tx + text_w + spec["end_slack"]
    u = 2                                       # 3x3 pixel plus at the end of the underline
    plus = 3 * u
    W = round(line_end + 4 + plus + pad + spec["end_slack"])
    body = _icon(grid, pad, (H - ih) / 2, cell, color)
    body += (f'<text x="{tx:g}" y="{base:.1f}" font-size="{fs}" font-weight="600" fill="{color}">'
             f'{esc(link["label"])}</text>')
    body += (f'<rect x="{tx:g}" y="{uy - 1}" width="{line_end - tx:.1f}" height="2" fill="{color}" '
             f'shape-rendering="crispEdges"/>'
             f'<rect x="{tx:g}" y="{uy - 2}" width="{line_end - tx:.1f}" height="4" fill="{color}" '
             f'fill-opacity=".16" shape-rendering="crispEdges"/>')
    px, py = line_end + 4, uy - plus / 2
    body += (f'<g fill="{color}" shape-rendering="crispEdges">'
             f'<rect x="{px:g}" y="{py + u:g}" width="{plus}" height="{u}"/>'
             f'<rect x="{px + u:g}" y="{py:g}" width="{u}" height="{plus}"/></g>')
    return svg_doc(W, H, body, link["label"], cfg.tokens["font_stack"])


def render_divider(cfg: Config, mode: str) -> str:
    d, H = cfg.tokens["connect"]["divider"], cfg.tokens["connect"][mode]["height"]
    W = d["width_mobile"] if mode == "mobile" else d["width"]
    cx, c = W / 2, d["line_color"]
    body = (
        f'<defs><linearGradient id="v" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{c}" stop-opacity="0"/><stop offset=".5" stop-color="{c}" stop-opacity=".7"/>'
        f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient></defs>'
        f'<rect x="{cx - 1:g}" y="4" width="2" height="{H - 8}" fill="url(#v)" shape-rendering="crispEdges"/>'
        f'<rect x="{cx - 2:g}" y="{H / 2 - 2:g}" width="4" height="4" fill="{d["dot_color"]}" shape-rendering="crispEdges"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="presentation" aria-hidden="true">{body}</svg>\n')
