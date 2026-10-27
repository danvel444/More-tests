"""Build the warranty and service page: the site's hero, then an A to Z brand directory.

Reuses the block format and palette from build_policy_blocks.py. To add a vendor,
add a line to BRANDS; the list is sorted by name when the page is built.
"""
import html
import json
from urllib.parse import quote

from build_policy_blocks import (
    ACCENT, BODY, GS_PREVIEW_CSS, HERE, INK, RULE, Block, Raw, _seed, make_hero, write,
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


STIHL = json.loads((HERE / "warranty-page" / "stihl-partners.json").read_text())

# The STIHL partner list opens in a native popover (no script): the button toggles it,
# Esc, the close button or a click outside closes it. Browsers without popover support
# hide the button and show the list inline instead.
STIHL_CSS = f"""
.tfgr-stihl{{margin-top:1.5rem;}}
.tfgr-stihl-callout{{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:1rem 2rem;
  background:#ffffff;border:1px solid {RULE};padding:1.25rem 1.5rem;}}
.tfgr-stihl-callout p{{margin:0;color:{BODY};max-width:44rem;}}
.tfgr-stihl-callout strong{{color:{INK};}}
.tfgr-stihl-open{{display:none;}}
.tfgr-stihl-btn{{display:inline-flex;align-items:center;gap:0.6rem;padding:0.75rem 1.5rem;cursor:pointer;
  background:{ACCENT};border:1px solid {ACCENT};color:#ffffff;font:inherit;font-weight:700;white-space:nowrap;
  transition:background-color .2s,border-color .2s;}}
.tfgr-stihl-btn:hover,.tfgr-stihl-btn:focus-visible{{background:{INK};border-color:{INK};}}
.tfgr-stihl-btn:focus-visible{{outline:2px solid {ACCENT};outline-offset:2px;}}
.tfgr-stihl-pop{{color:{BODY};}}
.tfgr-stihl-head{{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;
  padding-bottom:1rem;margin-bottom:1.5rem;border-bottom:2px solid {INK};}}
.tfgr-stihl-cap{{margin:0 0 0.44rem;font-weight:700;text-transform:uppercase;color:{ACCENT};}}
.tfgr-stihl-head h2{{margin:0;color:{INK};}}
.tfgr-stihl-close{{display:none;flex:0 0 auto;width:2.5rem;height:2.5rem;cursor:pointer;background:#ffffff;
  border:1px solid {RULE};color:{INK};font:inherit;font-size:1.25rem;line-height:1;}}
.tfgr-stihl-close:hover,.tfgr-stihl-close:focus-visible{{border-color:{INK};}}
.tfgr-stihl-city{{margin:1.5rem 0 0.75rem;color:{INK};}}
.tfgr-stihl-city:first-of-type{{margin-top:0;}}
.tfgr-stihl-grid{{display:grid;grid-template-columns:repeat(2,1fr);border-top:1px solid {RULE};border-left:1px solid {RULE};}}
.tfgr-stihl-card{{min-width:0;border-right:1px solid {RULE};border-bottom:1px solid {RULE};padding:1rem 1.25rem;}}
.tfgr-stihl-card p{{margin:0;}}
.tfgr-stihl-name{{font-weight:700;color:{INK};margin-bottom:0.4rem !important;}}
.tfgr-stihl-links{{display:flex;flex-wrap:wrap;gap:0.25rem 1.25rem;margin-top:0.6rem;}}
.tfgr-stihl-links a{{font-weight:700;text-decoration:none;}}
.tfgr-stihl-links a:hover{{text-decoration:underline;}}
.tfgr-stihl-tel{{color:{ACCENT};}}
.tfgr-stihl-dir{{color:{INK};}}
.tfgr-stihl-dir::after{{content:" \\2197" / " (opens in a new tab)";color:{ACCENT};}}
.tfgr-stihl-note{{margin:1.25rem 0 0;font-size:0.9em;color:#5f6468;}}
.tfgr-stihl-pop{{margin-top:1.5rem;background:#ffffff;border:1px solid {RULE};padding:1.5rem;}}
@supports selector(:popover-open){{
  .tfgr-stihl-open,.tfgr-stihl-close{{display:inline-flex;align-items:center;justify-content:center;}}
  .tfgr-stihl-pop{{box-sizing:border-box;position:fixed;inset:0;margin:auto;width:min(56rem,calc(100vw - 2rem));
    max-height:calc(100dvh - 4rem);overflow:auto;padding:1.75rem 2rem;box-shadow:0 1.5rem 3rem rgba(0,0,0,0.25);}}
  .tfgr-stihl-pop::backdrop{{background:rgba(13,14,16,0.6);}}
}}
@media (max-width: 600px){{
  .tfgr-stihl-grid{{grid-template-columns:1fr;}}
  .tfgr-stihl-callout{{padding:1rem;}}
  .tfgr-stihl-btn{{width:100%;justify-content:center;white-space:normal;text-align:center;}}
  @supports selector(:popover-open){{
    .tfgr-stihl-pop{{width:100%;max-width:none;height:100%;max-height:none;margin:0;padding:1.25rem 1rem;border:0;}}
  }}
}}
"""


def stihl_partners():
    """Callout under the brand grid plus the STIHL partner popover, as one Custom HTML block."""
    e = lambda t: html.escape(t, quote=True)
    cities = [c["city"] for c in STIHL["cities"]]
    city_list = ", ".join(cities[:-1]) + " and " + cities[-1]
    sections = []
    for c in STIHL["cities"]:
        cards = []
        for p in c["partners"]:
            tel = "tel:+1" + "".join(ch for ch in p["phone"] if ch.isdigit())
            maps = "https://www.google.com/maps?q=" + quote(f"{p['name']}, {p['street']}, {p['locality']}")
            cards.append(
                f'<div class="tfgr-stihl-card"><p class="tfgr-stihl-name">{e(p["name"])}</p>'
                f'<p>{e(p["street"])}</p><p>{e(p["locality"])}</p>'
                f'<p class="tfgr-stihl-links"><a class="tfgr-stihl-tel" href="{tel}">{e(p["phone"])}</a>'
                f'<a class="tfgr-stihl-dir" href="{e(maps)}" target="_blank" rel="noopener">Directions</a></p></div>')
        sections.append(f'<h3 class="tfgr-stihl-city">{e(c["city"])}</h3>'
                        f'<div class="tfgr-stihl-grid">{"".join(cards)}</div>')
    body = (
        f'<style>{STIHL_CSS.strip()}</style>\n'
        '<div class="tfgr-stihl">\n'
        '<div class="tfgr-stihl-callout">'
        f'<p><strong>STIHL owners:</strong> TFG-authorized STIHL service partners in {e(city_list)}.</p>'
        '<button type="button" class="tfgr-stihl-btn tfgr-stihl-open" popovertarget="tfgr-stihl-partners">'
        'View STIHL service partners</button></div>\n'
        '<div id="tfgr-stihl-partners" class="tfgr-stihl-pop" popover role="dialog" aria-labelledby="tfgr-stihl-title">'
        '<div class="tfgr-stihl-head"><div><p class="tfgr-stihl-cap">STIHL service</p>'
        '<h2 id="tfgr-stihl-title">TFG-authorized STIHL service partners</h2></div>'
        '<button type="button" class="tfgr-stihl-close" popovertarget="tfgr-stihl-partners" '
        'popovertargetaction="hide" aria-label="Close">&#x2715;</button></div>'
        + "".join(sections) +
        f'<p class="tfgr-stihl-note">Partner list as of {e(STIHL["as_of"])}.</p></div>\n</div>'
    )
    return Raw("<!-- wp:html -->\n" + body + "\n<!-- /wp:html -->")


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
    }, custom_css="{CURRENT}{scroll-margin-top:2rem;}", children=[heading, grid, stihl_partners()])


def hero():
    return make_hero(
        seed="warranty-hero", bg="#3a3a3a", caption="Warranty and service",
        title="Find Authorized Service Near You",
        intro=("Get the support you need with confidence. Click on the logo of your "
               "favourite brand below for direct access to their authorized warranty "
               "and repair services."),
        buttons=[("Browse brands", "#brands")],
    )


PAGE = {"dir": "warranty-page", "title": "Warranty and Service", "preview_css": GS_PREVIEW_CSS + """
body > .tfgr-policy{max-width:1200px;margin-left:auto;margin-right:auto}
"""}

if __name__ == "__main__":
    write(PAGE, directory(), before=hero())
