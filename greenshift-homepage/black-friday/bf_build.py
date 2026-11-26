#!/usr/bin/env python3
"""Build the Black Friday promo exports.

- bf-homepage-promo.html          -> bf-homepage-promo-blocks.txt
- src/bf-product-widget.src.html  -> three widget variants (both brands, Milwaukee only, Wera only),
                                     each as HTML and as block code with CSSRender for Blocksy content blocks.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from build import add_cssrender, convert, name_sections  # noqa: E402

FINE = {
    "both": "Offer valid online only. Milwaukee spend counts toward Milwaukee gifts and Wera spend toward Wera gifts. "
            "Limited quantities, first come, first served.",
    "mil": "Offer valid online only. Qualifying spend is on Milwaukee products only. "
           "Limited quantities, first come, first served.",
    "wera": "Offer valid online only. Qualifying spend is on Wera products only. "
            "Limited quantities, first come, first served.",
}


def widget_variant(src: str, keep: str) -> str:
    def brand(m):
        return m.group(2) if keep in ("both", m.group(1)) else ""
    html = re.sub(r"@@BRAND:(\w+)@@\n(.*?)@@END@@\n", brand, src, flags=re.S)
    html = html.replace("@@FINE@@", FINE[keep])
    assert "@@" not in html
    return html


def main():
    promo = convert(HERE / "bf-homepage-promo.html", HERE / "bf-homepage-promo-blocks.txt")
    (HERE / "bf-homepage-promo-blocks.txt").write_text(name_sections(promo, ["Black Friday swag promo"]))
    print("homepage promo")

    src = (HERE / "src/bf-product-widget.src.html").read_text()
    for keep, label in (("both", "both-brands"), ("mil", "milwaukee"), ("wera", "wera")):
        html_path = HERE / f"bf-product-widget-{label}.html"
        html_path.write_text(widget_variant(src, keep))
        blocks = convert(html_path, HERE / f"bf-product-widget-{label}-blocks.txt")
        (HERE / f"bf-product-widget-{label}-blocks.txt").write_text(add_cssrender(blocks))
        print("widget", label)


if __name__ == "__main__":
    main()
