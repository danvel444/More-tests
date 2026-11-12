"""Build the About Us page: hero, a history timeline, the three pillars, and the
leadership team (group photo plus a name and title roster, since there are no headshots).
"""
from build_policy_blocks import (
    ACCENT, BODY, GS_PREVIEW_CSS, INK, RULE, Block, _seed, make_hero, write,
)
from build_industries_page import section_heading

PAGE_COLOUR = "#040531"  # hero only, from the live page
PANEL_BG = "var(--wp--preset--color--palette-color-5, var(--theme-palette-color-5, #F0F2F3))"
TEAM_PHOTO = "https://thefastenergroup.com/wp-content/uploads/2026/02/LEADERSHIP-TEAM-WITH-DC-STAFF.webp"

# (label, text). Text may hold &amp; and is written as HTML.
TIMELINE = [
    ("1979", "Four friends, Mel Soloway, Jerry Miller, Ron Hall and Moe Gagnon, open the "
             "first Calgary Fasteners &amp; Tools location."),
    ("Growth", "Locations follow in Burnaby, Surrey, Kelowna, Vernon, Penticton, Kamloops, "
               "Edmonton, Red Deer, Lethbridge, Saskatoon, Winnipeg and Brandon."),
    ("2024", "The Fastener Group partners with TriWest Capital Partners, bringing our separate "
             "companies together as one organization."),
    ("2025", "We welcome JD Industrial Supplies in Regina and Ono Work and Safety in British Columbia."),
]

PILLARS = [
    ("Great people", "Customers buy from people, not just companies. Our staff are carefully "
                     "selected for their knowledge, friendliness and professionalism at every branch."),
    ("Great partners", "We work with the manufacturers our customers trust, so the tools, fasteners "
                       "and equipment on our shelves are ones we can stand behind."),
    ("Exceptional customer service", "We serve industrial, construction, manufacturing and maintenance "
                                     "customers across Canada with dependable supply for every job."),
]

# (name, title) in the order the live page lists them.
LEADERS = [
    ("Lylle Kephart", "President and CEO"),
    ("Ryan Chandler", "CFO"),
    ("Brett Driver", "VP, Sales"),
    ("Mike Hamilton", "VP, Branch &amp; DC Operations"),
    ("Justin Servedio", "VP, Marketing &amp; Product Management"),
    ("Ryan Deck", "VP, Procurement"),
    ("Sharon Kuystermans", "Director, HR"),
    ("Mike Rorquist", "Director, IT"),
]

PAD = {
    "paddingTop": ["2.25rem", None, None, "1.5rem"], "paddingBottom": ["2.25rem", None, None, "1.5rem"],
    "paddingLeft": ["1.5rem", None, None, "1rem"], "paddingRight": ["1.5rem", None, None, "1rem"],
}

# A horizontal line with a red marker per step on desktop; a vertical line on phones.
TIMELINE_CSS = (
    "{CURRENT}{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4, 1fr);column-gap:2rem;}"
    f"{{CURRENT}} li{{position:relative;margin:0;padding:1.75rem 0 0 0;border-top:2px solid {INK};}}"
    "{CURRENT} li::before{content:\"\";position:absolute;top:-7px;left:0;width:12px;height:12px;"
    f"background-color:{ACCENT};}}"
    f"{{CURRENT}} .tfgr-tl-label{{margin:0 0 0.5rem 0;font-weight:700;font-size:1.5em;line-height:1.2;color:{INK};}}"
    f"{{CURRENT}} .tfgr-tl-text{{margin:0;color:{BODY};}}"
    "@media (max-width: 991.98px){{CURRENT}{grid-template-columns:repeat(2, 1fr);row-gap:2.25rem;}}"
    "@media (max-width: 575.98px){{CURRENT}{grid-template-columns:1fr;row-gap:0;}"
    f"{{CURRENT}} li{{border-top:0;border-left:2px solid {INK};padding:0 0 1.75rem 1.5rem;}}"
    "{CURRENT} li:last-child{padding-bottom:0;}"
    "{CURRENT} li::before{top:0.35rem;left:-7px;}}"
)

PILLAR_CSS = (
    f"{{CURRENT}} .tfgr-pillar{{background-color:#ffffff;border-right:1px solid {RULE};border-bottom:1px solid {RULE};"
    "padding:1.5rem;}"
    f"{{CURRENT}} .tfgr-pillar-num{{margin:0 0 1rem 0;font-weight:700;color:{ACCENT};}}"
    f"{{CURRENT}} .tfgr-pillar-name{{margin:0 0 0.5rem 0;color:{INK};}}"
    f"{{CURRENT}} .tfgr-pillar-text{{margin:0;color:{BODY};}}"
    "@media (max-width: 575.98px){{CURRENT} .tfgr-pillar{padding:1.25rem;}}"
)

