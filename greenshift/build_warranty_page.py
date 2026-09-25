"""Build the warranty and service page: the site's hero, then an A to Z brand directory.

Reuses the block format and palette from build_policy_blocks.py. To add a vendor,
add a line to BRANDS; the list is sorted by name when the page is built.
"""
from build_policy_blocks import (
    ACCENT, BODY, GS_PREVIEW_CSS, HERE, INK, RULE, Block, _seed, write,
)

UPLOADS = "https://thefastenergroup.com/wp-content/uploads/2026/08/"

# (display name, logo file, alt text, service page)
BRANDS = [
    ("Bosch", "Bosch-Logo.webp", "Bosch Tools", "https://www.boschtools.com/ca/en/service/"),
    ("DeWalt", "DeWalt-Logo.webp", "Dewalt Tools", "https://www.toolservicenet.ca/en/"),
    ("EGO", "Ego-Power-Tools-Logo.webp", "Ego Tools", "https://egopowerplus.com/support"),
    ("Fein", "Fein-Logo.webp", "Fein Tools", "https://fein.com/en_ca/service/"),
    ("Guardian Fall Protection", "Guardian-Fall-Logo.webp", "Guardian Fall Protection", "https://guardianfall.com/en-CA/support/find-your-repair-center"),
    ("King Canada", "King-Canada-Logo.webp", "King Canada", "https://www.kingcanada.com/en/service-centers/"),
    ("Makita", "Makita-Logo.webp", "Makita Tools", "https://www.makita.ca/index2new.php?event=memberlanding2"),
    ("Milwaukee", "Milwaukee-Red-Logo.webp", "Milwaukee Tools", "https://service.milwaukeetool.ca/support"),
    ("MSA Safety", "MSA-Logo.webp", "MSA Safety", "https://ca.msasafety.com/service"),
    ("Ridgid", "Ridgid-Logo.webp", "Ridgid Tools", "https://www.ridgid.com/ca/en/service-and-support"),
    ("Stihl", "Stihl-Logo.webp", "Stihl Tools", "https://www.stihl.ca/en/service-events/dealer-services/repair"),
    ("Sumner", "Sumner-Logo.webp", "Sumner Material Lifts", "https://sumner.com/services/"),
    ("Walter", "Walter-Logo.webp", "Walter Tools", "https://www.walter.com/ca/contact-us"),
]
LOGO_W, LOGO_H = 660, 225  # every logo file is 660 x 225
# The theme's palette colour 5, so the panel follows the site palette if it changes.
PANEL_BG = "var(--wp--preset--color--palette-color-5, var(--theme-palette-color-5, #F0F2F3))"

# All tile styling lives on the grid block, so one edit covers every brand.
# Hover uses the panel colour. Logos use mix-blend-mode:multiply so white logo
# backgrounds melt into it.
# Lines: the grid draws the top and left edges, each tile its right and bottom,
# so a part-filled last row stays clean.
GRID_CSS = (
    "{CURRENT} .tfgr-brand{display:flex;flex-direction:column;background-color:#ffffff;"
    f"border-right:1px solid {RULE};border-bottom:1px solid {RULE};padding:1.5rem;"
    f"color:{BODY};text-decoration:none;transition:background-color .2s;}}"
    f"{{CURRENT}} .tfgr-brand:hover{{background-color:{PANEL_BG};}}"
    f"{{CURRENT}} .tfgr-brand:focus-visible{{outline:2px solid {ACCENT};outline-offset:-2px;}}"
    "{CURRENT} .tfgr-brand-logo{display:flex;align-items:center;justify-content:center;"
    "height:5.5rem;margin-bottom:1.25rem;}"
    "{CURRENT} .tfgr-brand-logo img{display:block;width:100%;max-width:12rem;height:auto;"
    "max-height:100%;object-fit:contain;mix-blend-mode:multiply;}"
    f"{{CURRENT}} .tfgr-brand-name{{margin:auto 0 0 0;padding-top:1rem;border-top:1px solid {RULE};"
    f"font-weight:700;color:{INK};}}"
    f"{{CURRENT}} .tfgr-brand-link{{margin:0.25rem 0 0 0;font-weight:700;color:{ACCENT};}}"
    "{CURRENT} .tfgr-brand-link::after{content:\" \\2197\" / \" (opens in a new tab)\";}"
    "{CURRENT} .tfgr-brand:hover .tfgr-brand-link{text-decoration:underline;}"
    "@media (max-width: 575.98px){{CURRENT} .tfgr-brand{padding:1rem;}"
    "{CURRENT} .tfgr-brand-logo{height:4rem;}}"
)


def brand_tile(name, logo, alt, url):
    return Block("a", class_name="tfgr-brand", href=url, name=name,
                 json_extra={"linkNewWindow": True},
                 html_attrs=[("target", "_blank"), ("rel", "noopener")],
                 children=[
                     Block(class_name="tfgr-brand-logo", children=[
                         Block("img", json_extra={
                             "src": UPLOADS + logo, "alt": alt,
                             "originalWidth": LOGO_W, "originalHeight": LOGO_H,
                         }, html_attrs=[
                             ("src", UPLOADS + logo), ("alt", alt),
                             ("width", str(LOGO_W)), ("height", str(LOGO_H)), ("loading", "lazy"),
                         ]),
                     ]),
                     Block("p", text=name, class_name="tfgr-brand-name"),
                     Block("p", text="Warranty and service", class_name="tfgr-brand-link"),
                 ])


