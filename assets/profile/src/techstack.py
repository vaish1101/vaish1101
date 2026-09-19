"""Tech Stack board: logo/glyph tiles placed sequentially into one fixed-column grid (7 columns on
desktop, 4 on mobile). Items come from config/profile.json -> tech_stack.items.

Labels are sized with a per-character width estimate (not measured glyphs) so the approved
desktop layout stays exactly as designed; the estimate is deterministic and needs no font.
"""
from __future__ import annotations

from config import Config
from svg_helpers import IdScope, esc, svg_doc, tech_icon


def _wrap_label(label: str) -> list[str]:
    """Split on the last space, or the last hyphen (kept with the first half)."""
    if " " in label:
        return list(label.rsplit(" ", 1))
    if "-" in label:
        i = label.rindex("-")
        return [label[:i + 1], label[i + 1:]]
    return [label]


LABEL_SIDE_SLACK = 10          # a label must leave this much room inside its column track


class _Board:
    def __init__(self, cfg: Config, mode: str):
        ts = cfg.tokens["tech_stack"]
        self.cfg, self.mode, self.p = cfg, mode, ts[mode]
        self.tile, self.logo, self.glyph = self.p["tile"], self.p["logo"], self.p["glyph"]
        self.fs, self.line = self.p["label_size"], self.p["label_line"]
        base = ts["desktop"]
        self.char_w = base["char_width"] * self.fs / base["label_size"]
        self.row_h = 1 + self.tile + self.line * 2 + 4   # replaced by the real label height in render_techstack

    def label_lines(self, label: str, width: float) -> list[str]:
        return [label] if len(label) * self.char_w + 6 <= width else _wrap_label(label)

    def tile_svg(self, theme: str, x, w, key, label, accent_i, ids: IdScope) -> str:
        t = self.cfg.tokens["themes"][theme]
        cx = x + w / 2
        accent = t["star"] if accent_i % 2 == 0 else t["peri"]
        tx = cx - self.tile / 2
        frag = f'<rect x="{tx + 1.4:.1f}" y="3.4" width="{self.tile}" height="{self.tile}" rx="8" fill="{t["plinth_shadow"]}"/>'
        if "logo" in self.cfg.profile["technologies"][key]:
            frag += (f'<rect x="{tx:.1f}" y="1" width="{self.tile}" height="{self.tile}" rx="8" fill="{t["tile"]}" '
                     f'stroke="{t["tile_st"]}" stroke-opacity="{t["tile_st_o"]}"/>')
            frag += tech_icon(self.cfg, key, round(cx - self.logo / 2, 1), 1 + (self.tile - self.logo) / 2, self.logo, t, ids)
        else:
            frag += (f'<rect x="{tx:.1f}" y="1" width="{self.tile}" height="{self.tile}" rx="8" fill="{t["ctile"]}" '
                     f'fill-opacity="{t["ctile_o"]}" stroke="{t["ctile_st"]}" stroke-opacity="{t["ctile_st_o"]}" '
                     f'stroke-dasharray="2.5 2"/>')
            frag += tech_icon(self.cfg, key, cx - self.glyph / 2, 1 + (self.tile - self.glyph) / 2, self.glyph, t, ids, glyph_width=1.55)
        frag += f'<rect x="{tx - .5:.1f}" y="0.5" width="2" height="2" fill="{accent}" shape-rendering="crispEdges"/>'
        ly = 1 + self.tile + self.line
        for part in self.label_lines(label, w - LABEL_SIDE_SLACK):
            frag += (f'<text x="{cx:.1f}" y="{ly:.1f}" text-anchor="middle" font-size="{self.fs}" '
                     f'font-weight="600" fill="{t["label"]}">{esc(part)}</text>')
            ly += self.line
        return frag


def render_techstack(cfg: Config, theme: str, mode: str) -> str:
    """mode is 'desktop' or 'mobile'. Items are placed sequentially into one fixed-column grid; a
    partial last row stays on the same column tracks (it is never centred on its own)."""
    items = cfg.profile["tech_stack"]["items"]
    b, ids = _Board(cfg, mode), IdScope()
    p = b.p
    cols = p["columns"]
    track = p["grid_width"] / cols if mode == "desktop" else p["track_width"]
    canvas_w = p["width"] if mode == "desktop" else p["canvas_width"]
    left = (canvas_w - track * cols) / 2
    max_lines = max(len(b.label_lines(label, track - LABEL_SIDE_SLACK)) for _, label in items)
    b.row_h = 1 + b.tile + b.line * max_lines + 4      # every row reserves the tallest label slot
    title = "Tech stack -- " + "; ".join(label for _, label in items)
    body = ""
    for i, (key, label) in enumerate(items):
        r, c = divmod(i, cols)
        x, y = left + c * track, 4 + r * (b.row_h + p["row_gap"])
        body += f'<g transform="translate({x:.1f} {y})">{b.tile_svg(theme, 0, track, key, label, c, ids)}</g>'
    rows = -(-len(items) // cols)
    H = 4 + rows * b.row_h + (rows - 1) * p["row_gap"] + 6
    return svg_doc(canvas_w, round(H), body, title, cfg.tokens["font_stack"])
