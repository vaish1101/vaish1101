#!/usr/bin/env python3
"""Validates the profile. Exits non-zero (failing CI) if anything is wrong.

    python assets/profile/src/validate_profile.py            # everything, incl. determinism check
    python assets/profile/src/validate_profile.py --fast     # skip the two-process determinism check

Checks: config schema; zero-overflow bounding-box QA of every generated SVG; committed assets
and the README Featured Work region are in sync with config; README markup and asset paths
(case-sensitive); public alt-text policy; mobile readability targets; no local paths or
secrets in generated output; and deterministic builds.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))


import config as cfgmod  # noqa: E402
from bounds import check_card, check_stack  # noqa: E402
from build_profile import generate, stale_generated_files  # noqa: E402
from readme_gen import BEGIN, END, featured_markup, sync_readme  # noqa: E402
from text_metrics import TextMetrics  # noqa: E402

FORBIDDEN_ALT = re.compile(r"\brepositor|\bnot yet\b|\bTODO\b|\bprivate\b|https?://|\.(svg|png|jpe?g)\b", re.I)
LOCAL_PATH = re.compile(r"/Users/|/home/[a-z]|/private/|/tmp/|[A-Za-z]:\\\\|file://")
SECRET_HINT = re.compile(
    r"(api[_-]?key|secret|passwd|password|access[_-]?token|auth[_-]?token)[\"']?\s*[:=]"
    r"|bearer\s+[A-Za-z0-9._-]{12,}|sk-[A-Za-z0-9]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_"
    r"|BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY", re.I)


def check_readability(cfg: cfgmod.Config, files: dict) -> list[str]:
    """Minimum EFFECTIVE mobile text sizes in GitHub's narrowest supported column."""
    tokens, errs = cfg.tokens, []
    col = tokens["card"]["github_column_px"][tokens["validation"]["readability_viewport"]]
    need = tokens["card"]["min_effective_mobile_text_px"]["_375"]
    L = tokens["card"]["mobile"]
    scale = min(1.0, col / L["width"])
    got = {"title": L["title_size"] * scale, "description": L["desc_size"] * scale,
           "chip": L["chip"]["font_size"] * scale, "cta": L["cta_size"] * scale}
    stack_w = float(re.search(r'width="(\d+)"', files[f"assets/profile/light/stack-board-mobile.svg"]).group(1))
    got["tech_stack_label"] = tokens["tech_stack"]["mobile"]["label_size"] * col / stack_w
    for k, v in got.items():
        if v + 1e-6 < need[k]:
            errs.append(f"mobile {k} renders at ~{v:.1f}px at 375px; minimum is {need[k]}px")
    return errs


class _Imgs(__import__("html.parser").parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.imgs, self.sources, self.pictures = [], [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img":
            self.imgs.append(a)
        elif tag == "source":
            self.sources.append(a)
        elif tag == "picture":
            self.pictures += 1


def check_readme(cfg: cfgmod.Config, files: dict) -> list[str]:
    errs = []
    text = (cfgmod.ROOT / "README.md").read_text(encoding="utf-8")
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        return [f"README.md: needs exactly one {BEGIN} / {END} marker pair"]
    if sync_readme(text, featured_markup(cfg)) != text:
        errs.append("README.md: Featured Work region is out of sync with config (run build_profile.py)")
    if LOCAL_PATH.search(text):
        errs.append("README.md: contains a local filesystem path")
    parser = _Imgs()
    parser.feed(text)
    refs = [i.get("src") for i in parser.imgs] + [s.get("srcset") for s in parser.sources]
    for ref in filter(None, refs):
        if ref.startswith("http"):
            continue
        cur = cfgmod.ROOT
        for part in pathlib.PurePosixPath(ref).parts:
            if part in (".", ""):
                continue
            if part not in os.listdir(cur):                      # exact-case existence check
                errs.append(f"README.md: {ref} does not exist (case-sensitive)")
                break
            cur = cur / part
    for img in parser.imgs:
        alt = img.get("alt")
        if alt is None:
            errs.append(f"README.md: <img src={img.get('src')}> has no alt attribute")
        elif alt and FORBIDDEN_ALT.search(alt):
            errs.append(f"README.md: alt text exposes internal/status wording or a filename: {alt[:60]!r}")
    for b, e in ((text.index(BEGIN), text.index(END)),):
        region = text[b:e]
        for p in cfg.projects:
            if p.get("url") is None and "<a href" in region.split(p.get("slug", p["id"]))[0].rsplit("<p align", 1)[-1]:
                errs.append(f"README.md: unlinked project {p['id']} is wrapped in a link")
    opens, closes = len(re.findall(r"<picture>", text)), len(re.findall(r"</picture>", text))
    if opens != closes:
        errs.append("README.md: unbalanced <picture> tags")
    return errs


def check_hygiene(cfg: cfgmod.Config, files: dict) -> list[str]:
    errs = []
    blobs = dict(files)
    for name in ("profile.json", "design_tokens.json", "sprites.json", "glyphs.json"):
        blobs[f"config/{name}"] = (cfgmod.CONFIG_DIR / name).read_text(encoding="utf-8")
    for name, text in blobs.items():
        if LOCAL_PATH.search(text):
            errs.append(f"{name}: contains a local filesystem path")
        if not name.endswith(".svg") and SECRET_HINT.search(text):
            errs.append(f"{name}: looks like it contains a secret")
    return errs


def check_determinism() -> list[str]:
    script = pathlib.Path(__file__).with_name("build_profile.py")
    out = []
    for seed in ("1", "2"):
        r = subprocess.run([sys.executable, str(script), "--hash"], capture_output=True, text=True,
                           env={**os.environ, "PYTHONHASHSEED": seed})
        if r.returncode:
            return [f"determinism: build failed: {r.stderr.strip()[:200]}"]
        out.append(r.stdout.strip())
    return [] if out[0] == out[1] else ["determinism: two builds produced different output"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fast", action="store_true", help="skip the determinism check")
    args = ap.parse_args(argv)

    cfg = cfgmod.load()
    errors = cfgmod.validate_config(cfg)
    if errors:
        print("\n".join(f"FAIL {e}" for e in errors))
        return 1
    metrics = TextMetrics(cfg.tokens)
    files, meta = generate(cfg, metrics)

    for path, svg in files.items():
        name = path.removeprefix("assets/profile/")
        if "/featured-" in path:
            errors += check_card(name, svg, metrics, cfg.tokens)
        elif "/stack-board" in path:
            errors += check_stack(name, svg, metrics)
        disk = cfgmod.ROOT / path
        if not disk.is_file() or disk.read_text(encoding="utf-8") != svg:
            errors.append(f"{name}: committed file differs from a fresh build (run build_profile.py)")
    errors += [f"{p.relative_to(cfgmod.ROOT)}: stale generated file with no enabled project"
               for p in stale_generated_files(cfg, files)]
    errors += check_readability(cfg, files)
    errors += check_readme(cfg, files)
    errors += check_hygiene(cfg, files)
    if not args.fast:
        errors += check_determinism()

    n_cards = sum(1 for p in files if "/featured-" in p)
    if errors:
        print("\n".join(f"FAIL {e}" for e in errors))
        print(f"\n{len(errors)} problem(s)")
        return 1
    print(f"OK: {len(cfg.projects)} project(s), {n_cards} cards + {len(files) - n_cards} other assets validated; "
          f"zero overflow; README in sync; deterministic" if not args.fast else
          f"OK (fast): {len(cfg.projects)} project(s), {n_cards} cards validated; zero overflow; README in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
