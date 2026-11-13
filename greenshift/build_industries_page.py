"""Build the Industries page: hero, the industries grid, a "why TFG" section with the
site's own count-up counter blocks on the brand red, and one closing call to action.
"""
from build_policy_blocks import (
    ACCENT, BODY, GS_PREVIEW_CSS, HERE, INK, RULE, SOFT_WHITE, THREAD_HERO_CSS, Block, Raw, _seed,
    make_hero, write,
)

PAGE_COLOUR = "#3d171d"  # hero only: brand burgundy #80102e at the shared hero darkness
BRAND_RED = ACCENT  # the theme's brand red, as the original stats panel used
PANEL_BG = "var(--wp--preset--color--palette-color-5, var(--theme-palette-color-5, #F0F2F3))"
UPLOADS = "https://thefastenergroup.com/wp-content/uploads/2026/02/"
CONTACT = "https://thefastenergroup.com/contact/"

# (name as GreenShift stores it, anchor, image file, description). Alphabetical, which is
# also the old page's reading order row by row.
INDUSTRIES = [
    ("Agriculture", "agriculture", "agriculture.webp",
     "Agriculture is built on reliability, season after season. We equip producers and ag businesses with the tools, hardware, and fastening solutions they need to keep equipment running, improve efficiency, and work confidently in the field."),
    ("Construction &amp; Infrastructure", "construction", "construction.webp",
     "Construction work leaves no margin for weak materials. From large-scale infrastructure to commercial builds, we supply the tools, fasteners, and jobsite essentials required to meet demanding conditions and deliver lasting results."),
    ("Distribution", "distribution", "distribution.webp",
     "Behind efficient distribution are well-run facilities and dependable systems. We provide the tools, fasteners, and hardware that support warehouse operations, material handling, and everyday facility maintenance."),
    ("Energy &amp; Utilities", "energy", "energy.webp",
     "Downtime isn’t an option in energy and utilities. We support field crews and facilities with the tools, fasteners, and supplies needed to maintain critical infrastructure and keep essential services running."),
    ("Facility Management &amp; Maintenance", "facility-maintenance", "mainentance.webp",
     "Keeping buildings operational takes consistent attention and fast response. We supply maintenance teams with the tools, fasteners, and supplies required for repairs, upgrades, and ongoing facility care."),
    ("Government", "government", "government.webp",
     "As public infrastructure and services evolve, dependable equipment and supplies are essential. We support government departments and agencies with dependable tools, fasteners, and hardware to help maintain facilities, assets, and essential operations."),
    ("Industrial Services", "industrial-services", "industrial.webp",
     "Industrial service work depends on equipment that performs in demanding environments. We supply the tools, fasteners, and hardware needed to support maintenance, repairs, and specialized service work with confidence."),
    ("Manufacturing &amp; Fabrication", "manufacturing", "Manufacturing.webp",
     "Production environments run on precision and consistency. From fabrication shops to full-scale manufacturing, we provide the tools, fasteners, and hardware that support output, maintenance, and continuous improvement."),
    ("Transportation &amp; Logistics", "transportation", "transportation.webp",
     "Moving goods efficiently starts with reliable equipment. We supply transportation and logistics operations with the tools, fasteners, and hardware needed to support fleet maintenance, facilities, and nonstop demand."),
]

CHECKLIST = [
    "Expansive Inventory", "High Quality Fasteners and Anchors", "Comprehensive Power Tool Solutions",
    "Accessories, Hardware, and Supplies for Every Job", "Safety Gear and Protective Equipment You Can Trust",
    "Knowledgeable and Attentive Staff", "Dedicated Outside Sales Representatives",
    "Fast and Reliable Service", "Proudly Canadian Company",
]


