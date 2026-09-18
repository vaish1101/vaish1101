"""Builds the README's theme-aware SVG cards (Tech Stack, Currently Building,
and — for future use — Featured Projects).

Why SVG at all: a GitHub README strips <style>, class and inline style from HTML,
and draws hard borders on every <table>. Soft cards, tinted groups and consistent
typography aren't reachable in plain GitHub-flavoured Markdown/HTML, so each card
is rendered as an SVG image instead — once for light mode, once for dark — and
swapped with <picture><source media="(prefers-color-scheme: dark)">.

Official logos are embedded as nested <svg> markup (not data: URIs): GitHub serves
raw.githubusercontent.com with a CSP of default-src 'none', which blocks data:
images, so a data-URI logo would render as a broken image.

Regenerate after editing this file or `assets/profile/src/logos/`:

    cd assets/profile/src
    python3 -m pip install lxml pillow   # once (text is measured with macOS's SFNS.ttf, so run on macOS)
    python3 build_cards.py

Output goes to assets/profile/{light,dark}/*.svg — commit those, not just this script.
"""
import sys, pathlib, re
from lxml import etree
from PIL import ImageFont  # build-time only: pixel-exact text wrapping for the Featured Work v2 cards

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parents[2]                 # repo root
LOGOS = HERE / "logos"
OUT = ROOT / "assets" / "profile"
SVG_NS = "http://www.w3.org/2000/svg"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

THEMES = {
    "light": dict(
        card="#F8F7FD", card_o=1, card_st="#EEEBF8", card_st_o=1,
        ai_a="#F2EFFD", ai_a_o=1, ai_b="#FDF1F5", ai_b_o=1, ai_st="#DED8F6", ai_st_o=1,
        heading="#6B61C4", star="#EC9A7E", star_hi="#F8C9B6", spark="#9B93E6",
        tile="#FFFFFF", tile_st="#ECE8F6", tile_st_o=1,
        ctile="#EFECFC", ctile_o=1, ctile_st="#E0DAF8", ctile_st_o=1, glyph="#6E63C6",
        label="#3A3F4B", big="#5A4FC4", phrase="#1F2328", sub="#5F6873",
        bar_a="#8B82DE", bar_b="#EC9A7E", icon="#A39CE8", tag_bg="#EFECFC", tag_fg="#5A4FC4",
        peri="#AAB9FF", plinth_shadow="#E4E0F5",
    ),
    "dark": dict(
        card="#FFFFFF", card_o=.03, card_st="#A9A2F0", card_st_o=.14,
        ai_a="#7B72D4", ai_a_o=.17, ai_b="#E98CA8", ai_b_o=.09, ai_st="#A9A2F0", ai_st_o=.32,
        heading="#AFA8F3", star="#F3B49C", star_hi="#FBDCCF", spark="#8F87DD",
        tile="#E7E4F2", tile_st="#E7E4F2", tile_st_o=0,
        ctile="#A9A2F0", ctile_o=.13, ctile_st="#A9A2F0", ctile_st_o=.30, glyph="#C4BEF7",
        label="#C9D1D9", big="#B8B1F6", phrase="#E6EDF3", sub="#8D96A0",
        bar_a="#9A92E6", bar_b="#F0AA92", icon="#7F77CF", tag_bg="#2A2440", tag_fg="#C4BEF7",
        peri="#AAB9FF", plinth_shadow="#100E22",
    ),
}

# ---------------------------------------------------------------- official logos
LOGO_FILES = {
    "python": ("python.svg", None), "sql": None, "powerbi": ("powerbi.svg", None),
    "excel": ("excel.svg", None), "tableau": ("tableau_mono.svg", "#E97627"),
    "dax": None, "powerquery": None,
    "postgresql": ("postgresql.svg", None), "databricks": ("databricks_mono.svg", "#FF3621"),
    "spark": ("apachespark.svg", None), "azure": ("azure.svg", None),
    "pandas": ("pandas.svg", None), "numpy": ("numpy.svg", None),
    "sklearn": ("scikitlearn.svg", None), "keras": ("keras.svg", None), "stats": None,
    "langchain": ("langchain_svgl.svg", None), "langgraph": ("langgraph_mono.svg", "#7FC8FF"),
    "fastapi": ("fastapi.svg", None), "llms": None, "rag": None, "agentic": None,
    "git": ("git.svg", None), "gha": ("githubactions.svg", None), "pytest": ("pytest.svg", None),
    "docker": ("docker.svg", None), "postman": ("postman.svg", None),
    "selenium": ("selenium.svg", None), "jira": ("jira.svg", None),
    "confluence": ("confluence_mono.svg", "#172B4D"),
    "streamlit": ("streamlit.svg", None),
    "mysql": ("mysql.svg", None),
    "pydantic": ("pydantic.svg", "#E92063"),  # official mark has no own fill; brand magenta
    "deltalake": None,   # no official logo in Devicon/Simple Icons/svgl -- custom glyph below
    "pgvector": None,    # no official logo anywhere -- custom PostgreSQL+vector glyph below
    "ml": None,
    "duckdb": ("duckdb.svg", None),   # verified official Simple Icons mark
    "ebay": ("ebay.svg", None),       # verified official Simple Icons mark
    "etl": None,   # generic concept, no brand -- custom funnel glyph below
}
_uid = [0]

def logo(key, x, y, size):
    fname, mono = LOGO_FILES[key]
    root = etree.parse(str(LOGOS / fname)).getroot()
    vb = root.get("viewBox")
    _uid[0] += 1
    p = f"l{_uid[0]}"
    for el in root.iter():
        if isinstance(el.tag, str) and etree.QName(el).localname in ("title", "desc", "metadata"):
            el.getparent().remove(el)
    ids = [el.get("id") for el in root.iter() if isinstance(el.tag, str) and el.get("id")]
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        for k, v in list(el.attrib.items()):
            if k == "id":
                el.set(k, f"{p}-{v}")
            else:
                for i in ids:
                    v = v.replace(f"url(#{i})", f"url(#{p}-{i})")
                    if v == f"#{i}":
                        v = f"#{p}-{i}"
                el.set(k, v)
    inner = "".join(etree.tostring(c, encoding="unicode") for c in root if isinstance(c.tag, str))
    inner = inner.replace(f' xmlns="{SVG_NS}"', "")
    fill = f' fill="{mono}"' if mono else ""
    return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{vb}"{fill}>{inner}</svg>'

# ---------------------------------------------------------------- concept glyphs
G = {
    "sql": '<rect x="3.5" y="5" width="17" height="14" rx="2.2"/><path d="M3.5 10h17M3.5 14.5h17M9.5 10v9"/>',
    "dax": '<text x="12" y="16.6" text-anchor="middle" font-family="Georgia,serif" font-style="italic" '
           'font-weight="700" font-size="13" stroke="none" fill="currentColor">fx</text>',
    "powerquery": '<path d="M4 4.5h16l-6 8.2v7l-4 2v-9z"/>',
    "stats": '<path d="M3 19h18"/><path d="M4 18.2c3.2 0 4-11.4 8-11.4s4.8 11.4 8 11.4"/><path d="M12 6.8V19" stroke-dasharray="1.6 2"/>',
    "llms": '<path d="M5 5.5h14a2 2 0 0 1 2 2v7.5a2 2 0 0 1-2 2h-7.5L7 20.5V17H5a2 2 0 0 1-2-2V7.5a2 2 0 0 1 2-2z"/>'
            '<circle cx="8.3" cy="11.3" r=".9" fill="currentColor"/><circle cx="12" cy="11.3" r=".9" fill="currentColor"/>'
            '<circle cx="15.7" cy="11.3" r=".9" fill="currentColor"/>',
    "rag": '<path d="M13 3.5H6.5a1.5 1.5 0 0 0-1.5 1.5v14a1.5 1.5 0 0 0 1.5 1.5H11"/><path d="M13 3.5l4.5 4.5v2.5"/>'
           '<path d="M8 9.5h5M8 12.8h3"/><circle cx="15.8" cy="16" r="3.3"/><path d="M18.2 18.4l2.6 2.6"/>',
    "agentic": '<circle cx="6" cy="17.5" r="2.4"/><circle cx="12" cy="5.8" r="2.4"/><circle cx="18" cy="17.5" r="2.4"/>'
               '<path d="M7.2 15.3l3.6-7.2M13.2 8.1l3.6 7.2M8.5 17.5h7"/>',
    "check": '<circle cx="12" cy="12" r="8.5"/><path d="M8.3 12.3l2.5 2.5 5-5.2"/>',
    "database": '<ellipse cx="12" cy="6" rx="7" ry="2.8"/><path d="M5 6v12c0 1.55 3.13 2.8 7 2.8s7-1.25 7-2.8V6"/>'
                '<path d="M5 12c0 1.55 3.13 2.8 7 2.8s7-1.25 7-2.8"/>',
    "terminal": '<rect x="3" y="4.5" width="18" height="15" rx="2.5"/><path d="M7 10l3 2.5L7 15M12.5 15.5H17"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5.5 5.5M8 10.5h5"/>',
    "shield": '<path d="M12 3.3l7 3v5.3c0 4.3-3 7.7-7 8.9-4-1.2-7-4.6-7-8.9V6.3z"/><path d="M8.8 12l2.3 2.3 4.2-4.4"/>',
    "layers": '<path d="M12 3.8l8.2 4.1L12 12 3.8 7.9z"/><path d="M3.8 12L12 16.1 20.2 12"/><path d="M3.8 16.1L12 20.2l8.2-4.1"/>',
    "nodesparkle": '<circle cx="6" cy="17.5" r="2.2"/><circle cx="17.8" cy="17.5" r="2.2"/><path d="M8.2 17.5h7.4"/>'
                   '<path d="M7 15.6l3.3-5.4M16.8 15.6l-3.3-5.4"/><path d="M12 2.8l1 2.9 2.9 1-2.9 1-1 2.9-1-2.9-2.9-1 2.9-1z"/>',
    # medallion-architecture triangle: two tier lines nod to Bronze/Silver/Gold layering
    "deltalake": '<path d="M12 3.3 L21 20.3 H3 Z"/><path d="M7.1 13.6h9.8"/><path d="M9.2 16.9h5.6"/>',
    # a small database with a few embedding points around it, loosely tied by thin lines
    "pgvector": '<ellipse cx="8" cy="5.3" rx="5" ry="2"/><path d="M3 5.3v6c0 1.1 2.24 2 5 2s5-.9 5-2v-6"/>'
                '<path d="M13.5 8.2 17 9.5 20 14.3 15 17.3" stroke-dasharray="1.3 1.6"/>'
                '<circle cx="17" cy="9.5" r="1" fill="currentColor" stroke="none"/>'
                '<circle cx="20" cy="14.3" r="1" fill="currentColor" stroke="none"/>'
                '<circle cx="15" cy="17.3" r="1" fill="currentColor" stroke="none"/>',
    # a small branching decision tree -- deliberately distinct from the agentic-workflow
    # triangle glyph, to read as classical ML rather than another agent/graph motif
    "ml": '<circle cx="12" cy="4.6" r="2.1"/><path d="M12 6.7v3.1M12 9.8 6.3 16M12 9.8 17.7 16"/>'
          '<circle cx="6.3" cy="18.1" r="2.1"/><circle cx="17.7" cy="18.1" r="2.1"/>'
          '<path d="M19.6 2.6v3M18.1 4.1h3"/>',
    # generic data-pipeline funnel -- no single brand covers "ETL" as a concept
    "etl": '<path d="M3.5 4.5h17l-6.2 7.6v6.4l-4.6 2.2v-8.6z"/>',
}

def glyph(key, x, y, size, color, width=1.7):
    s = size / 24
    return (f'<g transform="translate({x} {y}) scale({s:.4f})" fill="none" stroke="{color}" color="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">{G[key]}</g>')

def pixel_star(x, y, px, color, hi):
    cells = [(2, 0), (2, 1), (0, 2), (1, 2), (3, 2), (4, 2), (2, 3), (2, 4)]
    r = "".join(f'<rect x="{x + cx * px:.2f}" y="{y + cy * px:.2f}" width="{px}" height="{px}"/>' for cx, cy in cells)
    return (f'<g fill="{color}" shape-rendering="crispEdges">{r}</g>'
            f'<rect x="{x + 2 * px:.2f}" y="{y + 2 * px:.2f}" width="{px}" height="{px}" fill="{hi}" shape-rendering="crispEdges"/>')

BLUSH = "#E98CA8"

def pixel_heart(x, y, px, color=BLUSH):
    rows = [
        "01100110", "11111111", "11111111", "01111110", "00111100", "00011000",
    ]
    cells = [(cx, cy) for cy, row in enumerate(rows) for cx, v in enumerate(row) if v == "1"]
    r = "".join(f'<rect x="{x + cx*px:.2f}" y="{y + cy*px:.2f}" width="{px}" height="{px}"/>' for cx, cy in cells)
    return f'<g fill="{color}" shape-rendering="crispEdges">{r}</g>'

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def svg_doc(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(title)}" font-family="{FONT}"><title>{esc(title)}</title>{body}</svg>\n')

