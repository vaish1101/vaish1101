# Building the profile

Everything under `assets/profile/light/`, `assets/profile/dark/` and `assets/profile/divider.svg`
is **generated**, as is the Featured Work block of `README.md` (between the
`<!-- BEGIN GENERATED:FEATURED_WORK -->` / `<!-- END GENERATED:FEATURED_WORK -->` markers).
Do not hand-edit those; change the config and rebuild. No secrets, network access or browser
are needed, and nothing depends on a particular machine.

## Requirements

- Python **3.13** (CI uses the same)
- macOS or Linux (Windows should work; CI runs Linux)
- Dependencies are pinned in the repo-root `requirements.txt` (`lxml`, `Pillow`, `resvg-py`)

## From a clean checkout

```bash
git clone https://github.com/vaish1101/vaish1101.git
cd vaish1101
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt

python assets/profile/src/build_profile.py      # 1. build assets + sync README region
python assets/profile/src/validate_profile.py   # 2. validate (overflow, sync, alt text, determinism)
python assets/profile/src/render_preview.py     # 3. optional PNG previews in ./preview (git-ignored)
```

Text is measured with the bundled Inter fonts (`src/fonts/`, SIL OFL), so layout is identical on
every platform. Useful flags: `build_profile.py --check` (write nothing, exit 1 if stale),
`--hash` (digest of all outputs), `validate_profile.py --fast` (skip the determinism check).

SVG text is rendered using the viewer's available fallback font. Layout measurement includes a
conservative width allowance so common wider fallback fonts do not clip. The allowance is the
per-weight `text_metrics.text_measurement_safety_factor` in `design_tokens.json` (regular 1.07,
semibold 1.06, bold 1.1). It only affects where lines wrap and how wide chips and cards are
laid out; rendered text is never stretched (no `textLength`) and font sizes are unchanged.
Values are the smallest that measured clean across Inter, the Chrome default stack, Arial,
Helvetica, Noto Sans and DejaVu Sans; re-check with all of them if you change a value.

## Where things live

| Path | What |
|---|---|
| `assets/profile/config/profile.json` | **Content**: projects, technology registry, chip icons, Tech Stack rows |
| `assets/profile/config/design_tokens.json` | Every visual constant (colours, sizes, spacing, frame, targets) |
| `assets/profile/config/sprites.json` | Pixel sprites (24x22 character grids + palette) |
| `assets/profile/config/glyphs.json` | Concept glyphs for technologies without an official logo |
| `assets/profile/src/` | Code: `build_profile.py`, `validate_profile.py`, `render_preview.py`, `cards.py`, `techstack.py`, `decor.py`, ... and `logos/`, `fonts/` |
| `assets/profile/DESIGN.md` | The approved design spec -- read before changing visuals |

## Add a project

1. Add one object to `projects` in `config/profile.json`:

   ```json
   {
     "id": "my-project",
     "slug": "my-project",
     "title": "My Project Title",
     "description": "One or two public-facing sentences.",
     "icon": "ev",
     "technologies": ["Python", "SQL"],
     "url": null,
     "enabled": true,
     "order": 5
   }
   ```
   `icon` must be a key in `sprites.json`. Technologies with an entry in `chip_icons` get a logo
   or glyph; others render as text-only chips.
   *Optional:* `"chip_rows": {"desktop": [4, 3]}` forces a break after that many chips per row
   (must sum to the number of technologies; `desktop`/`mobile` are independent). Without it chips
   wrap automatically, which is the default for every project and for mobile.
2. *Only if you need a new visual:* add a 24x22 grid to `config/sprites.json` (see DESIGN.md).
3. `python assets/profile/src/build_profile.py` -- generates the four SVGs (light/dark x
   desktop/mobile), updates the README region and alt text.
4. `python assets/profile/src/validate_profile.py`.
5. Commit the config, generated SVGs and README together.

No renderer code changes, and any number of projects is supported.

## Change, hide, reorder

- **Change content:** edit `title`, `description` or `technologies`; rebuild. Alt text follows automatically.
- **Add a repository link:** set `"url": "https://github.com/..."` (public repos only) and rebuild.
  The link is added in README markup; the SVG only shows the text `View Project ↗`. `null` = unlinked card.
- **Hide:** `"enabled": false`; the builder removes its SVGs and README block.
- **Reorder:** change `order` (lower first; ties broken by `id`).
- **Add a new technology chip logo:** drop the official SVG in `src/logos/`, register it under
  `technologies` and map the label under `chip_icons`; credit it in `NOTICE.md`.
- **Change the Tech Stack:** edit `tech_stack.rows` (keep rows balanced; see DESIGN.md section 8).

## Regenerate everything

```bash
python assets/profile/src/build_profile.py && python assets/profile/src/validate_profile.py
```

Builds are deterministic (no timestamps, random ids or machine paths); the validator builds twice
under different hash seeds and compares. CI (`.github/workflows/profile-ci.yml`) runs
build -> `git diff --exit-code` -> validate on pull requests and pushes, so config and committed
assets cannot drift apart. It only checks; it never edits the repository.

## Guardrails

- The build fails if any element escapes its card's safe area, a sprite gets within 18px of the frame,
  mobile text drops below the readability minimums, README alt text mentions repositories/status/
  filenames, a README asset path is missing (case-sensitive), or generated output contains a local path.
- Never commit `.env`, keys, tokens, client data, VWP inventory/exports or private source. The profile
  needs metadata only.
- The contribution snake is published by `.github/workflows/snake.yml` to the `output` branch; leave it alone.
