# BC Fasteners: GreenShift pages

Built with the greenlight-vibe skill (`.claude/skills/greenlight-vibe`).

## Files

| File | What it is |
|------|------------|
| `bcf-homepage.html` | Homepage source (vanilla HTML/CSS/JS) |
| `bcf-homepage-blocks.txt` | Homepage block code, paste into the Gutenberg code editor |
| `src/product-page.src.html` | Product template source. `@@WC:...@@` marks where WooCommerce blocks go |
| `product-page.html` | Product template with the shared design-system CSS inlined (generated) |
| `product-page-blocks.txt` | Product template block code for the Gutenberg code editor |
| `product-page-blocks-cssrender.txt` | Same, with `CSSRender` on styled blocks, for when the template is rendered outside its own post |
| `build.py` | Regenerates everything above from the two sources |
| `preview-*.png` | Screenshots with sample data and placeholder images |

Rebuild after editing a source file:

```bash
python3 greenshift-homepage/build.py
```

## Design system

- **Hex nut**: brand motif. Product image backs, badges, bullets, rank numbers,
  swatches, icon frames, the "bolted plate" divider (`bcfh-nutrow`) and the faint
  honeycomb background (`bcfh-hexbg`). Buttons and price tags use angle-cut corners
  (`--bcfh-cham`).
- **Torn paper**: deals only. Hero edge (`bcfh-tear`), holiday price ticket
  (`bcfh-hang`), cross-sell coupon (`bcfh-coupon`), and the product page price when
  WooCommerce shows a sale (`.bcfh-pdprice:has(del)`).
- Fonts: Outfit (headings), Poppins (body). Colours live on `.bcfh-root`.

## Live product loops

New products, top sellers and "Popular right now" are GreenShift query loops:

- New: newest 14 published products.
- Top sellers: ordered by WooCommerce `total_sales`; podium shows #1, the list shows #2 to #7.
- Hidden and out-of-stock products are excluded (`product_visibility` taxonomy).
- Brand label uses `{{TERM_LINKS:product_brand}}` (WooCommerce Brands). If brands are an
  attribute instead, change it to `{{TERM_LINKS:pa_brand}}` in the source and rebuild.
- Price uses `{{META:_price}}`: current price, no "was" price, lowest price for variable products.

## Product template

Uses WooCommerce's own blocks for breadcrumbs, gallery, stock, price, add-to-cart form
(handles variations) and details tabs. The template needs a single-product context,
e.g. a Blocksy Pro Content Block set to "Custom Template" on single products.
