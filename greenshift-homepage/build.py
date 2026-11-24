#!/usr/bin/env python3
"""Build the GreenShift block exports for the BC Fasteners pages.

1. Copies the shared design-system CSS rules from bcf-homepage.html into the
   product page source (src/product-page.src.html -> product-page.html).
2. Runs the greenlight-vibe converter on both pages.
3. Names top-level sections for the editor list view.
4. Replaces @@WC:block-name@@ slot markers with real WooCommerce blocks.
5. Writes a CSSRender variant of the product template for Blocksy content blocks.
"""
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONVERT = HERE.parent / ".claude/skills/greenlight-vibe/scripts/convert.js"

SHARED_CLASSES = {
    "wp-section", "wp-content-wrap", "bcfh-root", "bcfh-paperbg", "bcfh-inkbg", "bcfh-slatebg",
    "bcfh-kicker", "bcfh-kickervolt", "bcfh-h2", "bcfh-arrow", "bcfh-btn", "bcfh-textlink",
    "bcfh-hexbg", "bcfh-hexline", "bcfh-nutrow", "bcfh-nutrowbg", "bcfh-nutrownut",
    "bcfh-head", "bcfh-headlink", "bcfh-headlinkvolt", "bcfh-tag", "bcfh-tagred", "bcfh-srt",
    "bcfh-pgrid", "bcfh-pcard", "bcfh-pmedia", "bcfh-pnut", "bcfh-pimg", "bcfh-pbody",
    "bcfh-pbrand", "bcfh-pname", "bcfh-pnamelink", "bcfh-psku", "bcfh-pfoot", "bcfh-pprice",
    "bcfh-pcur", "bcfh-pgo",
}

SECTION_NAMES = {
    "bcf-homepage": ["Hero and promo mosaic", "Trust strip", "New products (live)", "Product spotlight",
                     "PIP helmet colour picker", "Top selling items (live)", "Top brands", "Help and newsletter"],
    "product-page": ["Product buy box", "Product details and help", "Popular right now (live)"],
}


def shared_css(home_html: str) -> str:
    css = re.search(r'<style data-wp-block-html="css">(.*?)</style>', home_html, re.S).group(1)
    top = css.split("@keyframes", 1)[0]
    keep = []
    for line in top.splitlines():
        m = re.match(r"\.([a-zA-Z0-9_-]+)", line.strip())
        if m and m.group(1) in SHARED_CLASSES:
            keep.append(line.strip())
    rise = re.search(r"@keyframes bcfh-rise\{.*?\}\}", css).group(0)
    keep.append(rise)
    return "\n".join(keep)


def convert(src: Path, out: Path) -> str:
    subprocess.run(["node", str(CONVERT), str(src), "-o", str(out)], check=True, capture_output=True)
    return out.read_text()


def encode(params: dict) -> str:
    return (json.dumps(params, separators=(",", ":"), ensure_ascii=False)
            .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))


def name_sections(blocks: str, names: list) -> str:
    it = iter(names)
    out = []
    for line in blocks.split("\n"):
        m = re.match(r"<!-- wp:greenshift-blocks/element (\{.*\}) -->$", line)
        if m and '"tag":"section"' in m.group(1):
            params = json.loads(m.group(1))
            params["metadata"] = {"name": next(it)}
            line = f"<!-- wp:greenshift-blocks/element {encode(params)} -->"
        out.append(line)
    return "\n".join(out)


def wc_slots(blocks: str) -> str:
    pattern = re.compile(
        r'<!-- wp:greenshift-blocks/element \{[^{}]*"@@WC:([a-z-]+)@@"[^{}]*\} -->\n'
        r"<span>@@WC:\1@@</span>\n<!-- /wp:greenshift-blocks/element -->")
    blocks, n = pattern.subn(lambda m: f"<!-- wp:woocommerce/{m.group(1)} /-->", blocks)
    assert "@@WC:" not in blocks, "unreplaced WooCommerce slot"
    print(f"  replaced {n} WooCommerce slots")
    return blocks


def add_cssrender(blocks: str) -> str:
    def fix(m):
        params = json.loads(m.group(2))
        if "styleAttributes" in params or "dynamicGClasses" in params:
            params["CSSRender"] = "1"
        return f"<!-- wp:greenshift-blocks/{m.group(1)} {encode(params)} -->"
    return re.sub(r"<!-- wp:greenshift-blocks/(element) (\{.*\}) -->", fix, blocks)


def main():
    home_src = HERE / "bcf-homepage.html"
    product_src = HERE / "src/product-page.src.html"
    product_html = HERE / "product-page.html"

    product_html.write_text(product_src.read_text().replace("/*@@SHARED@@*/", shared_css(home_src.read_text())))

    print("homepage")
    home = convert(home_src, HERE / "bcf-homepage-blocks.txt")
    (HERE / "bcf-homepage-blocks.txt").write_text(name_sections(home, SECTION_NAMES["bcf-homepage"]))

    print("product page")
    prod = convert(product_html, HERE / "product-page-blocks.txt")
    prod = wc_slots(name_sections(prod, SECTION_NAMES["product-page"]))
    (HERE / "product-page-blocks.txt").write_text(prod)
    (HERE / "product-page-blocks-cssrender.txt").write_text(add_cssrender(prod))
    print("done")


if __name__ == "__main__":
    main()
