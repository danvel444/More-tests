"""Build the four footer widget columns for Blocksy's Footer Widget Areas 1 to 4.

Column 1: short description (the logo and Blocksy's Socials widget sit around it).
Columns 2 and 3: Company and Customers links.
Column 4: the family of companies, each hex logo linking to that company's own site.

Each column is written to its own paste file in footer/, plus footer.css for the
dark background, thread lines and red top edge.
"""
from build_policy_blocks import HERE, Block, _seed, write

SITE = "https://thefastenergroup.com/"
SOFT_WHITE = "rgba(255, 255, 255, 0.72)"
LINK_WHITE = "rgba(255, 255, 255, 0.82)"
HEX = SITE + "wp-content/uploads/2025/12/"

COMPANY = [
    ("About Us", SITE + "leadership-team/"),
    ("News", SITE + "news/"),
    ("Our Stores", SITE + "branches/"),
    ("Contact", SITE + "contact/"),
]
CUSTOMERS = [
    ("Industries We Serve", SITE + "services/"),
    ("Authorized Service", SITE + "service-centres/"),
    ("Policies and Terms", SITE + "policies-and-terms/"),
    ("Forced Labour Report", SITE + "forced-labour-report/"),
]
# (name, logo, website). Names are the alt text, so screen readers hear each company.
FAMILY = [
    ("BC Fasteners and Tools", HEX + "BC-Hex-Logo.png", "https://bcfasteners.com/"),
    ("BC Fasteners and Tools 2000", HEX + "BC2000-Hex-Logo.png", "https://www.blackcrowfasteners.com/"),
    ("Calgary Fasteners and Tools", HEX + "Calgary-Hex-Logo.png", "https://www.calfast.com/"),
    ("Construction Fasteners and Tools", HEX + "Construction-Hex-Logo.png", "https://cf-t.com/"),
    ("Edmonton Fasteners and Tools", HEX + "Edmonton-Hex-Logo.png", "https://edmfast.com/"),
    ("Lethbridge Fasteners and Tools", HEX + "Lethbridge-Hex-Logo.png", "https://www.lethfast.ca/"),
    ("Mid Canada Fasteners and Tools", HEX + "Mid-Can-Hex-Logo.png", "https://midcanadafasteners.shop/"),
    ("Red Deer Fasteners and Tools", HEX + "Red-Deer-Hex-Logo.png", "https://www.rdfasteners.com/"),
    ("JD Industrial Supplies", HEX + "JD-Hex-Logo.png", "https://jdindustrial.com/"),
    ("Ono Work and Safety", SITE + "wp-content/uploads/2026/02/Ono-Logo.webp", "https://www.onoworkandsafety.com/"),
]

LABEL_STYLES = {
    "marginTop": ["0px"], "marginBottom": ["1rem"], "fontWeight": ["700"],
    "textTransform": ["uppercase"], "letterSpacing": ["0.06em"], "color": ["#ffffff"],
}

LINKS_CSS = (
    "{CURRENT}{list-style:none;margin:0;padding:0;}"
    "{CURRENT} li{margin:0 0 0.6rem 0;padding:0;}"
    f"{{CURRENT}} a{{color:{LINK_WHITE};text-decoration:none;transition:color .2s;}}"
    "{CURRENT} a:hover,{CURRENT} a:focus-visible{color:#ffffff;text-decoration:underline;"
    "text-underline-offset:0.2em;}"
)

FAMILY_CSS = (
    "{CURRENT}{display:grid;grid-template-columns:repeat(5, minmax(0, 3rem));gap:0.6rem;}"
    "{CURRENT} a{display:block;opacity:0.9;transition:opacity .2s;}"
    "{CURRENT} a:hover,{CURRENT} a:focus-visible{opacity:1;}"
    "{CURRENT} a:focus-visible{outline:2px solid #ffffff;outline-offset:3px;}"
    "{CURRENT} img{display:block;width:100%;height:auto;aspect-ratio:1;object-fit:contain;}"
    # The Ono wordmark is not a hexagon; sit it a little higher so it lines up with the others.
    "{CURRENT} a:last-child img{object-position:50% 38%;}"
)


