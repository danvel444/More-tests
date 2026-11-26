"""Build a compact promo banner for a Blocksy Content Block (shown above product pages).

Data-driven, so the next promo only needs a new PROMO dict: a one-line header, then one
panel per brand with its spend tiers and a shop link in the brand's heading row.
"""
from build_policy_blocks import ACCENT, SOFT_WHITE, THREAD_HERO_CSS, Block, _seed, write

DARK = "#0d0e10"
LINE = "rgba(255, 255, 255, 0.14)"
SHOP = "https://bcfasteners.com/product-category/brand-names/"

PROMO = {
    "slug": "promo-black-friday",
    "title": "Black Friday",
    "subtitle": ("Free gifts with purchase.", " Deals are cumulative: the more you spend, the more you get."),
    "tag": "Online only. Extremely limited quantities.",
    "brands": [
        {
            "name": "Milwaukee", "count": "Up to 7 free gifts", "shop": "Shop Milwaukee",
            "url": SHOP + "milwaukee/",
            "tiers": [("$500+", "Hat + Toque"), ("$800+", "Bag + Towel"), ("$1,000+", "Sweater"),
                      ("$1,500+", "Chair"), ("$3,000+", "Cooler")],
        },
        {
            "name": "Wera", "count": "Up to 4 free gifts", "shop": "Shop Wera",
            "url": SHOP + "wera/",
            "tiers": [("$150+", "Trucker Hat"), ("$250+", "Toque"), ("$500+", "Flag"),
                      ("$600+", "Backpack")],
        },
    ],
}

# Tiers sit side by side with 1px lines between them (the grid gap shows the line colour).
# On phones each tier becomes a short row: amount on the left, gift on the right.
TIERS_CSS = (
    f"{{CURRENT}}{{list-style:none;margin:0;padding:0;display:grid;gap:1px;background-color:{LINE};"
    f"border:1px solid {LINE};border-top:2px solid {ACCENT};}}"
    f"{{CURRENT}} li{{margin:0;padding:0.55rem 0.75rem;background-color:{DARK};display:flex;"
    "flex-direction:column;gap:0.1rem;}"
    "{CURRENT} .tfgp-amount{font-weight:700;font-size:1.1rem;line-height:1.25;color:#ffffff;"
    "font-variant-numeric:tabular-nums;}"
    f"{{CURRENT}} .tfgp-gift{{font-size:0.85rem;line-height:1.3;color:{SOFT_WHITE};}}"
    "@media (max-width: 575.98px){"
    "{CURRENT}{grid-template-columns:1fr !important;}"
    "{CURRENT} li{flex-direction:row;justify-content:space-between;align-items:baseline;gap:1rem;"
    "padding:0.4rem 0.75rem;}"
    "{CURRENT} .tfgp-amount{font-size:1rem;}"
    "{CURRENT} .tfgp-gift{text-align:right;}}"
)

# A compact text link with an arrow, sitting at the end of each brand's heading row.
SHOP_LINK_CSS = (
    "{CURRENT}{display:inline-flex;align-items:center;gap:0.4rem;padding:0.3rem 0.75rem;"
    f"background-color:{ACCENT};border:1px solid {ACCENT};color:#ffffff;font-weight:700;font-size:0.85rem;"
    "text-decoration:none;white-space:nowrap;transition:background-color .2s,color .2s,border-color .2s;}"
    "{CURRENT}::after{content:\"\\2192\";}"
    "{CURRENT}:hover,{CURRENT}:focus-visible{background-color:#ffffff;border-color:#ffffff;color:#1d1f21;}"
    "{CURRENT}:focus-visible{outline:2px solid #ffffff;outline-offset:2px;}"
)

SMALL_CAPS = {
    "marginTop": ["0px"], "marginBottom": ["0px"], "fontSize": ["0.75rem"], "fontWeight": ["700"],
    "textTransform": ["uppercase"], "letterSpacing": ["0.06em"],
}


