"""Build the About Us page: hero, the history story with a milestones rail, the three
pillars, and the leadership team (group photo plus headshot profile cards).
"""
from build_policy_blocks import (
    ACCENT, BODY, GS_PREVIEW_CSS, INK, RULE, Block, _seed, make_hero, write,
)
from build_industries_page import section_heading

PAGE_COLOUR = "#040531"  # hero only, from the live page
PANEL_BG = "var(--wp--preset--color--palette-color-5, var(--theme-palette-color-5, #F0F2F3))"
TEAM_PHOTO = "https://thefastenergroup.com/wp-content/uploads/2026/02/LEADERSHIP-TEAM-WITH-DC-STAFF.webp"
# Headshots cropped from the senior leadership strip (files in about-page/headshots/),
# at the address WordPress gives them when uploaded in November 2026.
HEADSHOTS = "https://thefastenergroup.com/wp-content/uploads/2026/11/"
HAS_PHOTO = {"Lylle Kephart", "Ryan Chandler", "Brett Driver", "Ryan Deck", "Justin Servedio",
             "Sharon Kuystermans", "Mike Rorquist"}

# The site's own history copy. The first paragraph is set larger as the lead.
STORY = [
    "In 1979, four friends (Mel Soloway, Jerry Miller, Ron Hall, and Moe Gagnon) opened the first "
    "Calgary Fasteners &amp; Tools location.",
    "Over the years, the company grew, adding locations in Burnaby, Surrey, Kelowna, Vernon, "
    "Penticton, Kamloops, Edmonton, Red Deer, Lethbridge, Saskatoon, Winnipeg, and Brandon.",
    "In 2024, The Fastener Group partnered with TriWest Capital Partners to bring our separate "
    "companies together under one unified organization. The following year, we expanded further "
    "with the acquisitions of JD Industrial Supplies in Regina and Ono Work and Safety in British "
    "Columbia.",
    "As we continue to grow and integrate, we’re building a foundation that will make the next "
    "50 years even stronger than the last.",
]

# (label, text) for the milestones rail beside the story.
MILESTONES = [
    ("1979", "First Calgary Fasteners &amp; Tools location opens"),
    ("Growth", "12 more locations across BC, Alberta, Saskatchewan and Manitoba"),
    ("2024", "Partnership with TriWest Capital Partners unites the companies"),
    ("2025", "JD Industrial Supplies and Ono Work and Safety join the group"),
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
    ("John Sauer", "VP, Branch &amp; DC Operations"),
    ("Justin Servedio", "VP, Marketing &amp; Product Management"),
    ("Ryan Deck", "VP, Procurement"),
    ("Sharon Kuystermans", "Director, HR"),
    ("Mike Rorquist", "Director, IT"),
]

PAD = {
    "paddingTop": ["2.25rem", None, None, "1.5rem"], "paddingBottom": ["2.25rem", None, None, "1.5rem"],
    "paddingLeft": ["1.5rem", None, None, "1rem"], "paddingRight": ["1.5rem", None, None, "1rem"],
}

STORY_CSS = (
    f"{{CURRENT}} p{{margin:0 0 1.25rem 0;color:{BODY};}}"
    "{CURRENT} p:last-child{margin-bottom:0;}"
    f"{{CURRENT}} .tfgr-story-lead{{font-size:1.3em;line-height:1.45;color:{INK};}}"
    f"{{CURRENT}} .tfgr-story-close{{font-weight:700;color:{INK};}}"
)

# One continuous vertical line, a red square on it for each milestone.
RAIL_CSS = (
    "{CURRENT}{list-style:none;margin:0;padding:0;}"
    f"{{CURRENT}} li{{position:relative;margin:0;padding:0 0 1.5rem 1.75rem;border-left:2px solid {RULE};}}"
    "{CURRENT} li:last-child{padding-bottom:0;border-left-color:transparent;}"
    "{CURRENT} li::before{content:\"\";position:absolute;left:-7px;top:0.3rem;width:12px;height:12px;"
    f"background-color:{ACCENT};}}"
    f"{{CURRENT}} .tfgr-ms-label{{margin:0 0 0.15rem 0;font-weight:700;color:{INK};}}"
    f"{{CURRENT}} .tfgr-ms-text{{margin:0;color:{BODY};}}"
)

PILLAR_CSS = (
    f"{{CURRENT}} .tfgr-pillar{{background-color:#ffffff;border-right:1px solid {RULE};border-bottom:1px solid {RULE};"
    "padding:1.5rem;}"
    f"{{CURRENT}} .tfgr-pillar-num{{margin:0 0 1rem 0;font-weight:700;color:{ACCENT};}}"
    f"{{CURRENT}} .tfgr-pillar-name{{margin:0 0 0.5rem 0;color:{INK};}}"
    f"{{CURRENT}} .tfgr-pillar-text{{margin:0;color:{BODY};}}"
    "@media (max-width: 575.98px){{CURRENT} .tfgr-pillar{padding:1.25rem;}}"
)

