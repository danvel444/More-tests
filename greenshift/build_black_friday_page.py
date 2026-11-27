"""Build the Black Friday front page:
  1. Dark hero: big headline, offer, two jump buttons, and a square featured-promo image.
  2. Red strip with the three offer facts.
  3. Top promos: four square image slots, each with a title and link.
  4. Free gifts: the gift tiers for each brand on a grey panel.
  5. Shop the sale: the tagged WooCommerce products.
  6. Top brands: a ruled grid of logos linking to each brand's category.

The offer itself comes from build_promo_banner.PROMO, so the banner and the page always match.
Links are relative (/product-category/...), so the same page works on each store's site.
"""
from build_policy_blocks import (
    ACCENT, BODY, INK, RULE, SOFT_WHITE, THEME_CONTAINER, THREAD_HERO_CSS, Block, Raw, _seed,
    button_css, write,
)
from build_home_page import BRAND_CSS, ruled_grid
from build_warranty_page import BRANDS
from build_industries_page import SOLID_BUTTON_CSS, section_heading
from build_promo_banner import PROMO

PANEL_BG = "var(--wp--preset--color--palette-color-5, var(--theme-palette-color-5, #F0F2F3))"
SHORTCODE = '[products tag="black-friday" limit="24" columns="6" orderby="date" order="DESC"]'
BRAND_PATH = "/product-category/brand-names/"

# The gift ladder, light version: white cells with thin lines, a red rule along the top.
# On phones each tier becomes a row: amount on the left, gift on the right.
TIERS_CSS = (
    f"{{CURRENT}}{{list-style:none;margin:0;padding:0;display:grid;gap:1px;background-color:{RULE};"
    f"border:1px solid {RULE};border-top:3px solid {ACCENT};}}"
    "{CURRENT} li{margin:0;padding:1rem 0.9rem;background-color:#ffffff;display:flex;"
    "flex-direction:column;gap:0.2rem;}"
    f"{{CURRENT}} .tfgp-step{{font-size:0.75rem;font-weight:700;text-transform:uppercase;"
    f"letter-spacing:0.06em;color:{ACCENT};}}"
    f"{{CURRENT}} .tfgp-amount{{font-weight:700;font-size:1.35rem;line-height:1.2;color:{INK};"
    "font-variant-numeric:tabular-nums;}"
    f"{{CURRENT}} .tfgp-gift{{line-height:1.35;color:{BODY};}}"
    "@media (max-width: 575.98px){"
    "{CURRENT}{grid-template-columns:1fr !important;}"
    "{CURRENT} li{display:grid;grid-template-columns:auto 1fr;align-items:baseline;column-gap:1rem;"
    "padding:0.6rem 0.9rem;}"
    "{CURRENT} .tfgp-step{display:none;}"
    "{CURRENT} .tfgp-amount{font-size:1.1rem;}"
    "{CURRENT} .tfgp-gift{text-align:right;}}"
)

# WooCommerce's product grid, given six columns by the shortcode; fewer on smaller screens.
PRODUCTS_CSS = (
    "@media (max-width: 1199.98px){{CURRENT} ul.products{grid-template-columns:repeat(4, minmax(0, 1fr)) !important;}}"
    "@media (max-width: 767.98px){{CURRENT} ul.products{grid-template-columns:repeat(2, minmax(0, 1fr)) !important;}}"
)