def brand_panel(brand):
    tiers = brand["tiers"]
    return Block(name=brand["name"], children=[
        Block(name="Brand Heading", styles={
            "display": ["flex"], "flexWrap": ["wrap"], "alignItems": ["center"],
            "columnGap": ["0.75rem"], "rowGap": ["0.35rem"], "marginBottom": ["0.6rem"],
        # On phones the gift count drops under the name so the shop link stays on the name's row.
        }, custom_css="@media (max-width: 575.98px){{CURRENT} p{order:3;flex-basis:100%;}}", children=[
            Block("h3", text=brand["name"], styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "color": ["#ffffff"],
                "fontSize": ["1.2rem"], "lineHeight": ["1.2"],
            }),
            Block("p", text=brand["count"], styles={**SMALL_CAPS, "color": [SOFT_WHITE]}),
            Block("a", text=brand["shop"], href=brand["url"], custom_css=SHOP_LINK_CSS,
                  styles={"marginLeft": ["auto"]}),
        ]),
        Block("ul", name="Tiers", styles={
            "gridTemplateColumns": [f"repeat({len(tiers)}, minmax(0, 1fr))"],
        }, custom_css=TIERS_CSS, children=[
            Block("li", children=[
                Block("span", text=amount, class_name="tfgp-amount"),
                Block("span", text=gift, class_name="tfgp-gift"),
            ]) for amount, gift in tiers
        ]),
    ])


def banner(promo):
    _seed["slug"], _seed["n"] = promo["slug"], 0
    strong, rest = promo["subtitle"]
    head = Block(name="Header", styles={
        "display": ["flex"], "flexWrap": ["wrap"], "alignItems": ["center"],
        "justifyContent": ["space-between"], "columnGap": ["1.5rem"], "rowGap": ["0.6rem"],
        "marginBottom": ["1rem"],
    }, children=[
        Block(name="Title", styles={
            "display": ["flex"], "flexWrap": ["wrap"], "alignItems": ["baseline"],
            "columnGap": ["0.9rem"], "rowGap": ["0.15rem"],
        }, children=[
            Block("h2", text=promo["title"], styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "color": ["#ffffff"], "lineHeight": ["1.1"],
                "fontSize": ["clamp(1.5rem, 3vw, 1.9rem)"],
            }),
            Block("p", text=f"<strong>{strong}</strong>{rest}", text_is_html=True, styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "fontSize": ["0.95rem"], "color": [SOFT_WHITE],
            }, custom_css="{CURRENT} strong{color:#ffffff;}"),
        ]),
        Block("p", text=promo["tag"], styles={
            **SMALL_CAPS, "paddingTop": ["0.35rem"], "paddingBottom": ["0.35rem"],
            "paddingLeft": ["0.7rem"], "paddingRight": ["0.7rem"], "backgroundColor": [ACCENT],
            "color": ["#ffffff"], "letterSpacing": ["0.04em"],
        }),
    ])
    brands = Block(name="Brands", styles={
        "display": ["grid"],
        "gridTemplateColumns": [" ".join(f"minmax(0, {len(b['tiers'])}fr)" for b in promo["brands"]), "1fr"],
        "columnGap": ["2rem"], "rowGap": ["1.1rem"],
    }, children=[brand_panel(b) for b in promo["brands"]])
    return Block("section", name="Promo Banner", styles={
        "position": ["relative"], "overflow": ["hidden"], "backgroundColor": [DARK],
        "paddingTop": ["1.25rem", None, None, "1rem"], "paddingBottom": ["1.5rem", None, None, "1.25rem"],
        "paddingLeft": ["1.5rem", None, None, "1rem"], "paddingRight": ["1.5rem", None, None, "1rem"],
    }, custom_css=THREAD_HERO_CSS, children=[head, brands])


PAGE = {"dir": "promo-banner", "title": "Promo Banner", "preview_css": ""}

if __name__ == "__main__":
    write(PAGE, banner(PROMO))
