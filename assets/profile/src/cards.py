"""Featured Work card renderer.

One function renders any project, in any theme, at either width, from data + design tokens.
It knows nothing about how many projects exist. Text is wrapped by measured width and the
card grows to fit its content, so nothing is clipped by construction.
"""
from __future__ import annotations

from config import Config
from sprites import pixel_sprite
from svg_helpers import (IdScope, dot_cluster, esc, spark4, stair_path, svg_doc, tech_icon,
                         window_controls)
from text_metrics import TextMetrics

CHIP_STROKE_WIDTH = 1.7


def _chips(cfg: Config, metrics: TextMetrics, items: list[str], x0, y0, max_w, theme: str, chip: dict,
           ids: IdScope, row_counts: list[int] | None = None):
    """Technology chips: boxy pixel-frame pills with a real logo/glyph where one is known.
    Wraps to a new row only when a chip would overrun, or where the optional `row_counts`
    (chips per row, from the project's `chip_rows`) asks for a break. Returns (svg, total_height, rows)."""
    t, t5 = cfg.tokens["themes"][theme], cfg.tokens["card_colors"][theme]
    h, gap, icon_s = chip["height"], chip["gap"], chip["icon_size"]
    pad_l, pad_r, icon_gap, fs = chip["pad_left"], chip["pad_right"], chip["icon_gap"], chip["font_size"]
    row_gap = max(6, gap)
    chip_icons = cfg.profile["chip_icons"]
    cur_x, cur_y, frag = x0, y0, ""
    breaks, run = set(), 0
    for n in row_counts or []:
        run += n
        breaks.add(run)
    for i, label in enumerate(items):
        key = chip_icons.get(label)
        w = pad_l + (icon_s + icon_gap if key else 0) + metrics.width(label, fs, "600") + pad_r
        if cur_x > x0 and (i in breaks or cur_x + w > x0 + max_w):
            cur_x = x0
            cur_y += h + row_gap
        frag += (f'<rect data-role="chip" x="{cur_x:.1f}" y="{cur_y:.1f}" width="{w:.1f}" height="{h}" rx="{chip["radius"]}" '
                 f'fill="{t5["chip_bg"]}" fill-opacity="{t5["chip_bg_o"]}" stroke="{t5["chip_border"]}" '
                 f'stroke-opacity="{t5["chip_border_o"]}" stroke-width="{CHIP_STROKE_WIDTH}"/>')
        tx = cur_x + pad_l
        if key:
            frag += tech_icon(cfg, key, tx, cur_y + (h - icon_s) / 2, icon_s, t, ids)
            tx += icon_s + icon_gap
        frag += (f'<text x="{tx:.1f}" y="{cur_y + h / 2 + fs * 0.35:.1f}" font-size="{fs}" font-weight="600" '
                 f'fill="{t5["chip_text"]}">{esc(label)}</text>')
        cur_x += w + gap
    total_h = (cur_y - y0) + h
    return frag, total_h, round((total_h - h) / (h + row_gap)) + 1


