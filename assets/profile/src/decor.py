"""Fixed decorative art: the four About Me micro-icons and the section divider.

These are part of the approved design and do not depend on project content.
"""
from __future__ import annotations

from config import Config
from svg_helpers import pixel_heart, pixel_star, svg_doc


def about_icons(cfg: Config, theme: str) -> dict[str, str]:
    """Returns {filename: svg} for the About Me icons in one theme."""
    t, font = cfg.tokens["themes"][theme], cfg.tokens["font_stack"]

    database = (
        f'<ellipse cx="9" cy="4.2" rx="7" ry="2.6" fill="{t["glyph"]}"/>'
        f'<rect x="2" y="4.2" width="14" height="10.2" fill="{t["glyph"]}"/>'
        f'<ellipse cx="9" cy="14.4" rx="7" ry="2.6" fill="{t["glyph"]}"/>'
        f'<path d="M2 9.3 A7 2.4 0 0 0 16 9.3" fill="none" stroke="{t["tile"]}" stroke-opacity=".55" stroke-width="1"/>'
        f'<circle cx="17.5" cy="16.5" r="6" fill="{t["star_hi"]}"/>'
        f'<path d="M14.6 16.6 l2 2 3.4-3.6" fill="none" stroke="{t["star"]}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        + pixel_star(17.5, -0.5, 1.3, t["star"], t["star_hi"])
    )
    gradcap = (
        f'<path d="M9 1 L18 5 L9 9 L0 5 Z" fill="{t["glyph"]}"/>'
        f'<rect x="6.5" y="5.4" width="5" height="5.4" fill="{t["glyph"]}" opacity=".85"/>'
        f'<circle cx="9" cy="8.4" r="1" fill="{t["star_hi"]}"/>'
        f'<path d="M15.5 4.2 v4.4" stroke="{t["glyph"]}" stroke-width="1.1"/>'
        f'<circle cx="15.5" cy="9.6" r="1.4" fill="{t["star"]}"/>'
        f'<circle cx="16" cy="18" r="2.1" fill="{t["glyph"]}"/>'
        f'<circle cx="22" cy="14.5" r="1.8" fill="{t["star"]}"/>'
        f'<circle cx="21" cy="20.5" r="1.6" fill="{t["glyph"]}" opacity=".7"/>'
        f'<path d="M17.8 17 L20.6 15" stroke="{t["glyph"]}" stroke-width="1.1" stroke-opacity=".7"/>'
        f'<path d="M17.5 19 L19.7 20" stroke="{t["glyph"]}" stroke-width="1.1" stroke-opacity=".7"/>'
    )
    bars = [(0, 13, 10), (5.5, 8, 15), (11, 15, 8)]
    dashboard = "".join(
        f'<rect x="{x}" y="{y}" width="4.2" height="{23-y}" rx="1" fill="{t["glyph"]}" opacity="{op}"/>'
        for (x, y, h), op in zip(bars, (.55, .9, .7))
    ) + (
        f'<path d="M2 10.5 L7.5 5.5 L13 8.5" fill="none" stroke="{t["star"]}" stroke-width="1.3" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        + pixel_star(16.5, 1, 1.6, t["star"], t["star_hi"])
        + f'<circle cx="17.3" cy="7.8" r=".9" fill="{t["star_hi"]}"/>'
    )
    briefcase = (
        f'<path d="M8 3.5 h6 a1.6 1.6 0 0 1 1.6 1.6 v1.4 h-9.2 v-1.4 a1.6 1.6 0 0 1 1.6-1.6 z" '
        f'fill="none" stroke="{t["glyph"]}" stroke-width="1.4" stroke-linejoin="round"/>'
        f'<rect x="1.4" y="6.5" width="19.2" height="11.5" rx="2" fill="{t["glyph"]}"/>'
        f'<rect x="1.4" y="6.5" width="19.2" height="3.3" rx="2" fill="{t["glyph"]}" opacity=".55"/>'
        f'<rect x="9.4" y="9.8" width="3.2" height="3.2" rx=".6" fill="{t["star_hi"]}"/>'
        + pixel_heart(1.5, 0.5, 1.5)
    )
    return {
        "about-database.svg": svg_doc(24, 24, database, "QA, validation and data reliability background", font),
        "about-gradcap.svg": svg_doc(24, 24, gradcap, "RWTH Aachen: machine learning and optimization coursework", font),
        "about-dashboard.svg": svg_doc(24, 24, dashboard, "Analytics products and applied AI systems", font),
        "about-briefcase.svg": svg_doc(22, 22, briefcase, "Open to internship and working-student opportunities", font),
    }


def divider() -> str:
    """Theme-neutral section divider."""
    W, H = 360, 18
    cx = W / 2
    body = (
        '<defs>'
        '<linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="#9C94E4" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#9C94E4" stop-opacity=".6"/></linearGradient>'
        '<linearGradient id="r" x1="0" x2="1"><stop offset="0" stop-color="#9C94E4" stop-opacity=".6"/>'
        '<stop offset="1" stop-color="#9C94E4" stop-opacity="0"/></linearGradient></defs>'
        f'<rect x="{cx-128}" y="8.5" width="112" height="1" fill="url(#l)"/>'
        f'<rect x="{cx+16}" y="8.5" width="112" height="1" fill="url(#r)"/>'
        f'<rect x="{cx-140}" y="8" width="2" height="2" fill="#9C94E4" fill-opacity=".45"/>'
        f'<rect x="{cx+138}" y="8" width="2" height="2" fill="#9C94E4" fill-opacity=".45"/>'
        + pixel_star(cx - 4, 5, 1.6, "#EC9A7E", "#F8C9B6")
    )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="presentation" aria-hidden="true">{body}</svg>\n')