# ---------------------------------------------------------------- tech stack matrix
# A true column-aligned grid, not independently packed rows: column j has one shared
# width across all four rows (sized to whatever needs the most room in that column --
# 'PostgreSQL' in column 4, say), so tiles line up vertically top to bottom, the way a
# real product grid does. Row height is likewise uniform (every row reserves the same
# two-line label slot), so the whole matrix reads as one clean rhythm, not four
# independently-sized strips. Exactly four rows by design -- see build_cards README
# before adding a tool, since a fifth item anywhere means rebalancing all four rows.
TECH_ROWS = [
    [("python", "Python"), ("mysql", "MySQL"), ("postgresql", "PostgreSQL"), ("deltalake", "Delta Lake"),
     ("powerbi", "Power BI"), ("excel", "Excel"), ("tableau", "Tableau"), ("streamlit", "Streamlit")],
    [("pandas", "pandas"), ("numpy", "NumPy"), ("sklearn", "scikit-learn"), ("keras", "Keras"),
     ("ml", "Machine Learning"), ("databricks", "Databricks"), ("spark", "PySpark"), ("azure", "Azure")],
    [("langchain", "LangChain"), ("langgraph", "LangGraph"), ("fastapi", "FastAPI"), ("llms", "LLMs"),
     ("rag", "RAG"), ("agentic", "Agentic Workflows"), ("pydantic", "Pydantic"), ("pgvector", "pgvector")],
    [("git", "Git"), ("gha", "GitHub Actions"), ("docker", "Docker"), ("pytest", "Pytest"),
     ("postman", "Postman"), ("selenium", "Selenium"), ("jira", "Jira"), ("confluence", "Confluence")],
]
GRID_COLS = max(len(row) for row in TECH_ROWS)

TILE, LOGO_SIZE, GLYPH_SIZE = 34, 24, 19
LABEL_FS, LABEL_LINE = 9.5, 11
CHAR_W = 5.35  # approx per-character width at LABEL_FS, system-ui font

def _wrap_label(label):
    """Split on the last space, or the last hyphen (kept with the first half) if there is
    no space -- e.g. 'scikit-learn' becomes 'scikit-' / 'learn'. Single words stay on one line."""
    if " " in label:
        return list(label.rsplit(" ", 1))
    if "-" in label:
        i = label.rindex("-")
        return [label[:i + 1], label[i + 1:]]
    return [label]

def _label_lines(label, width):
    """Only wrap the label if it genuinely doesn't fit its column."""
    if len(label) * CHAR_W + 6 <= width:
        return [label]
    return _wrap_label(label)

def _item_width(label):
    single_w = len(label) * CHAR_W + 6
    if single_w <= TILE:
        return TILE
    wrapped_w = max(len(l) for l in _wrap_label(label)) * CHAR_W + 6
    return max(TILE, round(wrapped_w))

def _col_widths(rows):
    cols = [TILE] * GRID_COLS
    for row in rows:
        for j, (_, label) in enumerate(row):
            cols[j] = max(cols[j], _item_width(label))
    return cols

# every tile reserves the same two-line label slot, whether its own label needs one line
# or two -- that uniform reservation, not the label's actual length, is what makes every
# row the same height and every icon sit on the same baseline.
ROW_H = 1 + TILE + LABEL_LINE * 2 + 4

def _tile(t, x, w, key, label, accent_i):
    """One tile at left edge `x`, centred within column width `w`."""
    cx = x + w / 2
    accent = t["star"] if accent_i % 2 == 0 else t["peri"]
    tx = cx - TILE / 2
    frag = f'<rect x="{tx+1.4:.1f}" y="3.4" width="{TILE}" height="{TILE}" rx="8" fill="{t["plinth_shadow"]}"/>'
    if LOGO_FILES[key]:
        frag += (f'<rect x="{tx:.1f}" y="1" width="{TILE}" height="{TILE}" rx="8" fill="{t["tile"]}" '
                  f'stroke="{t["tile_st"]}" stroke-opacity="{t["tile_st_o"]}"/>')
        frag += logo(key, round(cx - LOGO_SIZE / 2, 1), 1 + (TILE - LOGO_SIZE) / 2, LOGO_SIZE)
    else:
        frag += (f'<rect x="{tx:.1f}" y="1" width="{TILE}" height="{TILE}" rx="8" fill="{t["ctile"]}" '
                  f'fill-opacity="{t["ctile_o"]}" stroke="{t["ctile_st"]}" stroke-opacity="{t["ctile_st_o"]}" '
                  f'stroke-dasharray="2.5 2"/>')
        frag += glyph(key, cx - GLYPH_SIZE / 2, 1 + (TILE - GLYPH_SIZE) / 2, GLYPH_SIZE, t["glyph"], 1.55)
    frag += f'<rect x="{tx-.5:.1f}" y="0.5" width="2" height="2" fill="{accent}" shape-rendering="crispEdges"/>'
    ly = 1 + TILE + LABEL_LINE
    for l in _label_lines(label, w):
        frag += (f'<text x="{cx:.1f}" y="{ly:.1f}" text-anchor="middle" font-size="{LABEL_FS}" '
                  f'font-weight="600" fill="{t["label"]}">{esc(l)}</text>')
        ly += LABEL_LINE
    return frag

TARGET_W = 820  # desktop canvas: close to a real README content column

def techstack_matrix(t, mobile=False):
    """Column-aligned grid on desktop (every row shares the same column widths and row
    height, so icons and labels line up top to bottom); mobile wraps each row onto more
    lines at its own natural width instead of stretching gaps on a narrow screen."""
    if mobile:
        body, y, max_w = "", 4, 0
        for items in TECH_ROWS:
            x, line_x, accent_i = 8, 8, 0
            liney = y
            for key, label in items:
                w = _item_width(label)
                if x + w > 300 + 8 and x > 8:
                    liney += ROW_H + 14
                    x = 8
                body += f'<g transform="translate({x} {liney})">{_tile(t, 0, w, key, label, accent_i)}</g>'
                x += w + 10
                max_w = max(max_w, x)
                accent_i += 1
            y = liney + ROW_H + 16
        H = y - 16 + 6
        W = max_w + 8
        labels = "; ".join(l for row in TECH_ROWS for _, l in row)
        return svg_doc(round(W), round(H), body, f"Tech stack -- {labels}")

    cols = _col_widths(TECH_ROWS)
    natural = sum(cols)
    gap = max(14, (TARGET_W - 16 - natural) / (GRID_COLS - 1))

    body, y = "", 4
    for row in TECH_ROWS:
        x, accent_i = 8, 0
        for j, (key, label) in enumerate(row):
            w = cols[j]
            body += f'<g transform="translate({x:.1f} {y})">{_tile(t, 0, w, key, label, accent_i)}</g>'
            x += w + gap
            accent_i += 1
        y += ROW_H + 16
    H = y - 16 + 6

    labels = "; ".join(l for row in TECH_ROWS for _, l in row)
    return svg_doc(TARGET_W, round(H), body, f"Tech stack -- {labels}")


# ---------------------------------------------------------------- featured work
def _wrap_text(text, max_chars):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if len(trial) > max_chars and cur:
            lines.append(cur); cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines

# One small pixel-art mark per project -- the same crisp-rect / simple-path language as
# the About Me icons, not a stroke glyph like the Tech Stack tiles, so it reads as
# personality rather than another UI icon. No background tile, same as About Me.
def _icon_bolt(t, x, y, s):
    """EV charging: a small lightning bolt with one amber spark."""
    k = s / 22
    return (f'<g transform="translate({x} {y}) scale({k:.3f})">'
             f'<path d="M12 1.5 L4.5 12.5 H10 L9 20.5 L17.5 9 H12 Z" fill="{t["glyph"]}"/>'
             + pixel_star(15.5, 0, 1.1, t["star"], t["star_hi"]) + '</g>')

def _icon_tag(t, x, y, s):
    """Pricing: a small price tag with a punched hole."""
    k = s / 22
    return (f'<g transform="translate({x} {y}) scale({k:.3f})">'
             f'<path d="M2 3 H12 L20 11 L11 20 L2 20 Z" fill="{t["glyph"]}"/>'
             f'<circle cx="6.3" cy="7.3" r="2.1" fill="{t["star_hi"]}"/>'
             + pixel_star(15, 13, 1.0, t["star"], t["star_hi"]) + '</g>')