def brand_card(brand):
    tiers = brand["tiers"]
    url = BRAND_PATH + brand["url"].rstrip("/").rsplit("/", 1)[-1] + "/"
    return Block(name=brand["name"], styles={
        "backgroundColor": ["#ffffff"], "border": [f"1px solid {RULE}"],
        "paddingTop": ["1.5rem", None, None, "1.25rem"], "paddingBottom": ["1.5rem", None, None, "1.25rem"],
        "paddingLeft": ["1.5rem", None, None, "1rem"], "paddingRight": ["1.5rem", None, None, "1rem"],
    }, children=[
        Block(name="Brand Heading", styles={
            "display": ["flex"], "flexWrap": ["wrap"], "alignItems": ["center"],
            "justifyContent": ["space-between"], "columnGap": ["1rem"], "rowGap": ["0.75rem"],
            "marginBottom": ["1.25rem"],
        }, children=[
            Block(name="Name", children=[
                Block("h3", text=brand["name"], styles={
                    "marginTop": ["0px"], "marginBottom": ["0.15rem"], "color": [INK],
                }),
                Block("p", text=brand["count"], styles={
                    "marginTop": ["0px"], "marginBottom": ["0px"], "fontWeight": ["700"],
                    "fontSize": ["0.8rem"], "textTransform": ["uppercase"], "letterSpacing": ["0.06em"],
                    "color": [BODY],
                }),
            ]),
            Block("a", text=brand["shop"], href=url, custom_css=SOLID_BUTTON_CSS),
        ]),
        Block("ul", name="Gift Tiers", styles={
            "gridTemplateColumns": [f"repeat({len(tiers)}, minmax(0, 1fr))", None, None, None],
        }, custom_css=TIERS_CSS, children=[
            Block("li", children=[
                Block("span", text=f"Tier {i}", class_name="tfgp-step"),
                Block("span", text=amount, class_name="tfgp-amount"),
                Block("span", text=gift, class_name="tfgp-gift"),
            ]) for i, (amount, gift) in enumerate(tiers, 1)
        ]),
    ])


DARK = "#0d0e10"
# WooCommerce's own placeholder: square, and present on every store, so each slot shows
# something until you swap in your promo image (Image block > Replace).
PLACEHOLDER = "/wp-content/plugins/woocommerce/assets/images/placeholder.png"
LOGOS = "https://thefastenergroup.com/wp-content/uploads/"
TOP_BRANDS = ["Milwaukee", "Makita", "DeWalt", "Bosch", "Klein Tools", "Ridgid",
              "Stihl", "EGO", "Fein", "King Canada", "MSA Safety", "Walter"]
PROMO_SLOTS = 4


def square_image(alt, name="Image"):
    return Block("img", name=name, json_extra={"src": PLACEHOLDER, "alt": alt},
                 html_attrs=[("src", PLACEHOLDER), ("alt", alt), ("width", "1200"), ("height", "1200"),
                             ("loading", "lazy")],
                 styles={"display": ["block"], "width": ["100%"], "height": ["auto"],
                         "aspectRatio": ["1 / 1"], "objectFit": ["cover"]})


def wrap(name, children, styles=None, **kw):
    """A full-width band whose content lines up with the theme's container."""
    return Block("section", name=name, align="full", styles={
        "display": ["flex"], "flexDirection": ["column"], "alignItems": ["center"],
        "marginTop": ["0px"], "marginBottom": ["0px"], **(styles or {}),
    }, json_extra={"isVariation": "contentcolumns"}, children=[
        Block(name="Content Area", styles=dict(THEME_CONTAINER), json_extra={"isVariation": "contentarea"},
              children=children),
    ], **kw)


def hero(promo):
    _seed["slug"], _seed["n"] = "bf-front-hero", 0
    strong, rest = promo["subtitle"]
    text = Block(name="Hero Text", children=[
        Block("p", text="Online only", styles={
            "display": ["inline-block"], "marginTop": ["0px"], "marginBottom": ["1.25rem"],
            "paddingTop": ["0.3rem"], "paddingBottom": ["0.3rem"], "paddingLeft": ["0.7rem"], "paddingRight": ["0.7rem"],
            "backgroundColor": [ACCENT], "color": ["#ffffff"], "fontWeight": ["700"], "fontSize": ["0.8rem"],
            "textTransform": ["uppercase"], "letterSpacing": ["0.08em"],
        }),
        Block("h1", text=promo["title"], styles={
            "marginTop": ["0px"], "marginBottom": ["0px"], "color": ["#ffffff"],
            "fontSize": ["clamp(3.25rem, 8vw, 6.5rem)"], "lineHeight": ["0.95"], "letterSpacing": ["-0.02em"],
        }),
        Block("p", text=f"<strong>{strong}</strong>{rest}", text_is_html=True, styles={
            "marginTop": ["1.5rem"], "marginBottom": ["0px"], "maxWidth": ["30rem"], "fontSize": ["1.15rem"],
            "color": ["rgba(255, 255, 255, 0.85)"],
        }, custom_css="{CURRENT} strong{color:#ffffff;}"),
        Block(name="Buttons", styles={
            "display": ["flex"], "flexWrap": ["wrap"], "columnGap": ["0.75rem"], "rowGap": ["0.75rem"],
            "marginTop": ["2rem"],
        }, children=[
            Block("a", text="Shop the deals", href="#deals", custom_css=SOLID_BUTTON_CSS.replace('"\\2192"', '"\\2193"').replace(
                "background-color:#1d1f21;border-color:#1d1f21;color:#ffffff;",
                "background-color:#ffffff;border-color:#ffffff;color:#1d1f21;")),
            Block("a", text="See the free gifts", href="#gifts", custom_css=button_css("0", accent=ACCENT)),
        ]),
    ])
    feature = Block("a", name="Featured Promo", href="#", styles={
        "display": ["block"], "border": ["1px solid rgba(255, 255, 255, 0.14)"],
    }, children=[square_image("Featured promo", "Featured Promo Image")])
    grid = Block(name="Hero Columns", styles={
        "display": ["grid"], "gridTemplateColumns": ["minmax(0, 7fr) minmax(0, 5fr)", None, "1fr"],
        "columnGap": ["4rem", "2.5rem"], "rowGap": ["2.5rem"], "alignItems": ["center"],
    }, children=[text, feature])
    return wrap("Hero", [grid], styles={
        "position": ["relative"], "overflow": ["hidden"], "backgroundColor": [DARK],
        "paddingTop": ["4.5rem", None, None, "3rem"], "paddingBottom": ["4.5rem", None, None, "3rem"],
    }, custom_css=THREAD_HERO_CSS)


