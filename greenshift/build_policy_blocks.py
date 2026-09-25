"""Build the branch policy tables (Returns, Special Orders) as GreenShift element blocks.

Output mirrors the block format used in the GreenLight theme's own patterns
(wpsoul/greenlight): every block has id + localId, table > tr > td nesting,
cell styling on the table block, and Gutenberg's JSON escaping.
"""
import hashlib
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
MEDIA = [None, "(max-width: 991.98px)", "(max-width: 767.98px)", "(max-width: 575.98px)"]

INK = "#1d1f21"
BODY = "#3a3d40"
ACCENT = "#a3231b"
RULE = "#d9d5cc"
PAPER = "#faf8f4"
NUM_BG = "#f1ede5"

VOID_TAGS = {"img"}

_seed = {"slug": "returns", "n": 0}


def new_id():
    _seed["n"] += 1
    return "gsbp-" + hashlib.md5(f"tfgr-{_seed['slug']}-{_seed['n']}".encode()).hexdigest()[:7]


def kebab(prop):
    return re.sub(r"[A-Z]", lambda m: "-" + m.group(0).lower(), prop)


def style_css(selector, style_attrs):
    """Render styleAttributes the way GreenShift writes inlineCssStyles."""
    per_bp = [[] for _ in MEDIA]
    for prop, values in style_attrs.items():
        if prop.endswith("_Extra"):
            continue
        for i, v in enumerate(values):
            if v is not None:
                per_bp[i].append(f"{kebab(prop)}:{v};")
    css = ""
    for i, decls in enumerate(per_bp):
        if not decls:
            continue
        rule = f"{selector}{{{''.join(decls)}}}"
        css += rule if MEDIA[i] is None else f"@media {MEDIA[i]}{{{rule}}}"
    return css


def table_css(selector, table_styles):
    t = table_styles["table"]
    css = f"{selector}{{border-collapse:{t['border']};table-layout:{t['layout']};}}"
    td = table_styles["td"]
    decls = "".join(
        f"{kebab(k)}:{v[0] if isinstance(v, list) else v};" for k, v in td.items()
    )
    return css + f"{selector} td{{{decls}}}"


class Block:
    def __init__(self, tag="div", text=None, children=None, class_name=None,
                 styles=None, custom_css=None, table_styles=None, name=None, anchor=None, href=None, json_extra=None, html_attrs=None):
        self.id = new_id()
        self.json_extra = json_extra or {}
        self.html_attrs = html_attrs or []
        self.anchor = anchor
        self.href = href
        self.tag = tag
        self.text = text
        self.children = children or []
        self.class_name = class_name
        self.styles = styles or {}
        self.custom_css = custom_css
        self.table_styles = table_styles
        self.name = name

    def css(self):
        sel = "." + self.id
        css = ""
        if self.table_styles:
            css += table_css(sel, self.table_styles)
        css += style_css(sel, self.styles)
        if self.custom_css:
            css += self.custom_css.replace("{CURRENT}", sel)
        return css

    def attrs(self):
        a = {"id": self.id}
        if self.anchor:
            a["anchor"] = self.anchor
        css = self.css()
        if css:
            a["inlineCssStyles"] = css
        if self.text is not None:
            a["textContent"] = self.text
        if self.tag != "div":
            a["tag"] = self.tag
        if self.text is None and self.tag not in VOID_TAGS:
            a["type"] = "inner"
        if self.class_name:
            a["className"] = self.class_name
        a["localId"] = self.id
        if self.href:
            a["href"] = self.href
        a.update(self.json_extra)
        if self.table_styles:
            a["tableStyles"] = self.table_styles
        if self.styles or self.custom_css:
            sa = dict(self.styles)
            if self.custom_css:
                sa["customCSS_Extra"] = self.custom_css
            a["styleAttributes"] = sa
        if self.name:
            a["metadata"] = {"name": self.name}
        return a

    def classes(self):
        cls = []
        if self.class_name:
            cls.append(self.class_name)
        if self.css():
            cls.append(self.id)
        return cls

    def serialize(self):
        cls = self.classes()
        open_tag = f"<{self.tag}" + (f' class="{" ".join(cls)}"' if cls else "")
        open_tag += (f' id="{self.anchor}"' if self.anchor else "")
        open_tag += (f' href="{self.href}"' if self.href else "")
        open_tag += "".join(f' {k}="{html.escape(v)}"' for k, v in self.html_attrs)
        if self.tag in VOID_TAGS:
            return (f"<!-- wp:greenshift-blocks/element {encode(self.attrs())} -->\n"
                    f"{open_tag}/>\n<!-- /wp:greenshift-blocks/element -->")
        open_tag += ">"
        if self.text is not None:
            inner = html.escape(self.text, quote=False)
        else:
            inner = "\n\n".join(c.serialize() for c in self.children)
        return (f"<!-- wp:greenshift-blocks/element {encode(self.attrs())} -->\n"
                f"{open_tag}{inner}</{self.tag}>\n"
                f"<!-- /wp:greenshift-blocks/element -->")


