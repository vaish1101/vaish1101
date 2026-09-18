"""Deterministic, platform-independent text measurement.

Widths come from the bundled Inter fonts (SIL Open Font License, see fonts/OFL-Inter.txt)
measured with Pillow's BASIC layout engine -- no system fonts, no kerning/shaping engine
that could differ between macOS and Linux. A per-weight safety factor (design_tokens.json)
keeps every estimate at or above what Chrome renders for the SVG's font stack, so a line
that "fits" here also fits for viewers whose fallback font is a little wider.
"""
from __future__ import annotations

from PIL import ImageFont

from config import SRC_DIR

_REF = 200  # measure large and scale down: no per-size hinting differences


class TextMetrics:
    def __init__(self, tokens: dict):
        spec = tokens["text_metrics"]
        self._fonts = {
            w: ImageFont.truetype(str(SRC_DIR / path), _REF, layout_engine=ImageFont.Layout.BASIC)
            for w, path in spec["fonts"].items()
        }
        self._factors = spec["factors"]

    def width(self, text: str, size: float, weight: str = "400") -> float:
        return self._fonts[weight].getlength(text) * (size / _REF) * self._factors[weight]

    def wrap(self, text: str, max_px: float, size: float, weight: str = "400") -> list[str]:
        """Greedy wrap by measured width; a single over-long word stays on its own line."""
        words, lines, cur = text.split(), [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if self.width(trial, size, weight) > max_px and cur:
                lines.append(cur)
                cur = w
            else:
                cur = trial
        if cur:
            lines.append(cur)
        return lines
