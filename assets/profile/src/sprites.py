"""Renders a project sprite (a grid of palette characters from config/sprites.json)."""
from __future__ import annotations

from config import Config


def pixel_sprite(cfg: Config, key: str, x, y, cell) -> str:
    """Same-colour horizontal runs merged into <rect>s. Tagged data-role="icon" so the
    validator can compute the artwork's exact bounding box from the rects themselves."""
    out = []
    for j, row in enumerate(cfg.sprites[key]):
        i = 0
        while i < len(row):
            ch = row[i]
            if ch == ".":
                i += 1
                continue
            k = i
            while k + 1 < len(row) and row[k + 1] == ch:
                k += 1
            out.append(f'<rect x="{x + i * cell:g}" y="{y + j * cell:g}" width="{(k - i + 1) * cell:g}" '
                       f'height="{cell:g}" fill="{cfg.sprite_palette[ch]}"/>')
            i = k + 1
    return f'<g data-role="icon" shape-rendering="crispEdges">{"".join(out)}</g>'
