"""Build the Forced Labour Report page: the thread-line hero, a short key-facts strip, then
the four report pages in a simple document viewer with page jump links.
"""
from build_policy_blocks import (
    ACCENT, BODY, GS_PREVIEW_CSS, INK, RULE, SOFT_WHITE, THREAD_HERO_CSS, Block, _seed,
    make_hero, write,
)
from build_industries_page import section_heading

PAGE_COLOUR = "#0d0e10"  # hero only: TFG black
PANEL_BG = "var(--wp--preset--color--palette-color-5, var(--theme-palette-color-5, #F0F2F3))"
PAGES = [
    "https://thefastenergroup.com/wp-content/uploads/2026/06/TFG-Forced-Labour-Report_2026__Page_1.webp",
    "https://thefastenergroup.com/wp-content/uploads/2026/06/TFG-Forced-Labour-Report_2026__Page_2.webp",
    "https://thefastenergroup.com/wp-content/uploads/2026/06/TFG-Forced-Labour-Report_2026__Page_3.webp",
    "https://thefastenergroup.com/wp-content/uploads/2026/06/TFG-Forced-Labour-Report_2026__Page_4.webp",
]

# (label, value) taken from the report itself.
FACTS = [
    ("Reporting period", "January 1 to December 31, 2025"),
    ("Legislation", "Fighting Against Forced Labour and Child Labour in Supply Chains Act (Bill S-211)"),
    ("Approved by", "Lylle Kephart, President and CEO, May 29, 2026"),
]

FACTS_CSS = (
    f"{{CURRENT}} .tfgr-fact{{background-color:#ffffff;border-right:1px solid {RULE};border-bottom:1px solid {RULE};"
    "padding:1.25rem 1.5rem;}"
    f"{{CURRENT}} .tfgr-fact-label{{margin:0 0 0.35rem 0;font-weight:700;text-transform:uppercase;color:{ACCENT};}}"
    f"{{CURRENT}} .tfgr-fact-value{{margin:0;color:{INK};}}"
    "@media (max-width: 575.98px){{CURRENT} .tfgr-fact{padding:1rem 1.25rem;}}"
)

JUMP_CSS = (
    "{CURRENT}{display:flex;flex-wrap:wrap;align-items:center;gap:0.5rem;}"
    f"{{CURRENT}} .tfgr-jump-label{{margin:0 0.5rem 0 0;font-weight:700;color:{INK};}}"
    f"{{CURRENT}} a{{display:inline-flex;align-items:center;justify-content:center;min-width:2.5rem;height:2.5rem;"
    f"padding:0 0.75rem;border:1px solid {RULE};background-color:#ffffff;color:{INK};font-weight:700;"
    "text-decoration:none;transition:border-color .2s,color .2s;}"
    f"{{CURRENT}} a:hover,{{CURRENT}} a:focus-visible{{border-color:{ACCENT};color:{ACCENT};}}"
)


def facts():
    return Block(name="Key Facts", styles={
        "display": ["grid"], "gridTemplateColumns": ["repeat(3, 1fr)", None, "1fr"],
        "borderTop": [f"1px solid {RULE}"], "borderLeft": [f"1px solid {RULE}"],
        "marginBottom": ["2.25rem"],
    }, custom_css=FACTS_CSS, children=[
        Block(class_name="tfgr-fact", name=label, children=[
            Block("p", text=label, class_name="tfgr-fact-label"),
            Block("p", text=value, class_name="tfgr-fact-value"),
        ]) for label, value in FACTS
    ])


def jump_links():
    return Block(name="Page Links", custom_css=JUMP_CSS, styles={"marginBottom": ["1.5rem"]}, children=[
        Block("p", text="Go to page", class_name="tfgr-jump-label"),
        *[Block("a", text=str(i), href=f"#report-page-{i}",
                html_attrs=[("aria-label", f"Page {i}")]) for i in range(1, len(PAGES) + 1)],
    ])


def report_pages():
    total = len(PAGES)
    pages = []
    for i, src in enumerate(PAGES, 1):
        pages.append(Block(name=f"Page {i}", anchor=f"report-page-{i}", children=[
            Block("p", text=f"Page {i} of {total}", styles={
                "marginTop": ["0px"], "marginBottom": ["0.5rem"], "fontWeight": ["700"], "color": [BODY],
            }),
            Block("img", json_extra={"src": src, "alt": f"Forced Labour Report, page {i}",
                                     "originalWidth": 1700, "originalHeight": 2200},
                  html_attrs=[("src", src), ("alt", f"Forced Labour Report, page {i}"),
                              ("width", "1700"), ("height", "2200"), ("loading", "lazy")],
                  styles={"display": ["block"], "width": ["100%"], "height": ["auto"],
                          "border": [f"1px solid {RULE}"], "backgroundColor": ["#ffffff"]}),
        ]))
    return Block(name="Report Pages", styles={
        "display": ["flex"], "flexDirection": ["column"], "rowGap": ["2.25rem", None, None, "1.5rem"],
        "maxWidth": ["52rem"], "marginLeft": ["auto"], "marginRight": ["auto"],
    }, children=pages)


def panel():
    return Block(name="Forced Labour Report", class_name="tfgr-policy", anchor="report", styles={
        "backgroundColor": [PANEL_BG],
        "paddingTop": ["2.25rem", None, None, "1.5rem"], "paddingBottom": ["2.25rem", None, None, "1.5rem"],
        "paddingLeft": ["1.5rem", None, None, "1rem"], "paddingRight": ["1.5rem", None, None, "1rem"],
    }, children=[
        section_heading("At a glance", "2025 reporting year"),
        facts(),
        Block(name="Viewer", styles={"maxWidth": ["52rem"], "marginLeft": ["auto"], "marginRight": ["auto"]},
              children=[jump_links()]),
        report_pages(),
    ])


def body():
    _seed["slug"], _seed["n"] = "report", 0
    return Block(name="Report Page", class_name="tfgr-page", styles={
        # The panel is pulled up over the bottom of the hero.
        "marginTop": ["-4rem", None, None, "-3rem"], "position": ["relative"], "zIndex": ["2"],
        "marginBottom": ["4.5rem", None, None, "2.25rem"],
    }, custom_css="{CURRENT} [id]{scroll-margin-top:2rem;}", children=[panel()])


def hero():
    return make_hero(
        seed="report-hero", bg=PAGE_COLOUR, caption="Bill S-211", title="Forced Labour Report",
        intro=("Our annual report under Canada’s Fighting Against Forced Labour and Child Labour in "
               "Supply Chains Act, covering January 1 to December 31, 2025."),
        buttons=[("Read the report", "#report")],
        accent=ACCENT, pattern_css=THREAD_HERO_CSS, caption_color=SOFT_WHITE,
    )


PAGE = {"dir": "report-page", "title": "Forced Labour Report", "preview_css": GS_PREVIEW_CSS + """
body > .tfgr-page{max-width:1200px;margin-left:auto;margin-right:auto}
"""}

if __name__ == "__main__":
    write(PAGE, body(), before=hero())
