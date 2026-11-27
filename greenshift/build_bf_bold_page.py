"""Build the bold Black Friday front page (the black, red and blue design).

Same sections as build_black_friday_page.py, restyled: a black hero with a giant two-line
headline and a framed featured deal, a three-colour fact strip, then each section opens with
a solid colour banner over a black 6px frame. Gift tiers carry a square product image each.

The offer comes from build_promo_banner.PROMO, so the banner and this page always match.
All styling sits in each block's custom CSS, as in the design this was built from.
"""
import re

from build_policy_blocks import THEME_CONTAINER, Block, Raw, _seed, write
from build_black_friday_page import BRAND_PATH, LOGOS, PLACEHOLDER, SHORTCODE, TOP_BRANDS
from build_promo_banner import PROMO
from build_warranty_page import BRANDS

RED = "var(--wp--preset--color--palette-color-1, var(--theme-palette-color-1, #b11f24))"
BLUE = "#2c5169"
GIFTS = "/wp-content/uploads/2026/11/"  # bf-gift-<brand>-<gift>.webp, 600 x 600
PROMO_SLOTS = 4


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def css(text):
    """Custom CSS with the brand colour tokens filled in."""
    return text.replace("RED", RED).replace("BLUE", BLUE)


def full_band(name, children, rule):
    return Block("section", name=name, align="full", custom_css=css(rule), children=children)


# ---- Hero ---------------------------------------------------------------------------------

HERO_CSS = (
    "{CURRENT}{display:flex;flex-direction:column;align-items:center;margin-top:0px;margin-bottom:0px;"
    "position:relative;overflow:hidden;background-color:#000000;padding-top:4.5rem;padding-bottom:4.5rem;}"
    "@media (max-width: 575.98px){{CURRENT}{padding-top:2.75rem;padding-bottom:3rem;}}"
    "{CURRENT}::after{content:\"\";position:absolute;left:0;right:0;bottom:0;height:6px;pointer-events:none;"
    "background-color:RED;}"
)
BIG = "font-weight:900;text-transform:uppercase;letter-spacing:-0.01em;"
BUTTON = ("display:inline-flex;align-items:center;gap:0.6rem;padding:0.85rem 1.6rem;font-weight:800;"
          "text-transform:uppercase;letter-spacing:0.08em;font-size:0.9rem;text-decoration:none;white-space:nowrap;")


def hero():
    container = "".join(f"{k.replace('maxWidth', 'max-width')}:{v[0]};" for k, v in THEME_CONTAINER.items())
    text = Block(name="Hero Text", children=[
        Block("p", text="Online only · Limited quantities", custom_css=css(
            "{CURRENT}{display:inline-block;margin:0 0 1.5rem 0;padding:0.45rem 0.9rem;background-color:RED;"
            "color:#ffffff;font-weight:800;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.14em;}")),
        Block("h1", text=f"{PROMO['title']} <span>Deals</span>", text_is_html=True, custom_css=css(
            "{CURRENT}{margin:0;color:#ffffff;" + BIG + "font-size:clamp(3.5rem, 9vw, 7.25rem);line-height:0.9;}"
            "{CURRENT} span{display:block;color:RED;}")),
        Block("p", text="<strong>Free gifts with purchase.</strong> Deals are cumulative: the more you spend, "
                        "the more you get.", text_is_html=True, custom_css=(
            "{CURRENT}{margin:1.75rem 0 0 0;max-width:30rem;font-size:1.15rem;line-height:1.5;"
            "color:rgba(255, 255, 255, 0.85);}{CURRENT} strong{color:#ffffff;}")),
        Block(name="Buttons", custom_css=(
            "{CURRENT}{display:flex;flex-wrap:wrap;column-gap:0.75rem;row-gap:0.75rem;margin-top:2rem;}"), children=[
            Block("a", text="Shop the deals", href="#deals", custom_css=css(
                "{CURRENT}{" + BUTTON + "background-color:RED;border:2px solid RED;color:#ffffff;"
                "transition:background-color .2s,border-color .2s,color .2s;}"
                "{CURRENT}::after{content:\"\\2193\";}"
                "{CURRENT}:hover,{CURRENT}:focus-visible{background-color:#ffffff;border-color:#ffffff;color:#000000;}"
                "{CURRENT}:focus-visible{outline:2px solid #ffffff;outline-offset:3px;}")),
            Block("a", text="See the free gifts", href="#gifts", custom_css=css(
                "{CURRENT}{" + BUTTON + "border:2px solid #ffffff;color:#ffffff;transition:background-color .2s,color .2s;}"
                "{CURRENT}::after{content:\"\\2193\";}"
                "{CURRENT}:hover,{CURRENT}:focus-visible{background-color:#ffffff;color:#000000;}"
                "{CURRENT}:focus-visible{outline:2px solid RED;outline-offset:3px;}")),
        ]),
    ])
    feature = Block("a", name="Featured Promo", href="#", custom_css=(
        "{CURRENT}{display:block;background-color:#ffffff;border:3px solid #ffffff;text-decoration:none;position:relative;}"
        "{CURRENT} img{display:block;width:100%;height:auto;aspect-ratio:1 / 1;object-fit:cover;}"
        "{CURRENT}:focus-visible{outline:2px solid #ffffff;outline-offset:3px;}"), children=[
        Block("p", text="Featured deal", custom_css=(
            "{CURRENT}{position:absolute;top:0;left:0;z-index:1;margin:0;padding:0.5rem 1rem;background-color:#000000;"
            "color:#ffffff;font-weight:800;font-size:0.85rem;text-transform:uppercase;letter-spacing:0.1em;}")),
        image(PLACEHOLDER, "Featured promo", 1200, "Featured Promo Image"),
        Block("p", text="Shop the featured deal ›", custom_css=css(
            "{CURRENT}{margin:0;padding:0.9rem 1rem;background-color:RED;color:#ffffff;text-align:center;"
            "font-weight:800;text-transform:uppercase;letter-spacing:0.08em;transition:background-color .2s;}"
            "a:hover > {CURRENT}{background-color:#000000;}")),
    ])
    columns = Block(name="Hero Columns", custom_css=(
        "{CURRENT}{display:grid;grid-template-columns:minmax(0, 7fr) minmax(0, 5fr);column-gap:4rem;row-gap:2.5rem;"
        "align-items:center;}"
        "@media (max-width: 991.98px){{CURRENT}{column-gap:2.5rem;}}"
        "@media (max-width: 767.98px){{CURRENT}{grid-template-columns:1fr;}}"), children=[text, feature])
    return full_band("Hero", [Block(name="Content Area", custom_css="{CURRENT}{" + container + "}",
                                    children=[columns])], HERO_CSS)