def directory():
    _seed["slug"], _seed["n"] = "warranty", 0
    heading = Block(name="Heading", styles={
        "paddingBottom": ["1.5rem"], "marginBottom": ["2.25rem"],
        "borderBottom": [f"2px solid {INK}"],
    }, children=[
        Block("p", text="Authorized warranty and repair", styles={
            "marginTop": ["0px"], "marginBottom": ["0.44rem"], "fontWeight": ["700"],
            "textTransform": ["uppercase"], "color": [ACCENT],
        }),
        Block("h2", text="Brands A to Z", styles={
            "marginTop": ["0px"], "marginBottom": ["0px"], "color": [INK],
        }),
    ])
    grid = Block(name="Brand Directory", styles={
        "display": ["grid"],
        "gridTemplateColumns": ["repeat(4, 1fr)", "repeat(3, 1fr)", "repeat(2, 1fr)", "repeat(2, 1fr)"],
        "borderTop": [f"1px solid {RULE}"], "borderLeft": [f"1px solid {RULE}"],
        "backgroundColor": ["#ffffff"],
    }, custom_css=GRID_CSS, children=[
        brand_tile(*b) for b in sorted(BRANDS, key=lambda b: b[0].lower())
    ])
    return Block(name="Warranty and Service", class_name="tfgr-policy", anchor="brands", styles={
        "backgroundColor": [PANEL_BG],
        "paddingTop": ["2.25rem", None, None, "1.5rem"],
        "paddingBottom": ["2.25rem", None, None, "1.5rem"],
        "paddingLeft": ["1.5rem", None, None, "1rem"],
        "paddingRight": ["1.5rem", None, None, "1rem"],
        # Pulled up over the bottom of the hero so the two read as one piece.
        "marginTop": ["-4rem", None, None, "-3rem"],
        "position": ["relative"], "zIndex": ["2"],
    }, custom_css="{CURRENT}{scroll-margin-top:2rem;}", children=[heading, grid])


HERO_BG = "#3a3a3a"
HERO_ACCENT = "#ec8a80"  # brand red lightened to pass 4.5:1 contrast on the grey
PATTERN = "https://thefastenergroup.com/wp-content/uploads/2026/02/Background-3.svg"

HERO_CSS = (
    # The nut-outline pattern sits on a pseudo-element so its opacity leaves the text alone.
    "{CURRENT}::before{content:\"\";position:absolute;inset:0;"
    f"background:url({PATTERN}) center / cover no-repeat;opacity:0.09;pointer-events:none;}}"
    "{CURRENT} > *{position:relative;z-index:1;}"
)

BUTTON_CSS = (
    "{CURRENT}{display:inline-flex;align-items:center;gap:0.6rem;margin-top:2rem;"
    f"padding:0.6rem 1.25rem;border:1px solid {HERO_ACCENT};color:#ffffff;font-weight:700;"
    "text-decoration:none;transition:background-color .2s,border-color .2s;}"
    f"{{CURRENT}}::after{{content:\"\\2193\";color:{HERO_ACCENT};}}"
    f"{{CURRENT}}:hover,{{CURRENT}}:focus-visible{{background-color:{ACCENT};border-color:{ACCENT};color:#ffffff;}}"
    "{CURRENT}:hover::after,{CURRENT}:focus-visible::after{color:#ffffff;}"
    f"{{CURRENT}}:focus-visible{{outline:2px solid {HERO_ACCENT};outline-offset:2px;}}"
)


def hero():
    """Full-width hero: caption, h1 and intro stacked in one left column, pattern on the right."""
    _seed["slug"], _seed["n"] = "warranty-hero", 0
    text_col = Block(name="Hero Text", styles={"maxWidth": ["44rem"]}, children=[
        Block("p", text="Warranty and service", styles={
            "marginTop": ["0px"], "marginBottom": ["0.75rem"], "fontWeight": ["700"],
            "textTransform": ["uppercase"], "color": [HERO_ACCENT],
        }),
        Block("h1", text="Find Authorized Service Near You", styles={
            "marginTop": ["0px"], "marginBottom": ["0px"], "color": ["#ffffff"],
            "fontSize": ["var(--wp--preset--font-size--giga, clamp(3rem, 5vw, 4.5rem))"],
            "lineHeight": ["1.1"],
        }),
        Block("p", text=("Get the support you need with confidence. Click on the logo of your "
                         "favourite brand below for direct access to their authorized warranty "
                         "and repair services."), styles={
            "marginTop": ["1.25rem"], "marginBottom": ["0px"], "maxWidth": ["36rem"],
            "color": ["rgba(255, 255, 255, 0.85)"],
        }),
        Block("a", text="Browse brands", href="#brands", custom_css=BUTTON_CSS),
    ])
    content = Block(name="Content Area", styles={
        "maxWidth": ["100%"], "width": ["var(--wp--style--global--wide-size, 1200px)"],
    }, json_extra={"isVariation": "contentarea"}, children=[text_col])
    return Block("section", name="Hero", align="full", styles={
        "display": ["flex"], "flexDirection": ["column"], "alignItems": ["center"],
        "position": ["relative"], "overflow": ["hidden"], "backgroundColor": [HERO_BG],
        # Top padding clears the theme's see-through header; the bottom leaves room
        # for the brand panel to overlap.
        "paddingTop": ["190px", "170px", None, "140px"],
        "paddingBottom": ["8rem", None, None, "6rem"],
        "paddingLeft": ["var(--wp--custom--spacing--side, min(3vw, 20px))"],
        "paddingRight": ["var(--wp--custom--spacing--side, min(3vw, 20px))"],
        "marginTop": ["0px"], "marginBottom": ["0px"],
    }, json_extra={"isVariation": "contentcolumns"}, custom_css=HERO_CSS, children=[content])


PAGE = {"dir": "warranty-page", "title": "Warranty and Service", "preview_css": GS_PREVIEW_CSS + """
body > .tfgr-policy{max-width:1200px;margin-left:auto;margin-right:auto}
"""}

if __name__ == "__main__":
    write(PAGE, directory(), before=hero())
