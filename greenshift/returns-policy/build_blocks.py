"""Build the returns policy table as GreenShift element blocks.

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

_counter = [0]


def new_id():
    _counter[0] += 1
    return "gsbp-" + hashlib.md5(f"tfgr-returns-{_counter[0]}".encode()).hexdigest()[:7]


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
                 styles=None, custom_css=None, table_styles=None, name=None):
        self.id = new_id()
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
        css = self.css()
        if css:
            a["inlineCssStyles"] = css
        if self.text is not None:
            a["textContent"] = self.text
        if self.tag != "div":
            a["tag"] = self.tag
        if self.text is None:
            a["type"] = "inner"
        if self.class_name:
            a["className"] = self.class_name
        a["localId"] = self.id
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
        open_tag = f"<{self.tag}" + (f' class="{" ".join(cls)}"' if cls else "") + ">"
        if self.text is not None:
            inner = html.escape(self.text, quote=False)
        else:
            inner = "\n\n".join(c.serialize() for c in self.children)
        return (f"<!-- wp:greenshift-blocks/element {encode(self.attrs())} -->\n"
                f"{open_tag}{inner}</{self.tag}>\n"
                f"<!-- /wp:greenshift-blocks/element -->")


def encode(obj):
    """Match Gutenberg's serializeAttributes escaping."""
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    s = s.replace("--", "\\u002d\\u002d").replace("<", "\\u003c")
    s = s.replace(">", "\\u003e").replace("&", "\\u0026").replace('\\"', "\\u0022")
    return s


TERMS = [
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


root = Block(name="Returns Policy", class_name="tfgr-policy", styles={
    "backgroundColor": [PAPER],
    "paddingTop": ["2.25rem", None, None, "1.5rem"],
    "paddingBottom": ["2.25rem", None, None, "1.5rem"],
    "paddingLeft": ["1.5rem", None, None, "1rem"],
    "paddingRight": ["1.5rem", None, None, "1rem"],
}, children=[
    Block(name="Heading", styles={
        "paddingBottom": ["1.5rem"], "marginBottom": ["2.25rem"],
        "borderBottom": [f"2px solid {INK}"],
    }, children=[
        Block("p", text="Branch return policy statement", styles={
            "marginTop": ["0px"], "marginBottom": ["0.44rem"], "fontWeight": ["700"],
            "textTransform": ["uppercase"], "color": [ACCENT],
        }),
        Block("h2", text="Returns", styles={
            "marginTop": ["0px"], "marginBottom": ["0px"], "color": [INK],
        }),
    ]),
    Block(name="Columns", styles={
        "display": ["grid"],
        "gridTemplateColumns": ["repeat(2, 1fr)", "repeat(1, 1fr)"],
        "columnGap": ["2.25rem"], "rowGap": ["2.25rem", "0px"],
        "alignItems": ["start"],
    }, children=[
        table(TERMS[:7], "Terms 01 to 07"),
        table(TERMS[7:], "Terms 08 to 11", {"marginTop": ["0px", "-1px"]}),
    ]),
])

blocks = root.serialize() + "\n"
(HERE / "returns-policy-greenshift-blocks.txt").write_text(blocks)

# Browser preview built from the exact same markup and CSS the blocks carry.
css = []
def collect(b):
    if b.css():
        css.append(b.css())
    for c in b.children:
        collect(c)
collect(root)
markup = re.sub(r"<!-- /?wp:[^>]*-->\n?", "", blocks)
(HERE / "returns-policy-greenshift-preview.html").write_text(
    "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
    "<title>Returns Policy Preview</title>\n<style>\n" + "\n".join(css) + "\n</style>\n</head>\n"
    "<body style=\"margin:0;padding:40px;font-family:system-ui,sans-serif;line-height:1.6\">\n"
    + markup + "</body>\n</html>\n"
)
print("blocks:", blocks.count("<!-- wp:greenshift-blocks/element"))