def _icon_agents(t, x, y, s):
    """Multi-agent: a hub routing to two agents, with a small verification check."""
    k = s / 22
    return (f'<g transform="translate({x} {y}) scale({k:.3f})">'
             f'<g stroke="{t["glyph"]}" stroke-width="1.6" stroke-opacity=".75">'
             f'<line x1="6" y1="7" x2="14" y2="4"/><line x1="6" y1="7" x2="13" y2="15"/></g>'
             f'<circle cx="6" cy="7" r="3.4" fill="{t["glyph"]}"/>'
             f'<circle cx="15" cy="3.2" r="2.6" fill="{t["glyph"]}" fill-opacity=".75"/>'
             f'<circle cx="14" cy="16" r="2.6" fill="{t["glyph"]}" fill-opacity=".75"/>'
             f'<circle cx="17.5" cy="18.5" r="4" fill="{t["star_hi"]}"/>'
             f'<path d="M15.6 18.6 l1.4 1.4 l2.3-2.5" fill="none" stroke="{t["star"]}" '
             f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></g>')

def _icon_retain(t, x, y, s):
    """Churn: a small person with an upward retention arrow."""
    k = s / 22
    return (f'<g transform="translate({x} {y}) scale({k:.3f})">'
             f'<circle cx="6.5" cy="6" r="3.4" fill="{t["glyph"]}"/>'
             f'<path d="M1 20 C1 14.5 4 12 6.5 12 C9 12 12 14.5 12 20 Z" fill="{t["glyph"]}"/>'
             f'<path d="M14 13 L18.5 8 M18.5 8 H14.8 M18.5 8 V11.7" fill="none" stroke="{t["star"]}" '
             f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></g>')

ICONS = {"bolt": _icon_bolt, "tag": _icon_tag, "agents": _icon_agents, "retain": _icon_retain}

def project_card(t, name, sentence, stack, icon, cta="View Project ↗", min_h=None):
    """One tile of the Featured Work grid -- compact, theme-aware, no keyword strip: the
    project name is the first thing read. `cta` is drawn as a label, not a real link (SVG
    can't carry one reliably once GitHub re-serves it); the README wraps the whole image
    in a single <a href> for projects that have one. Pass a note like "Private repository"
    instead of "View Project" for an unlinked project.

    Single sequential pass: every line is drawn against a running y-cursor, so height is
    however tall the real content needs -- nothing gets silently truncated to fit a
    pre-guessed box."""
    W, pad = 400, 20
    usable = W - 2 * pad
    icon_s, icon_gap = 26, 12
    title_x = pad + icon_s + icon_gap

    name_lines = _wrap_text(name, int((usable - icon_s - icon_gap) / 8.6))
    sentence_lines = _wrap_text(sentence, int(usable / 5.7))  # never truncated: a hard cap
                                                                # here would silently cut real
                                                                # content mid-sentence instead
    stack_line = "Tech: " + " · ".join(stack)
    stack_lines = _wrap_text(stack_line, int(usable / 4.9))

    body, y = "", 30
    body += ICONS[icon](t, pad, y - 21, icon_s)
    for i, l in enumerate(name_lines):
        body += f'<text x="{title_x}" y="{y}" font-size="17" font-weight="700" fill="{t["phrase"]}">{esc(l)}</text>'
        y += 21
    y = max(y, 9 + icon_s) + 12
    for l in sentence_lines:
        body += f'<text x="{pad}" y="{y}" font-size="12" fill="{t["sub"]}">{esc(l)}</text>'
        y += 17
    y += 11
    for l in stack_lines:
        body += f'<text x="{pad}" y="{y}" font-size="10" font-weight="500" letter-spacing=".2" ' \
                f'fill="{t["heading"]}" fill-opacity=".85">{esc(l)}</text>'
        y += 13
    y += 14
    H = max(y + 12, min_h or 0)  # a shared min_h keeps every card in the grid equal
                                   # height, so their CTAs line up along a common bottom edge

    if cta:
        cta_color = t["heading"] if "↗" in cta else t["sub"]
        cta_y = H - 20
        body += (f'<text x="{W-pad}" y="{cta_y}" text-anchor="end" font-size="11.5" font-weight="700" '
                  f'fill="{cta_color}">{esc(cta)}</text>')

    card = (f'<rect x="5" y="5" width="{W-10}" height="{H-10}" rx="16" fill="{t["card"]}" '
             f'fill-opacity="{t["card_o"]}" stroke="{t["card_st"]}" stroke-opacity="{t["card_st_o"]}"/>')

    title = " ".join(name_lines)
    return svg_doc(W, round(H), card + body, f"{title}. {sentence}")

# ---------------------------------------------------------------- About Me micro-icons
# Expressive, ~20-22px on the page, one per About paragraph. Real pixel-art (crisp-edge
# rects, banner palette), not the thin stroke-glyphs used in the Tech Stack tiles —
# these are meant to feel cute and to visibly belong to the banner. Decorative only:
# the copy stays real, selectable HTML text.
def about_icon_database(t):
    """QA / industry paragraph: filled pixel database + check badge + sparkle."""
    W = H = 24
    body = (
        f'<ellipse cx="9" cy="4.2" rx="7" ry="2.6" fill="{t["glyph"]}"/>'
        f'<rect x="2" y="4.2" width="14" height="10.2" fill="{t["glyph"]}"/>'
        f'<ellipse cx="9" cy="14.4" rx="7" ry="2.6" fill="{t["glyph"]}"/>'
        f'<path d="M2 9.3 A7 2.4 0 0 0 16 9.3" fill="none" stroke="{t["tile"]}" stroke-opacity=".55" stroke-width="1"/>'
        f'<circle cx="17.5" cy="16.5" r="6" fill="{t["star_hi"]}"/>'
        f'<path d="M14.6 16.6 l2 2 3.4-3.6" fill="none" stroke="{t["star"]}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        + pixel_star(17.5, -0.5, 1.3, t["star"], t["star_hi"])
    )
    return svg_doc(W, H, body, "QA, validation and data reliability background")

def about_icon_gradcap(t):
    """RWTH paragraph: graduation cap with tassel + two connected optimization nodes."""
    W = H = 24
    body = (
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
    return svg_doc(W, H, body, "RWTH Aachen: machine learning and optimization coursework")

def about_icon_dashboard(t):
    """'I build...' paragraph: dashboard blocks + connected path + AI sparkle."""
    W = H = 24
    bars = [(0, 13, 10), (5.5, 8, 15), (11, 15, 8)]
    body = "".join(
        f'<rect x="{x}" y="{y}" width="4.2" height="{23-y}" rx="1" fill="{t["glyph"]}" opacity="{op}"/>'
        for (x, y, h), op in zip(bars, (.55, .9, .7))
    )
    body += (
        f'<path d="M2 10.5 L7.5 5.5 L13 8.5" fill="none" stroke="{t["star"]}" stroke-width="1.3" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        + pixel_star(16.5, 1, 1.6, t["star"], t["star_hi"])
        + f'<circle cx="17.3" cy="7.8" r=".9" fill="{t["star_hi"]}"/>'
    )
    return svg_doc(W, H, body, "Analytics products and applied AI systems")

def about_icon_briefcase(t):
    """opportunity line: small briefcase + the one blush heart on the page."""
    W = H = 22
    body = (
        f'<path d="M8 3.5 h6 a1.6 1.6 0 0 1 1.6 1.6 v1.4 h-9.2 v-1.4 a1.6 1.6 0 0 1 1.6-1.6 z" '
        f'fill="none" stroke="{t["glyph"]}" stroke-width="1.4" stroke-linejoin="round"/>'
        f'<rect x="1.4" y="6.5" width="19.2" height="11.5" rx="2" fill="{t["glyph"]}"/>'
        f'<rect x="1.4" y="6.5" width="19.2" height="3.3" rx="2" fill="{t["glyph"]}" opacity=".55"/>'
        f'<rect x="9.4" y="9.8" width="3.2" height="3.2" rx=".6" fill="{t["star_hi"]}"/>'
        + pixel_heart(1.5, 0.5, 1.5)
    )
    return svg_doc(W, H, body, "Open to internship and working-student opportunities")

# ---------------------------------------------------------------- divider (theme-neutral)
def divider():
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

# ---------------------------------------------------------------- featured work content
# All four requested projects are shown, per this round's explicit instruction to render
# the CTA even where no working link exists yet and report it separately rather than
# omit the card. Only "url" set to a real *public* repo gets wrapped in a clickable <a>
# in the README -- a private or nonexistent repo would 404 for every visitor, so those
# show the "View Project" CTA as a label only. See build summary for what's missing.
PROJECTS = [
    dict(
        slug="project-ev-charging",
        name="EV Charging Expansion Intelligence",
        icon="bolt",
        sentence=("Regional analytics platform for identifying where public EV charging infrastructure may "
                   "be low relative to EV adoption across Germany. Uses official mobility and charging data "
                   "to compare regions, track validated KPIs, and support decision-making through dashboards."),
        stack=["Databricks", "PySpark", "Python", "SQL", "Power BI", "GitHub Actions"],
        url="https://github.com/vaish1101/ev-charging-expansion-intelligence",  # verified public
    ),
    dict(
        slug="project-watch-pricing",
        name="Automated Pricing and Market Analysis Tool",
        icon="tag",
        sentence=("Pricing and market analysis tool developed for a real vintage watch-parts business. Cleans "
                   "marketplace and inventory data, compares competitor pricing, and supports SKU-level "
                   "pricing decisions through an interactive analytics dashboard."),
        stack=["Python", "PostgreSQL", "SQL", "pandas", "Streamlit", "Statistical Analysis"],
        url=None,  # repo exists (vaish1101/vintage-watch-parts) but is private -- see build summary
    ),
    dict(
        slug="project-ai-agent",
        name="Multi-Agent AI Analytics Agent",
        icon="agents",
        sentence=("Multi-agent analytics system designed to answer business questions safely using governed "
                   "company data. A supervisor routes requests between analytical and knowledge/RAG agents, "
                   "deterministic tools perform the calculations, and a verification layer checks metric "
                   "definitions, grounding, and unsupported claims before the final response is returned."),
        stack=["Python", "LangGraph", "LLM APIs", "RAG", "PostgreSQL/pgvector", "Pydantic", "FastAPI"],
        url=None,  # no matching repository found on the account -- see build summary
    ),
    dict(
        slug="project-churn",
        name="Customer Churn Prediction and Retention",
        icon="retain",
        sentence=("Predictive churn analysis project focused on identifying customers at risk of leaving, "
                   "explaining the main drivers, and supporting retention decisions. Combines classification, "
                   "calibration, explainability, and business-facing outputs for actionable decision-making."),
        stack=["Python", "pandas", "scikit-learn", "Calibration", "Explainability", "Dashboarding"],
        url=None,  # no matching repository found on the account -- see build summary
    ),
]

_SFNS = "/System/Library/Fonts/SFNS.ttf"
_REF = 200  # measure at a fixed large size and scale down -- avoids per-size rounding error
_font_ref = ImageFont.truetype(_SFNS, _REF)
# SFNS.ttf renders noticeably narrower than what Chrome actually lays out for the
# "-apple-system" stack (measured via real getBoundingClientRect() in Chrome headless: a
# 12.5px regular sentence came out 341px vs 301.5px from this font, and a 15px bold title
# came out 258.6px vs 221.9px regular-weight). Both factors below are calibrated from
# those measurements with a small safety margin on top -- rounded up, never down, so a
# wrap decision errs toward an extra line rather than an overflowing one.
_BASE_FACTOR = 1.14   # regular-weight correction vs SFNS.ttf's own metrics
_BOLD_FACTOR = 1.06   # additional correction for bold weight (SFNS.ttf has no bold instance)

def _text_w(s, size, bold=False):
    w = _font_ref.getlength(s) * (size / _REF) * _BASE_FACTOR
    return w * _BOLD_FACTOR if bold else w

def _wrap_px(text, max_px, size, bold=False):
    """Wraps by measured pixel width (not a character-count guess), so a line can never run
    past `max_px` regardless of how word lengths happen to fall -- the char-count approach
    used elsewhere in this file was verified to overflow on real sentences."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if _text_w(trial, size, bold) > max_px and cur:
            lines.append(cur); cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- Featured Work v2
# Part-2 refinement: three card DESIGN variations to compare before picking one, plus
# four redesigned project icons. None of this is wired into __main__ / PROJECTS yet --
# run with `python3 build_cards.py --preview-variants` to render comparison SVGs only,
# without touching the production project-*.svg files the live README references.

def _icon_ev_v2(t, x, y, s):
    """EV charging: charger body with a bolt cut-out, a small map/broadcast signal, one spark."""
    k = s / 24
    return (f'<g transform="translate({x} {y}) scale({k:.3f})">'
             f'<rect x="2" y="4" width="10" height="17" rx="2.4" fill="{t["glyph"]}"/>'
             f'<path d="M8.6 6.6 L5.2 13.4 H7.7 L6.6 18.6 L11.3 11.6 H8.7 Z" fill="{t["card"]}" fill-opacity=".92"/>'
             f'<path d="M14.4 5.4 a5.2 5.2 0 0 1 0 9" fill="none" stroke="{t["glyph"]}" stroke-width="1.3" '
             f'stroke-linecap="round" stroke-opacity=".8"/>'
             f'<path d="M16.6 3 a8.3 8.3 0 0 1 0 13.8" fill="none" stroke="{t["glyph"]}" stroke-width="1.1" '
             f'stroke-linecap="round" stroke-opacity=".4"/>'
             + pixel_star(15.5, 16.5, 1.1, t["star"], t["star_hi"]) + '</g>')

def _icon_watch_v2(t, x, y, s):
    """Pricing: a small watch-part gear + a price tag carrying a trend line, not a $ sign."""
    k = s / 24
    teeth = [(13.4, 8), (10.3, 2.6), (4.1, 2.6), (1, 8), (4.1, 13.4), (10.3, 13.4)]
    teeth_svg = "".join(f'<rect x="{tx-1.1:.1f}" y="{ty-1.1:.1f}" width="2.2" height="2.2" rx=".4" fill="{t["glyph"]}"/>' for tx, ty in teeth)
    return (f'<g transform="translate({x} {y}) scale({k:.3f})">'
             + teeth_svg +
             f'<circle cx="7.2" cy="8" r="5.1" fill="{t["glyph"]}"/>'
             f'<circle cx="7.2" cy="8" r="2" fill="{t["card"]}" fill-opacity=".92"/>'
             f'<path d="M14.5 12.2 H19.6 L22.5 15.2 L19.6 18.2 H14.5 Z" fill="{t["star"]}" opacity=".92"/>'
             f'<circle cx="16.4" cy="15.2" r="1" fill="{t["star_hi"]}"/>'
             f'<path d="M15.6 17 L17.3 15.3 L18.7 16.4 L20.6 14.2" fill="none" stroke="{t["star_hi"]}" '
             f'stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></g>')

def _icon_agents_v2(t, x, y, s):
    """Multi-agent: a supervisor hub branching into three specialist nodes that converge
    into one verification check -- reads as orchestration, not a generic bot/sparkle."""
    k = s / 24
    nodes = [(5, 10.5), (12, 13), (19, 10.5)]
    lines_down = "".join(f'<line x1="12" y1="4.6" x2="{nx}" y2="{ny-2.4}"/>' for nx, ny in nodes)
    lines_conv = "".join(f'<line x1="{nx}" y1="{ny+2.2}" x2="12" y2="19.4"/>' for nx, ny in nodes)
    node_circles = "".join(f'<circle cx="{nx}" cy="{ny}" r="2.4" fill="{t["glyph"]}" fill-opacity=".8"/>' for nx, ny in nodes)
    return (f'<g transform="translate({x} {y}) scale({k:.3f})">'
             f'<g stroke="{t["glyph"]}" stroke-width="1.3" stroke-opacity=".55">{lines_down}{lines_conv}</g>'
             f'<circle cx="12" cy="4.2" r="3" fill="{t["glyph"]}"/>'
             + node_circles +
             f'<circle cx="12" cy="20.6" r="4" fill="{t["star_hi"]}"/>'
             f'<path d="M10 20.6 l1.6 1.6 l2.6-2.9" fill="none" stroke="{t["star"]}" '
             f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></g>')

def _icon_churn_v2(t, x, y, s):
    """Churn: a person, a short downward risk trend, and a curved retention arrow looping back up."""
    k = s / 24
    return (f'<g transform="translate({x} {y}) scale({k:.3f})">'
             f'<circle cx="6.2" cy="5.6" r="3.2" fill="{t["glyph"]}"/>'
             f'<path d="M1 20 C1 14.7 3.8 12.3 6.2 12.3 C8.6 12.3 11.4 14.7 11.4 20 Z" fill="{t["glyph"]}"/>'
             f'<path d="M13.4 6.4 L16.6 8.6 L15.4 11.6 L18.4 13.8" fill="none" stroke="{t["star"]}" '
             f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'
             f'<path d="M13.6 19.8 C18.4 20.4 20.8 17.4 19.6 13.6" fill="none" stroke="{t["glyph"]}" '
             f'stroke-width="1.6" stroke-linecap="round"/>'
             f'<path d="M17 12.6 L19.9 13.2 L19 16" fill="none" stroke="{t["glyph"]}" stroke-width="1.6" '
             f'stroke-linecap="round" stroke-linejoin="round"/></g>')

ICONS_V2 = {"ev": _icon_ev_v2, "watch": _icon_watch_v2, "agents2": _icon_agents_v2, "churn2": _icon_churn_v2}

def variant_a_pixel_editorial(t, name, sentence, stack, icon, cta="View Project ↗", min_h=None):
    """A -- Pixel Editorial: almost-borderless card, generous whitespace, one small sparkle,
    the icon carries the personality and everything else stays quiet and modern-editorial."""
    W, pad = 400, 24
    usable = W - 2 * pad
    icon_s, icon_gap = 24, 12
    title_x = pad + icon_s + icon_gap

    name_lines = _wrap_px(name, usable - icon_s - icon_gap, 19, bold=True)
    sentence_lines = _wrap_px(sentence, usable, 12.5)
    stack_line = "Tech: " + " · ".join(stack)
    stack_lines = _wrap_px(stack_line, usable, 10, bold=True)

    body, y = "", 32
    body += ICONS_V2[icon](t, pad, y - 20, icon_s)
    last_w = 0
    for l in name_lines:
        body += f'<text x="{title_x}" y="{y}" font-size="19" font-weight="700" letter-spacing="-.1" fill="{t["phrase"]}">{esc(l)}</text>'
        last_w = _text_w(l, 19, bold=True)
        y += 24
    body += pixel_star(min(title_x + last_w + 8, W - pad - 6), y - 34, 1.1, t["star"], t["star_hi"])
    y = max(y, 12 + icon_s) + 16
    for l in sentence_lines:
        body += f'<text x="{pad}" y="{y}" font-size="12.5" fill="{t["sub"]}">{esc(l)}</text>'
        y += 19
    y += 12
    for l in stack_lines:
        body += f'<text x="{pad}" y="{y}" font-size="10" font-weight="500" fill="{t["heading"]}" fill-opacity=".85">{esc(l)}</text>'
        y += 13
    y += 16
    H = max(y + 12, min_h or 0)

    if cta:
        cta_y = H - 22
        body += (f'<text x="{W-pad}" y="{cta_y}" text-anchor="end" font-size="11.5" font-weight="700" '
                  f'fill="{t["heading"]}">{esc(cta)}</text>')

    corner = (f'<rect x="9" y="9" width="2" height="2" fill="{t["peri"]}" fill-opacity=".55" shape-rendering="crispEdges"/>'
              f'<rect x="{W-11}" y="9" width="2" height="2" fill="{t["peri"]}" fill-opacity=".55" shape-rendering="crispEdges"/>')
    card = (f'<rect x="5" y="5" width="{W-10}" height="{H-10}" rx="14" fill="{t["card"]}" '
             f'fill-opacity="{t["card_o"]}" stroke="{t["card_st"]}" stroke-opacity=".55"/>' + corner)

    return svg_doc(W, round(H), card + body, f"{' '.join(name_lines)}. {sentence}")


def variant_b_pixel_title_tab(t, name, sentence, stack, icon, cta="View Project ↗", min_h=None):
    """B -- Pixel Title Tab: a small tinted title tab (dusk indigo -> lavender, peach pixel
    corners) sits top-left, closest to the banner's visual language; the rest of the card
    stays clean and uncluttered underneath it."""
    W, pad = 400, 22
    usable = W - 2 * pad
    icon_s = 20
    title_x = 14 + icon_s + 9

    max_tab_w = W - 60
    title_budget = max_tab_w - title_x - 20  # room left for the title inside the tab before it must wrap
    name_lines = _wrap_px(name, title_budget, 15, bold=True) if _text_w(name, 15, bold=True) > title_budget \
        else [name]
    tab_h = 34 if len(name_lines) == 1 else 34 + 18 * (len(name_lines) - 1)
    widest_line = max(_text_w(l, 15, bold=True) for l in name_lines)
    name_w = min(max(title_x + widest_line + 20, 90), max_tab_w)

    sentence_lines = _wrap_px(sentence, usable, 12.5)
    stack_line = "Tech: " + " · ".join(stack)
    stack_lines = _wrap_px(stack_line, usable, 10, bold=True)

    body = (f'<defs><linearGradient id="tab" x1="0" x2="1">'
            f'<stop offset="0" stop-color="{t["ai_a"]}" stop-opacity="1"/>'
            f'<stop offset="1" stop-color="{t["ai_b"]}" stop-opacity="1"/></linearGradient></defs>')
    body += (f'<path d="M0 6 a6 6 0 0 1 6-6 H{name_w-6:.0f} a6 6 0 0 1 6 6 V{tab_h} H0 Z" '
              f'fill="url(#tab)" stroke="{t["ai_st"]}" stroke-opacity="{t["ai_st_o"]}"/>')
    body += (f'<rect x="0" y="4" width="2" height="2" fill="{t["star"]}" shape-rendering="crispEdges"/>'
              f'<rect x="{name_w-8:.0f}" y="4" width="2" height="2" fill="{t["star"]}" shape-rendering="crispEdges"/>')
    body += ICONS_V2[icon](t, 14, 9, icon_s)
    ty = 24
    for l in name_lines:
        body += f'<text x="{title_x}" y="{ty}" font-size="15" font-weight="700" fill="{t["phrase"]}">{esc(l)}</text>'
        ty += 18
    body += pixel_star(name_w - 2, -4, 1.3, t["star"], t["star_hi"])

    y = tab_h + 26
    for l in sentence_lines:
        body += f'<text x="{pad}" y="{y}" font-size="12.5" fill="{t["sub"]}">{esc(l)}</text>'
        y += 18
    y += 12
    for l in stack_lines:
        body += f'<text x="{pad}" y="{y}" font-size="10" font-weight="500" fill="{t["heading"]}" fill-opacity=".85">{esc(l)}</text>'
        y += 13
    y += 16
    H = max(y + 12, min_h or 0)

    if cta:
        cta_y = H - 20
        body += (f'<text x="{W-pad}" y="{cta_y}" text-anchor="end" font-size="11.5" font-weight="700" '
                  f'fill="{t["heading"]}">{esc(cta)}</text>')

    card = (f'<rect x="5" y="5" width="{W-10}" height="{H-10}" rx="14" fill="{t["card"]}" '
             f'fill-opacity="{t["card_o"]}" stroke="{t["card_st"]}" stroke-opacity="{t["card_st_o"]}"/>')

    return svg_doc(W, round(H), card + body, f"{name}. {sentence}")


def variant_c_project_shelf(t, name, sentence, stack, icon, cta="View Project ↗", min_h=None):
    """C -- Project Shelf: a large icon anchors a left column, title/description/tech/CTA
    sit in a right column separated by a thin pixel-underline, reading as a product/profile
    card rather than a horizontal resume row."""
    W, pad = 400, 22
    icon_col = 74
    icon_s = 40
    text_x = pad + icon_col
    usable = W - text_x - pad

    name_lines = _wrap_px(name, usable, 17.5, bold=True)
    sentence_lines = _wrap_px(sentence, usable, 12.5)
    stack_line = "Tech: " + " · ".join(stack)
    stack_lines = _wrap_px(stack_line, usable, 10, bold=True)

    body = (f'<rect x="{pad-8}" y="24" width="{icon_col-4}" height="{icon_col-4}" rx="16" fill="{t["ctile"]}" '
             f'fill-opacity="{t["ctile_o"]}" stroke="{t["ctile_st"]}" stroke-opacity="{t["ctile_st_o"]}"/>')
    body += ICONS_V2[icon](t, pad + (icon_col - 4 - icon_s) / 2 - 8, 24 + (icon_col - 4 - icon_s) / 2, icon_s)

    y = 42
    for l in name_lines:
        body += f'<text x="{text_x}" y="{y}" font-size="17.5" font-weight="700" fill="{t["phrase"]}">{esc(l)}</text>'
        y += 22
    y += 4
    body += f'<rect x="{text_x}" y="{y-14:.0f}" width="30" height="2" fill="{t["star"]}"/>'
    y += 10
    for l in sentence_lines:
        body += f'<text x="{text_x}" y="{y}" font-size="12.5" fill="{t["sub"]}">{esc(l)}</text>'
        y += 18
    y += 11
    for l in stack_lines:
        body += f'<text x="{text_x}" y="{y}" font-size="10" font-weight="500" fill="{t["heading"]}" fill-opacity=".85">{esc(l)}</text>'
        y += 13
    y += 16
    icon_bottom = 24 + (icon_col - 4) + 12
    H = max(y + 12, icon_bottom, min_h or 0)

    if cta:
        cta_y = H - 20
        body += (f'<text x="{W-pad}" y="{cta_y}" text-anchor="end" font-size="11.5" font-weight="700" '
                  f'fill="{t["heading"]}">{esc(cta)}</text>')

    card = (f'<rect x="5" y="5" width="{W-10}" height="{H-10}" rx="16" fill="{t["card"]}" '
             f'fill-opacity="{t["card_o"]}" stroke="{t["card_st"]}" stroke-opacity="{t["card_st_o"]}"/>')

    return svg_doc(W, round(H), card + body, f"{' '.join(name_lines)}. {sentence}")

VARIANTS = {"a": variant_a_pixel_editorial, "b": variant_b_pixel_title_tab, "c": variant_c_project_shelf}

# Updated Part-2 project copy (not yet applied to the live PROJECTS list / README).
PROJECTS_V2 = [
    dict(
        slug="ev-charging", name="EV Charging Expansion Intelligence", icon="ev",
        sentence=("Regional analytics platform for identifying where public EV charging infrastructure may be "
                   "insufficient relative to EV adoption across Germany. Uses official mobility and charging "
                   "data to compare regions, monitor validated KPIs, and support infrastructure planning "
                   "through Databricks and Power BI dashboards."),
        stack=["Databricks", "PySpark", "Python", "SQL", "Power BI", "GitHub Actions"],
    ),
    dict(
        slug="watch-pricing", name="Automated Pricing and Market Analysis Tool", icon="watch",
        sentence=("Pricing and market analysis tool for a real vintage watch-parts business. Cleans inventory "
                   "and marketplace data, benchmarks competitor pricing, and generates SKU-level pricing "
                   "guidance through an interactive analytics dashboard."),
        stack=["Python", "PostgreSQL", "SQL", "pandas", "Streamlit", "Statistical Analysis"],
    ),
    dict(
        slug="ai-agent", name="Multi-Agent AI Analytics Agent", icon="agents2",
        sentence=("Multi-agent analytics system for answering business questions safely from governed company "
                   "data. A supervisor routes requests across analytical and knowledge/RAG agents, "
                   "deterministic tools calculate results, and a verification layer checks grounding and "
                   "numerical correctness before returning the final response."),
        stack=["Python", "LangGraph", "LLM APIs", "RAG", "pgvector", "Pydantic", "FastAPI"],
    ),
    dict(
        slug="churn", name="Customer Churn Prediction and Retention", icon="churn2",
        sentence=("Predictive churn analysis for identifying customers at risk of leaving, understanding the "
                   "main drivers, and prioritizing retention action. Combines classification, probability "
                   "calibration, model explainability, and business-facing outputs to support customer "
                   "retention decisions."),
        stack=["Python", "pandas", "scikit-learn", "Logistic Regression", "SVM", "Model Evaluation"],
    ),
]

# ---------------------------------------------------------------- Featured Work v3
# Round 2 of Part 2: A/B/C read as boxed UI components, not an extension of the banner
# -- too tall, icons too dominant, borders/tabs doing too much work. This round targets
# the banner directly: thin full-opacity-free outlines, a small stepped-pixel corner
# cut (the banner's actual corner motif, confirmed by inspecting assets/banner.png),
# 4-point peach sparkles, near-transparent card surface, and much smaller icons that
# behave like inline sprites next to the title rather than standalone artwork.

def _icon_ev_v3(t, x, y, s):
    """EV charging: tiny charger + 2px map pin + a short signal arc. No background."""
    k = s / 24
    return (f'<g transform="translate({x} {y}) scale({k:.3f})">'
             f'<rect x="2.5" y="5" width="8" height="14" rx="2" fill="{t["glyph"]}"/>'
             f'<path d="M7.7 7.3 L4.8 12.7 H6.9 L6 17.3 L10 11.7 H7.9 Z" fill="{t["card"]}" fill-opacity=".9"/>'
             f'<circle cx="16.5" cy="7" r="1.6" fill="{t["star"]}"/>'
             f'<path d="M16.5 8.6 L14.6 12.6 M16.5 8.6 L18.4 12.6 M16.5 8.6 V13.4" fill="none" '
             f'stroke="{t["star"]}" stroke-width="1" stroke-linecap="round" opacity=".8"/>'
             f'<path d="M13.5 16.4 a4 4 0 0 1 6 0" fill="none" stroke="{t["glyph"]}" stroke-width="1.1" '
             f'stroke-linecap="round" opacity=".55"/></g>')

def _icon_watch_v3(t, x, y, s):
    """Pricing: a tiny watch face (not a gear) + a small tag + a short trend line."""
    k = s / 24
    return (f'<g transform="translate({x} {y}) scale({k:.3f})">'
             f'<circle cx="8" cy="9" r="6.4" fill="none" stroke="{t["glyph"]}" stroke-width="1.5"/>'
             f'<path d="M8 9 L8 4.8 M8 9 L11.2 10.4" fill="none" stroke="{t["glyph"]}" stroke-width="1.3" stroke-linecap="round"/>'
             f'<rect x="6.5" y="0.8" width="3" height="1.6" rx=".5" fill="{t["glyph"]}"/>'
             f'<path d="M15.5 12.4 H20 L22.5 15 L20 17.6 H15.5 Z" fill="{t["star"]}" opacity=".92"/>'
             f'<circle cx="17.2" cy="15" r=".9" fill="{t["star_hi"]}"/>'
             f'<path d="M14.5 6.5 L16.7 5.2 L18.6 6.4 L21 3.6" fill="none" stroke="{t["glyph"]}" '
             f'stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round" opacity=".7"/></g>')

def _icon_agents_v3(t, x, y, s):
    """Multi-agent: a glowing central node, two smaller nodes, a tiny verification sparkle."""
    k = s / 24
    return (f'<g transform="translate({x} {y}) scale({k:.3f})">'
             f'<circle cx="9" cy="8" r="5.2" fill="{t["glyph"]}" fill-opacity=".14"/>'
             f'<g stroke="{t["glyph"]}" stroke-width="1.1" stroke-opacity=".6">'
             f'<line x1="9" y1="8" x2="2.6" y2="14.2"/><line x1="9" y1="8" x2="15.4" y2="14.2"/></g>'
             f'<circle cx="9" cy="8" r="2.6" fill="{t["glyph"]}"/>'
             f'<circle cx="2.6" cy="15.2" r="1.7" fill="{t["glyph"]}" fill-opacity=".8"/>'
             f'<circle cx="15.4" cy="15.2" r="1.7" fill="{t["glyph"]}" fill-opacity=".8"/>'
             + pixel_star(9, -2, 1, t["star"], t["star_hi"]) +
             f'<path d="M17.5 8.5 l1.1 1.1 l1.9-2.1" fill="none" stroke="{t["star"]}" stroke-width="1.3" '
             f'stroke-linecap="round" stroke-linejoin="round"/></g>')

def _icon_churn_v3(t, x, y, s):
    """Churn: small person, a short falling line, a curved retention arrow looping back up."""
    k = s / 24
    return (f'<g transform="translate({x} {y}) scale({k:.3f})">'
             f'<circle cx="6" cy="5.4" r="2.9" fill="{t["glyph"]}"/>'
             f'<path d="M1.6 17.5 C1.6 12.9 3.8 10.8 6 10.8 C8.2 10.8 10.4 12.9 10.4 17.5 Z" fill="{t["glyph"]}"/>'
             f'<path d="M13 6.4 L15.6 8.2 L14.6 10.8" fill="none" stroke="{t["star"]}" stroke-width="1.2" '
             f'stroke-linecap="round" stroke-linejoin="round"/>'
             f'<path d="M12.6 16.8 C16.4 17.3 18.3 14.8 17.3 11.7" fill="none" stroke="{t["glyph"]}" '
             f'stroke-width="1.3" stroke-linecap="round"/>'
             f'<path d="M15.1 10.9 L17.6 11.4 L16.9 13.7" fill="none" stroke="{t["glyph"]}" stroke-width="1.3" '
             f'stroke-linecap="round" stroke-linejoin="round"/></g>')

ICONS_V3 = {"ev": _icon_ev_v3, "watch": _icon_watch_v3, "agents2": _icon_agents_v3, "churn2": _icon_churn_v3}

def _stepped_corner(x, y, px, color, corner="tl", opacity=.65):
    """The banner's own corner motif (a small stepped/notched cut), not a heavy bracket --
    two shrinking pixel blocks stepping in from the corner, reused verbatim from the tile
    accent already used elsewhere in this file."""
    dx = -1 if corner in ("tl", "bl") else 1
    dy = -1 if corner in ("tl", "tr") else 1
    cells = [(0, 0), (1 * dx, 0), (0, 1 * dy)]
    r = "".join(f'<rect x="{x+cx*px:.2f}" y="{y+cy*px:.2f}" width="{px}" height="{px}"/>' for cx, cy in cells)
    return f'<g fill="{color}" fill-opacity="{opacity}" shape-rendering="crispEdges">{r}</g>'

def _pixel_underline(x, y, color):
    """3 small stepped blocks fading into a thin line -- the 'pixel underline' motif for variant E."""
    blocks = "".join(f'<rect x="{x+i*5:.1f}" y="{y-1.3:.1f}" width="3" height="2.6" fill="{color}" '
                      f'fill-opacity="{0.85 - i*0.18:.2f}" shape-rendering="crispEdges"/>' for i in range(3))
    return blocks + f'<rect x="{x+15}" y="{y-0.5:.1f}" width="26" height="1" fill="{color}" fill-opacity=".35"/>'

def variant_d_pixel_frame(t, name, sentence, stack, icon, cta="View Project ↗", min_h=None):
    """D -- Pixel Frame: icon + title + CTA share one top row, description runs the full
    card width below, thin barely-there border with stepped-pixel corners instead of a
    full heavy outline, one small sparkle. Compact -- target ~160-185px tall."""
    W, pad = 406, 14
    usable = W - 2 * pad
    icon_s, icon_gap = 20, 7
    title_x = pad + icon_s + icon_gap

    cta_w = _text_w(cta, 11, bold=True) if cta else 0
    title_budget = usable - icon_s - icon_gap - (cta_w + 12 if cta else 0)
    name_line = name if _text_w(name, 15.5, bold=True) <= title_budget else None
    name_lines = [name_line] if name_line else _wrap_px(name, usable - icon_s - icon_gap, 15.5, bold=True)

    sentence_lines = _wrap_px(sentence, usable, 13.5)
    stack_line = "Tech: " + " · ".join(stack)
    stack_lines = _wrap_px(stack_line, usable, 12, bold=True)

    body, y = "", 20
    body += ICONS_V3[icon](t, pad, y - 15, icon_s)
    body += f'<text x="{title_x}" y="{y}" font-size="15.5" font-weight="600" fill="{t["phrase"]}">{esc(name_lines[0])}</text>'
    if cta:
        body += (f'<text x="{W-pad}" y="{y}" text-anchor="end" font-size="11" font-weight="700" '
                  f'fill="{t["heading"]}">{esc(cta)}</text>')
    y += 19
    for l in name_lines[1:]:
        body += f'<text x="{title_x}" y="{y}" font-size="15.5" font-weight="600" fill="{t["phrase"]}">{esc(l)}</text>'
        y += 19
    y = max(y, 8 + icon_s) + 7
    for l in sentence_lines:
        body += f'<text x="{pad}" y="{y}" font-size="13.5" fill="{t["sub"]}">{esc(l)}</text>'
        y += 17
    y += 6
    for l in stack_lines:
        body += f'<text x="{pad}" y="{y}" font-size="12" font-weight="500" fill="{t["heading"]}" fill-opacity=".82">{esc(l)}</text>'
        y += 14
    y += 8
    H = max(y, min_h or 0)

    corners = (_stepped_corner(pad - 8, 7, 2, t["peri"], "tl")
               + _stepped_corner(W - pad + 6, H - 9, 2, t["star"], "br"))
    sparkle = pixel_star(W - pad - 4, H - 16, 1, t["star"], t["star_hi"])
    card = (f'<rect x="3" y="3" width="{W-6}" height="{H-6}" rx="11" fill="{t["card"]}" '
             f'fill-opacity="{t["card_o"]}" stroke="{t["card_st"]}" stroke-opacity=".4" stroke-width="1"/>')

    return svg_doc(W, round(H), card + corners + sparkle + body, f"{' '.join(name_lines)}. {sentence}")


def variant_e_pixel_underline(t, name, sentence, stack, icon, cta="View Project ↗", min_h=None):
    """E -- Pixel Underline: no full border at all, just a soft wash; the card is defined
    by spacing and a small stepped pixel underline beneath the title instead of any box."""
    W, pad = 406, 16
    usable = W - 2 * pad
    icon_s, icon_gap = 20, 7
    title_x = pad + icon_s + icon_gap

    name_lines = _wrap_px(name, usable - icon_s - icon_gap, 15.5, bold=True)
    sentence_lines = _wrap_px(sentence, usable, 13.5)
    stack_line = "Tech: " + " · ".join(stack)
    stack_lines = _wrap_px(stack_line, usable, 12, bold=True)

    body, y = "", 19
    body += ICONS_V3[icon](t, pad, y - 14, icon_s)
    for l in name_lines:
        body += f'<text x="{title_x}" y="{y}" font-size="15.5" font-weight="600" fill="{t["phrase"]}">{esc(l)}</text>'
        y += 18
    y += 3
    body += _pixel_underline(title_x, y, t["star"])
    y = max(y + 9, 6 + icon_s + 13)
    for l in sentence_lines:
        body += f'<text x="{pad}" y="{y}" font-size="13.5" fill="{t["sub"]}">{esc(l)}</text>'
        y += 16.5
    y += 5
    for l in stack_lines:
        body += f'<text x="{pad}" y="{y}" font-size="12" font-weight="500" fill="{t["heading"]}" fill-opacity=".82">{esc(l)}</text>'
        y += 13.5
    y += 8
    H = max(y + 6, min_h or 0)

    if cta:
        body += (f'<text x="{W-pad}" y="{H-10}" text-anchor="end" font-size="11" font-weight="700" '
                  f'fill="{t["heading"]}">{esc(cta)}</text>')

    wash = f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="10" fill="{t["card"]}" fill-opacity="{t["card_o"]}"/>'

    return svg_doc(W, round(H), wash + body, f"{' '.join(name_lines)}. {sentence}")


def variant_f_pixel_corner_float(t, name, sentence, stack, icon, cta="View Project ↗", min_h=None):
    """F -- Pixel Corner Float: no visible border at all; only two opposing stepped-pixel
    corners (top-left / bottom-right) imply the card boundary, closest to the banner's own
    corner-cut motif."""
    W, pad = 406, 16
    usable = W - 2 * pad
    icon_s, icon_gap = 20, 7
    title_x = pad + icon_s + icon_gap

    name_lines = _wrap_px(name, usable - icon_s - icon_gap, 15.5, bold=True)
    sentence_lines = _wrap_px(sentence, usable, 13.5)
    stack_line = "Tech: " + " · ".join(stack)
    stack_lines = _wrap_px(stack_line, usable, 12, bold=True)

    body, y = "", 19
    body += ICONS_V3[icon](t, pad, y - 14, icon_s)
    for l in name_lines:
        body += f'<text x="{title_x}" y="{y}" font-size="15.5" font-weight="600" fill="{t["phrase"]}">{esc(l)}</text>'
        y += 18
    y = max(y, 6 + icon_s) + 6
    for l in sentence_lines:
        body += f'<text x="{pad}" y="{y}" font-size="13.5" fill="{t["sub"]}">{esc(l)}</text>'
        y += 16.5
    y += 5
    for l in stack_lines:
        body += f'<text x="{pad}" y="{y}" font-size="12" font-weight="500" fill="{t["heading"]}" fill-opacity=".82">{esc(l)}</text>'
        y += 13.5
    y += 8
    H = max(y + 6, min_h or 0)

    if cta:
        body += (f'<text x="{W-pad-8}" y="{H-10}" text-anchor="end" font-size="11" font-weight="700" '
                  f'fill="{t["heading"]}">{esc(cta)}</text>')
        body += _stepped_corner(W - pad + 6, H - 16, 2, t["star"], "br")

    corners = _stepped_corner(pad - 9, 7, 2.2, t["peri"], "tl")
    wash = f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="10" fill="{t["card"]}" fill-opacity="{t["card_o"]}"/>'

    return svg_doc(W, round(H), wash + corners + body, f"{' '.join(name_lines)}. {sentence}")

VARIANTS_V2 = {"d": variant_d_pixel_frame, "e": variant_e_pixel_underline, "f": variant_f_pixel_corner_float}

# ---------------------------------------------------------------- Featured Work v4 (chips)
# Round 3 of Part 2: refines an externally-generated reference card (structured, chip-based
# tech stack, strong title, CTA bottom-right) with the top project-id strip, category line
# and bottom stat row stripped out per instruction, and the frame/palette pulled back to
# this file's existing soft pastel tokens instead of the reference's neon glow.

def _chips(items, x0, y0, max_w, t, font_size=11):
    """Lays out tech-stack pills left-to-right, wrapping to a new row when one would run
    past max_w. Returns (svg_fragment, total_height_used)."""
    pad_x, h, gap, row_gap = 9, 21, 6, 7
    cur_x, cur_y = x0, y0
    frag = ""
    for it in items:
        w = _text_w(it, font_size, bold=True) + pad_x * 2
        if cur_x + w > x0 + max_w and cur_x > x0:
            cur_x = x0
            cur_y += h + row_gap
        frag += (f'<rect x="{cur_x:.1f}" y="{cur_y:.1f}" width="{w:.1f}" height="{h}" rx="{h/2:.1f}" '
                  f'fill="{t["ctile"]}" fill-opacity="{t["ctile_o"]}" stroke="{t["ctile_st"]}" '
                  f'stroke-opacity="{t["ctile_st_o"]}"/>')
        frag += (f'<text x="{cur_x+w/2:.1f}" y="{cur_y+h/2+3.6:.1f}" text-anchor="middle" '
                  f'font-size="{font_size}" font-weight="600" fill="{t["heading"]}">{esc(it)}</text>')
        cur_x += w + gap
    total_h = (cur_y - y0) + h
    return frag, total_h

def variant_g_chips(t, name, sentence, stack, icon, cta="View Project ↗", min_h=None):
    """G -- refines the external reference: icon + title, description, chip-based tech
    stack, CTA bottom-right. No top id strip, no category line, no stat row -- those were
    the three things explicitly called out for removal. Thin single-outline frame with two
    stepped-pixel corners and one sparkle, in this file's existing palette tokens rather
    than the reference's neon glow."""
    W, pad = 406, 18
    usable = W - 2 * pad
    icon_s, icon_gap = 24, 9
    title_x = pad + icon_s + icon_gap

    name_lines = _wrap_px(name, usable - icon_s - icon_gap, 16.5, bold=True)
    sentence_lines = _wrap_px(sentence, usable, 13.5)

    body, y = "", 24
    body += ICONS_V3[icon](t, pad, y - 18, icon_s)
    for l in name_lines:
        body += f'<text x="{title_x}" y="{y}" font-size="16.5" font-weight="600" fill="{t["phrase"]}">{esc(l)}</text>'
        y += 20
    y = max(y, 8 + icon_s) + 10
    for l in sentence_lines:
        body += f'<text x="{pad}" y="{y}" font-size="13.5" fill="{t["sub"]}">{esc(l)}</text>'
        y += 17
    y += 10
    chip_frag, chip_h = _chips(stack, pad, y - 15, usable, t, font_size=11)
    body += chip_frag
    y += chip_h - 15 + 12
    H = max(y + 22, min_h or 0)

    if cta:
        body += (f'<text x="{W-pad}" y="{H-16}" text-anchor="end" font-size="11.5" font-weight="700" '
                  f'fill="{t["heading"]}">{esc(cta)}</text>')

    corners = (_stepped_corner(pad - 10, 8, 2.2, t["peri"], "tl")
               + _stepped_corner(W - pad + 8, H - 10, 2.2, t["star"], "br"))
    sparkle = pixel_star(W - pad - 6, H - 24, 1, t["star"], t["star_hi"])
    card = (f'<rect x="3" y="3" width="{W-6}" height="{H-6}" rx="13" fill="{t["card"]}" '
             f'fill-opacity="{t["card_o"]}" stroke="{t["card_st"]}" stroke-opacity=".4" stroke-width="1"/>')

    return svg_doc(W, round(H), card + corners + sparkle + body, f"{' '.join(name_lines)}. {sentence}")

# ---------------------------------------------------------------- Featured Work v5 (wide)
# Round 4 of Part 2: the 2x2 chip grid squeezed every sentence into a ~370px column, which
# is what forced 5-7 line descriptions. Switching to four full-width stacked cards gives
# each project ~760px of text width instead, so the new (deliberately shortened) copy
# below can actually read as 1-2 lines rather than a wall of text.

PROJECTS_V3 = [
    dict(
        slug="ev-charging", name="EV Charging Expansion Intelligence", icon="ev",
        sentence=("Regional analytics platform comparing EV adoption with public charging infrastructure "
                   "across Germany to identify underserved regions and support infrastructure planning."),
        stack=["Databricks", "PySpark", "Python", "SQL", "Power BI", "GitHub Actions"],
    ),
    dict(
        slug="watch-pricing", name="Automated Pricing and Market Analysis Tool", icon="watch",
        sentence=("Pricing intelligence tool for a real vintage watch-parts business that benchmarks "
                   "market listings and generates SKU-level pricing guidance."),
        stack=["Python", "PostgreSQL", "SQL", "pandas", "Streamlit", "Statistical Analysis"],
    ),
    dict(
        slug="ai-agent", name="Multi-Agent AI Analytics Agent", icon="agents2",
        sentence=("Multi-agent analytics system that routes business questions across specialized agents, "
                   "computes results with controlled tools, and verifies answers before responding."),
        stack=["Python", "LangGraph", "LLM APIs", "RAG", "pgvector", "Pydantic", "FastAPI"],
    ),
    dict(
        slug="churn", name="Customer Churn Prediction and Retention", icon="churn2",
        sentence=("Predictive analytics workflow that identifies customers at churn risk, explains key "
                   "drivers, and supports targeted retention decisions."),
        stack=["Python", "pandas", "scikit-learn", "Logistic Regression", "SVM", "Model Evaluation"],
    ),
]

def _chips_slim(items, x0, y0, max_w, t, font_size=11):
    """Slimmer pill row for the wide card -- less padding/height than _chips, tuned for
    ~22-25px chip height. Same wrap-to-new-row behaviour; returns (frag, total_height)."""
    pad_x, h, gap, row_gap = 7, 22, 5, 6
    cur_x, cur_y = x0, y0
    frag = ""
    for it in items:
        w = _text_w(it, font_size, bold=True) + pad_x * 2
        if cur_x + w > x0 + max_w and cur_x > x0:
            cur_x = x0
            cur_y += h + row_gap
        frag += (f'<rect x="{cur_x:.1f}" y="{cur_y:.1f}" width="{w:.1f}" height="{h}" rx="{h/2:.1f}" '
                  f'fill="{t["ctile"]}" fill-opacity="{t["ctile_o"]}" stroke="{t["ctile_st"]}" '
                  f'stroke-opacity="{t["ctile_st_o"]}"/>')
        frag += (f'<text x="{cur_x+w/2:.1f}" y="{cur_y+h/2+3.4:.1f}" text-anchor="middle" '
                  f'font-size="{font_size}" font-weight="600" fill="{t["heading"]}">{esc(it)}</text>')
        cur_x += w + gap
    total_h = (cur_y - y0) + h
    rows = round((total_h - h) / (h + row_gap)) + 1 if total_h else 1
    return frag, total_h, rows

def variant_h_wide(t, name, sentence, stack, icon, cta="View Project ↗", min_h=None, url=None, W=800):
    """H -- full-width stacked card: icon+title on top, a short (target 1-2 line)
    description, then chips-left / CTA-right sharing a bottom baseline. Same thin frame
    and stepped-pixel corners as variant G, just laid out wide instead of squeezed narrow.
    `W` is parametrized so the same layout logic can render the mobile-width reflow too."""
    pad = 20 if W >= 500 else 14
    usable = W - 2 * pad
    icon_s, icon_gap = 24, 9
    title_x = pad + icon_s + icon_gap

    name_line = name if _text_w(name, 17.5, bold=True) <= usable - icon_s - icon_gap else None
    name_lines = [name_line] if name_line else _wrap_px(name, usable - icon_s - icon_gap, 17.5, bold=True)
    sentence_lines = _wrap_px(sentence, usable, 13.5)

    body, y = "", 26
    body += ICONS_V3[icon](t, pad, y - 18, icon_s)
    for l in name_lines:
        body += f'<text x="{title_x}" y="{y}" font-size="17.5" font-weight="600" fill="{t["phrase"]}">{esc(l)}</text>'
        y += 21
    y = max(y, 8 + icon_s) + 8
    for l in sentence_lines:
        body += f'<text x="{pad}" y="{y}" font-size="13.5" fill="{t["sub"]}">{esc(l)}</text>'
        y += 18
    y += 14

    cta_w = _text_w(cta, 11.5, bold=True) if cta else 0
    chip_max_w = usable - (cta_w + 24 if cta else 0)
    chip_frag, chip_h, chip_rows = _chips_slim(stack, pad, y, chip_max_w, t, font_size=11)
    body += chip_frag
    cta_baseline = y + 15  # first chip row's text baseline, so CTA sits on the same line
    if cta:
        body += (f'<text x="{W-pad}" y="{cta_baseline:.1f}" text-anchor="end" font-size="11.5" '
                  f'font-weight="700" fill="{t["heading"]}">{esc(cta)}</text>')
    y += chip_h + 16
    H = max(y, min_h or 0)

    corners = (_stepped_corner(pad - 10, 8, 2.2, t["peri"], "tl")
               + _stepped_corner(W - pad + 8, H - 10, 2.2, t["star"], "br"))
    card = (f'<rect x="3" y="3" width="{W-6}" height="{H-6}" rx="13" fill="{t["card"]}" '
             f'fill-opacity="{t["card_o"]}" stroke="{t["card_st"]}" stroke-opacity=".4" stroke-width="1"/>')

    svg = svg_doc(W, round(H), card + corners + body, f"{' '.join(name_lines)}. {sentence}")
    return svg, dict(title_lines=len(name_lines), desc_lines=len(sentence_lines), chip_rows=chip_rows, h=round(H))

# ---------------------------------------------------------------- Featured Work FINAL
# Round 5 of Part 2: faithful recreation of an externally-generated reference image the
# user approved as final -- visible indigo/lavender pixel-window card (not the near-
# transparent wash used in D/E/F/G/H), tiny top-right window-control glyphs + dot grid
# (echoing the banner's own window chrome), stepped corners on all four sides, and
# icon-bearing tech chips. This is the version wired into production below.

CARD5 = {
    "dark": dict(
        bg="#191330", bg_o=1, bevel="#100C24", border="#A79AF2", border_o=.95, glow="#9C8FF0", glow_o=.55,
        title="#F6EEDC", desc="#BBB6DC", chip_bg="#221B40", chip_bg_o=1,
        chip_border="#9C8FF0", chip_border_o=.85, chip_text="#DED9F7", cta="#B6AEF7", corner="#F3C9A8",
        spark="#D5CEFF",
    ),
    "light": dict(
        bg="#F1EDFB", bg_o=1, bevel="#D9D1F3", border="#8074D6", border_o=.85, glow="#B9AEEA", glow_o=.3,
        title="#2E2760", desc="#544C82", chip_bg="#E7E1F9", chip_bg_o=1,
        chip_border="#8074D6", chip_border_o=.7, chip_text="#372F6E", cta="#5B4FCF", corner="#E08A5C",
        spark="#7F72DB",
    ),
}

# ---- hand-pixelled project sprites --------------------------------------------------
# 24-column pixel grids drawn with the banner's palette (dark indigo outline, periwinkle,
# lavender, peach, blush, cream, amber). Built procedurally so every row is exactly 24
# cells wide; rendered as crisp <rect> runs, so the icon's true bounding box is exactly
# its cell grid (which is what the containment QA checks).
SPRITE_PAL = {
    "O": "#2a2455", "D": "#3b3f9f", "B": "#6f7ff0", "L": "#a9b6ff", "V": "#8a78e6", "G": "#6d5bd0",
    "W": "#c9c0ff", "P": "#f2a67e", "Q": "#f8cfae", "R": "#ee7b95", "Y": "#ffd76a", "C": "#f6eedc", "A": "#f3b95f",
}
SPRITE_COLS, SPRITE_ROWS = 24, 22

class _Grid:
    def __init__(self):
        self.g = [["."] * SPRITE_COLS for _ in range(SPRITE_ROWS)]
    def put(self, x, y, ch):
        if 0 <= x < SPRITE_COLS and 0 <= y < SPRITE_ROWS:
            self.g[y][x] = ch
    def rect(self, x0, y0, x1, y1, ch):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, ch)
    def box(self, x0, y0, x1, y1, outline, fill):
        self.rect(x0, y0, x1, y1, outline)
        self.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill)
    def stamp(self, x, y, pat):
        for j, line in enumerate(pat):
            for i, c in enumerate(line):
                if c != ".":
                    self.put(x + i, y + j, c)
    def line(self, x0, y0, x1, y1, ch, thick=1):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n)
            y = round(y0 + (y1 - y0) * i / n)
            for t_ in range(thick):
                self.put(x, y + t_, ch)
    def rows(self):
        return ["".join(r) for r in self.g]

