"""Build the homepage.

The hero is the site's own (it works as intended) with targeted fixes only: live URLs
instead of staging, an h1, and alt text for the company logos. Below it: "Stronger
Together" as real text with the impact counters, an industries band, and the about teaser.
The count-up counters are the site's own GreenShift blocks, reused unchanged.
"""
import re

from build_policy_blocks import (
    ACCENT, BODY, GS_PREVIEW_CSS, HERE, INK, RULE, SOFT_WHITE, THREAD_HERO_CSS,
    Block, Raw, _seed, button_css, write,
)
from build_industries_page import SOLID_BUTTON_CSS, section_heading

LIVE = "https://thefastenergroup.com/"
STAGING = "https://s48517.p261.sites.pressdns.com/"
DARK = "#0d0e10"  # TFG black, the homepage hero colour
PANEL_BG = "var(--wp--preset--color--palette-color-5, var(--theme-palette-color-5, #F0F2F3))"
HERO_ROW = "#gspb_row-id-gsbp-2f17145"  # the site's own hero row

LOGO_ALTS = {  # logo file -> company name, for screen readers and search
    "BC-Hex-Logo.png": "BC Fasteners and Tools",
    "BC2000-Hex-Logo.png": "BC Fasteners and Tools 2000",
    "Calgary-Hex-Logo.png": "Calgary Fasteners and Tools",
    "Construction-Hex-Logo.png": "Construction Fasteners and Tools",
    "Edmonton-Hex-Logo.png": "Edmonton Fasteners and Tools",
    "Lethbridge-Hex-Logo.png": "Lethbridge Fasteners and Tools",
    "Mid-Can-Hex-Logo.png": "Mid Canada Fasteners and Tools",
    "Red-Deer-Hex-Logo.png": "Red Deer Fasteners and Tools",
    "JD-Hex-Logo.png": "JD Industrial Supplies",
}


def replace_once(s, old, new, count=1):
    assert s.count(old) == count, f"expected {count}x: {old[:60]}"
    return s.replace(old, new)


def hero():
    s = (HERE / "home-page" / "source-hero.txt").read_text().strip()
    # Two staging buttons and one staging photo -> live site (each in JSON and markup).
    s = replace_once(s, STAGING, LIVE, count=6)
    # "We are The Fastener Group" becomes the page's h1.
    s = replace_once(s, '{"id":"gsbp-9655ebd","headingContent"', '{"id":"gsbp-9655ebd","headingTag":"h1","headingContent"')
    s = replace_once(s, '<h2 id="gspb_heading-id-gsbp-9655ebd"', '<h1 id="gspb_heading-id-gsbp-9655ebd"')
    s = replace_once(s, 'The Fastener Group</mark></h2>', 'The Fastener Group</mark></h1>')
    # Alt text on the logo row; sizes and layout untouched.
    for file, name in LOGO_ALTS.items():
        s, n = re.subn(rf'({re.escape(file)}","mediaid":\d+,"alt":)""', rf'\1"{name}"', s)
        assert n == 1, file
        s = replace_once(s, f'{file}" data-src="" alt=""', f'{file}" data-src="" alt="{name}"')
    return Raw(s)


# The thread-line pattern and red bottom edge used on every page hero, applied to the
# homepage hero's existing overlay layer. The hero row keeps its old overlay settings so
# the block stays valid in the editor; these rules override the old hexagon image.
HERO_PATTERN_CSS = (
    f"{HERO_ROW}{{position:relative;box-shadow:inset 0 -4px 0 {ACCENT};}}"
    f"{HERO_ROW} > .gspb_backgroundOverlay{{position:absolute;inset:0;pointer-events:none;opacity:1 !important;"
    "background:repeating-linear-gradient(115deg, rgba(255, 255, 255, 0.07) 0 1px, transparent 1px 14px) !important;"
    "-webkit-mask-image:linear-gradient(to left, #000 20%, transparent 75%);"
    "mask-image:linear-gradient(to left, #000 20%, transparent 75%);}"
    f"{HERO_ROW} > .gspb_row__content{{position:relative;z-index:1;}}"
)


def counter_cells():
    return [Raw(c.strip()) for c in (HERE / "home-page" / "source-counters.txt").read_text().split("=====")]


def caption(text, color=ACCENT):
    return Block("p", text=text, styles={
        "marginTop": ["0px"], "marginBottom": ["0.44rem"], "fontWeight": ["700"],
        "textTransform": ["uppercase"], "color": [color],
    })


