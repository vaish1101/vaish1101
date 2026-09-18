# Regenerating the profile assets

`build_cards.py` renders every generated image in `assets/profile/{light,dark}/` --
the Tech Stack board, the four Featured Work cards (desktop + mobile), and the About Me
icons -- plus `assets/profile/divider.svg`. GitHub strips `<style>`/class/inline style from
README HTML and puts hard borders on every `<table>`, so these are pre-rendered SVGs,
swapped by theme (and by viewport for the mobile variants) with `<picture>`.

## Regenerate after an edit

```bash
python3 -m pip install lxml pillow   # once
python3 assets/profile/src/build_cards.py
```

Output is deterministic (two clean runs are byte-identical). Commit the regenerated files
in `assets/profile/{light,dark}/`, not just this script. Text is measured with macOS's
`/System/Library/Fonts/SFNS.ttf` and calibrated against Chrome, so regenerate on macOS.

## Featured Work

Project copy, chips and icon keys live in `PROJECTS_FINAL`; the card renderer is
`final_card()`. The pixel sprites are 24-column grids in `SPRITES`. Desktop cards are
820px wide with a 275px baseline height (`APPROVED_DESKTOP_H`) and only grow if their own
text needs it; mobile cards are 335px wide and take the height their content needs.

## Add a new tool chip / Tech Stack tile

If the tool has a real logo, drop its official SVG into `logos/` and add
`"key": ("file.svg", None)` to `LOGO_FILES` (the second value is a hex colour, only needed
for mono outline sources). If there is no real logo, add a small glyph to `G` and register
the key as `"key": None` in `LOGO_FILES` instead of inventing a fake logo. Featured Work
chips pick up icons through `CHIP_ICON_MAP`.