def _sprite_ev():
    c = _Grid()
    c.box(1, 0, 10, 18, "O", "B")
    c.rect(2, 2, 2, 16, "L")
    c.box(3, 2, 8, 10, "O", "D")
    c.stamp(4, 3, ["..YY", ".YY.", "YYYY", "..YY", ".YY.", ".Y.."])
    c.rect(4, 12, 7, 12, "D"); c.rect(4, 14, 7, 14, "D")
    c.box(0, 19, 11, 21, "O", "B")
    c.rect(0, 8, 0, 15, "O"); c.put(1, 15, "O")
    c.stamp(14, 0, [".OOOO.", "ORRRRO", "ORCCRO", "ORCCRO", ".ORRO.", ".ORRO.", "..OO.."])
    for y in (8, 10, 12):
        c.put(17, y, "G")
    for i, l in enumerate([15, 14, 14, 13, 13, 12, 12]):
        c.put(l, 14 + i, "B"); c.put(l + 9, 14 + i, "B")
    c.rect(15, 14, 23, 14, "B"); c.rect(12, 20, 21, 20, "B")
    c.rect(15, 17, 22, 17, "B"); c.line(19, 14, 17, 20, "B")
    return c.rows()

def _sprite_watch():
    c = _Grid()
    cx, cy = 7.5, 11
    c.box(5, 0, 10, 4, "O", "V"); c.box(5, 18, 10, 21, "O", "V")
    for y in range(SPRITE_ROWS):
        for x in range(SPRITE_COLS):
            d = ((x + .5 - cx) ** 2 + (y + .5 - cy) ** 2) ** .5
            if d <= 7.4:
                c.put(x, y, "O" if d > 6.4 else ("P" if d > 5.2 else "D"))
    c.rect(8, 8, 8, 11, "C"); c.rect(8, 11, 11, 11, "C"); c.put(7, 11, "C")
    c.rect(15, 9, 15, 13, "O"); c.rect(16, 10, 16, 12, "P")
    for (x0, y0) in ((16, 17), (19, 14), (22, 11)):
        c.rect(x0, y0, x0 + 1, 20, "B"); c.rect(x0, y0, x0 + 1, y0, "L")
    c.line(15, 9, 22, 3, "R", 2)
    c.rect(18, 1, 23, 1, "R"); c.rect(23, 1, 23, 6, "R")
    return c.rows()