class Raw:
    """Existing block code dropped in unchanged (the site's own blocks)."""
    children = []

    def __init__(self, code):
        self.code = code.strip()

    def css(self):
        return ""

    def serialize(self):
        return self.code


def encode(obj):
    """Match Gutenberg's serializeAttributes escaping."""
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    s = s.replace("--", "\\u002d\\u002d").replace("<", "\\u003c")
    s = s.replace(">", "\\u003e").replace("&", "\\u0026").replace('\\"', "\\u0022")
    return s


# Everything about the cells lives on each table block, so one edit covers every row.
# Change vertical-align on td.tfgr-num to middle or bottom to move the numbers.
TABLE_CUSTOM_CSS = (
    "{CURRENT} td.tfgr-num{width:4.25rem;vertical-align:top;text-align:center;"
    f"padding-left:0;padding-right:0;background-color:{NUM_BG};color:{ACCENT};"
    "font-weight:700;font-variant-numeric:tabular-nums;}"
    "{CURRENT} td{vertical-align:top;}"
    "{CURRENT} td p{margin-top:0;margin-bottom:0;}"
    "{CURRENT} .tfgr-sub{list-style:none;margin:0.44rem 0 0 0;padding:0;}"
    "{CURRENT} .tfgr-sub li{position:relative;margin:0;padding:0.2rem 0 0.2rem 1.25rem;}"
    "{CURRENT} .tfgr-sub li::before{content:\"\";position:absolute;left:0;"
    f"top:calc(0.2rem + 0.5lh - 1px);width:0.6rem;height:2px;background-color:{ACCENT};}}"
    "@media (max-width: 575.98px){{CURRENT} td.tfgr-num{width:3rem;}}"
)

TABLE_STYLES = {
    "table": {"layout": "fixed", "border": "collapse"},
    "td": {
        "paddingTop": ["1rem"], "paddingBottom": ["1rem"],
        "paddingRight": ["1.5rem"], "paddingLeft": ["1.5rem"],
        "borderStyle": "solid", "borderWidth": "1px", "borderColor": RULE,
    },
}


def term_row(num, text, subs):
    cell = [Block("p", text=text)]
    if subs:
        cell.append(Block("ul", class_name="tfgr-sub",
                          children=[Block("li", text=s) for s in subs]))
    return Block("tr", name=f"Term {num}", children=[
        Block("td", class_name="tfgr-num", children=[Block("span", text=num)]),
        Block("td", children=cell),
    ])


def table(rows, name, extra_styles=None):
    styles = {"width": ["100%"], "marginTop": ["0px"], "marginBottom": ["0px"],
              "backgroundColor": ["#ffffff"], "color": [BODY]}
    styles.update(extra_styles or {})
    return Block("table", class_name="tfgr-table", name=name, styles=styles,
                 custom_css=TABLE_CUSTOM_CSS, table_styles=TABLE_STYLES,
                 children=[term_row(*t) for t in rows])



def columns(terms, split):
    first, second = terms[:split], terms[split:]
    return Block(name="Columns", styles={
        "display": ["grid"],
        "gridTemplateColumns": ["repeat(2, 1fr)", "repeat(1, 1fr)"],
        "columnGap": ["2.25rem"], "rowGap": ["2.25rem", "0px"],
        "alignItems": ["start"],
    }, children=[
        table(first, f"Terms {first[0][0]} to {first[-1][0]}"),
        table(second, f"Terms {second[0][0]} to {second[-1][0]}", {"marginTop": ["0px", "-1px"]}),
    ])