ROSTER_CSS = (
    f"{{CURRENT}} .tfgr-leader{{display:flex;flex-direction:column;background-color:#ffffff;"
    f"border-right:1px solid {RULE};border-bottom:1px solid {RULE};padding:1.5rem;}}"
    f"{{CURRENT}} .tfgr-leader-name{{margin:0 0 0.35rem 0;padding-top:1rem;border-top:3px solid {ACCENT};"
    f"font-size:1.15em;color:{INK};}}"
    f"{{CURRENT}} .tfgr-leader-title{{margin:0;color:{BODY};}}"
    "@media (max-width: 575.98px){{CURRENT} .tfgr-leader{padding:1rem;}{CURRENT} .tfgr-leader-name{font-size:1em;}}"
)


def ruled_grid(name, cols, css, children):
    return Block(name=name, styles={
        "display": ["grid"], "gridTemplateColumns": cols,
        "borderTop": [f"1px solid {RULE}"], "borderLeft": [f"1px solid {RULE}"],
    }, custom_css=css, children=children)


def history():
    timeline = Block("ol", name="Timeline", custom_css=TIMELINE_CSS, children=[
        Block("li", children=[
            Block("p", text=label, class_name="tfgr-tl-label"),
            Block("p", text=text, class_name="tfgr-tl-text", text_is_html=True),
        ]) for label, text in TIMELINE
    ])
    return Block(name="Our History", class_name="tfgr-policy", styles={"backgroundColor": [PANEL_BG], **PAD},
                 children=[
                     section_heading("Our history", "From one Calgary store to a Western Canadian network",
                                     anchor="history"),
                     timeline,
                     Block("p", text=("As we continue to grow and integrate, we’re building a foundation "
                                      "that will make the next 50 years even stronger than the last."), styles={
                         "marginTop": ["2.25rem"], "marginBottom": ["0px"], "maxWidth": ["44rem"],
                         "fontWeight": ["700"], "color": [INK],
                     }),
                 ])


def pillars():
    cards = [Block(class_name="tfgr-pillar", name=n, children=[
        Block("p", text=f"0{i}", class_name="tfgr-pillar-num"),
        Block("h3", text=n, class_name="tfgr-pillar-name"),
        Block("p", text=t, class_name="tfgr-pillar-text"),
    ]) for i, (n, t) in enumerate(PILLARS, 1)]
    return Block(name="Three Pillars", children=[
        section_heading("What we stand for", "Built on three pillars"),
        ruled_grid("Pillars", ["repeat(3, 1fr)", None, "repeat(1, 1fr)"], PILLAR_CSS, cards),
    ])


def leadership():
    photo = Block("img", json_extra={
        "src": TEAM_PHOTO, "alt": "The TFG leadership team with distribution centre staff",
        "originalWidth": 1029, "originalHeight": 598,
    }, html_attrs=[
        ("src", TEAM_PHOTO), ("alt", "The TFG leadership team with distribution centre staff"),
        ("width", "1029"), ("height", "598"), ("loading", "lazy"),
    ], styles={"display": ["block"], "width": ["100%"], "height": ["auto"], "marginBottom": ["2.25rem"]})
    cards = [Block(class_name="tfgr-leader", name=n.replace("&amp;", "&"), children=[
        Block("h3", text=n, class_name="tfgr-leader-name"),
        Block("p", text=t, class_name="tfgr-leader-title", text_is_html=True),
    ]) for n, t in LEADERS]
    return Block(name="Leadership Team", children=[
        section_heading("Leadership", "Meet our leadership team", anchor="leadership"),
        photo,
        ruled_grid("Roster", ["repeat(4, 1fr)", "repeat(3, 1fr)", "repeat(2, 1fr)", "repeat(2, 1fr)"],
                   ROSTER_CSS, cards),
    ])


def body():
    _seed["slug"], _seed["n"] = "about", 0
    return Block(name="About Page", class_name="tfgr-page", styles={
        "display": ["flex"], "flexDirection": ["column"], "rowGap": ["4.5rem", "3.38rem", None, "2.25rem"],
        # The history panel is pulled up over the bottom of the hero.
        "marginTop": ["-4rem", None, None, "-3rem"], "position": ["relative"], "zIndex": ["2"],
        "marginBottom": ["4.5rem", None, None, "2.25rem"],
    }, custom_css="{CURRENT} [id]{scroll-margin-top:2rem;}",
        children=[history(), pillars(), leadership()])


def hero():
    return make_hero(
        seed="about-hero", bg=PAGE_COLOUR, caption="Since 1979", title="About Us",
        intro="A look at our history, our growth, and what continues to drive us forward.",
        buttons=[("Our history", "#history"), ("Leadership team", "#leadership")],
        accent=ACCENT,
    )


PAGE = {"dir": "about-page", "title": "About Us", "preview_css": GS_PREVIEW_CSS + """
body > .tfgr-page{max-width:1200px;margin-left:auto;margin-right:auto}
"""}

if __name__ == "__main__":
    write(PAGE, body(), before=hero())