def _sprite_agents():
    c = _Grid()
    c.stamp(9, 0, ["...A...", "...A...", "..AQA..", "AAQCQAA", "..AQA..", "...A...", "...A..."])
    c.put(12, 8, "W"); c.put(12, 9, "W")
    for (x, y) in ((10, 8), (8, 9), (6, 10), (4, 11), (14, 8), (16, 9), (18, 10), (20, 11), (12, 11), (12, 12)):
        c.put(x, y, "G")
    head = ["OOOOOOO", "OLLLLLO", "OLDLDLO", "OLLLLLO", "OBBBBBO", "OOOOOOO"]
    for (x, y) in ((0, 12), (17, 12), (8, 14)):
        c.stamp(x, y, head)
        c.put(x + 3, y - 1, "O")
    return c.rows()

def _sprite_churn():
    c = _Grid()
    c.stamp(2, 0, ["..OOO..", ".OVVVO.", "OVVVVVO", "OVVVVVO", "OVVVVVO", ".OVVVO.", "..OOO.."])
    c.stamp(0, 8, ["...OOOOOO...", "..OVVVVVVO..", ".OVVVVVVVVO.", "OVVVVVVVVVVO", "OVVVVVVVVVVO",
                   "OVVVVVVVVVVO", "OVVVVVVVVVVO", "OVVVVVVVVVVO", "OVVVVVVVVVVO", "OVVVVVVVVVVO",
                   "OVVVVVVVVVVO", "OOOOOOOOOOOO"])
    c.rect(2, 11, 2, 18, "W")
    for (x0, y0) in ((13, 15), (16, 11), (19, 7)):
        c.rect(x0, y0, x0 + 1, 20, "B"); c.rect(x0, y0, x0 + 1, y0, "L")
    c.line(12, 9, 22, 2, "R", 2)
    c.rect(18, 1, 23, 1, "R"); c.rect(23, 1, 23, 6, "R")
    return c.rows()

