"""Build the Contact Us page: the honeycomb hero, then one panel with the enquiry form
beside the "not a form person?" options and the store link.
"""
from build_policy_blocks import (
    ACCENT, BODY, GS_PREVIEW_CSS, INK, RULE, SOFT_WHITE, THREAD_HERO_CSS, HEX_CLASS, Block, Raw, _seed,
    make_hero, write,
)
from build_industries_page import SOLID_BUTTON_CSS, section_heading

PAGE_COLOUR = "#26272a"  # hero only: TFG grey at the shared hero darkness
PANEL_BG = "var(--wp--preset--color--palette-color-5, var(--theme-palette-color-5, #F0F2F3))"
STORES = "https://thefastenergroup.com/branches/"
PHOTO = ("https://thefastenergroup.com/wp-content/uploads/2025/12/"
         "pexels-tiger-lily-4483610-1-scaled-e1767131868289.webp")
FORM = '<!-- wp:fluentfom/guten-block {"formId":"4","themeStyle":"ffs_inherit_theme"} /-->'

CARD = {
    "backgroundColor": ["#ffffff"], "border": [f"1px solid {RULE}"],
    "paddingTop": ["2rem", None, None, "1.5rem"], "paddingBottom": ["2rem", None, None, "1.5rem"],
    "paddingLeft": ["2rem", None, None, "1.25rem"], "paddingRight": ["2rem", None, None, "1.25rem"],
}


def form_card():
    return Block(name="Enquiry Form", styles=CARD, children=[
        Block("p", text="Send us a message", styles={
            "marginTop": ["0px"], "marginBottom": ["0.44rem"], "fontWeight": ["700"],
            "textTransform": ["uppercase"], "color": [ACCENT],
        }),
        Block("h3", text="Our team is always here for support and assistance", styles={
            "marginTop": ["0px"], "marginBottom": ["1.5rem"], "maxWidth": ["28rem"], "color": [INK],
        }),
        # The Fluent Forms block, unchanged. Its fields follow the theme's form styles.
        Block(class_name="tfgr-form", name="Form", children=[Raw(FORM)]),
    ])


def photo_card():
    img = Block("img", json_extra={"src": PHOTO, "alt": ""},
                html_attrs=[("src", PHOTO), ("alt", ""), ("loading", "lazy")],
                styles={"display": ["block"], "width": ["100%"], "height": ["auto"],
                        "aspectRatio": ["4 / 3"], "objectFit": ["cover"], "objectPosition": ["50% 60%"]})
    return Block(name="Support You Can Trust", styles={
        "backgroundColor": ["#ffffff"], "border": [f"1px solid {RULE}"],
    }, children=[
        img,
        Block(name="Caption", styles={
            "paddingTop": ["1.25rem"], "paddingBottom": ["1.5rem"],
            "paddingLeft": ["1.5rem", None, None, "1.25rem"], "paddingRight": ["1.5rem", None, None, "1.25rem"],
            "borderTop": [f"3px solid {ACCENT}"],
        }, children=[
            Block("h3", text="Support you can trust", styles={
                "marginTop": ["0px"], "marginBottom": ["0.35rem"], "color": [INK],
            }),
            Block("p", text="Always available to provide reliable solutions whenever you need us.", styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "color": [BODY],
            }),
        ]),
    ])


# The dark card takes the honeycomb from the shared tfg-hex class.
CARD_THREADS = ""


def stores_card():
    return Block(name="Not a Form Person", class_name=HEX_CLASS, styles={
        "position": ["relative"], "overflow": ["hidden"], "backgroundColor": [INK],
        "paddingTop": ["1.75rem", None, None, "1.5rem"], "paddingBottom": ["1.75rem", None, None, "1.5rem"],
        "paddingLeft": ["1.75rem", None, None, "1.25rem"], "paddingRight": ["1.75rem", None, None, "1.25rem"],
    }, custom_css=CARD_THREADS, children=[
            Block("h3", text="Not a form person?", styles={
                "marginTop": ["0px"], "marginBottom": ["0.5rem"], "color": ["#ffffff"],
            }),
            Block("p", text="No problem. Call us or drop by one of our stores.", styles={
                "marginTop": ["0px"], "marginBottom": ["1.5rem"], "color": ["rgba(255, 255, 255, 0.85)"],
            }),
            Block("a", text="See our stores", href=STORES, custom_css=SOLID_BUTTON_CSS),
        ])


def panel():
    side = Block(name="Other Ways to Reach Us", styles={
        "display": ["flex"], "flexDirection": ["column"], "rowGap": ["1.5rem"],
    }, children=[stores_card(), photo_card()])
    return Block(name="Contact Us", class_name="tfgr-policy", anchor="contact", styles={
        "backgroundColor": [PANEL_BG],
        "paddingTop": ["2.25rem", None, None, "1.5rem"], "paddingBottom": ["2.25rem", None, None, "1.5rem"],
        "paddingLeft": ["1.5rem", None, None, "1rem"], "paddingRight": ["1.5rem", None, None, "1rem"],
    }, children=[
        section_heading("Get in touch", "Contact us today"),
        Block(name="Two Columns", styles={
            "display": ["grid"], "gridTemplateColumns": ["minmax(0, 3fr) minmax(0, 2fr)", "1fr"],
            "columnGap": ["2.25rem"], "rowGap": ["1.5rem"], "alignItems": ["start"],
        }, children=[form_card(), side]),
    ])


def body():
    _seed["slug"], _seed["n"] = "contact", 0
    return Block(name="Contact Page", class_name="tfgr-page", styles={
        # The panel is pulled up over the bottom of the hero.
        "marginTop": ["-4rem", None, None, "-3rem"], "position": ["relative"], "zIndex": ["2"],
        "marginBottom": ["4.5rem", None, None, "2.25rem"],
    }, custom_css="{CURRENT} [id]{scroll-margin-top:2rem;}", children=[panel()])


def hero():
    return make_hero(
        seed="contact-hero", bg=PAGE_COLOUR, caption="Contact us", title="Let’s Connect",
        intro=("Reliable support starts with a conversation. Contact our team to discuss products, "
               "availability, or solutions tailored to your operation."),
        buttons=[("Send a message", "#contact")],
        accent=ACCENT, pattern_css=THREAD_HERO_CSS, caption_color=SOFT_WHITE,
    )


PAGE = {"dir": "contact-page", "title": "Contact Us", "preview_css": GS_PREVIEW_CSS + """
body > .tfgr-page{max-width:1200px;margin-left:auto;margin-right:auto}
.tfgr-form{min-height:420px;background:repeating-linear-gradient(0deg,#f5f5f5 0 56px,#fff 56px 72px);outline:1px dashed #ccc}
"""}

if __name__ == "__main__":
    write(PAGE, body(), before=hero())