# Profile cards. The portrait frame shows initials for now; an image placed inside the
# frame covers them, so headshots can be added later without changing the layout.
ROSTER_CSS = (
    f"{{CURRENT}} .tfgr-leader{{display:flex;flex-direction:column;background-color:#ffffff;"
    f"border-right:1px solid {RULE};border-bottom:1px solid {RULE};}}"
    "{CURRENT} .tfgr-leader-photo{position:relative;display:flex;align-items:center;justify-content:center;"
    f"aspect-ratio:4 / 5;overflow:hidden;background-color:{PANEL_BG};border-bottom:3px solid {ACCENT};}}"
    f"{{CURRENT}} .tfgr-leader-initials{{margin:0;font-size:clamp(2.25rem, 4vw, 3.25rem);font-weight:700;"
    f"line-height:1;letter-spacing:0.04em;color:{INK};opacity:0.8;}}"
    "{CURRENT} .tfgr-leader-photo img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}"
    "{CURRENT} .tfgr-leader-body{padding:1.25rem 1.5rem 1.5rem;}"
    f"{{CURRENT}} .tfgr-leader-name{{margin:0 0 0.35rem 0;font-size:1.15em;color:{INK};}}"
    f"{{CURRENT}} .tfgr-leader-title{{margin:0;color:{BODY};}}"
    "@media (max-width: 575.98px){{CURRENT} .tfgr-leader-body{padding:1rem;}"
    "{CURRENT} .tfgr-leader-name{font-size:1em;}}"
)


def ruled_grid(name, cols, css, children):
    return Block(name=name, styles={
        "display": ["grid"], "gridTemplateColumns": cols,
        "borderTop": [f"1px solid {RULE}"], "borderLeft": [f"1px solid {RULE}"],
    }, custom_css=css, children=children)


def history():
    last = len(STORY) - 1
    story = Block(name="Story", custom_css=STORY_CSS, children=[
        Block("p", text=t, text_is_html=True,
              class_name="tfgr-story-lead" if i == 0 else "tfgr-story-close" if i == last else None)
        for i, t in enumerate(STORY)
    ])
    rail = Block(name="Milestones", styles={
        "backgroundColor": ["#ffffff"], "border": [f"1px solid {RULE}"],
        "paddingTop": ["1.5rem"], "paddingBottom": ["1.5rem"],
        "paddingLeft": ["1.5rem", None, None, "1.25rem"], "paddingRight": ["1.5rem", None, None, "1.25rem"],
    }, children=[
        Block("p", text="Milestones", styles={
            "marginTop": ["0px"], "marginBottom": ["1.25rem"], "fontWeight": ["700"],
            "textTransform": ["uppercase"], "color": [ACCENT],
        }),
        Block("ol", custom_css=RAIL_CSS, children=[
            Block("li", children=[
                Block("p", text=label, class_name="tfgr-ms-label"),
                Block("p", text=text, class_name="tfgr-ms-text", text_is_html=True),
            ]) for label, text in MILESTONES
        ]),
    ])
    return Block(name="Our History", class_name="tfgr-policy", styles={"backgroundColor": [PANEL_BG], **PAD},
                 children=[
                     section_heading("Our history", "From one Calgary store to a Western Canadian network",
                                     anchor="history"),
                     Block(name="Two Columns", styles={
                         "display": ["grid"], "gridTemplateColumns": ["minmax(0, 3fr) minmax(0, 2fr)", "1fr"],
                         "columnGap": ["3rem"], "rowGap": ["2.25rem"], "alignItems": ["start"],
                     }, children=[story, rail]),
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


def initials(name):
    return "".join(part[0] for part in name.split()[:2]).upper()


def headshot(name):
    """The person's photo if we have one, otherwise their initials in the same frame."""
    if name not in HAS_PHOTO:
        return Block("p", text=initials(name), class_name="tfgr-leader-initials",
                     html_attrs=[("aria-hidden", "true")])
    src = HEADSHOTS + "leader-" + name.lower().replace(" ", "-") + ".webp"
    return Block("img", json_extra={"src": src, "alt": name, "originalWidth": 400, "originalHeight": 500},
                 html_attrs=[("src", src), ("alt", name), ("width", "400"), ("height", "500"),
                             ("loading", "lazy")])


def leader_card(name, title):
    return Block(class_name="tfgr-leader", name=name, children=[
        Block(class_name="tfgr-leader-photo", name="Photo", children=[headshot(name)]),
        Block(class_name="tfgr-leader-body", children=[
            Block("h3", text=name, class_name="tfgr-leader-name"),
            Block("p", text=title, class_name="tfgr-leader-title", text_is_html=True),
        ]),
    ])


def leadership():
    photo = Block("img", json_extra={
        "src": TEAM_PHOTO, "alt": "The TFG leadership team with distribution centre staff",
        "originalWidth": 1029, "originalHeight": 598,
    }, html_attrs=[
        ("src", TEAM_PHOTO), ("alt", "The TFG leadership team with distribution centre staff"),
        ("width", "1029"), ("height", "598"), ("loading", "lazy"),
    ], styles={"display": ["block"], "width": ["100%"], "height": ["auto"], "marginBottom": ["2.25rem"]})
    return Block(name="Leadership Team", children=[
        section_heading("Leadership", "Meet our leadership team", anchor="leadership"),
        photo,
        ruled_grid("Roster", ["repeat(4, 1fr)", "repeat(3, 1fr)", "repeat(2, 1fr)", "repeat(2, 1fr)"],
                   ROSTER_CSS, [leader_card(n, t) for n, t in LEADERS]),
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
