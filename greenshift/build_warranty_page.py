"""Build the warranty and service page: the site's hero, then an A to Z brand directory.

Reuses the block format and palette from build_policy_blocks.py. To add a vendor,
add a line to BRANDS; the list is sorted by name when the page is built.
"""
from build_policy_blocks import (
    ACCENT, BODY, GS_PREVIEW_CSS, HERE, INK, NUM_BG, PAPER, RULE, Block, _seed, write,
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

# All tile styling lives on the grid block, so one edit covers every brand.
# Logos use mix-blend-mode:multiply so white logo backgrounds melt into the hover colour.
# Lines: the grid draws the top and left edges, each tile its right and bottom,
# so a part-filled last row stays clean.
GRID_CSS = (
    "{CURRENT} .tfgr-brand{display:flex;flex-direction:column;background-color:#ffffff;"
    f"border-right:1px solid {RULE};border-bottom:1px solid {RULE};padding:1.5rem;"
    f"color:{BODY};text-decoration:none;transition:background-color .2s;}}"
    f"{{CURRENT}} .tfgr-brand:hover{{background-color:{NUM_BG};}}"
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
        "backgroundColor": [PAPER],
        "paddingTop": ["2.25rem", None, None, "1.5rem"],
        "paddingBottom": ["2.25rem", None, None, "1.5rem"],
        "paddingLeft": ["1.5rem", None, None, "1rem"],
        "paddingRight": ["1.5rem", None, None, "1rem"],
    }, children=[heading, grid])


PAGE = {"dir": "warranty-page", "title": "Warranty and Service", "preview_css": GS_PREVIEW_CSS + """
.gspb_row-id-gsbp-7eecdd8{background:#3a3a3a;color:#fff;padding:120px 40px 60px;margin-bottom:120px}
.gspb_row-id-gsbp-7eecdd8 .gspb_row__content{max-width:1200px;margin:0 auto;align-items:center}
.gspb_heading-id-gsbp-a22facd{font-size:56px;line-height:1.2em;margin:0}
"""}

if __name__ == "__main__":
    hero = (HERE / "warranty-page" / "source-hero.txt").read_text().strip()
    write(PAGE, directory(), before=hero)