SPRITES = {"ev": _sprite_ev(), "watch": _sprite_watch(), "agents2": _sprite_agents(), "churn2": _sprite_churn()}
assert all(len(r) == SPRITE_COLS for rows in SPRITES.values() for r in rows)

def pixel_sprite(key, x, y, cell):
    """Renders a sprite as merged same-colour <rect> runs. Tagged data-role="icon" so the
    QA script can compute the artwork's exact bounding box from the rects themselves."""
    out = []
    for j, row in enumerate(SPRITES[key]):
        i = 0
        while i < len(row):
            ch = row[i]
            if ch == ".":
                i += 1
                continue
            k = i
            while k + 1 < len(row) and row[k + 1] == ch:
                k += 1
            out.append(f'<rect x="{x + i * cell:g}" y="{y + j * cell:g}" width="{(k - i + 1) * cell:g}" '
                        f'height="{cell:g}" fill="{SPRITE_PAL[ch]}"/>')
            i = k + 1
    return f'<g data-role="icon" shape-rendering="crispEdges">{"".join(out)}</g>'

def _stair_path(x0, y0, x1, y1, st):
    """Rectangle whose four corners are 2-step pixel stairs instead of rounded arcs."""
    c = 2 * st
    return (f"M{x0+c:g},{y0:g} H{x1-c:g} v{st:g} h{st:g} v{st:g} h{st:g} V{y1-c:g} h-{st:g} v{st:g} h-{st:g} "
            f"v{st:g} H{x0+c:g} v-{st:g} h-{st:g} v-{st:g} h-{st:g} V{y0+c:g} h{st:g} v-{st:g} h{st:g} v-{st:g} Z")

