"""Loads and validates the profile configuration (content + design tokens).

Content lives in ``config/profile.json``; every visual constant lives in
``config/design_tokens.json``; sprites and glyphs are data too. Nothing in the renderer
knows how many projects exist or what they are called.
"""
from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass, field

SRC_DIR = pathlib.Path(__file__).resolve().parent
PROFILE_DIR = SRC_DIR.parent
ROOT = PROFILE_DIR.parent.parent
CONFIG_DIR = PROFILE_DIR / "config"
LOGOS_DIR = SRC_DIR / "logos"

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@dataclass
class Config:
    tokens: dict
    profile: dict
    sprites: dict
    sprite_palette: dict
    glyphs: dict
    themes: tuple = field(default=("light", "dark"))

    @property
    def projects(self) -> list[dict]:
        """Enabled projects in display order (stable: ties broken by id)."""
        enabled = [p for p in self.profile["projects"] if p.get("enabled", True)]
        return sorted(enabled, key=lambda p: (p.get("order", 0), p["id"]))


def _read(name: str) -> dict:
    return json.loads((CONFIG_DIR / name).read_text(encoding="utf-8"))


def load() -> Config:
    sprites = _read("sprites.json")
    return Config(
        tokens=_read("design_tokens.json"),
        profile=_read("profile.json"),
        sprites=sprites["sprites"],
        sprite_palette=sprites["palette"],
        glyphs=_read("glyphs.json")["glyphs"],
    )


def validate_config(cfg: Config) -> list[str]:
    """Returns a list of human-readable problems (empty when the config is valid)."""
    errors: list[str] = []
    profile, tokens = cfg.profile, cfg.tokens
    techs = profile.get("technologies", {})
    chip_icons = profile.get("chip_icons", {})
    cols, rows = tokens["card"]["sprite_cols"], tokens["card"]["sprite_rows"]

    ids, slugs = set(), set()
    for i, p in enumerate(profile.get("projects", [])):
        where = f"projects[{i}] ({p.get('id', '?')})"
        for key in ("id", "title", "description", "icon", "technologies"):
            if key not in p:
                errors.append(f"{where}: missing '{key}'")
        pid, slug = p.get("id", ""), p.get("slug", p.get("id", ""))
        if not _ID_RE.match(pid):
            errors.append(f"{where}: id must match [a-z0-9-]+ (got {pid!r})")
        if not _ID_RE.match(slug):
            errors.append(f"{where}: slug must match [a-z0-9-]+ (got {slug!r})")
        if pid in ids:
            errors.append(f"{where}: duplicate id")
        if slug in slugs:
            errors.append(f"{where}: duplicate slug (asset filenames would collide)")
        ids.add(pid)
        slugs.add(slug)
        for key in ("title", "description"):
            if not isinstance(p.get(key), str) or not p.get(key, "").strip():
                errors.append(f"{where}: '{key}' must be a non-empty string")
        if p.get("icon") not in cfg.sprites:
            errors.append(f"{where}: unknown icon {p.get('icon')!r} (sprites: {sorted(cfg.sprites)})")
        tech = p.get("technologies")
        if not isinstance(tech, list) or not tech or not all(isinstance(t, str) and t.strip() for t in tech):
            errors.append(f"{where}: 'technologies' must be a non-empty list of strings")
        chip_rows_cfg = p.get("chip_rows")
        if chip_rows_cfg is not None:
            if not isinstance(chip_rows_cfg, dict) or set(chip_rows_cfg) - {"desktop", "mobile"}:
                errors.append(f"{where}: 'chip_rows' must be an object with optional 'desktop'/'mobile' lists")
            else:
                for variant, counts in chip_rows_cfg.items():
                    if (not isinstance(counts, list) or not counts
                            or not all(isinstance(n, int) and not isinstance(n, bool) and n > 0 for n in counts)
                            or (isinstance(tech, list) and sum(counts) != len(tech))):
                        errors.append(f"{where}: chip_rows.{variant} must be positive integers summing to "
                                      f"the number of technologies")
        url = p.get("url")
        if url is not None and not (isinstance(url, str) and url.startswith("https://")):
            errors.append(f"{where}: url must be null or an https:// URL")
        if not isinstance(p.get("enabled", True), bool):
            errors.append(f"{where}: 'enabled' must be true/false")
        if not isinstance(p.get("order", 0), int):
            errors.append(f"{where}: 'order' must be an integer")

    for name, grid in cfg.sprites.items():
        if len(grid) != rows or any(len(r) != cols for r in grid):
            errors.append(f"sprite {name!r}: must be {cols}x{rows} characters")
        bad = {c for r in grid for c in r} - set(cfg.sprite_palette) - {"."}
        if bad:
            errors.append(f"sprite {name!r}: characters not in palette: {sorted(bad)}")

    for label, key in chip_icons.items():
        if key not in techs:
            errors.append(f"chip_icons[{label!r}] -> unknown technology key {key!r}")
    for key, spec in techs.items():
        if "logo" in spec and not (LOGOS_DIR / spec["logo"]["file"]).is_file():
            errors.append(f"technology {key!r}: logo file {spec['logo']['file']!r} not found in src/logos")
        if "glyph" in spec and spec["glyph"] not in cfg.glyphs:
            errors.append(f"technology {key!r}: unknown glyph {spec['glyph']!r}")
    for r, row in enumerate(profile.get("tech_stack", {}).get("rows", [])):
        for key, _label in row:
            if key not in techs:
                errors.append(f"tech_stack row {r}: unknown technology key {key!r}")
    for theme in cfg.themes:
        if theme not in tokens["themes"] or theme not in tokens["card_colors"]:
            errors.append(f"design_tokens: theme {theme!r} missing")
    return errors