def section_heading(caption, title, anchor=None, dark=False):
    return Block(name="Heading", styles={
        "paddingBottom": ["1.5rem"], "marginBottom": ["2.25rem"],
        "borderBottom": [f"2px solid {INK}"],
    }, children=[
        Block("p", text=caption, styles={
            "marginTop": ["0px"], "marginBottom": ["0.44rem"], "fontWeight": ["700"],
            "textTransform": ["uppercase"], "color": [ACCENT],
        }),
        Block("h2", text=title, anchor=anchor, styles={
            "marginTop": ["0px"], "marginBottom": ["0px"], "color": [INK],
        }),
    ])


TILE_CSS = (
    "{CURRENT} .tfgr-ind{display:flex;flex-direction:column;background-color:#ffffff;"
    f"border-right:1px solid {RULE};border-bottom:1px solid {RULE};color:{BODY};}}"
    "{CURRENT} .tfgr-ind img{display:block;width:100%;height:auto;aspect-ratio:16 / 9;object-fit:cover;}"
    "{CURRENT} .tfgr-ind-body{padding:1.25rem 1.5rem 1.5rem;}"
    f"{{CURRENT}} .tfgr-ind-name{{margin:0 0 0.5rem 0;color:{INK};}}"
    "{CURRENT} .tfgr-ind-desc{margin:0;}"
    "@media (max-width: 575.98px){{CURRENT} .tfgr-ind-body{padding:1rem 1.25rem 1.25rem;}}"
)


def industries_panel():
    tiles = []
    for name, anchor, image, desc in INDUSTRIES:
        tiles.append(Block(class_name="tfgr-ind", anchor=anchor, name=name.replace("&amp;", "&"), children=[
            Block("img", json_extra={"src": UPLOADS + image, "alt": "",
                                     "originalWidth": 700, "originalHeight": 500},
                  html_attrs=[("src", UPLOADS + image), ("alt", ""), ("width", "700"),
                              ("height", "500"), ("loading", "lazy")]),
            Block(class_name="tfgr-ind-body", children=[
                Block("h3", text=name, class_name="tfgr-ind-name", text_is_html=True),
                Block("p", text=desc, class_name="tfgr-ind-desc"),
            ]),
        ]))
    grid = Block(name="Industry Tiles", styles={
        "display": ["grid"],
        "gridTemplateColumns": ["repeat(3, 1fr)", "repeat(2, 1fr)", "repeat(2, 1fr)", "repeat(1, 1fr)"],
        "borderTop": [f"1px solid {RULE}"], "borderLeft": [f"1px solid {RULE}"],
        "backgroundColor": ["#ffffff"],
    }, custom_css=TILE_CSS, children=tiles)
    return Block(name="Industries", class_name="tfgr-policy", styles={
        "backgroundColor": [PANEL_BG],
        "paddingTop": ["2.25rem", None, None, "1.5rem"], "paddingBottom": ["2.25rem", None, None, "1.5rem"],
        "paddingLeft": ["1.5rem", None, None, "1rem"], "paddingRight": ["1.5rem", None, None, "1rem"],
    }, children=[
        section_heading("Who we supply", "Supplying the industries that build Western Canada", anchor="industries"),
        grid,
        Block(name="Footer", styles={"marginTop": ["1.5rem"]}, children=[closing_cta()]),
    ])


CHECK_CSS = (
    "{CURRENT}{list-style:none;margin:0;padding:0;display:grid;"
    "grid-template-columns:repeat(2, 1fr);column-gap:2rem;}"
    "{CURRENT} li{position:relative;margin:0;padding:0.6rem 0 0.6rem 1.5rem;"
    f"border-bottom:1px solid {RULE};color:{INK};}}"
    "{CURRENT} li::before{content:\"\";position:absolute;left:0;"
    f"top:calc(0.6rem + 0.5lh - 1px);width:0.75rem;height:2px;background-color:{ACCENT};}}"
    "@media (max-width: 767.98px){{CURRENT}{grid-template-columns:1fr;}}"
)