def image(src, alt, size, name="Image"):
    return Block("img", name=name, json_extra={"src": src, "alt": alt, "originalWidth": size, "originalHeight": size},
                 html_attrs=[("src", src), ("alt", alt), ("width", str(size)), ("height", str(size)),
                             ("loading", "lazy")])


# ---- Fact strip ---------------------------------------------------------------------------

STRIP_LIST_CSS = (
    "{CURRENT}{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3, minmax(0, 1fr));"
    "gap:2px;background-color:#000000;}"
    "{CURRENT} li{margin:0;padding:0.95rem 1rem;background-color:BLUE;color:#ffffff;text-align:center;"
    "font-weight:900;text-transform:uppercase;font-size:1.05rem;line-height:1.25;letter-spacing:0.02em;}"
    "{CURRENT} li:first-child{background-color:RED;}"
    "{CURRENT} li span{display:block;font-weight:600;font-size:0.72rem;letter-spacing:0.14em;opacity:0.85;"
    "margin-bottom:0.15rem;}"
    "@media (max-width: 767.98px){{CURRENT}{grid-template-columns:1fr;}{CURRENT} li{padding:0.7rem 1rem;}}"
)
FACTS = [("Free gifts", "With purchase"), ("The more you spend", "The more you get"),
         ("Online only", "Extremely limited qty")]


def strip():
    facts = Block("ul", name="Facts", custom_css=css(STRIP_LIST_CSS), children=[
        Block("li", text=f"<span>{small}</span>{big}", text_is_html=True) for small, big in FACTS
    ])
    return full_band("Offer Strip", [facts],
                     "{CURRENT}{margin-top:0px;margin-bottom:0px;background-color:#000000;padding:0 0 6px 0;}")


# ---- Section parts ------------------------------------------------------------------------

def banner(label, title, bg, extra=""):
    return Block(name="Banner", custom_css=css(
        "{CURRENT}{background-color:" + bg + ";padding:1.4rem 1.5rem 1.3rem;text-align:center;" + extra + "}"
        "@media (max-width: 575.98px){{CURRENT}{padding:1.1rem 1rem 1rem;}}"), children=[
        Block("p", text=label, custom_css=(
            "{CURRENT}{margin:0 0 0.35rem 0;color:#ffffff;font-weight:700;font-size:0.8rem;text-transform:uppercase;"
            "letter-spacing:0.28em;opacity:0.9;}")),
        Block("h2", text=title, custom_css=(
            "{CURRENT}{margin:0;color:#ffffff;" + BIG + "font-size:clamp(1.9rem, 4.5vw, 3rem);line-height:1;}")),
    ])


