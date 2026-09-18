"""Generates the README's Featured Work region from project data.

Only the text between the BEGIN/END markers is ever replaced; every human-written line of the
README is left exactly as it is. Alt text is derived from the same data as the cards, so the
two cannot drift apart. The clickable link is added here (never baked into the SVG): a project
with ``url: null`` becomes an unlinked card.
"""
from __future__ import annotations

import html

from config import Config

BEGIN = "<!-- BEGIN GENERATED:FEATURED_WORK -->"
END = "<!-- END GENERATED:FEATURED_WORK -->"
MOBILE_MAX_WIDTH = 560


def alt_text(project: dict) -> str:
    """Public-facing description only: title, description, technologies. No internal status."""
    techs = ", ".join(project["technologies"])
    return f"{project['title']}. {project['description'].strip().rstrip('.')}. Tech: {techs}."


def _asset(theme: str, slug: str, mobile: bool) -> str:
    return f"./assets/profile/{theme}/featured-{slug}{'-mobile' if mobile else ''}.svg"


def project_block(project: dict) -> str:
    slug = project.get("slug", project["id"])
    alt = html.escape(alt_text(project), quote=True)
    picture = "\n".join([
        "<picture>",
        f'<source media="(prefers-color-scheme: dark) and (max-width: {MOBILE_MAX_WIDTH}px)" srcset="{_asset("dark", slug, True)}" />',
        f'<source media="(max-width: {MOBILE_MAX_WIDTH}px)" srcset="{_asset("light", slug, True)}" />',
        f'<source media="(prefers-color-scheme: dark)" srcset="{_asset("dark", slug, False)}" />',
        f'<img src="{_asset("light", slug, False)}" alt="{alt}" />',
        "</picture>",
    ])
    if project.get("url"):
        picture = f'<a href="{html.escape(project["url"], quote=True)}">\n{picture}\n</a>'
    return f'<p align="center">\n{picture}\n</p>'


def featured_markup(cfg: Config) -> str:
    return "\n\n".join(project_block(p) for p in cfg.projects)


def sync_readme(text: str, markup: str) -> str:
    """Returns README text with the generated region replaced; raises if markers are unusable."""
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError(f"README.md must contain exactly one '{BEGIN}' and one '{END}' marker")
    head, rest = text.split(BEGIN)
    _, tail = rest.split(END)
    return f"{head}{BEGIN}\n{markup}\n{END}{tail}"
