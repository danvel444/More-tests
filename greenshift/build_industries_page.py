"""Build the Industries page: hero, the industries grid, a "why TFG" section with the
site's own count-up counter blocks, and one closing call to action.

The page colour (the hero's wine) returns as the stats panel background, so each page's
hero colour carries into its body.
"""
from build_policy_blocks import (
    ACCENT, BODY, GS_PREVIEW_CSS, HERE, HERO_CSS, INK, RULE, Block, Raw, _seed, make_hero, write,
)

PAGE_COLOUR = "#3a0916"
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
    "{CURRENT} .tfgr-ind img{display:block;width:100%;height:auto;aspect-ratio:7 / 5;object-fit:cover;}"
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


def why_section():
    counters = (HERE / "industries-page" / "source-counters.txt").read_text()
    checklist_card = Block(name="Everything Your Business Needs", styles={
        "backgroundColor": ["#ffffff"], "border": [f"1px solid {RULE}"],
        "paddingTop": ["2rem", None, None, "1.5rem"], "paddingBottom": ["2rem", None, None, "1.5rem"],
        "paddingLeft": ["2rem", None, None, "1.25rem"], "paddingRight": ["2rem", None, None, "1.25rem"],
    }, children=[
        Block("h3", text="Everything Your Business Needs to Succeed", styles={
            "marginTop": ["0px"], "marginBottom": ["1rem"], "color": [INK],
        }),
        Block("ul", custom_css=CHECK_CSS, children=[Block("li", text=t) for t in CHECKLIST]),
    ])
    stats_card = Block(name="Here to Help You Build", styles={
        "position": ["relative"], "overflow": ["hidden"], "backgroundColor": [PAGE_COLOUR],
        "paddingTop": ["2rem", None, None, "1.5rem"], "paddingBottom": ["2rem", None, None, "1.5rem"],
        "paddingLeft": ["2rem", None, None, "1.25rem"], "paddingRight": ["2rem", None, None, "1.25rem"],
    }, custom_css=HERO_CSS, children=[
        Block("h3", text="We Are Here to Help You Build", styles={
            "marginTop": ["0px"], "marginBottom": ["1rem"], "color": ["#ffffff"],
        }),
        Block("p", text=("With decades of experience, a wide selection of products, and trusted "
                         "supplier partnerships, we help businesses across Western Canada work "
                         "smarter, faster, and safer."), styles={
            "marginTop": ["0px"], "marginBottom": ["2.25rem"], "color": ["rgba(255, 255, 255, 0.85)"],
        }),
        Raw(counters),
    ])
    return Block(name="Why TFG", children=[
        section_heading("Why TFG", "Expertise, reliable products and dedicated support"),
        Block(name="Two Columns", styles={
            "display": ["grid"], "gridTemplateColumns": ["repeat(2, 1fr)", "repeat(1, 1fr)"],
            "columnGap": ["2.25rem"], "rowGap": ["2.25rem"], "alignItems": ["stretch"],
        }, children=[checklist_card, stats_card]),
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
        # The industries panel is pulled up over the bottom of the hero.
        "marginTop": ["-4rem", None, None, "-3rem"], "position": ["relative"], "zIndex": ["2"],
    }, custom_css="{CURRENT} [id]{scroll-margin-top:2rem;}",
        children=[industries_panel(), why_section(), closing_cta()])


def hero():
    return make_hero(
        seed="industries-hero", bg=PAGE_COLOUR, caption="Industries", title="Industries We Serve",
        intro=("Our team of specialists have deep expertise across a range of industries. We "
               "offer solutions and services designed to help businesses of all types get the "
               "equipment they need to build."),
        buttons=[("Explore industries", "#industries")],
    )


PAGE = {"dir": "industries-page", "title": "Industries We Serve", "preview_css": GS_PREVIEW_CSS + """
body > .tfgr-page{max-width:1200px;margin-left:auto;margin-right:auto}
.gs-counter{font-size:50px;line-height:1em;font-weight:600;color:#fff;margin-bottom:10px}
.gspb_text{color:#ffffffd6;font-weight:500}
.gspb_row__col--6{width:50%;padding:0 25px 40px 0;box-sizing:border-box}
"""}

if __name__ == "__main__":
    write(PAGE, body(), before=hero())