# "Stronger" slides in from the left and "Together" from the right as the heading
# scrolls into view, echoing the old image animation. Pure CSS: it runs in the editor
# too, is skipped for people who turn off motion, and browsers without scroll-driven
# animations simply show the words.
REVEAL_CSS = (
    "@keyframes tfgr-in-left{from{opacity:0;transform:translateX(-2rem);}to{opacity:1;transform:none;}}"
    "@keyframes tfgr-in-right{from{opacity:0;transform:translateX(2rem);}to{opacity:1;transform:none;}}"
    "{CURRENT} span{display:inline-block;}"
    "@media (prefers-reduced-motion: no-preference){@supports (animation-timeline: view()){"
    "{CURRENT} .tfgr-st-1{animation:tfgr-in-left linear both;animation-timeline:view();animation-range:entry 10% cover 35%;}"
    "{CURRENT} .tfgr-st-2{animation:tfgr-in-right linear both;animation-timeline:view();animation-range:entry 20% cover 45%;}"
    "}}"
)

CELL_CSS = (
    "{CURRENT} > div{background-color:#ffffff;padding:1.75rem 1.5rem;}"
    "{CURRENT} .gspb_text{color:#5f6468;}"
    "@media (max-width: 575.98px){{CURRENT} > div{padding:1.25rem 1rem;}}"
)


def stat_grid(cells, cols):
    return Block(name="Numbers", styles={
        "display": ["grid"], "gridTemplateColumns": cols,
        "columnGap": ["1px"], "rowGap": ["1px"],
        "backgroundColor": [RULE], "border": [f"1px solid {RULE}"],
    }, custom_css=CELL_CSS, children=[Block(children=[c]) for c in cells])


def numbers_section(cells):
    return Block(name="Stronger Together", custom_css=HERO_PATTERN_CSS, styles={
        "marginTop": ["5.06rem", None, None, "3.38rem"], "marginBottom": ["5.06rem", None, None, "3.38rem"],
    }, children=[
        Block(name="Heading", styles={
            "paddingBottom": ["1.5rem"], "marginBottom": ["2.25rem"], "borderBottom": [f"2px solid {INK}"],
        }, children=[
            caption("Our impact in numbers"),
            Block("h2", name="Stronger Together", styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "color": [INK],
                "fontSize": ["var(--wp--preset--font-size--giga, clamp(3rem, 5vw, 4.5rem))"],
                "lineHeight": ["1.05"], "textTransform": ["uppercase"],
            }, custom_css=REVEAL_CSS, children=[
                Block("span", text="Stronger", class_name="tfgr-st-1"),
                Block("span", text="Together", class_name="tfgr-st-2", styles={"color": [ACCENT]}),
            ]),
        ]),
        stat_grid(cells, ["repeat(4, 1fr)", "repeat(2, 1fr)"]),
    ])


# (name as stored, Industries page anchor, image)
INDUSTRY_TILES = [
    ("Energy &amp; Utilities", "energy", "2025/09/pexels-pixabay-247763-1-scaled.jpg", ""),
    ("Manufacturing &amp; Fabrication", "manufacturing", "2026/02/pexels-rezwan-1216544-scaled.webp", ""),
    ("Construction &amp; Infrastructure", "construction", "2025/09/pexels-pixabay-159358-scaled.jpg", ""),
]

TILE_CSS = (
    "{CURRENT} .tfgr-home-ind{display:flex;flex-direction:column;background-color:#ffffff;"
    f"color:{INK};text-decoration:none;}}"
    "{CURRENT} .tfgr-home-ind img{display:block;width:100%;height:auto;aspect-ratio:3 / 2;object-fit:cover;}"
    "{CURRENT} .tfgr-home-ind-name{display:flex;justify-content:space-between;align-items:center;gap:1rem;"
    "margin:0;padding:1.1rem 1.5rem;}"
    f"{{CURRENT}} .tfgr-home-ind-name::after{{content:\"\\2192\";color:{ACCENT};}}"
    "{CURRENT} .tfgr-home-ind:hover .tfgr-home-ind-name{text-decoration:underline;}"
    "{CURRENT} .tfgr-home-ind:focus-visible{outline:2px solid #ffffff;outline-offset:3px;}"
)