def label(text):
    return Block("p", text=text, styles=LABEL_STYLES)


def links(title, items):
    return Block(name=title, children=[
        label(title),
        Block("ul", custom_css=LINKS_CSS, children=[
            Block("li", children=[Block("a", text=t, href=u)]) for t, u in items
        ]),
    ])


def column_1():
    _seed["slug"], _seed["n"] = "footer-1", 0
    logo = SITE + "wp-content/uploads/2025/10/TFG-Logo-Stacked_WHITE.png"
    return Block(name="Footer About", children=[
        Block("a", href=SITE, name="Logo", styles={"display": ["inline-block"], "marginBottom": ["1.25rem"]},
              children=[
            Block("img", json_extra={"src": logo, "alt": "The Fastener Group Ltd. home"},
                  html_attrs=[("src", logo), ("alt", "The Fastener Group Ltd. home"), ("loading", "lazy")],
                  styles={"display": ["block"], "width": ["11rem", None, None, "9.5rem"],
                          "maxWidth": ["100%"], "height": ["auto"]}),
        ]),
        Block("p", text=("Western Canada’s source for fasteners, tools, safety gear and "
                         "accessories since 1979."), styles={
            "marginTop": ["0px"], "marginBottom": ["0px"], "maxWidth": ["22rem"], "color": [SOFT_WHITE],
        }),
    ])


def column_2():
    _seed["slug"], _seed["n"] = "footer-2", 0
    return links("Company", COMPANY)


def column_3():
    _seed["slug"], _seed["n"] = "footer-3", 0
    return links("Customers", CUSTOMERS)


def column_4():
    _seed["slug"], _seed["n"] = "footer-4", 0
    logos = []
    for name, src, url in FAMILY:
        logos.append(Block("a", href=url, children=[
            Block("img", json_extra={"src": src, "alt": name},
                  html_attrs=[("src", src), ("alt", name), ("width", "48"), ("height", "48"),
                              ("loading", "lazy")]),
        ]))
    return Block(name="Family of Companies", children=[
        label("Our family of companies"),
        Block(name="Logos", custom_css=FAMILY_CSS, children=logos),
        Block("p", text="Local names, one group. Each logo opens that company’s own site.", styles={
            "marginTop": ["1rem"], "marginBottom": ["0px"], "fontSize": ["0.875rem"],
            "color": ["rgba(255, 255, 255, 0.55)"],
        }),
    ])


# Additional CSS (Customizer). Blocksy's footer: footer.ct-footer > [data-row] > .ct-container.
FOOTER_CSS = """/* TFG footer: one dark background with honeycomb behind every row, red top edge. */
.ct-footer {
  position: relative;
  overflow: hidden;
  background-color: #0d0e10;
  border-top: 4px solid var(--theme-palette-color-1, #b11f24);
}
/* Let the rows show the footer's background instead of painting their own. */
.ct-footer [data-row] {
  background: transparent !important;
}
.ct-footer::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: var(--tfg-hex-image) 0 0 / var(--tfg-hex-size) repeat;
  opacity: var(--tfg-hex-opacity);
  -webkit-mask-image: linear-gradient(to left, #000 5%, transparent 45%);
  mask-image: linear-gradient(to left, #000 5%, transparent 45%);
}
.ct-footer [data-row] {
  position: relative;
  z-index: 1;
}
"""

PAGE = {"dir": "footer", "title": "Footer", "preview_css": """
body{background:#0d0e10!important;padding:0!important}
body{display:grid;grid-template-columns:1.4fr 1fr 1fr 1.2fr;gap:48px;padding:56px 40px!important;
border-top:4px solid #b11f24;color:#fff}
@media (max-width:900px){body{grid-template-columns:1fr 1fr}}
@media (max-width:560px){body{grid-template-columns:1fr}}
"""}

if __name__ == "__main__":
    cols = [column_1(), column_2(), column_3(), column_4()]
    write(PAGE, cols)
    out = HERE / "footer"
    (out / "footer-greenshift-blocks.txt").unlink()
    for i, c in enumerate(cols, 1):
        (out / f"footer-widget-area-{i}.txt").write_text(c.serialize() + "\n")
    (out / "footer.css").write_text(FOOTER_CSS)