# The hero's thread lines, without its red edge, for the red numbers card.
CARD_THREADS = (
    "{CURRENT}::before{content:\"\";position:absolute;inset:0;pointer-events:none;"
    "background:repeating-linear-gradient(115deg, rgba(255, 255, 255, 0.08) 0 1px, transparent 1px 14px);"
    "-webkit-mask-image:linear-gradient(to left, #000 10%, transparent 80%);"
    "mask-image:linear-gradient(to left, #000 10%, transparent 80%);}"
    "{CURRENT} > *{position:relative;z-index:1;}"
)


def visit_section():
    """The homepage's store map and province counts (imported here to avoid a circular import)."""
    from build_home_page import map_section
    return map_section()


CHECK3_CSS = CHECK_CSS.replace("grid-template-columns:repeat(2, 1fr);", "grid-template-columns:repeat(3, 1fr);") + (
    "@media (max-width: 991.98px){{CURRENT}{grid-template-columns:repeat(2, 1fr);}}"
    "@media (max-width: 767.98px){{CURRENT}{grid-template-columns:1fr;}}"
)


def why_section():
    return Block(name="Why TFG", children=[
        section_heading("Why TFG", "Everything your business needs to succeed"),
        Block(name="Checklist Card", styles={
            "backgroundColor": ["#ffffff"], "border": [f"1px solid {RULE}"],
            "paddingTop": ["1.5rem", None, None, "1rem"], "paddingBottom": ["1.5rem", None, None, "1rem"],
            "paddingLeft": ["2rem", None, None, "1.25rem"], "paddingRight": ["2rem", None, None, "1.25rem"],
        }, children=[
            Block("ul", custom_css=CHECK3_CSS, children=[Block("li", text=t) for t in CHECKLIST]),
        ]),
    ])


# The red band under the hero. The site's own counter row (two columns that wrap to 2 x 2)
# is laid out four across from here, so the counter blocks themselves stay unchanged.
BAND_CSS = CARD_THREADS + (
    "{CURRENT} .gspb_row,{CURRENT} .gspb_row__content{margin:0 !important;padding:0 !important;max-width:none !important;width:auto !important;}"
    "{CURRENT} .gspb_row__content{display:grid !important;grid-template-columns:repeat(4, minmax(0, 1fr)) !important;"
    "column-gap:1.5rem !important;row-gap:1.5rem !important;}"
    "{CURRENT} .gspb_row__content > .gspb_row__col--6{width:auto !important;max-width:none !important;"
    "flex:none !important;padding:0 !important;margin:0 !important;display:block !important;min-width:0 !important;}"
    # GreenShift's own column styles squeeze the label; make every item in a cell full width.
    "{CURRENT} .gspb_row__content > .gspb_row__col--6 > *{display:block !important;width:100% !important;"
    "max-width:none !important;min-width:0 !important;flex:none !important;}"
    "{CURRENT} .gspb_row__content > .gspb_row__col--6 .gspb_text{white-space:normal !important;"
    "word-break:normal !important;overflow-wrap:normal !important;}"
    "@media (max-width: 575.98px){{CURRENT} .gspb_row__content{grid-template-columns:repeat(2, minmax(0, 1fr)) !important;}}"
)


def stats_band():
    counters = (HERE / "industries-page" / "source-counters.txt").read_text()
    return Block(name="Here to Help You Build", styles={
        "display": ["grid"], "gridTemplateColumns": ["minmax(0, 2fr) minmax(0, 3fr)", "1fr"],
        "columnGap": ["3rem"], "rowGap": ["2rem"], "alignItems": ["center"],
        "position": ["relative"], "overflow": ["hidden"], "backgroundColor": [BRAND_RED],
        "paddingTop": ["2.25rem", None, None, "1.5rem"], "paddingBottom": ["2.25rem", None, None, "1.5rem"],
        "paddingLeft": ["2.25rem", None, None, "1.25rem"], "paddingRight": ["2.25rem", None, None, "1.25rem"],
    }, custom_css=BAND_CSS, children=[
        Block(name="Text", children=[
            Block("h2", text="We Are Here to Help You Build", styles={
                "marginTop": ["0px"], "marginBottom": ["0.75rem"], "color": ["#ffffff"],
            }),
            Block("p", text=("With decades of experience, a wide selection of products, and trusted "
                             "supplier partnerships, we help businesses across Western Canada work "
                             "smarter, faster, and safer."), styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "color": ["rgba(255, 255, 255, 0.85)"],
            }),
        ]),
        Raw(counters),
    ])


