"""Build the Locations page: hero with province jump links, an overview map, and every
store as a card grouped by province.

Store details live in locations-page/stores.json (also read by build_locations_map.js,
which draws locations-page/map.svg). Edit the JSON, rerun both scripts, re-paste.
"""
import json
from urllib.parse import quote, urlparse

from build_policy_blocks import (
    ACCENT, BODY, GS_PREVIEW_CSS, HERE, INK, RULE, Block, Raw, _seed, make_hero, write,
)

DATA = json.loads((HERE / "locations-page" / "stores.json").read_text())
PANEL_BG = "var(--wp--preset--color--palette-color-5, var(--theme-palette-color-5, #F0F2F3))"
MUTED = "#5f6468"


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


def domain(url):
    host = urlparse(url).netloc
    return host[4:] if host.startswith("www.") else host


# All card styling lives on each province grid, so one edit covers its stores.
GRID_CSS = (
    "{CURRENT} .tfgr-store{display:flex;flex-direction:column;background-color:#ffffff;"
    f"border-right:1px solid {RULE};border-bottom:1px solid {RULE};padding:1.5rem;color:{BODY};}}"
    f"{{CURRENT}} .tfgr-store-city{{margin:0;font-weight:700;color:{INK};}}"
    f"{{CURRENT}} .tfgr-store-name{{margin:0 0 0.75rem 0;color:{MUTED};}}"
    "{CURRENT} .tfgr-store-addr{margin:0;}"
    f"{{CURRENT}} .tfgr-store-phone{{display:inline-block;margin-top:0.75rem;font-weight:700;color:{ACCENT};text-decoration:none;}}"
    "{CURRENT} .tfgr-store-phone:hover{text-decoration:underline;}"
    # Links always stack, so the divider sits at the same height in every card of a row.
    "{CURRENT} .tfgr-store-links{display:flex;flex-direction:column;align-items:flex-start;"
    f"row-gap:0.25rem;margin-top:auto;padding-top:1rem;}}"
    "{CURRENT} .tfgr-store-links::before{content:\"\";align-self:stretch;margin-bottom:0.75rem;"
    f"border-top:1px solid {RULE};}}"
    f"{{CURRENT}} .tfgr-store-link{{font-weight:700;color:{INK};text-decoration:none;}}"
    "{CURRENT} .tfgr-store-link::after{content:\" \\2197\" / \" (opens in a new tab)\";"
    f"color:{ACCENT};}}"
    "{CURRENT} .tfgr-store-link:hover{text-decoration:underline;}"
    f"{{CURRENT}} a:focus-visible{{outline:2px solid {ACCENT};outline-offset:2px;}}"
    "@media (max-width: 575.98px){{CURRENT} .tfgr-store{padding:1.25rem;}}"
)


def ext_link(text, url, cls):
    return Block("a", text=text, href=url, class_name=cls, json_extra={"linkNewWindow": True},
                 html_attrs=[("target", "_blank"), ("rel", "noopener")])


def store_card(s, anchor):
    maps = "https://www.google.com/maps?q=" + quote(f"{s['name']}, {s['street']}, {s['locality']}")
    tel = "tel:+1" + "".join(c for c in s["phone"] if c.isdigit())
    return Block(class_name="tfgr-store", anchor=anchor, name=f"{s['city']}: {s['name']}", children=[
        Block("p", text=s["city"], class_name="tfgr-store-city"),
        Block("p", text=s["name"], class_name="tfgr-store-name"),
        Block("p", text=s["street"], class_name="tfgr-store-addr"),
        Block("p", text=s["locality"], class_name="tfgr-store-addr"),
        Block("a", text=s["phone"], href=tel, class_name="tfgr-store-phone"),
        Block(class_name="tfgr-store-links", children=[
            ext_link("Directions", maps, "tfgr-store-link"),
            ext_link(domain(s["website"]), s["website"], "tfgr-store-link"),
        ]),
    ])


def province_section(p, seen_cities):
    stores = sorted(p["stores"], key=lambda s: (s["city"], s["name"]))
    cards = []
    for s in stores:
        anchor = None
        if s["city"] not in seen_cities:  # map pins link to the first store in each city
            seen_cities.add(s["city"])
            anchor = "store-" + slug(s["city"])
        cards.append(store_card(s, anchor))
    n = len(stores)
    return Block(name=p["name"], children=[
        Block(name="Heading", styles={
            "paddingBottom": ["1rem"], "marginBottom": ["1.5rem"],
            "borderBottom": [f"2px solid {INK}"],
        }, children=[
            Block("p", text=f"{n} location{'s' if n > 1 else ''}", styles={
                "marginTop": ["0px"], "marginBottom": ["0.44rem"], "fontWeight": ["700"],
                "textTransform": ["uppercase"], "color": [ACCENT],
            }),
            Block("h2", text=p["name"], anchor=p["id"], styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "color": [INK],
            }),
        ]),
        Block(name="Store Cards", styles={
            "display": ["grid"],
            "gridTemplateColumns": ["repeat(3, 1fr)", "repeat(2, 1fr)", "repeat(2, 1fr)", "repeat(1, 1fr)"],
            "borderTop": [f"1px solid {RULE}"], "borderLeft": [f"1px solid {RULE}"],
            "backgroundColor": ["#ffffff"],
        }, custom_css=GRID_CSS, children=cards),
    ])


def directory():
    _seed["slug"], _seed["n"] = "locations", 0
    svg = (HERE / "locations-page" / "map.svg").read_text().strip()
    map_box = Block(name="Store Map", styles={
        "border": [f"1px solid {RULE}"], "backgroundColor": ["#ffffff"], "marginBottom": ["0.75rem"],
    }, children=[Raw("<!-- wp:html -->\n" + svg + "\n<!-- /wp:html -->")])
    map_note = Block("p", text="Select a pin to jump to that store's details.", styles={
        "marginTop": ["0px"], "marginBottom": ["3rem", None, None, "2.25rem"], "color": [MUTED],
    })
    seen = set()
    sections = [province_section(p, seen) for p in DATA["provinces"]]
    return Block(name="Store Directory", class_name="tfgr-policy", styles={
        "backgroundColor": [PANEL_BG],
        "paddingTop": ["2.25rem", None, None, "1.5rem"],
        "paddingBottom": ["2.25rem", None, None, "1.5rem"],
        "paddingLeft": ["1.5rem", None, None, "1rem"],
        "paddingRight": ["1.5rem", None, None, "1rem"],
        # Pulled up over the bottom of the hero so the two read as one piece.
        "marginTop": ["-4rem", None, None, "-3rem"],
        "position": ["relative"], "zIndex": ["2"],
        "display": ["flex"], "flexDirection": ["column"], "rowGap": ["0px"],
    }, custom_css=(
        "{CURRENT} [id]{scroll-margin-top:2rem;}"
        "{CURRENT} > div + div{margin-top:3rem;}"
    ), children=[map_box, map_note] + sections)


def hero():
    return make_hero(
        seed="locations-hero", bg="var(--wp--preset--color--textcolor, #333333)",
        caption="Locations", title="Our Stores",
        intro=("Our 20 Western Canada locations make it easy to serve customers when "
               "and where they need us."),
        buttons=[(p["name"], "#" + p["id"]) for p in DATA["provinces"]],
    )


PAGE = {"dir": "locations-page", "title": "Our Stores", "preview_css": GS_PREVIEW_CSS + """
body > .tfgr-policy{max-width:1200px;margin-left:auto;margin-right:auto}
"""}

if __name__ == "__main__":
    write(PAGE, directory(), before=hero())