def make_root(policy):
    """The policy's panel: heading, optional definition, then its tables or custom body."""
    _seed["slug"], _seed["n"] = policy["seed"], 0
    heading = Block(name="Heading", styles={
        "paddingBottom": ["1.5rem"], "marginBottom": ["2.25rem"],
        "borderBottom": [f"2px solid {INK}"],
    }, children=[
        Block("p", text=policy["eyebrow"], styles={
            "marginTop": ["0px"], "marginBottom": ["0.44rem"], "fontWeight": ["700"],
            "textTransform": ["uppercase"], "color": [ACCENT],
        }),
        Block("h2", text=policy["title"], styles={
            "marginTop": ["0px"], "marginBottom": ["0px"], "color": [INK],
        }),
    ])
    parts = [heading]
    if policy.get("note"):
        label, text = policy["note"]
        parts.append(Block(name="Definition", styles={
            "backgroundColor": ["#ffffff"], "border": [f"1px solid {RULE}"],
            "paddingTop": ["1.25rem"], "paddingBottom": ["1.25rem"],
            "paddingLeft": ["1.5rem"], "paddingRight": ["1.5rem"],
            "marginBottom": ["2.25rem"],
        }, children=[
            Block("p", text=label, styles={
                "marginTop": ["0px"], "marginBottom": ["0.44rem"], "fontWeight": ["700"],
                "textTransform": ["uppercase"], "color": [ACCENT],
            }),
            Block("p", text=text, styles={
                "marginTop": ["0px"], "marginBottom": ["0px"], "color": [BODY],
            }),
        ]))
    if policy.get("body"):
        parts.extend(policy["body"]())
    else:
        parts.append(columns(policy["terms"], policy["split"]))
    root = Block(name=policy["name"], class_name="tfgr-policy", anchor=policy.get("anchor"), styles={
        "backgroundColor": [PAPER],
        "paddingTop": ["2.25rem", None, None, "1.5rem"],
        "paddingBottom": ["2.25rem", None, None, "1.5rem"],
        "paddingLeft": ["1.5rem", None, None, "1rem"],
        "paddingRight": ["1.5rem", None, None, "1rem"],
    }, children=parts)
    return root


def write(policy, root, before=""):
    """Write <dir>/<dir>-greenshift-blocks.txt and a browser preview built from the same code."""
    out_dir = HERE / policy["dir"]
    out_dir.mkdir(exist_ok=True)
    blocks = (before + "\n\n" if before else "") + root.serialize() + "\n"
    (out_dir / f"{policy['dir']}-greenshift-blocks.txt").write_text(blocks)

    # Browser preview built from the exact same markup and CSS the blocks carry.
    css = []
    def collect(b):
        if b.css():
            css.append(b.css())
        for c in b.children:
            collect(c)
    collect(root)
    markup = re.sub(r"<!-- /?wp:[^>]*-->\n?", "", blocks)
    (out_dir / f"{policy['dir']}-greenshift-preview.html").write_text(
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{policy['title']} Preview</title>\n<style>\n" + policy.get("preview_css", "") + "\n".join(css) + "\n</style>\n</head>\n"
        "<body style=\"margin:0;padding:40px;font-family:system-ui,sans-serif;line-height:1.6\">\n"
        + markup + "</body>\n</html>\n"
    )
    print(policy["dir"], "blocks:", blocks.count("<!-- wp:greenshift-blocks/element"))


def build(policy):
    write(policy, make_root(policy))


RETURNS = {
    "dir": "returns-policy", "seed": "returns", "name": "Returns Policy", "anchor": "returns",
    "eyebrow": "Branch return policy statement", "title": "Returns",
    "split": 7,
    "terms": [
    ("01", "Items purchased from The Fastener Group Ltd. (TFG) may be returned or exchanged within 30 days of the invoice date at any TFG location, unless they are final sale.", []),
    ("02", "A valid proof of purchase is required to qualify for a refund or exchange.", []),
    ("03", "Returned items must be unused, undamaged, in original packaging, and in saleable condition.", []),
    ("04", "All returns are subject to inspection and TFG approval. Returns after 30 days require approval from a Branch Manager or above.", []),
    ("05", "Credit Account Customers must obtain an RMA number and include it on the waybill to ship returns to a TFG branch. All Cash Sale returns must be done in person.", []),
    ("06", "Refunds will be issued to the original payment method after the return is received and approved. If the payment method was cash, the refund may be issued from A/R.", []),
    ("07", "Customers must report shortages, incorrect items, or other shipping discrepancies within three business days of delivery. Claims reported after this period may be subject to additional review and approval.", []),
    ("08", "If the return is not due to TFG error or a defective item, then:", [
        "A restocking fee of up to 25% may apply, as determined by the Branch Manager.",
        "The customer is responsible for return freight charges.",
    ]),
    ("09", "Final sale items cannot be returned or exchanged, including:", [
        "Special orders.",
        "Hygienic and emergency response items.",
        "Safety products with open packaging.",
        "Clearance items.",
        "Any other items designated by TFG as final sale.",
    ]),
    ("10", "Returns may be accepted when covered by a vendor’s customer satisfaction guarantee or policy, subject to the vendor’s applicable terms and conditions.", []),
    ("11", "Products are subject solely to the manufacturer’s warranty, if any, and warranty claims are not considered standard returns.", []),
]
}