# Three facts on the red strip, divided by thin lines; stacked on phones.
STRIP_CSS = (
    "{CURRENT}{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3, minmax(0, 1fr));}"
    "{CURRENT} li{margin:0;padding:0 1.5rem;color:#ffffff;font-weight:700;text-transform:uppercase;"
    "letter-spacing:0.06em;font-size:0.85rem;text-align:center;border-left:1px solid rgba(255, 255, 255, 0.35);}"
    "{CURRENT} li:first-child{border-left:0;}"
    "@media (max-width: 767.98px){{CURRENT}{grid-template-columns:1fr;row-gap:0.5rem;}"
    "{CURRENT} li{border-left:0;padding:0;}}"
)


def strip(promo):
    facts = ["Free gifts with purchase", "Deals are cumulative", promo["tag"].rstrip(".").replace(". ", ", ").lower().capitalize()]
    return wrap("Offer Strip", [Block("ul", name="Facts", custom_css=STRIP_CSS, children=[
        Block("li", text=f) for f in facts
    ])], styles={
        "backgroundColor": [ACCENT], "paddingTop": ["1rem"], "paddingBottom": ["1rem"],
    })


PROMO_CSS = (
    "{CURRENT} .tfgbf-promo{display:flex;flex-direction:column;text-decoration:none;color:inherit;}"
    f"{{CURRENT}} .tfgbf-promo img{{border:1px solid {RULE};transition:border-color .2s;}}"
    f"{{CURRENT}} .tfgbf-promo-title{{margin:0.85rem 0 0.2rem 0;color:{INK};font-weight:700;font-size:1.1rem;}}"
    f"{{CURRENT}} .tfgbf-promo-link{{margin:0;color:{ACCENT};font-weight:700;}}"
    "{CURRENT} .tfgbf-promo-link::after{content:\" \\2192\";}"
    f"{{CURRENT}} .tfgbf-promo:hover img,{{CURRENT}} .tfgbf-promo:focus-visible img{{border-color:{ACCENT};}}"
    "{CURRENT} .tfgbf-promo:hover .tfgbf-promo-link,{CURRENT} .tfgbf-promo:focus-visible .tfgbf-promo-link{text-decoration:underline;}"
    f"{{CURRENT}} .tfgbf-promo:focus-visible{{outline:2px solid {ACCENT};outline-offset:3px;}}"
)


