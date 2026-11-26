"""Build a promo banner for a Blocksy Content Block: the Black Friday gift-with-purchase offer.

Data-driven, so the next promo only needs a new PROMO dict: a header, one panel per brand
with its spend tiers, a shop button each, and a closing note. It uses the shared honeycomb
(tfg-hex class from Additional CSS) and the red bottom edge from the page heroes.
"""
from build_policy_blocks import ACCENT, HEX_CLASS, SOFT_WHITE, THREAD_HERO_CSS, Block, _seed, write
from build_industries_page import SOLID_BUTTON_CSS

DARK = "#0d0e10"
LINE = "rgba(255, 255, 255, 0.14)"

PROMO = {
    "slug": "promo-black-friday",
    "title": "Black Friday",
    "subtitle": "Free gifts with purchase",
    "tag": "Online only. Extremely limited quantities.",
    "note": ("Deals are cumulative.", " The more you spend, the more you get."),
    "brands": [
        {
            "name": "Milwaukee", "count": "Up to 7 free gifts", "shop": "Shop Milwaukee", "url": "#",
            "tiers": [("$500+", "Hat + Toque"), ("$800+", "Bag + Towel"), ("$1,000+", "Sweater"),
                      ("$1,500+", "Chair"), ("$3,000+", "Cooler")],
        },
        {
            "name": "Wera", "count": "Up to 4 free gifts", "shop": "Shop Wera", "url": "#",
            "tiers": [("$150+", "Trucker Hat"), ("$250+", "Toque"), ("$500+", "Flag"),
                      ("$600+", "Backpack")],
        },
    ],
}

# Tiers sit side by side as a ladder with 1px lines between them (the grid gap shows the
# line colour). On phones each tier becomes a row: amount on the left, gift on the right.
TIERS_CSS = (
    f"{{CURRENT}}{{list-style:none;margin:0;padding:0;display:grid;gap:1px;background-color:{LINE};"
    f"border:1px solid {LINE};}}"
    f"{{CURRENT}} li{{margin:0;padding:0.9rem 0.75rem;background-color:{DARK};display:flex;"
    "flex-direction:column;gap:0.3rem;}"
    "{CURRENT} .tfgp-amount{font-weight:700;font-size:1.25rem;line-height:1.2;color:#ffffff;"
    "font-variant-numeric:tabular-nums;}"
    f"{{CURRENT}} .tfgp-amount::before{{content:\"\";display:block;width:1.25rem;height:2px;"
    f"margin-bottom:0.6rem;background-color:{ACCENT};}}"
    f"{{CURRENT}} .tfgp-gift{{font-size:0.9rem;line-height:1.35;color:{SOFT_WHITE};}}"
    "@media (max-width: 575.98px){"
    "{CURRENT}{grid-template-columns:1fr !important;}"
    "{CURRENT} li{flex-direction:row;justify-content:space-between;align-items:baseline;gap:1rem;}"
    "{CURRENT} .tfgp-amount{font-size:1.1rem;}"
    "{CURRENT} .tfgp-amount::before{display:none;}"
    "{CURRENT} .tfgp-gift{text-align:right;}}"
)

BUTTON_CSS = SOLID_BUTTON_CSS.replace(
    "{CURRENT}:hover,{CURRENT}:focus-visible{background-color:#1d1f21;border-color:#1d1f21;color:#ffffff;}",
    "{CURRENT}:hover,{CURRENT}:focus-visible{background-color:#ffffff;border-color:#ffffff;color:#1d1f21;}",
)


