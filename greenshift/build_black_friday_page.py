"""Build the Black Friday landing page: a dark hero, the free-gift ladders for each brand on
a grey panel pulled up over the hero, then the tagged WooCommerce products.

The offer itself comes from build_promo_banner.PROMO, so the banner and the page always match.
Links are relative (/product-category/...), so the same page works on each store's site.
"""
from build_policy_blocks import (
    ACCENT, BODY, INK, RULE, SOFT_WHITE, THREAD_HERO_CSS, Block, Raw, _seed, make_hero, write,
)
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


def gifts_panel(promo):
    strong, rest = promo["subtitle"]
    return Block(name="Free Gifts", anchor="gifts", styles={
        "backgroundColor": [PANEL_BG],
        "paddingTop": ["2.25rem", None, None, "1.5rem"], "paddingBottom": ["2.25rem", None, None, "1.5rem"],
        "paddingLeft": ["1.5rem", None, None, "1rem"], "paddingRight": ["1.5rem", None, None, "1rem"],
    }, children=[
        section_heading("Free gifts with purchase", "Spend more, get more"),
        Block(name="Brands", styles={
            "display": ["flex"], "flexDirection": ["column"], "rowGap": ["1.5rem"],
        }, children=[brand_card(b) for b in promo["brands"]]),
        Block("p", text=f"<strong>{rest.strip().split(':')[0]}.</strong> {rest.split(':', 1)[1].strip().capitalize()} "
                        f"{promo['tag']}", text_is_html=True, styles={
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


def body(promo):
    _seed["slug"], _seed["n"] = "black-friday-page", 0
    return Block(name="Black Friday Page", class_name="tfgr-page", styles={
        # The panel is pulled up over the bottom of the hero, as on the other pages.
        "marginTop": ["-4rem", None, None, "-3rem"], "position": ["relative"], "zIndex": ["2"],
        "marginBottom": ["4.5rem", None, None, "2.25rem"],
    }, custom_css="{CURRENT} [id]{scroll-margin-top:2rem;}",
        children=[gifts_panel(promo), products_section()])


def hero(promo):
    strong, rest = promo["subtitle"]
    return make_hero(
        seed="black-friday-hero", bg="#0d0e10", caption=promo["tag"], title=promo["title"],
        intro=strong + rest,
        buttons=[("See the free gifts", "#gifts"), ("Shop the deals", "#deals")],
        accent=ACCENT, pattern_css=THREAD_HERO_CSS, caption_color=SOFT_WHITE,
        align_to_theme=True, hex=False, top_padding=["5rem", None, None, "3.5rem"],
    )


PAGE = {"dir": "black-friday-page", "title": "Black Friday", "preview_css": """
body > .tfgr-page{max-width:1200px;margin-left:auto;margin-right:auto}
ul.products{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:24px}
"""}

if __name__ == "__main__":
    write(PAGE, body(PROMO), before=hero(PROMO))
