"""Zero-overflow bounding-box QA for generated SVGs.

Parses the finished SVG (not the layout code's own bookkeeping) and checks every visible
element: sprite, title, description, chips, chip icons/text, CTA, sparkle, window controls and
frame decoration. Used by build_profile.py (which refuses to write anything that fails) and
by validate_profile.py.
"""
from __future__ import annotations

import re

from lxml import etree

from text_metrics import TextMetrics

NS = "{http://www.w3.org/2000/svg}"


def _local(el) -> str | None:
    return etree.QName(el).localname if isinstance(el.tag, str) else None


def _weight(el) -> str:
    return {"700": "700", "bold": "700", "600": "600"}.get(el.get("font-weight", "400"), "400")


def collect_boxes(root, metrics: TextMetrics):
    """Every visible element in card space as (role, x0, y0, x1, y1). Embedded logos count as
    one box (their inner coordinates use their own viewBox)."""
    boxes = []

    def walk(el, ox=0.0, oy=0.0):
        tag = _local(el)
        if tag in (None, "defs", "title"):
            return
        if tag == "g":
            if el.get("data-role") == "icon":
                rects = [(float(r.get("x")), float(r.get("y")), float(r.get("width")), float(r.get("height")))
                         for r in el.iter(NS + "rect")]
                boxes.append(("icon", min(x for x, *_ in rects), min(y for _, y, *_ in rects),
                              max(x + w for x, _, w, _ in rects), max(y + h for _, y, _, h in rects)))
                return
            tr = el.get("transform", "")
            m = re.fullmatch(r"translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+)\)", tr)
            if m:                                   # concept glyph: a 24-unit box scaled to size
                x, y, k = (float(v) for v in m.groups())
                boxes.append(("glyph", x + ox, y + oy, x + ox + 24 * k, y + oy + 24 * k))
                return
            m = re.fullmatch(r"translate\(([-\d.]+) ([-\d.]+)\)", tr)
            dx, dy = (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)
            for c in el:
                walk(c, ox + dx, oy + dy)
            return
        if tag == "svg" and el.getparent() is not None:
            x, y, w, h = (float(el.get(k)) for k in ("x", "y", "width", "height"))
            boxes.append(("logo", x + ox, y + oy, x + ox + w, y + oy + h))
            return
        if tag == "text":
            x, y, fs = float(el.get("x")), float(el.get("y")), float(el.get("font-size"))
            w = metrics.width(el.text or "", fs, _weight(el))
            anchor = el.get("text-anchor", "start")
            l = x - w if anchor == "end" else x - w / 2 if anchor == "middle" else x
            boxes.append(("text:" + (el.text or "")[:24], l + ox, y + oy - fs * .8, l + ox + w, y + oy + fs * .25))
            return
        if tag == "rect":
            x, y, w, h = (float(el.get(k)) for k in ("x", "y", "width", "height"))
            role = "chip" if el.get("data-role") == "chip" else "deco"
            boxes.append((role, x + ox, y + oy, x + ox + w, y + oy + h))
            return
        if tag == "path" and not el.get("filter") and re.fullmatch(r"[MQZ0-9.\- ]+", el.get("d", "")):
            n = [float(v) for v in re.findall(r"-?\d+\.?\d*", el.get("d"))]
            boxes.append(("spark" if el.get("fill") not in (None, "none") else "deco",
                          min(n[0::2]), min(n[1::2]), max(n[0::2]), max(n[1::2])))
            return
        for c in el:
            walk(c, ox, oy)

    for child in root:
        walk(child)
    return boxes


def _overlap(a, b) -> bool:
    return a[1] < b[3] and b[1] < a[3] and a[2] < b[4] and b[2] < a[4]


def check_card(name: str, svg: str, metrics: TextMetrics, tokens: dict) -> list[str]:
    root = etree.fromstring(svg.encode())
    W, H = float(root.get("width")), float(root.get("height"))
    safe, icon_margin = tokens["validation"]["safe_margin"], tokens["validation"]["icon_margin"]
    boxes, errs = collect_boxes(root, metrics), []
    for b in boxes:
        if b[1] < safe - .01 or b[2] < safe - .01 or b[3] > W - safe + .01 or b[4] > H - safe + .01:
            errs.append(f"{name}: {b[0]} escapes the {safe}px safe area {tuple(round(v, 1) for v in b[1:])}")
    icon = next((b for b in boxes if b[0] == "icon"), None)
    if icon is None:
        errs.append(f"{name}: no sprite found")
    elif icon[1] < icon_margin or icon[2] < icon_margin or icon[3] > W - icon_margin or icon[4] > H - icon_margin:
        errs.append(f"{name}: sprite closer than {icon_margin}px to the frame {tuple(round(v, 1) for v in icon[1:])}")
    chips = [b for b in boxes if b[0] == "chip"]
    for b in boxes:
        if b[0].startswith("text:") or b[0] in ("logo", "glyph"):
            host = next((c for c in chips if c[1] <= b[1] + .5 and b[1] <= c[3] and c[2] - 4 <= b[2] and b[4] <= c[4] + 4), None)
            if host and b[3] > host[3] - 4:
                errs.append(f"{name}: chip content {b[0]} is clipped by its chip")
    inside = lambda b: any(c[1] <= b[1] and b[3] <= c[3] and c[2] <= b[2] and b[4] <= c[4] for c in chips)
    content = [b for b in boxes if b[0] in ("icon", "chip", "spark") or b[0].startswith("text:")]
    for i, a in enumerate(content):
        for b in content[i + 1:]:
            if (a[0] == "chip" and b[0].startswith("text:") and inside(b)) or \
               (b[0] == "chip" and a[0].startswith("text:") and inside(a)):
                continue
            if _overlap(a, b):
                errs.append(f"{name}: {a[0]} overlaps {b[0]}")
    for a in (b for b in content if b[0] != "chip"):
        for c in (b for b in boxes if b[0] == "deco"):
            if _overlap(a, c):
                errs.append(f"{name}: {a[0]} overlaps window chrome/decoration")
    return errs


def check_stack(name: str, svg: str, metrics: TextMetrics) -> list[str]:
    root = etree.fromstring(svg.encode())
    W, H = float(root.get("width")), float(root.get("height"))
    return [f"{name}: {b[0]} outside the {W:g}x{H:g} canvas"
            for b in collect_boxes(root, metrics)
            if b[1] < -.5 or b[2] < -.5 or b[3] > W + .5 or b[4] > H + .5]