def frame(children, extra="", css_extra=""):
    return Block(name="Frame", custom_css="{CURRENT}{background-color:#000000;padding:6px;" + extra + "}" + css_extra,
                 children=children)


def section(name, anchor, children):
    return Block(name=name, anchor=anchor, custom_css=(
        "{CURRENT}{margin-top:4rem;}@media (max-width: 575.98px){{CURRENT}{margin-top:2.5rem;}}"), children=children)


# ---- Top promos ---------------------------------------------------------------------------

PROMO_GRID_CSS = (
    "{CURRENT}{display:grid;grid-template-columns:repeat(4, minmax(0, 1fr));gap:6px;}"
    "@media (max-width: 767.98px){{CURRENT}{grid-template-columns:repeat(2, minmax(0, 1fr));}}"
    "{CURRENT} .tfgbf-promo{display:flex;flex-direction:column;position:relative;background-color:#ffffff;"
    "text-decoration:none;color:inherit;}"
    "{CURRENT} .tfgbf-promo-tag{position:absolute;top:0;left:0;z-index:1;margin:0;padding:0.35rem 0.8rem;"
    "background-color:#000000;color:#ffffff;font-weight:800;font-size:0.75rem;text-transform:uppercase;"
    "letter-spacing:0.08em;}"
    "{CURRENT} .tfgbf-promo img{display:block;width:100%;height:auto;aspect-ratio:1 / 1;object-fit:cover;}"
    "{CURRENT} .tfgbf-promo-title{margin:0;padding:0.85rem 0.75rem 0.75rem;color:#000000;font-weight:800;"
    "font-size:1.05rem;line-height:1.25;text-align:center;}"
    "{CURRENT} .tfgbf-promo-link{margin:auto 0 0 0;padding:0.75rem;background-color:RED;color:#ffffff;"
    "font-weight:800;text-transform:uppercase;letter-spacing:0.08em;text-align:center;transition:background-color .2s;}"
    "{CURRENT} .tfgbf-promo-link::after{content:\" \\203A\";}"
    "{CURRENT} .tfgbf-promo:hover .tfgbf-promo-link,{CURRENT} .tfgbf-promo:focus-visible .tfgbf-promo-link"
    "{background-color:#000000;}"
    "{CURRENT} .tfgbf-promo:focus-visible{outline:3px solid #ffffff;outline-offset:-3px;}"
    "@media (max-width: 575.98px){{CURRENT} .tfgbf-promo-title{font-size:0.95rem;padding:0.7rem 0.5rem 0.6rem;}"
    "{CURRENT} .tfgbf-promo-link{font-size:0.85rem;padding:0.65rem 0.4rem;}}"
)


def promos_section():
    cards = [Block("a", class_name="tfgbf-promo", name=f"Promo {i}", href="#", children=[
        Block("p", text="Hot deal", class_name="tfgbf-promo-tag"),
        image(PLACEHOLDER, f"Promo {i}", 1200),
        Block("p", text=f"Promo title {i}", class_name="tfgbf-promo-title"),
        Block("p", text="Shop now", class_name="tfgbf-promo-link"),
    ]) for i in range(1, PROMO_SLOTS + 1)]
    return section("Top Promos", "promos", [
        banner("Top promos", "This week’s biggest deals", RED),
        frame([Block(name="Promo Grid", custom_css=css(PROMO_GRID_CSS), children=cards)]),
    ])


# ---- Free gifts ---------------------------------------------------------------------------

TIERS_CSS = (
    "{CURRENT}{list-style:none;margin:0;padding:0;display:grid;gap:2px;background-color:#000000;"
    "border-top:2px solid #000000;}"
    "{CURRENT} li{margin:0;padding:1.1rem 0.75rem;background-color:#ffffff;display:flex;flex-direction:column;"
    "align-items:center;text-align:center;gap:0.45rem;}"
    "{CURRENT} .tfgp-step{font-size:0.72rem;font-weight:800;text-transform:uppercase;letter-spacing:0.12em;color:RED;}"
    "{CURRENT} .tfgp-amount{display:inline-block;padding:0.3rem 0.75rem;background-color:#000000;color:#ffffff;"
    "font-weight:900;font-size:1.3rem;line-height:1.15;font-variant-numeric:tabular-nums;}"
    "{CURRENT} .tfgp-gift{font-weight:700;line-height:1.3;color:#000000;}"
    "{CURRENT} li img{display:block;width:100%;max-width:170px;height:auto;aspect-ratio:1 / 1;object-fit:contain;"
    "margin-bottom:0.25rem;}"
    "@media (max-width: 575.98px){{CURRENT}{grid-template-columns:1fr !important;}"
    "{CURRENT} li{display:grid;grid-template-columns:72px 1fr auto;align-items:center;column-gap:0.9rem;"
    "padding:0.5rem 0.8rem;text-align:left;}"
    "{CURRENT} li img{grid-column:1;grid-row:1;max-width:72px;margin:0;}"
    "{CURRENT} .tfgp-step{display:none;}"
    "{CURRENT} .tfgp-gift{grid-column:2;grid-row:1;}"
    "{CURRENT} .tfgp-amount{grid-column:3;grid-row:1;font-size:1.05rem;}}"
)