SOLID_BUTTON_CSS = (
    "{CURRENT}{display:inline-flex;align-items:center;gap:0.6rem;padding:0.75rem 1.5rem;"
    f"background-color:{ACCENT};border:1px solid {ACCENT};color:#ffffff;font-weight:700;"
    "text-decoration:none;white-space:nowrap;transition:background-color .2s,border-color .2s;}"
    "{CURRENT}::after{content:\"\\2192\";}"
    f"{{CURRENT}}:hover,{{CURRENT}}:focus-visible{{background-color:{INK};border-color:{INK};color:#ffffff;}}"
    f"{{CURRENT}}:focus-visible{{outline:2px solid {ACCENT};outline-offset:2px;}}"
)


def closing_cta():
    return Block(name="Get In Touch", styles={
        "display": ["flex"], "flexWrap": ["wrap"], "alignItems": ["center"],
        "justifyContent": ["space-between"], "columnGap": ["2rem"], "rowGap": ["1.25rem"],
        "backgroundColor": ["#ffffff"], "border": [f"1px solid {RULE}"],
        "paddingTop": ["2rem", None, None, "1.5rem"], "paddingBottom": ["2rem", None, None, "1.5rem"],
        "paddingLeft": ["2rem", None, None, "1.25rem"], "paddingRight": ["2rem", None, None, "1.25rem"],
    }, children=[
        Block(children=[
            Block("h2", text="And many more", styles={
                "marginTop": ["0px"], "marginBottom": ["0.5rem"], "color": [INK],
            }),
            Block("p", text="Don’t see your industry? Tell us what you’re working on and our team will help you find the right products.", styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "maxWidth": ["40rem"], "color": [BODY],
            }),
        ]),
        Block("a", text="Get in touch", href=CONTACT, custom_css=SOLID_BUTTON_CSS),
    ])


def body():
    _seed["slug"], _seed["n"] = "industries", 0
    return Block(name="Industries Page", class_name="tfgr-page", styles={
        "display": ["flex"], "flexDirection": ["column"], "rowGap": ["4.5rem", "3.38rem", None, "2.25rem"],
        # The red band is pulled up over the bottom of the hero.
        "marginTop": ["-4rem", None, None, "-3rem"], "position": ["relative"], "zIndex": ["2"],
    }, custom_css="{CURRENT} [id]{scroll-margin-top:2rem;}",
        children=[stats_band(), industries_panel(), why_section(), visit_section()])


def hero():
    return make_hero(
        seed="industries-hero", bg=PAGE_COLOUR, caption="Industries", title="Industries We Serve",
        intro=("Our team of specialists have deep expertise across a range of industries. We "
               "offer solutions and services designed to help businesses of all types get the "
               "equipment they need to build."),
        buttons=[("Explore industries", "#industries")],
        accent=ACCENT, pattern_css=THREAD_HERO_CSS, caption_color=SOFT_WHITE,
    )


PAGE = {"dir": "industries-page", "title": "Industries We Serve", "preview_css": GS_PREVIEW_CSS + """
body > .tfgr-page{max-width:1200px;margin-left:auto;margin-right:auto}
.gs-counter{font-size:50px;line-height:1em;font-weight:600;color:#fff;margin-bottom:10px}
.gspb_text{color:#ffffffd6;font-weight:500}
.gspb_row__col--6{width:50%;padding:0 25px 40px 0;box-sizing:border-box}
"""}

if __name__ == "__main__":
    write(PAGE, body(), before=hero())