def industries_band():
    tiles = [
        Block("a", class_name="tfgr-home-ind", href=f"{LIVE}services/#{anchor}",
              name=name.replace("&amp;", "&"), children=[
                  Block("img", json_extra={"src": LIVE + "wp-content/uploads/" + img, "alt": alt,
                                           "originalWidth": 2560, "originalHeight": 1707},
                        html_attrs=[("src", LIVE + "wp-content/uploads/" + img), ("alt", alt),
                                    ("width", "2560"), ("height", "1707"), ("loading", "lazy")]),
                  Block("h3", text=name, class_name="tfgr-home-ind-name", text_is_html=True),
              ])
        for name, anchor, img, alt in INDUSTRY_TILES
    ]
    header = Block(name="Heading", styles={
        "display": ["flex"], "flexWrap": ["wrap"], "alignItems": ["flex-end"],
        "justifyContent": ["space-between"], "columnGap": ["2rem"], "rowGap": ["1.25rem"],
        "paddingBottom": ["1.5rem"], "marginBottom": ["2.25rem"],
        "borderBottom": ["2px solid rgba(255, 255, 255, 0.85)"],
    }, children=[
        Block(styles={"maxWidth": ["40rem"]}, children=[
            caption("Industries", SOFT_WHITE),
            Block("h2", text="Solutions built for industries that rely on precision and quality", styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "color": ["#ffffff"],
            }),
        ]),
        Block("a", text="See more industries", href=f"{LIVE}services/", custom_css=button_css("0", "\\2192", accent=ACCENT)),
    ])
    grid = Block(name="Industry Tiles", styles={
        "display": ["grid"], "gridTemplateColumns": ["repeat(3, 1fr)", "repeat(1, 1fr)"],
        "columnGap": ["1.5rem"], "rowGap": ["1.5rem"],
    }, custom_css=TILE_CSS, children=tiles)
    content = Block(name="Content Area", styles={
        "maxWidth": ["100%"], "width": ["var(--wp--style--global--wide-size, 1200px)"],
    }, json_extra={"isVariation": "contentarea"}, children=[header, grid])
    return Block("section", name="Industries", align="full", styles={
        "display": ["flex"], "flexDirection": ["column"], "alignItems": ["center"],
        "position": ["relative"], "overflow": ["hidden"], "backgroundColor": [DARK],
        "paddingTop": ["5.06rem", None, None, "3.38rem"], "paddingBottom": ["5.06rem", None, None, "3.38rem"],
        "paddingLeft": ["var(--wp--custom--spacing--side, min(3vw, 20px))"],
        "paddingRight": ["var(--wp--custom--spacing--side, min(3vw, 20px))"],
        "marginTop": ["0px"], "marginBottom": ["0px"],
    }, json_extra={"isVariation": "contentcolumns"}, custom_css=THREAD_HERO_CSS, children=[content])


def about_section(cells):
    photo = LIVE + "wp-content/uploads/2026/02/20220708_123454-scaled.webp"
    return Block(name="About", styles={
        "display": ["grid"], "gridTemplateColumns": ["repeat(2, 1fr)", "repeat(1, 1fr)"],
        "columnGap": ["4.5rem", "2.25rem"], "rowGap": ["2.25rem"], "alignItems": ["center"],
        "marginTop": ["5.06rem", None, None, "3.38rem"], "marginBottom": ["5.06rem", None, None, "3.38rem"],
    }, children=[
        Block(name="Text", children=[
            caption("About us"),
            Block("h2", text="Find out who we are and where we started", styles={
                "marginTop": ["0px"], "marginBottom": ["2.25rem"], "color": [INK],
            }),
            stat_grid(cells, ["repeat(2, 1fr)"]),
            Block(styles={"marginTop": ["2.25rem"]}, children=[
                Block("a", text="Learn about us", href=f"{LIVE}leadership-team/", custom_css=SOLID_BUTTON_CSS),
            ]),
        ]),
        Block("img", name="Photo", styles={
            "display": ["block"], "width": ["100%"], "height": ["auto"],
        }, custom_css="{CURRENT}{aspect-ratio:4 / 3;object-fit:cover;}",
            json_extra={"src": photo, "alt": "", "originalWidth": 2560, "originalHeight": 1920},
            html_attrs=[("src", photo), ("alt", ""), ("width", "2560"), ("height", "1920"), ("loading", "lazy")]),
    ])


OUTLINE_DARK_CSS = (
    "{CURRENT}{display:inline-flex;align-items:center;gap:0.6rem;padding:0.75rem 1.5rem;"
    f"border:1px solid {INK};color:{INK};font-weight:700;text-decoration:none;white-space:nowrap;"
    "transition:background-color .2s,color .2s;}"
    "{CURRENT}::after{content:\"\\2192\";}"
    f"{{CURRENT}}:hover,{{CURRENT}}:focus-visible{{background-color:{INK};color:#ffffff;}}"
    f"{{CURRENT}}:focus-visible{{outline:2px solid {ACCENT};outline-offset:2px;}}"
)