def brand_panel(brand):
    tiers = brand["tiers"]
    return Block(name=brand["name"], styles={"display": ["flex"], "flexDirection": ["column"]}, children=[
        Block(name="Brand Heading", styles={
            "display": ["flex"], "flexWrap": ["wrap"], "alignItems": ["baseline"],
            "justifyContent": ["space-between"], "columnGap": ["1rem"], "rowGap": ["0.25rem"],
            "marginBottom": ["0.85rem"],
        }, children=[
            Block("h3", text=brand["name"], styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "color": ["#ffffff"],
            }),
            Block("p", text=brand["count"], styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "fontSize": ["0.8rem"], "fontWeight": ["700"],
                "textTransform": ["uppercase"], "letterSpacing": ["0.06em"], "color": [SOFT_WHITE],
            }),
        ]),
        Block("ul", name="Tiers", styles={
            "gridTemplateColumns": [f"repeat({len(tiers)}, minmax(0, 1fr))"],
        }, custom_css=TIERS_CSS, children=[
            Block("li", children=[
                Block("span", text=amount, class_name="tfgp-amount", text_is_html=False),
                Block("span", text=gift, class_name="tfgp-gift"),
            ]) for amount, gift in tiers
        ]),
        Block(name="Button Row", styles={"marginTop": ["1.25rem"]}, children=[
            Block("a", text=brand["shop"], href=brand["url"], custom_css=BUTTON_CSS),
        ]),
    ])


def banner(promo):
    _seed["slug"], _seed["n"] = promo["slug"], 0
    head = Block(name="Header", styles={
        "display": ["flex"], "flexWrap": ["wrap"], "alignItems": ["flex-end"],
        "justifyContent": ["space-between"], "columnGap": ["2rem"], "rowGap": ["1rem"],
        "paddingBottom": ["1.5rem"], "marginBottom": ["1.75rem"], "borderBottom": [f"1px solid {LINE}"],
    }, children=[
        Block(name="Title", children=[
            Block("h2", text=promo["title"], styles={
                "marginTop": ["0px"], "marginBottom": ["0.35rem"], "color": ["#ffffff"], "lineHeight": ["1.1"],
                "fontSize": ["clamp(2rem, 4vw, 2.75rem)"],
            }),
            Block("p", text=promo["subtitle"], styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "fontSize": ["1.125rem"], "color": [SOFT_WHITE],
            }),
        ]),
        Block("p", text=promo["tag"], styles={
            "marginTop": ["0px"], "marginBottom": ["0px"], "paddingTop": ["0.5rem"], "paddingBottom": ["0.5rem"],
            "paddingLeft": ["0.9rem"], "paddingRight": ["0.9rem"], "backgroundColor": [ACCENT],
            "color": ["#ffffff"], "fontWeight": ["700"], "fontSize": ["0.85rem"],
            "textTransform": ["uppercase"], "letterSpacing": ["0.04em"],
        }),
    ])
    brands = Block(name="Brands", styles={
        "display": ["grid"],
        "gridTemplateColumns": [" ".join(f"minmax(0, {len(b['tiers'])}fr)" for b in promo["brands"]), "1fr"],
        "columnGap": ["2.5rem"], "rowGap": ["2.25rem"],
    }, children=[brand_panel(b) for b in promo["brands"]])
    strong, rest = promo["note"]
    note = Block("p", text=f"<strong>{strong}</strong>{rest}", text_is_html=True, styles={
        "marginTop": ["1.75rem"], "marginBottom": ["0px"], "paddingTop": ["1.25rem"],
        "borderTop": [f"1px solid {LINE}"], "color": [SOFT_WHITE],
    }, custom_css="{CURRENT} strong{color:#ffffff;}")
    return Block("section", name="Promo Banner", class_name=HEX_CLASS, styles={
        "position": ["relative"], "overflow": ["hidden"], "backgroundColor": [DARK],
        "paddingTop": ["2.25rem", None, None, "1.5rem"], "paddingBottom": ["2.5rem", None, None, "1.75rem"],
        "paddingLeft": ["2.25rem", None, None, "1.25rem"], "paddingRight": ["2.25rem", None, None, "1.25rem"],
    }, custom_css=THREAD_HERO_CSS, children=[head, brands, note])


PAGE = {"dir": "promo-banner", "title": "Promo Banner", "preview_css": ""}

if __name__ == "__main__":
    write(PAGE, banner(PROMO))
