"""Tech Stack board: a column-aligned grid of logo/glyph tiles (desktop) or a wrapped flow of
the same tiles (mobile). Rows come from config/profile.json -> tech_stack.rows.

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


def _balanced_line_size(widths: list[int], gap: int, limit: float) -> int:
    """Items per line when a row has to wrap: as even as possible (e.g. 4+3, not 5+2).

    Falls back to plain greedy filling when an even split would not fit the limit."""
    def lines_greedy() -> int:
        n, x = 1, 8
        for i, w in enumerate(widths):
            if x + w > limit and x > 8:
                n, x = n + 1, 8
            x += w + gap
        return n

    n_lines = lines_greedy()
    if n_lines == 1:
        return len(widths)
    per = -(-len(widths) // n_lines)
    for start in range(0, len(widths), per):
        if 8 + sum(widths[start:start + per]) + gap * (len(widths[start:start + per]) - 1) > limit:
            return len(widths)
    return per


class _Board:
    def __init__(self, cfg: Config, mode: str):
        ts = cfg.tokens["tech_stack"]
        self.cfg, self.mode, self.p = cfg, mode, ts[mode]
        self.tile, self.logo, self.glyph = self.p["tile"], self.p["logo"], self.p["glyph"]
        self.fs, self.line = self.p["label_size"], self.p["label_line"]
        base = ts["desktop"]
        self.char_w = base["char_width"] * self.fs / base["label_size"]
        self.row_h = 1 + self.tile + self.line * 2 + 4   # every row reserves a two-line label slot

    def label_lines(self, label: str, width: float) -> list[str]:
        return [label] if len(label) * self.char_w + 6 <= width else _wrap_label(label)

    def item_width(self, label: str) -> int:
        if len(label) * self.char_w + 6 <= self.tile:
            return self.tile
        wrapped = max(len(part) for part in _wrap_label(label)) * self.char_w + 6
        return max(self.tile, round(wrapped))

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
        for part in self.label_lines(label, w):
            frag += (f'<text x="{cx:.1f}" y="{ly:.1f}" text-anchor="middle" font-size="{self.fs}" '
                     f'font-weight="600" fill="{t["label"]}">{esc(part)}</text>')
            ly += self.line
        return frag


def render_techstack(cfg: Config, theme: str, mode: str) -> str:
    """mode is 'desktop' or 'mobile'."""
    rows = cfg.profile["tech_stack"]["rows"]
    b, ids = _Board(cfg, mode), IdScope()
    labels = "; ".join(label for row in rows for _, label in row)
    title = f"Tech stack -- {labels}"
    body, y = "", 4

    if mode == "mobile":
        p = b.p
        canvas_w = round(p["row_wrap_limit"] + 5)       # fixed width keeps the README's column scaling stable
        for items in rows:
            widths = [b.item_width(label) for _, label in items]
            per_line = _balanced_line_size(widths, p["item_gap"], p["row_wrap_limit"])
            lines = [list(range(i, min(i + per_line, len(items)))) for i in range(0, len(items), per_line)]
            liney = y
            for n, line in enumerate(lines):
                total = sum(widths[i] for i in line) + p["item_gap"] * (len(line) - 1)
                x = round((canvas_w - total) / 2, 1)          # each line centred in the canvas
                for i in line:
                    key, label = items[i]
                    body += f'<g transform="translate({x:g} {liney})">{b.tile_svg(theme, 0, widths[i], key, label, i, ids)}</g>'
                    x += widths[i] + p["item_gap"]
                if n < len(lines) - 1:
                    liney += b.row_h + p["wrap_gap"]
            y = liney + b.row_h + p["row_gap"]
        H = y - p["row_gap"] + 6
        return svg_doc(canvas_w, round(H), body, title, cfg.tokens["font_stack"])

    p = b.p
    n_cols = max(len(r) for r in rows)
    cols = [b.tile] * n_cols
    for row in rows:
        for j, (_, label) in enumerate(row):
            cols[j] = max(cols[j], b.item_width(label))
    gap = max(p["min_gap"], (p["width"] - 16 - sum(cols)) / (n_cols - 1))
    for row in rows:
        x, accent_i = 8, 0
        for j, (key, label) in enumerate(row):
            body += f'<g transform="translate({x:.1f} {y})">{b.tile_svg(theme, 0, cols[j], key, label, accent_i, ids)}</g>'
            x += cols[j] + gap
            accent_i += 1
        y += b.row_h + p["row_gap"]
    H = y - p["row_gap"] + 6
    return svg_doc(p["width"], round(H), body, title, cfg.tokens["font_stack"])