SPECIAL_ORDERS = {
    "dir": "special-orders", "seed": "special-orders", "name": "Special Orders Policy", "anchor": "special-orders",
    "eyebrow": "Branch special order policy statement", "title": "Special Orders",
    "note": ("Definition", "A special order is any product ordered specifically for a customer that is not normally stocked by TFG, is sourced outside standard inventory replenishment, is custom-made, altered, configured, cut, packaged, or otherwise supplied to meet a customer-specific requirement, or is identified by a vendor as non-cancellable or non-returnable."),
    "split": 4,
    "terms": [
        ("01", "Only Credit Customers may place special orders; Cash Customers are not eligible.", []),
        ("02", "Special order items are final sale and cannot be returned, exchanged, or cancelled once confirmed, unless due to TFG error, vendor defect, or approved management exception.", []),
        ("03", "A deposit may be required if a customer exceeds their credit limit.", []),
        ("04", "Special orders must be bought in vendor-defined pack quantities.", []),
        ("05", "Lead times are estimates and may change due to vendor availability, freight delays, production schedules, or other factors outside TFG’s control.", []),
        ("06", "A Purchase Order is required and will signify customer acceptance of special order terms.", []),
        ("07", "Damaged, incorrect, or defective special orders must follow the applicable vendor claim, warranty, or return process.", []),
        ("08", "Exceptions must be approved by the Branch Manager or may be escalated to VP Operations or VP Sales.", []),
    ],
}

def terms_of_sale_body():
    """The site's own accordion row, unchanged except for the Expand all block's contents."""
    row = (HERE / "terms-of-sale" / "source-row.txt").read_text()
    new_html = (HERE / "terms-of-sale" / "expand-all.html").read_text().strip()
    start = row.index("<!-- wp:html -->\n") + len("<!-- wp:html -->\n")
    end = row.index("\n<!-- /wp:html -->")
    return [Raw(row[:start] + new_html + row[end:])]


# Stand-in for GreenShift's own accordion and row CSS, only used by the browser preview
# so the overrides can be checked against something similar.
GS_PREVIEW_CSS = """
.gspb_row__content{display:flex;flex-wrap:wrap;margin:0 -20px}
.gspb_row__col--12{width:100%;padding:0 20px;box-sizing:border-box}
.gspb_row__col--6{width:50%;padding:0 20px;box-sizing:border-box}
@media (max-width: 767.98px){.gspb_row__col--6{width:100%}}
#gspb_accordion-id-gsbp-3648954 .gs-accordion-item,#gspb_accordion-id-gsbp-af89e2f .gs-accordion-item{margin-bottom:12px;border:1px solid #e5e5e5;box-shadow:0 2px 0 #ddd}
.gs-accordion-item__title{display:flex;justify-content:space-between;align-items:center;cursor:pointer}
#gspb_accordion-id-gsbp-3648954 .gs-accordion-item__title,#gspb_accordion-id-gsbp-af89e2f .gs-accordion-item__title{padding:18px 20px;background:#f7f7f7}
.gsclose .gs-accordion-item__content{display:none}
.iconfortoggle{position:relative;width:14px;height:14px;flex-shrink:0}
.gs-iconbefore,.gs-iconafter{position:absolute;background:#111;left:0;top:6px;width:14px;height:2px}
.gs-iconafter{transform:rotate(90deg)}
.gsopen .gs-iconafter{transform:rotate(0)}
"""

TERMS_OF_SALE = {
    "dir": "terms-of-sale", "seed": "terms-of-sale", "name": "Terms of Sale",
    "anchor": "terms-of-sale",
    "eyebrow": "General Terms of Sale and Customer Account Conditions", "title": "Terms of Sale",
    "body": terms_of_sale_body,
    "preview_css": GS_PREVIEW_CSS,
}

# The three cards under the hero, redone as a numbered index that matches the tables.
INDEX = [
    ("01", "#returns", "Returns", "Branch Return Policy Statement"),
    ("02", "#special-orders", "Special Orders", "Branch Special Order Policy Statement"),
    ("03", "#terms-of-sale", "Terms of Sale", "General Terms of Sale and Customer Account Conditions"),
]