def _window_controls(W, top, sq, gap, right, c, opacity=.95, bg="#191330"):
    """Minimise / restore / close squares (the banner's own window-control language) as
    solid pixel squares with a dark glyph, aligned to the top-right of the frame."""
    x = W - right - (3 * sq + 2 * gap)
    g = ""
    for n in range(3):
        sx = x + n * (sq + gap)
        g += f'<rect x="{sx:g}" y="{top:g}" width="{sq:g}" height="{sq:g}" rx="1.5" fill="{c}" fill-opacity="{opacity}"/>'
    u = sq / 13
    g += f'<rect x="{x + 3*u:g}" y="{top + 8.4*u:g}" width="{7*u:g}" height="{1.8*u:g}" fill="{bg}"/>'
    sx = x + (sq + gap)
    g += (f'<rect x="{sx + 3.2*u:g}" y="{top + 3.2*u:g}" width="{6.6*u:g}" height="{6.6*u:g}" fill="none" '
          f'stroke="{bg}" stroke-width="{1.5*u:g}"/>')
    sx = x + 2 * (sq + gap)
    g += (f'<path d="M{sx + 3.6*u:g} {top + 3.6*u:g} L{sx + 9.4*u:g} {top + 9.4*u:g} M{sx + 9.4*u:g} {top + 3.6*u:g} '
          f'L{sx + 3.6*u:g} {top + 9.4*u:g}" stroke="{bg}" stroke-width="{1.6*u:g}" stroke-linecap="square"/>')
    return g

def _dot_cluster(x, y, c, opacity=.85, d=3):
    pts = [(0, 0), (2 * d, d), (2 * d, 3 * d), (0, 4 * d)]
    return "".join(f'<rect x="{x + px:g}" y="{y + py:g}" width="{d:g}" height="{d:g}" fill="{c}" fill-opacity="{opacity}"/>'
                   for px, py in pts)

def _spark4(cx, cy, r, c):
    """Smooth 4-point sparkle (concave sides) used beside the CTA."""
    return (f'<path d="M{cx:g} {cy-r:g} Q{cx:g} {cy:g} {cx+r:g} {cy:g} Q{cx:g} {cy:g} {cx:g} {cy+r:g} '
            f'Q{cx:g} {cy:g} {cx-r:g} {cy:g} Q{cx:g} {cy:g} {cx:g} {cy-r:g} Z" fill="{c}"/>')


# label -> icon-system key, reusing the exact same logo/glyph assets as the Tech Stack
# section for every chip that has one, for visual + palette consistency across the profile
CHIP_ICON_MAP = {
    "Databricks": ("logo", "databricks"), "PySpark": ("logo", "spark"), "Delta Lake": ("glyph", "deltalake"),
    "Power BI": ("logo", "powerbi"), "GitHub Actions": ("logo", "gha"), "Python": ("logo", "python"),
    "PostgreSQL": ("logo", "postgresql"), "DuckDB": ("logo", "duckdb"), "ETL": ("glyph", "etl"),
    "eBay API": ("logo", "ebay"), "Streamlit": ("logo", "streamlit"),
    "LangGraph": ("logo", "langgraph"), "LLM APIs": ("glyph", "llms"), "RAG": ("glyph", "rag"),
    "pgvector": ("glyph", "pgvector"), "Pydantic": ("logo", "pydantic"), "FastAPI": ("logo", "fastapi"),
    "scikit-learn": ("logo", "sklearn"),
}

def _chip_icon(t, label, x, y, size):
    kind_key = CHIP_ICON_MAP.get(label)
    if not kind_key:
        return "", 0
    kind, key = kind_key
    if kind == "logo":
        return logo(key, x, y, size), size
    return glyph(key, x, y, size, t["glyph"], 1.5), size

def _chips_final(items, x0, y0, max_w, t, t5, font_size=13, h=36, icon_s=20, gap=8, pad_l=11, pad_r=12,
                 icon_gap=8, radius=6):
    """Tech chips: boxy pixel-frame pills (thin bright border, dark fill), a real brand /
    concept icon where one exists, wrapping to a new row only if a chip would overrun."""
    row_gap = max(6, gap)
    cur_x, cur_y = x0, y0
    frag = ""
    for it in items:
        has_icon = it in CHIP_ICON_MAP
        text_w = _text_w(it, font_size, bold=True)
        w = pad_l + (icon_s + icon_gap if has_icon else 0) + text_w + pad_r
        if cur_x + w > x0 + max_w and cur_x > x0:
            cur_x = x0
            cur_y += h + row_gap
        frag += (f'<rect x="{cur_x:.1f}" y="{cur_y:.1f}" width="{w:.1f}" height="{h}" rx="{radius}" '
                 f'fill="{t5["chip_bg"]}" fill-opacity="{t5["chip_bg_o"]}" stroke="{t5["chip_border"]}" '
                 f'stroke-opacity="{t5["chip_border_o"]}" stroke-width="1.7"/>')
        tx = cur_x + pad_l
        if has_icon:
            frag += _chip_icon(t, it, tx, cur_y + (h - icon_s) / 2, icon_s)[0]
            tx += icon_s + icon_gap
        frag += (f'<text x="{tx:.1f}" y="{cur_y+h/2+font_size*0.35:.1f}" font-size="{font_size}" font-weight="600" '
                 f'fill="{t5["chip_text"]}">{esc(it)}</text>')
        cur_x += w + gap
    total_h = (cur_y - y0) + h
    rows = round((total_h - h) / (h + row_gap)) + 1
    return frag, total_h, rows

def final_card(theme, t, name, sentence, chips, icon, cta="View Project ↗", min_h=None, W=820):
    """Featured Work card, laid out like the approved reference: a hand-pixelled sprite in
    its own left column, title + description in the column to its right, a full-width chip
    row beneath, and the CTA on its own row at the bottom right. Framed as a stepped-corner
    pixel window with layered edges, window controls and a dot cluster at the top right."""
    t5 = CARD5[theme]
    wide = W >= 700
    if wide:
        pad, cell, icon_x, icon_y = 26, 4.5, 24, 26
        title_fs, desc_fs, desc_lh = 25, 15.5, 23
        chip = dict(font_size=13.5, h=38, icon_s=18, gap=7, pad_l=10, pad_r=10, icon_gap=7)
        title_x = icon_x + SPRITE_COLS * cell + 22
        title_y0, desc_gap = 69, 38
        right_bound = W - 74           # keep text clear of the top-right window chrome
    else:
        pad, cell, icon_x, icon_y = 18, 2, 18, 26
        title_fs, desc_fs, desc_lh = 16.5, 13.5, 18.5
        chip = dict(font_size=11.5, h=28, icon_s=16, gap=6, pad_l=9, pad_r=10, icon_gap=6)
        title_x = icon_x + SPRITE_COLS * cell + 12
        title_y0, desc_gap = 44, 0
        right_bound = W - pad
    sprite_w, sprite_h = SPRITE_COLS * cell, SPRITE_ROWS * cell
    usable = W - 2 * pad

    title_w = right_bound - title_x
    name_lines = [name] if _text_w(name, title_fs, bold=True) <= title_w else _wrap_px(name, title_w, title_fs, bold=True)
    body = pixel_sprite(icon, icon_x, icon_y, cell)
    y = title_y0
    for l in name_lines:
        body += f'<text x="{title_x}" y="{y}" font-size="{title_fs}" font-weight="700" fill="{t5["title"]}">{esc(l)}</text>'
        y += title_fs + 5
    title_bottom = y - (title_fs + 5)

    if wide:
        desc_x, desc_w = title_x, W - title_x - pad
        y = title_bottom + desc_gap
    else:
        desc_x, desc_w = pad, usable
        y = max(title_bottom + 12, icon_y + sprite_h) + 18
    sentence_lines = _wrap_px(sentence, desc_w, desc_fs)
    for l in sentence_lines:
        body += f'<text x="{desc_x}" y="{y}" font-size="{desc_fs}" fill="{t5["desc"]}">{esc(l)}</text>'
        y += desc_lh
    desc_bottom = y - desc_lh

    cta_gap, bottom_pad = (38, 24) if wide else (26, 20)
    _, chip_total, chip_rows = _chips_final(chips, pad, 0, usable, t, t5, **chip)
    natural_top = max(desc_bottom + (22 if wide else 16), icon_y + sprite_h + (18 if wide else 14))
    H = max(natural_top + chip_total + cta_gap + bottom_pad, min_h or 0)
    # chips hang from the CTA row, not from the description, so the chip row and the CTA
    # land at the same position on every card regardless of how many lines the copy wraps to
    chips_top = H - bottom_pad - cta_gap - chip_total
    chip_frag, _, _ = _chips_final(chips, pad, chips_top, usable, t, t5, **chip)
    body += chip_frag

    cta_fs = 17 if wide else 12.5
    cta_y = H - bottom_pad
    cta_right = W - (60 if wide else 34)
    body += (f'<text x="{cta_right}" y="{cta_y:.1f}" text-anchor="end" font-size="{cta_fs}" font-weight="700" '
             f'fill="{t5["cta"]}">{esc(cta)}</text>')
    sr = 11 if wide else 6.5
    body += _spark4(cta_right + sr + 6 if wide else cta_right + sr + 4, cta_y - 20 if wide else cta_y - 12, sr, t5["spark"])
    body += (f'<rect x="{W - 30 if wide else cta_right + sr*2 + 6:g}" y="{cta_y - 2:g}" width="3" height="3" fill="{t5["corner"]}"/>')

    ins_outer, ins_main, ins_inner, st = 1.5, 4.5, 9.5, 5
    _uid[0] += 1
    gid = f"glow{_uid[0]}"
    frame = (f'<defs><filter id="{gid}" x="-10%" y="-25%" width="120%" height="150%">'
             f'<feGaussianBlur stdDeviation="3"/></filter></defs>'
             f'<path d="{_stair_path(ins_main, ins_main, W - ins_main, H - ins_main, st)}" fill="none" stroke="{t5["glow"]}" '
             f'stroke-opacity="{t5["glow_o"]}" stroke-width="5" filter="url(#{gid})"/>'
             f'<path d="{_stair_path(ins_outer, ins_outer, W - ins_outer, H - ins_outer, st + 1)}" fill="none" '
             f'stroke="{t5["border"]}" stroke-opacity=".38" stroke-width="1.3"/>'
             f'<path d="{_stair_path(ins_main, ins_main, W - ins_main, H - ins_main, st)}" fill="{t5["bg"]}" '
             f'fill-opacity="{t5["bg_o"]}" stroke="{t5["border"]}" stroke-opacity="{t5["border_o"]}" stroke-width="2.6" '
             f'stroke-linejoin="miter"/>'
             f'<line x1="{ins_main + 2*st}" y1="{ins_main + 1.2}" x2="{W - ins_main - 2*st}" y2="{ins_main + 1.2}" '
             f'stroke="{t5["border"]}" stroke-width="1.4"/>'
             f'<path d="{_stair_path(ins_inner, ins_inner, W - ins_inner, H - ins_inner, 4)}" fill="none" '
             f'stroke="{t5["border"]}" stroke-opacity=".34" stroke-width="1.3"/>')
    acc = 3
    frame += "".join(f'<rect x="{ax}" y="{ay}" width="{acc}" height="{acc}" fill="{t5["border"]}" fill-opacity=".8"/>'
                     for ax, ay in ((12, 12), (W - 12 - acc, H - 12 - acc), (12, H - 12 - acc)))
    if wide:
        frame += _window_controls(W, 16, 14, 5, 26, t5["border"], bg=t5["bg"])
        frame += _dot_cluster(W - 44, 46, t5["border"])
    else:
        frame += _window_controls(W, 12, 10, 4, 18, t5["border"], bg=t5["bg"])
        frame += _dot_cluster(W - 18 - 38 - 20, 12, t5["border"], d=2)

    svg = svg_doc(W, round(H), frame + body, f"{' '.join(name_lines)}. {sentence}")
    meta = dict(title_lines=len(name_lines), desc_lines=len(sentence_lines), chip_rows=chip_rows, h=round(H), w=W)
    return svg, meta


APPROVED_DESKTOP_H = 275