def brand_card(brand):
    tiers = brand["tiers"]
    url = BRAND_PATH + slug(brand["name"]) + "/"
    return Block(name=brand["name"], custom_css="{CURRENT}{background-color:#ffffff;}", children=[
        Block(name="Brand Heading", custom_css=css(
            "{CURRENT}{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;column-gap:1rem;"
            "row-gap:0.75rem;padding:1.1rem 1.25rem;border-bottom:4px solid RED;}"
            "@media (max-width: 575.98px){{CURRENT}{padding:0.9rem 1rem;}}"), children=[
            Block(name="Name", custom_css=(
                "{CURRENT}{display:flex;flex-wrap:wrap;align-items:center;column-gap:0.9rem;row-gap:0.4rem;}"), children=[
                Block("h3", text=brand["name"], custom_css=(
                    "{CURRENT}{margin:0;color:#000000;" + BIG + "font-size:clamp(1.5rem, 3vw, 2rem);line-height:1;}")),
                Block("p", text=brand["count"], custom_css=(
                    "{CURRENT}{margin:0;padding:0.3rem 0.7rem;background-color:#000000;color:#ffffff;font-weight:800;"
                    "font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;}")),
            ]),
            Block("a", text=brand["shop"], href=url, custom_css=css(
                "{CURRENT}{display:inline-flex;align-items:center;gap:0.6rem;padding:0.75rem 1.4rem;background-color:RED;"
                "color:#ffffff;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;font-size:0.85rem;"
                "text-decoration:none;white-space:nowrap;transition:background-color .2s;}"
                "{CURRENT}::after{content:\"\\203A\";font-size:1.1em;}"
                "{CURRENT}:hover,{CURRENT}:focus-visible{background-color:#000000;}"
                "{CURRENT}:focus-visible{outline:2px solid RED;outline-offset:2px;}")),
        ]),
        Block("ul", name="Gift Tiers", custom_css=css(
            "{CURRENT}{grid-template-columns:repeat(" + str(len(tiers)) + ", minmax(0, 1fr));}" + TIERS_CSS), children=[
            Block("li", children=[
                image(f"{GIFTS}bf-gift-{slug(brand['name'])}-{slug(gift)}.webp", gift, 600, "Gift Image"),
                Block("span", text=f"Tier {i}", class_name="tfgp-step"),
                Block("span", text=amount, class_name="tfgp-amount"),
                Block("span", text=gift, class_name="tfgp-gift"),
            ]) for i, (amount, gift) in enumerate(tiers, 1)
        ]),
    ])


def gifts_section():
    note = Block("p", text="<strong>Deals are cumulative.</strong> The more you spend, the more you get. "
                           + PROMO["tag"], text_is_html=True, custom_css=(
        "{CURRENT}{margin:0;padding:0.8rem 1rem 0.7rem;color:rgba(255, 255, 255, 0.8);text-align:center;font-size:0.95rem;}"
        "{CURRENT} strong{color:#ffffff;}"))
    return section("Free Gifts", "gifts", [
        banner("Free gifts with purchase", "Spend more, get more", BLUE),
        frame([*(brand_card(b) for b in PROMO["brands"]), note], "display:flex;flex-direction:column;row-gap:6px;"),
    ])


# ---- Products -----------------------------------------------------------------------------

