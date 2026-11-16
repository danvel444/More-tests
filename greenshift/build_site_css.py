"""Write the one block of Customizer > Additional CSS the site needs.

It holds the honeycomb used by every hero and dark card (the "tfg-hex" class), plus the
footer. Change the pattern's strength or size here, in one place.
"""
from build_footer import FOOTER_CSS
from build_policy_blocks import HERE, HEX_TILE

HEX_CSS = f"""/* TFG honeycomb. Used by heroes and dark cards (class "tfg-hex") and the footer.
   Strength: --tfg-hex-opacity. Cell size: --tfg-hex-size (keep the 52 : 90 ratio,
   e.g. 39px 67.5px for smaller cells). */
:root {{
  --tfg-hex-image: url("{HEX_TILE}");
  --tfg-hex-size: 51.96px 90px;
  --tfg-hex-opacity: 0.09;
}}
.tfg-hex {{
  position: relative;
  isolation: isolate;
}}
.tfg-hex::before {{
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  background: var(--tfg-hex-image) 0 0 / var(--tfg-hex-size) repeat;
  opacity: var(--tfg-hex-opacity);
  -webkit-mask-image: linear-gradient(to left, #000 15%, transparent 70%);
  mask-image: linear-gradient(to left, #000 15%, transparent 70%);
}}
"""

if __name__ == "__main__":
    out = HERE / "site-css"
    out.mkdir(exist_ok=True)
    (out / "tfg-additional-css.css").write_text(HEX_CSS + "\n" + FOOTER_CSS)
    print("site-css/tfg-additional-css.css written")