PROJECTS_FINAL = [
    dict(
        slug="ev-charging", name="EV Charging Infrastructure Intelligence", icon="ev",
        sentence=("Regional analytics platform that integrates official German mobility and charging data "
                   "into validated KPIs and dashboards to identify underserved regions and support "
                   "infrastructure planning."),
        chips=["Databricks", "PySpark", "Delta Lake", "Power BI", "GitHub Actions", "Python"],
        url="https://github.com/vaish1101/ev-charging-expansion-intelligence", url_verified_public=True,
    ),
    dict(
        slug="watch-pricing", name="Vintage Watch Parts Pricing & Turnover Intelligence", icon="watch",
        sentence=("Commercial analytics system for a real vintage watch parts business, using evidence based "
                   "pricing and turnover analysis to generate explainable market value recommendations and "
                   "selling horizon estimates from historical and active marketplace listings"),
        chips=["Python", "DuckDB", "PostgreSQL", "ETL", "eBay API", "Streamlit"],
        url="https://github.com/vaish1101/vintage-watch-parts", url_verified_public=False,  # private -- see report
    ),
    dict(
        slug="ai-agent", name="Business Analytics AI Assistant", icon="agents2",
        sentence=("Multi agent AI system that turns business questions into end to end analysis, orchestrating "
                   "analytics and RAG workflows to investigate KPIs, trends, and performance and provide "
                   "grounded, validated decision support."),
        chips=["Python", "LangGraph", "LLM APIs", "RAG", "pgvector", "Pydantic", "FastAPI"],
        url=None, url_verified_public=False,  # no repository URL provided -- see report
    ),
    dict(
        slug="churn", name="Customer Churn Prediction & Retention", icon="churn2",
        sentence=("Predictive retention system that identifies customers at churn risk, explains the main "
                   "drivers, and converts model outputs into prioritized retention decisions."),
        chips=["Python", "scikit-learn", "Logistic Regression", "SVM", "Model Evaluation", "Power BI"],
        url=None, url_verified_public=False,  # no repository URL provided -- see report
    ),
]

def _svg_height(svg_text):
    return int(re.search(r'height="(\d+)"', svg_text).group(1))

if __name__ == "__main__" and "--preview-variants" in sys.argv:
    # Part-2 comparison render only -- writes to a scratch folder, never touches the
    # production project-*.svg files the live README points at.
    out_dir = pathlib.Path(sys.argv[sys.argv.index("--preview-variants") + 1]
                            if len(sys.argv) > sys.argv.index("--preview-variants") + 1
                            and not sys.argv[sys.argv.index("--preview-variants") + 1].startswith("-")
                            else HERE / "_variants_preview")
    out_dir.mkdir(parents=True, exist_ok=True)
    ev = PROJECTS_V2[0]  # "at least one project" -- EV Charging, the only one with a public repo
    for vkey, vfn in VARIANTS.items():
        probe_h = _svg_height(vfn(THEMES["light"], ev["name"], ev["sentence"], ev["stack"], ev["icon"]))
        for theme, t in THEMES.items():
            svg = vfn(t, ev["name"], ev["sentence"], ev["stack"], ev["icon"], min_h=probe_h)
            (out_dir / f"variant-{vkey}-{theme}.svg").write_text(svg)
    print("wrote", len(VARIANTS) * len(THEMES), "preview svgs to", out_dir)
    sys.exit(0)

if __name__ == "__main__" and "--preview-variants-v2" in sys.argv:
    # Round 2 (D/E/F) comparison render -- same non-destructive contract as --preview-variants.
    out_dir = HERE / "_variants_preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    ev = PROJECTS_V2[0]
    heights = {}
    for vkey, vfn in VARIANTS_V2.items():
        probe_h = _svg_height(vfn(THEMES["light"], ev["name"], ev["sentence"], ev["stack"], ev["icon"]))
        heights[vkey] = probe_h
        for theme, t in THEMES.items():
            svg = vfn(t, ev["name"], ev["sentence"], ev["stack"], ev["icon"], min_h=probe_h)
            (out_dir / f"variant-{vkey}-{theme}.svg").write_text(svg)
    print("heights:", heights)

    # icon montage (v3, compact)
    names = {"ev": "EV Charging", "watch": "Pricing / Watch", "agents2": "Multi-Agent AI", "churn2": "Churn / Retention"}
    for theme, t in THEMES.items():
        cell, size = 92, 26
        body = ""
        for i, (key, label) in enumerate(names.items()):
            cx = i * cell
            body += ICONS_V3[key](t, cx + (cell - size) / 2, 14, size)
            body += (f'<text x="{cx+cell/2}" y="66" text-anchor="middle" font-size="8.5" '
                     f'fill="{t["sub"]}">{esc(label)}</text>')
        (out_dir / f"icons-v3-{theme}.svg").write_text(svg_doc(cell * 4, 78, body, "Redesigned project icons"))

    # 2x2 mockup using the most compact of the three (measured, not assumed)
    winner = min(heights, key=heights.get)
    vfn = VARIANTS_V2[winner]
    for theme, t in THEMES.items():
        gap = 16
        cw, ch = 400, heights[winner]
        cards = []
        for i, p in enumerate(PROJECTS_V2):
            svg = vfn(t, p["name"], p["sentence"], p["stack"], p["icon"], min_h=heights[winner])
            cards.append((i, svg))
        rows = []
        max_h_per_row = [0, 0]
        parsed = []
        for i, svg in cards:
            h = _svg_height(svg)
            row = i // 2
            max_h_per_row[row] = max(max_h_per_row[row], h)
            parsed.append((i, svg, h))
        body = ""
        row_y = [0, 0]
        row_y[1] = max_h_per_row[0] + gap
        for i, svg, h in parsed:
            col, row = i % 2, i // 2
            x = col * (cw + gap)
            y = row_y[row]
            inner = re.search(r'<svg[^>]*>(.*)</svg>', svg, re.S).group(1)
            body += f'<g transform="translate({x} {y})">{inner}</g>'
        total_w = cw * 2 + gap
        total_h = row_y[1] + max_h_per_row[1]
        (out_dir / f"mockup-2x2-{winner}-{theme}.svg").write_text(
            svg_doc(total_w, total_h, body, f"2x2 mockup, variant {winner}"))
    print("mockup uses variant:", winner, "(measured shortest, not a chosen winner)")
    sys.exit(0)

if __name__ == "__main__" and "--preview-chips" in sys.argv:
    # Round 3 (chip-based "G") comparison render -- same non-destructive contract as the
    # other preview flags: writes only to the scratch folder, all 4 projects, both themes.
    out_dir = HERE / "_variants_preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    heights = [_svg_height(variant_g_chips(THEMES["light"], p["name"], p["sentence"], p["stack"], p["icon"]))
               for p in PROJECTS_V2]
    card_h = max(heights)
    print("per-project heights:", dict(zip([p["slug"] for p in PROJECTS_V2], heights)), "-> shared", card_h)

    for theme, t in THEMES.items():
        for p in PROJECTS_V2:
            svg = variant_g_chips(t, p["name"], p["sentence"], p["stack"], p["icon"], min_h=card_h)
            (out_dir / f"chips-{p['slug']}-{theme}.svg").write_text(svg)

        gap = 16
        cw = 406
        body = ""
        for i, p in enumerate(PROJECTS_V2):
            svg = variant_g_chips(t, p["name"], p["sentence"], p["stack"], p["icon"], min_h=card_h)
            col, row = i % 2, i // 2
            x, y = col * (cw + gap), row * (card_h + gap)
            inner = re.search(r'<svg[^>]*>(.*)</svg>', svg, re.S).group(1)
            body += f'<g transform="translate({x} {y})">{inner}</g>'
        total_w, total_h = cw * 2 + gap, card_h * 2 + gap
        (out_dir / f"chips-2x2-{theme}.svg").write_text(svg_doc(total_w, total_h, body, "Featured Work, chip variant, 2x2"))
    print("wrote 4 per-project cards x 2 themes + 2 grid mockups to", out_dir)
    sys.exit(0)

if __name__ == "__main__" and "--preview-wide" in sys.argv:
    # Round 4 (full-width stacked "H") comparison render -- same non-destructive contract.
    out_dir = HERE / "_variants_preview"
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {}
    heights = []
    for p in PROJECTS_V3:
        _, meta = variant_h_wide(THEMES["light"], p["name"], p["sentence"], p["stack"], p["icon"])
        report[p["slug"]] = meta
        heights.append(meta["h"])
    card_h = max(heights)
    print("per-project geometry (desktop, width 800):")
    for slug, meta in report.items():
        print(f"  {slug}: title_lines={meta['title_lines']} desc_lines={meta['desc_lines']} "
              f"chip_rows={meta['chip_rows']} natural_h={meta['h']}")
    print("shared card height:", card_h)

    gap = 18
    for theme, t in THEMES.items():
        body, y = "", 0
        for p in PROJECTS_V3:
            svg, _ = variant_h_wide(t, p["name"], p["sentence"], p["stack"], p["icon"], min_h=card_h)
            inner = re.search(r'<svg[^>]*>(.*)</svg>', svg, re.S).group(1)
            body += f'<g transform="translate(0 {y})">{inner}</g>'
            y += card_h + gap
            (out_dir / f"wide-{p['slug']}-{theme}.svg").write_text(svg)
        total_h = y - gap
        (out_dir / f"wide-stack-{theme}.svg").write_text(svg_doc(800, total_h, body, "Featured Work, wide stacked cards"))

    # mobile: same layout function at a narrow width, so wrapping/reflow is genuine, not simulated
    mob_w = 360
    t = THEMES["light"]
    mob_heights = []
    for p in PROJECTS_V3:
        _, meta = variant_h_wide(t, p["name"], p["sentence"], p["stack"], p["icon"], W=mob_w)
        mob_heights.append(meta["h"])
    mob_card_h = max(mob_heights)
    body, y = "", 0
    for p in PROJECTS_V3:
        svg, _ = variant_h_wide(t, p["name"], p["sentence"], p["stack"], p["icon"], min_h=mob_card_h, W=mob_w)
        inner = re.search(r'<svg[^>]*>(.*)</svg>', svg, re.S).group(1)
        body += f'<g transform="translate(0 {y})">{inner}</g>'
        y += mob_card_h + 14
    (out_dir / "wide-mobile-light.svg").write_text(svg_doc(mob_w, y - 14, body, "Featured Work, mobile stacked"))
    print("mobile card height:", mob_card_h)
    print("wrote wide stacked previews to", out_dir)
    sys.exit(0)

if __name__ == "__main__" and "--build-final" in sys.argv:
    # Round 5: writes the approved-final Featured Work cards directly to production
    # (assets/profile/{light,dark}/featured-*.svg), per this round's explicit instruction
    # to build production-ready assets rather than another preview-only round.
    desktop_w, mobile_w = 820, 335
    heights_desktop = [final_card(th, THEMES[th], p["name"], p["sentence"], p["chips"], p["icon"], W=desktop_w)[1]["h"]
                        for th in ("light", "dark") for p in PROJECTS_FINAL]
    card_h_desktop = APPROVED_DESKTOP_H  # baseline: cards only grow if their own text needs more
    heights_mobile = [final_card(th, THEMES[th], p["name"], p["sentence"], p["chips"], p["icon"], W=mobile_w)[1]["h"]
                       for th in ("light", "dark") for p in PROJECTS_FINAL]
    card_h_mobile = max(heights_mobile)

    report = {}
    for theme in ("light", "dark"):
        d = OUT / theme
        for p in PROJECTS_FINAL:
            svg_d, meta_d = final_card(theme, THEMES[theme], p["name"], p["sentence"], p["chips"], p["icon"],
                                        min_h=card_h_desktop, W=desktop_w)
            svg_m, meta_m = final_card(theme, THEMES[theme], p["name"], p["sentence"], p["chips"], p["icon"],
                                        W=mobile_w)
            (d / f"featured-{p['slug']}.svg").write_text(svg_d)
            (d / f"featured-{p['slug']}-mobile.svg").write_text(svg_m)
            if theme == "light":
                report[p["slug"]] = dict(desktop=meta_d, mobile=meta_m)

    print(f"desktop baseline card height: {card_h_desktop}  (width {desktop_w})")
    print(f"shared mobile card height: {card_h_mobile}  (width {mobile_w})")
    for slug, r in report.items():
        print(f"  {slug}: desktop title_lines={r['desktop']['title_lines']} desc_lines={r['desktop']['desc_lines']} "
              f"chip_rows={r['desktop']['chip_rows']}  |  mobile chip_rows={r['mobile']['chip_rows']}")
    print("wrote", 4 * len(PROJECTS_FINAL), "production svgs to", OUT / "{light,dark}")
    sys.exit(0)

if __name__ == "__main__":
    # Default build: Tech Stack, the production Featured Work cards (the approved
    # "FINAL" pixel-window design -- see final_card / PROJECTS_FINAL above), the About Me
    # icons, and the divider. This is the single source of truth for everything under
    # assets/profile/{light,dark}/ -- re-run after any edit in this file.
    desktop_w, mobile_w = 820, 335
    card_h_desktop = APPROVED_DESKTOP_H  # baseline: cards only grow if their own text needs more
    card_h_mobile = max(final_card(th, THEMES[th], p["name"], p["sentence"], p["chips"], p["icon"], W=mobile_w)[1]["h"]
                         for th in ("light", "dark") for p in PROJECTS_FINAL)

    for theme, t in THEMES.items():
        d = OUT / theme
        d.mkdir(parents=True, exist_ok=True)
        (d / "stack-board.svg").write_text(techstack_matrix(t, mobile=False))
        (d / "stack-board-mobile.svg").write_text(techstack_matrix(t, mobile=True))
        for p in PROJECTS_FINAL:
            svg_d, _ = final_card(theme, t, p["name"], p["sentence"], p["chips"], p["icon"], min_h=card_h_desktop, W=desktop_w)
            svg_m, _ = final_card(theme, t, p["name"], p["sentence"], p["chips"], p["icon"], W=mobile_w)
            (d / f"featured-{p['slug']}.svg").write_text(svg_d)
            (d / f"featured-{p['slug']}-mobile.svg").write_text(svg_m)
        (d / "about-database.svg").write_text(about_icon_database(t))
        (d / "about-gradcap.svg").write_text(about_icon_gradcap(t))
        (d / "about-dashboard.svg").write_text(about_icon_dashboard(t))
        (d / "about-briefcase.svg").write_text(about_icon_briefcase(t))
    (OUT / "divider.svg").write_text(divider())
    print("built", sum(1 for _ in OUT.rglob("*.svg")), "svgs")