def render_card(cfg: Config, metrics: TextMetrics, theme: str, project: dict, variant: str):
    """Renders one project card. `variant` is 'desktop' or 'mobile'. Returns (svg, meta)."""
    tokens = cfg.tokens
    L, F = tokens["card"][variant], tokens["card"]["frame"]
    t5 = tokens["card_colors"][theme]
    ids = IdScope()
    wide = L["desc_beside_title"]

    W, pad, cell = L["width"], L["pad"], L["sprite_cell"]
    sprite_x, sprite_y = L["sprite_x"], L["sprite_y"]
    title_fs, desc_fs, desc_lh = L["title_size"], L["desc_size"], L["desc_line_height"]
    sprite_w = tokens["card"]["sprite_cols"] * cell
    sprite_h = tokens["card"]["sprite_rows"] * cell
    usable = W - 2 * pad
    title_x = sprite_x + sprite_w + L["title_gap_after_sprite"]
    title_w = (W - L["title_right_inset"]) - title_x

    title, description = project["title"], project["description"]
    name_lines = ([title] if metrics.width(title, title_fs, "700") <= title_w
                  else metrics.wrap(title, title_w, title_fs, "700"))

    body = pixel_sprite(cfg, project["icon"], sprite_x, sprite_y, cell)
    y = L["title_first_baseline"]
    for line in name_lines:
        body += (f'<text x="{title_x}" y="{y}" font-size="{title_fs}" font-weight="700" '
                 f'fill="{t5["title"]}">{esc(line)}</text>')
        y += title_fs + 5
    title_bottom = y - (title_fs + 5)

    if wide:
        desc_x, desc_w = title_x, W - title_x - pad
        y = title_bottom + L["desc_gap_after_title"]
    else:
        desc_x, desc_w = pad, usable
        y = max(title_bottom + L["stack_title_gap"], sprite_y + sprite_h) + L["stack_desc_offset"]
    description_lines = metrics.wrap(description, desc_w, desc_fs, "400")
    for line in description_lines:
        body += f'<text x="{desc_x}" y="{y}" font-size="{desc_fs}" fill="{t5["desc"]}">{esc(line)}</text>'
        y += desc_lh
    desc_bottom = y - desc_lh

    chip = L["chip"]
    row_counts = (project.get("chip_rows") or {}).get(variant)
    _, chip_total, chip_rows = _chips(cfg, metrics, project["technologies"], pad, 0, usable, theme, chip,
                                      IdScope(), row_counts)
    natural_top = max(desc_bottom + L["chips_gap_after_desc"], sprite_y + sprite_h + L["chips_gap_after_sprite"])
    H = max(natural_top + chip_total + L["cta_gap"] + L["bottom_pad"], L["min_height"])
    # chips hang from the CTA row, not from the description, so the chip row and the CTA land
    # at the same position on every card however many lines the copy wraps to
    chips_top = H - L["bottom_pad"] - L["cta_gap"] - chip_total
    chip_svg, _, _ = _chips(cfg, metrics, project["technologies"], pad, chips_top, usable, theme, chip, ids,
                            row_counts)
    body += chip_svg

    cta_y = H - L["bottom_pad"]
    cta_right = W - L["cta_right_inset"]
    body += (f'<text x="{cta_right}" y="{cta_y:.1f}" text-anchor="end" font-size="{L["cta_size"]}" font-weight="700" '
             f'fill="{t5["cta"]}">{esc(tokens["card"]["cta_label"])}</text>')
    sr = L["spark_radius"]
    body += spark4(cta_right + sr + L["spark_dx"], cta_y + L["spark_dy"], sr, t5["spark"])
    dot_x = W - L["dot_x_from_right"] if L["dot_x_from_right"] else cta_right + sr * 2 + 6
    body += f'<rect x="{dot_x:g}" y="{cta_y - 2:g}" width="3" height="3" fill="{t5["corner"]}"/>'

    o, m, i, st = F["outer_inset"], F["main_inset"], F["inner_inset"], F["stair_step"]
    frame = (f'<defs><filter id="cardglow" x="-10%" y="-25%" width="120%" height="150%">'
             f'<feGaussianBlur stdDeviation="{F["glow_blur"]}"/></filter></defs>'
             f'<path d="{stair_path(m, m, W - m, H - m, st)}" fill="none" stroke="{t5["glow"]}" '
             f'stroke-opacity="{t5["glow_o"]}" stroke-width="{F["glow_width"]}" filter="url(#cardglow)"/>'
             f'<path d="{stair_path(o, o, W - o, H - o, F["outer_stair_step"])}" fill="none" '
             f'stroke="{t5["border"]}" stroke-opacity=".38" stroke-width="{F["outer_width"]}"/>'
             f'<path d="{stair_path(m, m, W - m, H - m, st)}" fill="{t5["bg"]}" '
             f'fill-opacity="{t5["bg_o"]}" stroke="{t5["border"]}" stroke-opacity="{t5["border_o"]}" '
             f'stroke-width="{F["main_width"]}" stroke-linejoin="miter"/>'
             f'<line x1="{m + 2 * st}" y1="{m + 1.2}" x2="{W - m - 2 * st}" y2="{m + 1.2}" '
             f'stroke="{t5["border"]}" stroke-width="1.4"/>'
             f'<path d="{stair_path(i, i, W - i, H - i, F["inner_stair_step"])}" fill="none" '
             f'stroke="{t5["border"]}" stroke-opacity=".34" stroke-width="{F["inner_width"]}"/>')
    a, ai = F["accent_size"], F["accent_inset"]
    frame += "".join(f'<rect x="{ax}" y="{ay}" width="{a}" height="{a}" fill="{t5["border"]}" fill-opacity=".8"/>'
                     for ax, ay in ((ai, ai), (W - ai - a, H - ai - a), (ai, H - ai - a)))
    wc, dc = L["window_controls"], L["dot_cluster"]
    frame += window_controls(W, wc["top"], wc["size"], wc["gap"], wc["right"], t5["border"], t5["bg"])
    frame += dot_cluster(W - dc["x_from_right"], dc["y"], t5["border"], d=dc["size"])

    svg = svg_doc(W, round(H), frame + body, f"{title}. {description}", tokens["font_stack"])
    meta = dict(title_lines=len(name_lines), description_lines=len(description_lines),
                chip_rows=chip_rows, width=W, height=round(H))
    return svg, meta