def promos_section():
    cards = [Block("a", class_name="tfgbf-promo", name=f"Promo {i}", href="#", children=[
        square_image(f"Promo {i}"),
        Block("p", text=f"Promo title {i}", class_name="tfgbf-promo-title"),
        Block("p", text="Shop now", class_name="tfgbf-promo-link"),
    ]) for i in range(1, PROMO_SLOTS + 1)]
    return Block(name="Top Promos", anchor="promos", styles={
        "marginTop": ["4rem", None, None, "2.5rem"],
    }, children=[
        section_heading("Top promos", "This week's biggest deals"),
        Block(name="Promo Grid", styles={
            "display": ["grid"], "gridTemplateColumns": [f"repeat({PROMO_SLOTS}, minmax(0, 1fr))", None, "repeat(2, minmax(0, 1fr))"],
            "columnGap": ["1.5rem", None, None, "1rem"], "rowGap": ["2rem", None, None, "1.5rem"],
        }, custom_css=PROMO_CSS, children=cards),
    ])


def gifts_panel(promo):
    return Block(name="Free Gifts", anchor="gifts", styles={
        "backgroundColor": [PANEL_BG], "marginTop": ["4.5rem", None, None, "3rem"],
        "paddingTop": ["2.25rem", None, None, "1.5rem"], "paddingBottom": ["2.25rem", None, None, "1.5rem"],
        "paddingLeft": ["1.5rem", None, None, "1rem"], "paddingRight": ["1.5rem", None, None, "1rem"],
    }, children=[
        section_heading("Free gifts with purchase", "Spend more, get more"),
        Block(name="Brands", styles={
            "display": ["flex"], "flexDirection": ["column"], "rowGap": ["1.5rem"],
        }, children=[brand_card(b) for b in promo["brands"]]),
        Block("p", text="<strong>Deals are cumulative.</strong> The more you spend, the more you get. "
                        + promo["tag"], text_is_html=True, styles={
            "marginTop": ["1.5rem"], "marginBottom": ["0px"], "color": [BODY],
        }, custom_css=f"{{CURRENT}} strong{{color:{INK};}}"),
    ])


def products_section():
    return Block(name="Black Friday Deals", anchor="deals", styles={
        "marginTop": ["4.5rem", None, None, "3rem"],
    }, custom_css=PRODUCTS_CSS, children=[
        section_heading("Black Friday deals", "Shop the sale"),
        Block(name="Products", children=[Raw(f"<!-- wp:shortcode -->\n{SHORTCODE}\n<!-- /wp:shortcode -->")]),
    ])


def brands_section():
    by_name = {b[0]: b for b in BRANDS}
    logos = []
    for name in TOP_BRANDS:
        _n, logo, _alt, _url, w, h = by_name[name]
        slug = name.lower().replace(" tools", "").replace(" safety", "").replace(" ", "-")
        logos.append(Block("a", class_name="tfgr-logo", name=name, href=f"{BRAND_PATH}{slug}/", children=[
            Block("img", json_extra={"src": LOGOS + logo, "alt": name, "originalWidth": w, "originalHeight": h},
                  html_attrs=[("src", LOGOS + logo), ("alt", name), ("width", str(w)), ("height", str(h)),
                              ("loading", "lazy")]),
        ]))
    css = BRAND_CSS + (
        "{CURRENT} a.tfgr-logo{transition:background-color .2s;}"
        f"{{CURRENT}} a.tfgr-logo:hover,{{CURRENT}} a.tfgr-logo:focus-visible{{background-color:{PANEL_BG};}}"
        f"{{CURRENT}} a.tfgr-logo:focus-visible{{outline:2px solid {ACCENT};outline-offset:-2px;}}"
    )
    return Block(name="Top Brands", anchor="brands", styles={
        "marginTop": ["4.5rem", None, None, "3rem"],
    }, children=[
        section_heading("Top brands", "Shop by brand"),
        ruled_grid("Logos", ["repeat(6, 1fr)", "repeat(4, 1fr)", None, "repeat(3, 1fr)"], css, logos),
    ])


def body(promo):
    _seed["slug"], _seed["n"] = "bf-front-body", 0
    return Block(name="Black Friday Page", class_name="tfgr-page", styles={
        "marginBottom": ["4.5rem", None, None, "2.5rem"],
    }, custom_css="{CURRENT} [id]{scroll-margin-top:2rem;}",
        children=[promos_section(), gifts_panel(promo), products_section(), brands_section()])


PAGE = {"dir": "black-friday-page", "title": "Black Friday", "preview_css": """
body > .tfgr-page{max-width:1200px;margin-left:auto;margin-right:auto}
ul.products{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:24px}
"""}

if __name__ == "__main__":
    write(PAGE, [hero(PROMO), strip(PROMO), body(PROMO)])
