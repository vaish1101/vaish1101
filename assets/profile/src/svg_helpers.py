"""Small SVG building blocks shared by the card, Tech Stack and decoration renderers."""
from __future__ import annotations

from lxml import etree

from config import LOGOS_DIR, Config

SVG_NS = "http://www.w3.org/2000/svg"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_doc(w, h, body: str, title: str, font_stack: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(title)}" font-family="{font_stack}"><title>{esc(title)}</title>{body}</svg>\n')


class IdScope:
    """Per-document counter used to namespace ids of embedded logos.

    Embedded logos bring their own ids (gradients, clip paths). Prefixing them per document
    keeps every generated SVG self-contained, and because the counter restarts for each
    document, adding a project never renumbers ids inside unrelated files.
    """

    def __init__(self):
        self._n = 0

    def next(self) -> str:
        self._n += 1
        return f"l{self._n}"


def logo(cfg: Config, key: str, x, y, size, ids: IdScope) -> str:
    """Official logo embedded as nested <svg> markup (data: URIs are blocked by GitHub's CSP)."""
    spec = cfg.profile["technologies"][key]["logo"]
    root = etree.parse(str(LOGOS_DIR / spec["file"])).getroot()
    vb = root.get("viewBox")
    prefix = ids.next()
    for el in list(root.iter()):
        if isinstance(el.tag, str) and etree.QName(el).localname in ("title", "desc", "metadata"):
            el.getparent().remove(el)
    known = [el.get("id") for el in root.iter() if isinstance(el.tag, str) and el.get("id")]
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        for k, v in list(el.attrib.items()):
            if k == "id":
                el.set(k, f"{prefix}-{v}")
            else:
                for i in known:
                    v = v.replace(f"url(#{i})", f"url(#{prefix}-{i})")
                    if v == f"#{i}":
                        v = f"#{prefix}-{i}"
                el.set(k, v)
    inner = "".join(etree.tostring(c, encoding="unicode") for c in root if isinstance(c.tag, str))
    inner = inner.replace(f' xmlns="{SVG_NS}"', "")
    fill = f' fill="{spec["mono"]}"' if spec.get("mono") else ""
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{vb}"{fill}>{inner}</svg>'


def glyph(cfg: Config, name: str, x, y, size, color: str, width=1.7) -> str:
    s = size / 24
    return (f'<g transform="translate({x} {y}) scale({s:.4f})" fill="none" stroke="{color}" color="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">{cfg.glyphs[name]}</g>')


def tech_icon(cfg: Config, key: str, x, y, size, theme_tokens: dict, ids: IdScope, glyph_width=1.5) -> str:
    """Logo if the technology has one, otherwise its concept glyph."""
    spec = cfg.profile["technologies"][key]
    if "logo" in spec:
        return logo(cfg, key, x, y, size, ids)
    return glyph(cfg, spec["glyph"], x, y, size, theme_tokens["glyph"], glyph_width)


def pixel_star(x, y, px, color, hi) -> str:
    cells = [(2, 0), (2, 1), (0, 2), (1, 2), (3, 2), (4, 2), (2, 3), (2, 4)]
    r = "".join(f'<rect x="{x + cx * px:.2f}" y="{y + cy * px:.2f}" width="{px}" height="{px}"/>' for cx, cy in cells)
    return (f'<g fill="{color}" shape-rendering="crispEdges">{r}</g>'
            f'<rect x="{x + 2 * px:.2f}" y="{y + 2 * px:.2f}" width="{px}" height="{px}" fill="{hi}" shape-rendering="crispEdges"/>')


def pixel_heart(x, y, px, color="#E98CA8") -> str:
    rows = ["01100110", "11111111", "11111111", "01111110", "00111100", "00011000"]
    cells = [(cx, cy) for cy, row in enumerate(rows) for cx, v in enumerate(row) if v == "1"]
    r = "".join(f'<rect x="{x + cx * px:.2f}" y="{y + cy * px:.2f}" width="{px}" height="{px}"/>' for cx, cy in cells)
    return f'<g fill="{color}" shape-rendering="crispEdges">{r}</g>'


def stair_path(x0, y0, x1, y1, st) -> str:
    """Rectangle whose four corners are 2-step pixel stairs instead of rounded arcs."""
    c = 2 * st
    return (f"M{x0+c:g},{y0:g} H{x1-c:g} v{st:g} h{st:g} v{st:g} h{st:g} V{y1-c:g} h-{st:g} v{st:g} h-{st:g} "
            f"v{st:g} H{x0+c:g} v-{st:g} h-{st:g} v-{st:g} h-{st:g} V{y0+c:g} h{st:g} v-{st:g} h{st:g} v-{st:g} Z")


def window_controls(W, top, sq, gap, right, color, bg, opacity=.95) -> str:
    """Minimise / restore / close squares (the banner's own window-control language)."""
    x = W - right - (3 * sq + 2 * gap)
    g = ""
    for n in range(3):
        sx = x + n * (sq + gap)
        g += f'<rect x="{sx:g}" y="{top:g}" width="{sq:g}" height="{sq:g}" rx="1.5" fill="{color}" fill-opacity="{opacity}"/>'
    u = sq / 13
    g += f'<rect x="{x + 3*u:g}" y="{top + 8.4*u:g}" width="{7*u:g}" height="{1.8*u:g}" fill="{bg}"/>'
    sx = x + (sq + gap)
    g += (f'<rect x="{sx + 3.2*u:g}" y="{top + 3.2*u:g}" width="{6.6*u:g}" height="{6.6*u:g}" fill="none" '
          f'stroke="{bg}" stroke-width="{1.5*u:g}"/>')
    sx = x + 2 * (sq + gap)
    g += (f'<path d="M{sx + 3.6*u:g} {top + 3.6*u:g} L{sx + 9.4*u:g} {top + 9.4*u:g} M{sx + 9.4*u:g} {top + 3.6*u:g} '
          f'L{sx + 3.6*u:g} {top + 9.4*u:g}" stroke="{bg}" stroke-width="{1.6*u:g}" stroke-linecap="square"/>')
    return g


def dot_cluster(x, y, color, opacity=.85, d=3) -> str:
    pts = [(0, 0), (2 * d, d), (2 * d, 3 * d), (0, 4 * d)]
    return "".join(f'<rect x="{x + px:g}" y="{y + py:g}" width="{d:g}" height="{d:g}" fill="{color}" fill-opacity="{opacity}"/>'
                   for px, py in pts)


def spark4(cx, cy, r, color) -> str:
    """Smooth 4-point sparkle (concave sides) used beside the CTA."""
    return (f'<path d="M{cx:g} {cy-r:g} Q{cx:g} {cy:g} {cx+r:g} {cy:g} Q{cx:g} {cy:g} {cx:g} {cy+r:g} '
            f'Q{cx:g} {cy:g} {cx-r:g} {cy:g} Q{cx:g} {cy:g} {cx:g} {cy-r:g} Z" fill="{color}"/>')