def closing_band():
    return Block(name="Visit Us", styles={
        "display": ["flex"], "flexWrap": ["wrap"], "alignItems": ["center"], "justifyContent": ["space-between"],
        "columnGap": ["2rem"], "rowGap": ["1.5rem"], "backgroundColor": [PANEL_BG],
        "borderTop": [f"3px solid {ACCENT}"],
        "paddingTop": ["2.25rem", None, None, "1.5rem"], "paddingBottom": ["2.25rem", None, None, "1.5rem"],
        "paddingLeft": ["2.25rem", None, None, "1.25rem"], "paddingRight": ["2.25rem", None, None, "1.25rem"],
        "marginBottom": ["5.06rem", None, None, "3.38rem"],
    }, children=[
        Block(styles={"maxWidth": ["40rem"]}, children=[
            caption("Visit us"),
            Block("h2", text="Find your nearest TFG store", styles={
                "marginTop": ["0px"], "marginBottom": ["0.5rem"], "color": [INK],
            }),
            Block("p", text="Talk to our team in person, or send us a message and we’ll get back to you.", styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "color": [BODY],
            }),
        ]),
        Block(name="Buttons", styles={
            "display": ["flex"], "flexWrap": ["wrap"], "columnGap": ["0.75rem"], "rowGap": ["0.75rem"],
        }, children=[
            Block("a", text="See our stores", href=f"{LIVE}branches/", custom_css=SOLID_BUTTON_CSS),
            Block("a", text="Contact us", href=f"{LIVE}contact/", custom_css=OUTLINE_DARK_CSS),
        ]),
    ])


def body():
    _seed["slug"], _seed["n"] = "home", 0
    cells = counter_cells()
    return [numbers_section(cells[:4]), industries_band(), about_section(cells[4:]), closing_band()]


PAGE = {"dir": "home-page", "title": "The Fastener Group", "preview_css": GS_PREVIEW_CSS + """
body > div:not(.gspb_row){max-width:1200px;margin-left:auto;margin-right:auto}
.gspb_row-id-gsbp-2f17145{background:#0d0e10;color:#fff;padding:180px 40px 40px;margin:0 -40px}
.gspb_row-id-gsbp-2f17145 > .gspb_row__content{max-width:1200px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:60px}
.gspb_row-id-gsbp-2f17145 .gspb_row__col--6{width:auto;padding:0}
.gspb_heading-id-gsbp-cb84b76{font-size:20px}
.gspb_heading-id-gsbp-9655ebd{font-size:70px;line-height:1.2em;text-transform:uppercase;margin:0 0 10px}
.gspb_heading-id-gsbp-9655ebd mark{background:none;color:#b11f24}
.gspb_text-id-gsbp-4202ed7{margin:20px 0 120px;padding-right:20px}
.text-anim__word{display:none}.text-anim__word--in{display:inline;font-weight:700}
.gspb-buttonbox{display:inline-flex;align-items:center;gap:10px;padding:14px 24px;background:#b11f24;color:#fff;font-weight:700;text-decoration:none;border-radius:4px}
.gspb_button-id-gsbp-cf30e04 .gspb-buttonbox{background:none;padding:0}
.gspb-buttonbox svg{width:10px!important;height:10px!important;margin:0!important;fill:#fff}
.gspb_container-gsbp-2884193{display:flex;align-items:center;gap:30px;margin:0 0 50px}
.gspb_container-gsbp-c10170d{display:flex;gap:10px;align-items:flex-end}
.gspb_container-gsbp-c10170d img{height:50px;width:50px;object-fit:contain}
.gspb_col-id-gsbp-97a4559 > .gspb_row > .gspb_row__content{display:grid;grid-template-columns:1.2fr 1fr;gap:30px}
.gspb_col-id-gsbp-97a4559 img{display:block;width:100%;height:300px;object-fit:cover;border-radius:10px}
.gspb_image-id-gsbp-c116c17{margin-bottom:30px}
.gspb_col-id-gsbp-77ec8b0 img{height:630px}
@media (max-width:991.98px){.gspb_row-id-gsbp-2f17145 > .gspb_row__content{grid-template-columns:1fr}.gspb_col-id-gsbp-97a4559{display:none}}
@media (max-width:575.98px){.gspb_row-id-gsbp-2f17145{padding:140px 20px 30px;margin:0 -40px}.gspb_heading-id-gsbp-9655ebd{font-size:44px}.gspb_container-gsbp-c10170d{display:none}.gspb_container-gsbp-2884193{flex-wrap:wrap}}
.gs-counter{font-size:70px;line-height:1em;font-weight:600;color:#0f1a17;margin-bottom:10px}
.gspb_counter-id-gsbp-a27096d .gs-counter,.gspb_counter-id-gsbp-d9d6fe0 .gs-counter{font-size:30px}
.tfgr-st-1,.tfgr-st-2{animation:none!important}
"""}


if __name__ == "__main__":
    write(PAGE, body(), before=hero().serialize())
