"""Build the "Top brands" section of the bold Black Friday page with steady logo sizes.

The logo files come in different shapes: wide transparent ones (660 x 225), wide JPGs
(648 x 350) and square JPGs with white space built in (648 x 648, 1084 x 1084). Sizing by
width made every shape look a different size. Here each logo is fitted inside the same
box in every tile (object-fit: contain). Square files fill the box's width instead
(object-fit: cover), which trims the white space above and below their logo.
"""
from build_policy_blocks import Block, _seed, write
from build_bf_bold_page import banner, css, frame, section

BCF = "https://bcfasteners.com/"
UP = BCF + "wp-content/uploads/"
CAT = BCF + "product-category/brand-names/"

# (name, category slug, logo file, width, height): the brands and files on the live page.
LOGOS = [
    ("Milwaukee", "milwaukee", "https://thefastenergroup.com/wp-content/uploads/2026/08/Milwaukee-Red-Logo.webp", 660, 225),
    ("Wera", "wera", UP + "2022/06/WERA-LOGO.jpg", 648, 648),
    ("DeWalt", "dewalt", "https://thefastenergroup.com/wp-content/uploads/2026/08/DeWalt-Logo.webp", 660, 225),
    ("Knipex", "knipex", UP + "2025/03/Knipex-Logo.jpg", 648, 350),
    ("Klein Tools", "klein", UP + "2025/03/Klein-Logo.jpg", 648, 350),
    ("Megapro", "mega-pro", UP + "2022/06/MEGAPRO-LOGO.jpg", 648, 648),
    ("Gearwrench", "gearwrench", UP + "2025/03/Gearwrench-Logo-2.jpg", 648, 350),
    ("Irwin", "irwin", UP + "2024/06/27.png", 648, 648),
    ("Jet", "jet-tools", UP + "2025/03/Jet-Logo.jpg", 648, 350),
    ("Unilite", "unilite", UP + "2025/04/UNILITE-LOGO.jpg", 1084, 1084),
    ("Diablo", "diablo", UP + "2025/03/Diablo-Logo-1.jpg", 648, 350),
    ("Microjig", "microjig", UP + "2025/05/MICROJIG-2.jpg", 648, 648),
]

LOGO_GRID_CSS = (
    "{CURRENT}{display:grid;grid-template-columns:repeat(6, minmax(0, 1fr));gap:6px;}"
    "@media (max-width: 991.98px){{CURRENT}{grid-template-columns:repeat(4, minmax(0, 1fr));}}"
    "@media (max-width: 575.98px){{CURRENT}{grid-template-columns:repeat(3, minmax(0, 1fr));}}"
    # Every tile is the same 3:2 white box; the logo always fills the same inner area.
    "{CURRENT} .tfgr-logo{position:relative;display:block;overflow:hidden;aspect-ratio:3 / 2;"
    "background-color:#ffffff;border-bottom:4px solid #ffffff;transition:border-color .2s;}"
    "{CURRENT} .tfgr-logo img{position:absolute;top:50%;left:50%;width:78%;height:64%;max-width:none;"
    "transform:translate(-50%, -50%);object-fit:contain;}"
    # Square files carry white space above and below the logo; let them fill the box's width
    # (cover trims only that white space) so the logo matches the rest.
    "{CURRENT} .tfgr-logo img.tfgr-logo-square{object-fit:cover;}"
    "{CURRENT} a.tfgr-logo:hover,{CURRENT} a.tfgr-logo:focus-visible{border-bottom-color:RED;}"
    "{CURRENT} a.tfgr-logo:focus-visible{outline:2px solid RED;outline-offset:-2px;}"
)


def brands_section():
    _seed["slug"], _seed["n"] = "bf-bold-brands-v2", 0
    tiles = []
    for name, slug, src, w, h in LOGOS:
        square = w == h
        tiles.append(Block("a", class_name="tfgr-logo", name=name, href=f"{CAT}{slug}/", children=[
            Block("img", class_name="tfgr-logo-square" if square else None,
                  json_extra={"src": src, "alt": name, "originalWidth": w, "originalHeight": h},
                  html_attrs=[("src", src), ("alt", name), ("width", str(w)), ("height", str(h)),
                              ("loading", "lazy")]),
        ]))
    return section("Top Brands", "brands", [
        banner("Top brands", "Shop by brand", "#000000", "border-bottom:4px solid RED;"),
        frame([Block(name="Logos", custom_css=css(LOGO_GRID_CSS), children=tiles)]),
    ])


PAGE = {"dir": "black-friday-bold", "title": "Top Brands", "preview_css": ""}

if __name__ == "__main__":
    import shutil
    from build_policy_blocks import HERE
    out = HERE / "black-friday-bold"
    # write() names files after the folder; keep the full page's files and save this one separately.
    keep = {p: p.read_bytes() for p in out.glob("black-friday-bold-greenshift-*")}
    write(PAGE, brands_section())
    shutil.move(out / "black-friday-bold-greenshift-blocks.txt", out / "top-brands-section-greenshift-blocks.txt")
    shutil.move(out / "black-friday-bold-greenshift-preview.html", out / "top-brands-section-preview.html")
    for p, data in keep.items():
        p.write_bytes(data)