PRODUCTS_CSS = (
    "{CURRENT} ul.products{--grid-columns-gap:6px;gap:6px !important;margin:0 !important;}"
    "@media (max-width: 1199.98px){{CURRENT} ul.products{grid-template-columns:repeat(4, minmax(0, 1fr)) !important;}}"
    "@media (max-width: 767.98px){{CURRENT} ul.products{grid-template-columns:repeat(2, minmax(0, 1fr)) !important;}}"
    "{CURRENT} ul.products li.product{margin:0 !important;padding:0.75rem !important;background-color:#ffffff;"
    "border:0 !important;border-radius:0 !important;text-align:center;display:flex;flex-direction:column;}"
    "{CURRENT} ul.products li.product .woocommerce-loop-product__title{color:#000000;font-weight:800;"
    "font-size:0.95rem;line-height:1.3;}"
    "{CURRENT} ul.products li.product .price{color:RED !important;font-weight:900;font-size:1.3rem;}"
    "{CURRENT} ul.products li.product .price del{color:#777777;font-weight:400;font-size:0.85rem;}"
    "{CURRENT} ul.products li.product .price ins{text-decoration:none;}"
    "{CURRENT} ul.products li.product .onsale{background-color:#000000 !important;color:#ffffff;"
    "border-radius:0 !important;font-weight:800;text-transform:uppercase;letter-spacing:0.06em;}"
    "{CURRENT} ul.products li.product .button{margin-top:auto !important;width:100% !important;"
    "justify-content:center;background-color:RED !important;color:#ffffff !important;border:0 !important;"
    "border-radius:0 !important;font-weight:800;text-transform:uppercase;letter-spacing:0.08em;}"
    "{CURRENT} ul.products li.product .button:hover{background-color:#000000 !important;}"
)


def products_section():
    return section("Black Friday Deals", "deals", [
        banner("Black Friday deals", "Shop the sale", RED),
        frame([Raw(f"<!-- wp:shortcode -->\n{SHORTCODE}\n<!-- /wp:shortcode -->")], css_extra=css(PRODUCTS_CSS)),
    ])


# ---- Top brands ---------------------------------------------------------------------------

LOGO_GRID_CSS = (
    "{CURRENT}{display:grid;grid-template-columns:repeat(6, 1fr);gap:6px;}"
    "@media (max-width: 991.98px){{CURRENT}{grid-template-columns:repeat(4, 1fr);}}"
    "@media (max-width: 575.98px){{CURRENT}{grid-template-columns:repeat(3, 1fr);}}"
    "{CURRENT} .tfgr-logo{display:flex;align-items:center;justify-content:center;padding:1.25rem 1.5rem;"
    "aspect-ratio:3 / 2;background-color:#ffffff;border-bottom:4px solid #ffffff;transition:border-color .2s;}"
    "{CURRENT} .tfgr-logo img{display:block;width:100%;max-width:9rem;height:auto;max-height:100%;object-fit:contain;}"
    "@media (max-width: 575.98px){{CURRENT} .tfgr-logo{padding:0.6rem 0.75rem;}}"
    "{CURRENT} a.tfgr-logo:hover,{CURRENT} a.tfgr-logo:focus-visible{border-bottom-color:RED;}"
    "{CURRENT} a.tfgr-logo:focus-visible{outline:2px solid RED;outline-offset:-2px;}"
)


def brands_section():
    by_name = {b[0]: b for b in BRANDS}
    logos = []
    for name in TOP_BRANDS:
        _n, logo, _alt, _url, w, h = by_name[name]
        path = name.lower().replace(" tools", "").replace(" safety", "").replace(" ", "-")
        logos.append(Block("a", class_name="tfgr-logo", name=name, href=f"{BRAND_PATH}{path}/", children=[
            Block("img", json_extra={"src": LOGOS + logo, "alt": name, "originalWidth": w, "originalHeight": h},
                  html_attrs=[("src", LOGOS + logo), ("alt", name), ("width", str(w)), ("height", str(h)),
                              ("loading", "lazy")]),
        ]))
    return section("Top Brands", "brands", [
        banner("Top brands", "Shop by brand", "#000000", "border-bottom:4px solid RED;"),
        frame([Block(name="Logos", custom_css=css(LOGO_GRID_CSS), children=logos)]),
    ])


def body():
    return Block(name="Black Friday Page", class_name="tfgr-page", custom_css=(
        "{CURRENT}{margin-bottom:4.5rem;}@media (max-width: 575.98px){{CURRENT}{margin-bottom:2.5rem;}}"
        "{CURRENT} [id]{scroll-margin-top:2rem;}"),
        children=[promos_section(), gifts_section(), products_section(), brands_section()])


PAGE = {"dir": "black-friday-bold", "title": "Black Friday", "preview_css": """
body > .tfgr-page{max-width:1200px;margin-left:auto;margin-right:auto;padding:0 20px}
ul.products{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(6,minmax(0,1fr))}
"""}

if __name__ == "__main__":
    _seed["slug"], _seed["n"] = "bf-bold", 0
    write(PAGE, [hero(), strip(), body()])
