#!/usr/bin/env python3
"""Builds every generated profile asset from config/ and syncs the README's Featured Work region.

    python assets/profile/src/build_profile.py            # write assets + README region
    python assets/profile/src/build_profile.py --check    # write nothing; exit 1 if anything is stale
    python assets/profile/src/build_profile.py --hash     # print a digest of all outputs (determinism check)
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import config as cfgmod  # noqa: E402
from bounds import check_card, check_stack  # noqa: E402
from cards import render_card  # noqa: E402
from decor import about_icons, divider  # noqa: E402
from readme_gen import featured_markup, sync_readme  # noqa: E402
from techstack import render_techstack  # noqa: E402
from text_metrics import TextMetrics  # noqa: E402

REL_PROFILE = "assets/profile"


def generate(cfg: cfgmod.Config, metrics: TextMetrics | None = None):
    """Pure function: returns ({repo-relative path: svg text}, {path: layout meta})."""
    metrics = metrics or TextMetrics(cfg.tokens)
    files, meta = {}, {}
    files[f"{REL_PROFILE}/divider.svg"] = divider()
    for theme in cfg.themes:
        base = f"{REL_PROFILE}/{theme}"
        for mode, suffix in (("desktop", ""), ("mobile", "-mobile")):
            files[f"{base}/stack-board{suffix}.svg"] = render_techstack(cfg, theme, mode)
            for project in cfg.projects:
                slug = project.get("slug", project["id"])
                path = f"{base}/featured-{slug}{suffix}.svg"
                files[path], meta[path] = render_card(cfg, metrics, theme, project, mode)
        for name, svg in about_icons(cfg, theme).items():
            files[f"{base}/{name}"] = svg
    return files, meta


def check_bounds(cfg: cfgmod.Config, metrics: TextMetrics, files: dict) -> list[str]:
    """Zero-overflow QA on the finished SVGs; the build refuses to write if anything escapes."""
    errs = []
    for path, svg in files.items():
        name = path.removeprefix(REL_PROFILE + "/")
        if "/featured-" in path:
            errs += check_card(name, svg, metrics, cfg.tokens)
        elif "/stack-board" in path:
            errs += check_stack(name, svg, metrics)
    return errs


def stale_generated_files(cfg: cfgmod.Config, files: dict) -> list[pathlib.Path]:
    """featured-*.svg on disk that no enabled project produces any more."""
    stale = []
    for theme in cfg.themes:
        for p in (cfgmod.ROOT / REL_PROFILE / theme).glob("featured-*.svg"):
            if p.relative_to(cfgmod.ROOT).as_posix() not in files:
                stale.append(p)
    return stale


def digest(files: dict, readme: str) -> str:
    h = hashlib.sha256()
    for path in sorted(files):
        h.update(path.encode() + b"\0" + files[path].encode() + b"\0")
    h.update(readme.encode())
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="do not write; exit 1 if generated files are out of date")
    ap.add_argument("--hash", action="store_true", help="print a sha256 digest of every generated output")
    args = ap.parse_args(argv)

    cfg = cfgmod.load()
    problems = cfgmod.validate_config(cfg)
    if problems:
        print("Invalid configuration:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return 2

    metrics = TextMetrics(cfg.tokens)
    files, _meta = generate(cfg, metrics)
    overflow = check_bounds(cfg, metrics, files)
    if overflow:
        print("Build refused: content escapes its card bounds (nothing was written):\n  - " + "\n  - ".join(overflow[:20]), file=sys.stderr)
        return 3
    readme_path = cfgmod.ROOT / "README.md"
    current_readme = readme_path.read_text(encoding="utf-8")
    new_readme = sync_readme(current_readme, featured_markup(cfg))

    if args.hash:
        print(digest(files, new_readme))
        return 0

    changed = [p for p, svg in files.items()
               if not (cfgmod.ROOT / p).is_file() or (cfgmod.ROOT / p).read_text(encoding="utf-8") != svg]
    stale = stale_generated_files(cfg, files)
    readme_changed = new_readme != current_readme

    if args.check:
        for p in changed:
            print(f"out of date: {p}")
        for p in stale:
            print(f"stale (no enabled project): {p.relative_to(cfgmod.ROOT)}")
        if readme_changed:
            print("out of date: README.md (Featured Work region)")
        if changed or stale or readme_changed:
            print("Run: python assets/profile/src/build_profile.py", file=sys.stderr)
            return 1
        print(f"up to date: {len(files)} generated files + README region")
        return 0

    for p, svg in files.items():
        target = cfgmod.ROOT / p
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(svg, encoding="utf-8")
    for p in stale:
        p.unlink()
    if readme_changed:
        readme_path.write_text(new_readme, encoding="utf-8")
    print(f"built {len(files)} files ({len(changed)} changed, {len(stale)} removed, "
          f"README region {'updated' if readme_changed else 'unchanged'}); {len(cfg.projects)} enabled project(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