INDEX_CSS = (
    "{CURRENT} .tfgr-idx-card{display:flex;align-items:stretch;background-color:#ffffff;"
    f"color:{BODY};text-decoration:none;transition:background-color .2s;}}"
    f"{{CURRENT}} .tfgr-idx-card:hover{{background-color:{NUM_BG};}}"
    f"{{CURRENT}} .tfgr-idx-card:focus-visible{{outline:2px solid {ACCENT};outline-offset:-2px;}}"
    "{CURRENT} .tfgr-idx-num{flex:0 0 4.25rem;text-align:center;padding-top:1rem;"
    f"background-color:{NUM_BG};border-right:1px solid {RULE};color:{ACCENT};"
    "font-weight:700;font-variant-numeric:tabular-nums;}"
    "{CURRENT} .tfgr-idx-body{flex:1 1 auto;padding:1rem 1.5rem;}"
    f"{{CURRENT}} .tfgr-idx-title{{margin:0;font-weight:700;color:{INK};}}"
    "{CURRENT} .tfgr-idx-desc{margin:0.2rem 0 0 0;}"
    f"{{CURRENT}} .tfgr-idx-view{{margin:0.6rem 0 0 0;font-weight:700;color:{ACCENT};}}"
    "{CURRENT} .tfgr-idx-view::after{content:\" \\2192\";}"
    "{CURRENT} .tfgr-idx-card:hover .tfgr-idx-view{text-decoration:underline;}"
    "@media (max-width: 575.98px){{CURRENT} .tfgr-idx-num{flex-basis:3rem;}}"
)


def policy_index():
    _seed["slug"], _seed["n"] = "page-index", 0
    cards = [
        Block("a", class_name="tfgr-idx-card", href=href, name=title, children=[
            Block("span", text=num, class_name="tfgr-idx-num"),
            Block(class_name="tfgr-idx-body", children=[
                Block("p", text=title, class_name="tfgr-idx-title"),
                Block("p", text=desc, class_name="tfgr-idx-desc"),
                Block("p", text="View", class_name="tfgr-idx-view"),
            ]),
        ])
        for num, href, title, desc in INDEX
    ]
    # The 1px gaps over a rule-coloured background draw the lines between cards.
    return Block(name="Policy Index", styles={
        "display": ["grid"],
        "gridTemplateColumns": ["repeat(3, 1fr)", "repeat(1, 1fr)"],
        "columnGap": ["1px"], "rowGap": ["1px"],
        "backgroundColor": [RULE], "border": [f"1px solid {RULE}"],
    }, custom_css=INDEX_CSS, children=cards)


PAGE = {"dir": "policies-page", "title": "Policies and Terms", "preview_css": GS_PREVIEW_CSS + """
.gspb_row-id-gsbp-7eecdd8{background:#6d1216;color:#fff;padding:120px 40px 60px;margin-bottom:120px}
.gspb_row-id-gsbp-7eecdd8 .gspb_row__content{max-width:1200px;margin:0 auto;align-items:center}
.gspb_heading-id-gsbp-a22facd{font-size:70px;line-height:1.2em;margin:0}
body > .gsbp-wrap-preview{max-width:1200px;margin:0 auto}
"""}


def build_page():
    """The whole Policies and Terms page: hero, index, then the three policy panels."""
    hero = (HERE / "policies-page" / "source-hero.txt").read_text().strip()
    # The hero's mobile-landscape background was teal (#063532); every other size is dark red.
    hero = hero.replace('"color":["#6d1216","#6d1216","#063532","#6d1216"]',
                        '"color":["#6d1216","#6d1216","#6d1216","#6d1216"]')
    index = policy_index()
    panels = [make_root(RETURNS), make_root(SPECIAL_ORDERS), make_root(TERMS_OF_SALE)]
    _seed["slug"], _seed["n"] = "page-wrap", 0
    wrapper = Block(name="Policies", class_name="tfgr-page", styles={
        "display": ["flex"], "flexDirection": ["column"],
        "rowGap": ["3.38rem", "2.25rem"],
    }, custom_css="{CURRENT} [id]{scroll-margin-top:7rem;}", children=[index] + panels)
    write(PAGE, wrapper, before=hero)


if __name__ == "__main__":
    build(RETURNS)
    build(SPECIAL_ORDERS)
    build(TERMS_OF_SALE)
    build_page()
