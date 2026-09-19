# Profile design specification (approved and frozen)

This file exists so that no future session (human or AI) accidentally redesigns the approved
profile. **The visual identity is finished.** Content changes are made in
`config/profile.json`; visual constants live in `config/design_tokens.json`. If a change to
this document seems necessary, it needs the owner's explicit approval first.

## 1. Concept

A soft, dreamy, twilight pixel-art profile that continues the banner: lavender / periwinkle /
peach / cream on deep indigo (dark) or pale lavender (light), with crisp pixel details kept small
and integrated. The Featured Work cards are **retro pixel desktop windows** -- not rounded SaaS
cards. Every piece of generated art is a pre-rendered SVG, because GitHub strips `<style>`,
classes and inline styles from README HTML. Light/dark switching uses `<picture>` and
`prefers-color-scheme`; mobile uses separate, narrower SVGs selected by `max-width: 560px`.

## 2. Palettes (values live in `design_tokens.json`)

| Role | Dark | Light |
|---|---|---|
| Card surface | `#191330` | `#F1EDFB` |
| Frame / border | `#A79AF2` | `#8074D6` |
| Glow | `#9C8FF0` @ .55 | `#B9AEEA` @ .30 |
| Title | `#F6EEDC` (warm cream) | `#2E2760` (deep indigo) |
| Description | `#BBB6DC` | `#544C82` |
| Chip fill / border / text | `#221B40` / `#9C8FF0` / `#DED9F7` | `#E7E1F9` / `#8074D6` / `#372F6E` |
| CTA | `#B6AEF7` | `#5B4FCF` |
| Accent (corners, dot) | `#F3C9A8` (peach) | `#E08A5C` |

Sprites keep the same pastel palette in both themes (`config/sprites.json`). Do not introduce
pure black, flat grey, neon, or generic blue-purple gradients.

Contrast (WCAG): dark text 8.8:1-15.5:1 (AAA); light text 5.3:1-11.6:1 (AA or better).

## 3. Typography

System font stack `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial`
(no web fonts: they do not load inside `<img>` SVGs). Titles are bold, cream/indigo, sentence
case, never all-caps and never a pixel font. The pixel personality comes from sprites and frame.

| | Desktop (820px card) | Mobile (335px card) |
|---|---|---|
| Title | 25px / 700 | 18px / 700 |
| Description | 15.5px / 400, line 23 | 15.5px / 400, line 22 |
| Chip label | 13.5px / 600 | 13.5px / 600 |
| CTA | 17px / 700 | 14px / 700 |
| Tech Stack label | 9.5px / 600 | 12.5px / 600 |

### Readability targets (minimums; do not go below)

GitHub shrinks the 335px mobile card to about 87.5% in its narrowest (375px) column, so mobile
source sizes are chosen for the *effective* size: **title 15.5px, description 13px, chip 11.5px,
CTA 12px, Tech Stack label 11px** at a 375px viewport. `validate_profile.py` enforces this from
the tokens. Content readability wins over identical card heights.

## 4. Featured Work card

- **Size:** desktop 820px wide, 275px baseline height (`min_height`); a card grows only if its own
  text needs more (measured wrapping, never a fixed clip). Mobile 335px wide, height = content.
- **Fallback fonts:** SVG text is rendered using the viewer's available fallback font. Layout
  measurement includes a conservative width allowance so common wider fallback fonts do not clip;
  titles, descriptions and chip rows may therefore wrap a little earlier than the raw Inter
  width would suggest. Type size, colour and chip/CTA styling are unaffected.
- **Layout (desktop):** sprite in the left column, title above description to its right, one
  full-width chip row, CTA on its own row bottom-right. **Mobile:** sprite + title on top,
  description full width below, chips wrap naturally, CTA bottom-right.
- **Card contains only:** sprite, title, description, technology chips, `View Project ↗`.
  Never add a category strip, `PROJECT:` label, statistics/proof row, badges or metadata.
- **Spacing:** desktop padding 26, sprite at (24, 26), chip gap 7; mobile padding 18, sprite at
  (18, 26), chip gap 6. Chips hang from the CTA row so chips and CTA align on every card.
- **Safe area:** every element stays >=10px inside the card and sprites >=18px; enforced by the
  validator.

## 5. Window chrome and stepped corners

The frame is built from pixel geometry, not a CSS rounded border:

1. a soft blurred **glow** behind the frame (`feGaussianBlur`, sharp line drawn on top);
2. a dim **outer edge** line (1.5px inset);
3. the bright **main border** (2.6px, 4.5px inset) filled with the card surface;
4. a stronger **top edge** line to read as a window titlebar edge (decorative only, no text);
5. a subtle **inner inset** line (9.5px inset);
6. **stepped corners**: every corner is a two-step pixel stair (`stair_step` 5, outer 6, inner 4),
   never an arc;
7. three tiny 3px **corner accent squares** (top-left, bottom-left, bottom-right);
8. top-right **window controls** (minimise / restore / close squares) plus a small **dot cluster**;
9. a 4-point **sparkle** and one accent pixel beside the CTA.

## 6. Sprites

Hand-pixelled 24x22 grids (`config/sprites.json`), one per project: EV charger + map pin, watch +
rising chart, supervisor + three agent nodes + spark (multi-agent orchestration, *not* a robot or
chatbot), customer + bars + trend arrow. Dark indigo outline, lavender/periwinkle body, peach/
blush/cream highlights, at most one amber accent. Rendered as crisp `<rect>` runs (desktop cell
4.5px, mobile 2px). A new project that needs a new visual adds one grid; never use emoji or
generic vector icons.

## 7. Technology chips

Boxy rounded-6 pills, 1.7px periwinkle border, dark (or pale) fill, real official logo where one
exists (`config/profile.json` -> `chip_icons`), otherwise a concept glyph or text only. Desktop
38px tall, mobile 32px. Chips wrap to new rows only when needed. Official marks stay
recognisable; do not fake a logo for a concept (DAX, RAG, pgvector, ...).

## 8. Tech Stack board

One continuous grid, no category headings. Items are placed sequentially into fixed columns: 7 on
desktop (700px grid centred on the 820px canvas, equal tracks) and 4 on mobile (313px canvas, equal
tracks). A partial last row keeps the same column tracks (it is never centred on its own). Tiles are
34px with 24px logos (19px glyphs) and a small alternating corner pixel; labels are 9.5px desktop /
12.5px mobile and wrap only when they do not fit their track. Order and labels come from
`tech_stack.items`; column counts and widths from `tech_stack` in `design_tokens.json`.

## 9. Sections and other assets

Order: banner, About Me (four short paragraphs with pixel micro-icons), Tech Stack, Featured Work,
Let's Connect. GitHub's native contribution graph (shown automatically below the README) is the activity view; the README has no custom activity section. The banner is a
raster (`assets/banner.png`, 1024x254) and is **not generated** by this builder; do not redraw it.

## 10. Do NOT casually change

Card concept and chrome; stepped corners; sprites; palettes; typography hierarchy; the minimum
mobile sizes above; project order/names/descriptions (they are content, edited in `profile.json`
only when the owner asks); the "nothing above the title" rule; section order.
