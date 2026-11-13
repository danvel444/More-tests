"""Build the sidebar "Here to Help You Build" card for the Blocksy Main Sidebar widget area.

It matches the red numbers band on the Industries page: square corners, the thread-line
pattern, the site's own count-up counter blocks (unchanged) in a 2 x 2 grid, and a
"Find your store" button.
"""
from build_policy_blocks import ACCENT, GS_PREVIEW_CSS, SOFT_WHITE, Block, Raw, _seed, write
from build_industries_page import CARD_THREADS, counter_cells

STORES = "https://thefastenergroup.com/branches/"

# Thin white lines between the four numbers: the grid's gap shows the line colour behind.
NUMBERS_CSS = (
    "{CURRENT} > div{background-color:" + "var(--wp--preset--color--palette-color-1, var(--theme-palette-color-1, #b11f24))"
    ";padding:1rem 0.25rem 1rem 0;}"
    "{CURRENT} > div:nth-child(even){padding-left:1rem;}"
    "{CURRENT} .gs-counter{line-height:1;}"
)

OUTLINE_WHITE_CSS = (
    "{CURRENT}{display:inline-flex;align-items:center;gap:0.6rem;padding:0.6rem 1.25rem;"
    "border:1px solid #ffffff;color:#ffffff;font-weight:700;text-decoration:none;"
    "transition:background-color .2s,color .2s;}"
    "{CURRENT}::after{content:\"\\2192\";}"
    "{CURRENT}:hover,{CURRENT}:focus-visible{background-color:#ffffff;color:#1d1f21;}"
    "{CURRENT}:focus-visible{outline:2px solid #ffffff;outline-offset:2px;}"
)


def card():
    _seed["slug"], _seed["n"] = "sidebar-help", 0
    numbers = Block(name="Numbers", styles={
        "display": ["grid"], "gridTemplateColumns": ["repeat(2, minmax(0, 1fr))"],
        "columnGap": ["1px"], "rowGap": ["1px"],
        "backgroundColor": ["rgba(255, 255, 255, 0.25)"],
        "marginTop": ["1.5rem"], "marginBottom": ["1.75rem"],
    }, custom_css=NUMBERS_CSS, children=[Block(name="Counter", children=[Raw(c)]) for c in counter_cells()])
    return Block(name="Here to Help You Build", styles={
        "position": ["relative"], "overflow": ["hidden"], "backgroundColor": [ACCENT],
        "paddingTop": ["1.75rem"], "paddingBottom": ["1.75rem"],
        "paddingLeft": ["1.75rem"], "paddingRight": ["1.75rem"],
    }, custom_css=CARD_THREADS, children=[
        Block("p", text="Why TFG", styles={
            "marginTop": ["0px"], "marginBottom": ["0.5rem"], "fontWeight": ["700"],
            "textTransform": ["uppercase"], "color": [SOFT_WHITE],
        }),
        Block("h3", text="We Are Here to Help You Build", styles={
            "marginTop": ["0px"], "marginBottom": ["0.75rem"], "color": ["#ffffff"],
        }),
        Block("p", text=("With decades of experience, a wide selection of products, and trusted "
                         "supplier partnerships, we help businesses across Western Canada work "
                         "smarter, faster, and safer."), styles={
            "marginTop": ["0px"], "marginBottom": ["0px"], "color": ["rgba(255, 255, 255, 0.85)"],
        }),
        numbers,
        Block("a", text="Find your store", href=STORES, custom_css=OUTLINE_WHITE_CSS),
    ])


PAGE = {"dir": "sidebar-widget", "title": "Sidebar Widget", "preview_css": GS_PREVIEW_CSS + """
body > div{max-width:340px}
.gs-counter{font-size:36px;font-weight:600;color:#fff;margin-bottom:8px}
.gspb_text{color:#ffffffd6;font-weight:500}
"""}

if __name__ == "__main__":
    write(PAGE, card())
