#!/usr/bin/env python3
"""Renders PNG previews of the generated assets (QA only -- previews are never committed).

    python assets/profile/src/render_preview.py [--out preview] [--scale 2]

Uses resvg (a pure-Rust SVG renderer) with the bundled Inter fonts, so it needs no browser and
gives the same pixels on macOS and Linux. Output: one PNG per generated SVG plus four sheets
(desktop/mobile x light/dark) stacking the Tech Stack and Featured Work cards.
"""
from __future__ import annotations

import argparse
import io
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import resvg_py  # noqa: E402
from PIL import Image  # noqa: E402

import config as cfgmod  # noqa: E402
from build_profile import generate  # noqa: E402

BACKGROUND = {"light": "#ffffff", "dark": "#0d1117"}


def render_svg(svg: str, background: str | None, scale: float) -> Image.Image:
    fonts = [str(cfgmod.SRC_DIR / f"fonts/Inter-{w}.ttf") for w in ("Regular", "SemiBold", "Bold")]
    png = resvg_py.svg_to_bytes(svg_string=svg, background=background, skip_system_fonts=True, font_files=fonts,
                                font_family="Inter", sans_serif_family="Inter", zoom=scale)
    return Image.open(io.BytesIO(bytes(png))).convert("RGBA")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="preview", help="output directory (default: ./preview, git-ignored)")
    ap.add_argument("--scale", type=float, default=2.0, help="pixel density (2 = Retina)")
    args = ap.parse_args(argv)

    cfg = cfgmod.load()
    problems = cfgmod.validate_config(cfg)
    if problems:
        print("Invalid configuration:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return 2
    files, _ = generate(cfg)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    written = 0
    for path, svg in files.items():
        if not path.endswith(".svg") or path.endswith("divider.svg"):
            continue
        theme = "dark" if "/dark/" in path else "light"
        render_svg(svg, BACKGROUND[theme], args.scale).save(out / (pathlib.Path(path).parent.name + "-" + pathlib.Path(path).name.replace(".svg", ".png")))
        written += 1

    gap, margin = int(16 * args.scale), int(16 * args.scale)
    for theme in cfg.themes:
        for mode, suffix in (("desktop", ""), ("mobile", "-mobile")):
            base = f"assets/profile/{theme}"
            names = [f"{base}/stack-board{suffix}.svg"] + [
                f"{base}/featured-{p.get('slug', p['id'])}{suffix}.svg" for p in cfg.projects]
            tiles = [render_svg(files[n], None, args.scale) for n in names]
            width = max(t.width for t in tiles) + 2 * margin
            sheet = Image.new("RGBA", (width, sum(t.height for t in tiles) + gap * (len(tiles) - 1) + 2 * margin),
                              BACKGROUND[theme])
            y = margin
            for t in tiles:
                sheet.alpha_composite(t, ((width - t.width) // 2, y))
                y += t.height + gap
            sheet.convert("RGB").save(out / f"sheet-{mode}-{theme}.png")
            written += 1
    print(f"wrote {written} preview PNGs to {out}/ (QA output; not committed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
