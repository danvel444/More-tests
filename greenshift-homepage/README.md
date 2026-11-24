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

## Live product loops and rankings

New products, Most popular and "Popular right now" are GreenShift query loops that sort
by scores from `wp/bcf-product-rankings.php`. **Install that plugin first**: copy it to
`wp-content/mu-plugins/`, then open WooCommerce > Product rankings and click
"Recalculate now". Until it has run, the loops are empty.

- **Most popular** (`_bcf_popular_score`): number of separate orders containing the product
  in the last 90 days. An order of 1,000 screws counts once, the same as an order of one drill.
  Variations count toward their parent product. Refunds are ignored.
- **New products** (`_bcf_new_score`): products published in the last 120 days (and always
  the 40 newest), scored as
  `(1 + orders since launch) x log10(price + 10) x 0.5^(age / 30 days) x 3 if Featured`.
  A new power tool outranks a new driver bit out of the gate, but a bit that lots of
  separate orders pick up still climbs. Star a product as Featured to push a launch.
- Tag a product `exclude-from-rankings` to keep it out of both lists.
- Scores refresh twice a day (WP-Cron), from the admin page, or with `wp bcf rankings`.
- Settings (windows, half-life, Featured boost, brand attribute) are constants at the top of the plugin.
- Data comes from WooCommerce Analytics tables. If Analytics hasn't imported historical
  orders yet, run WooCommerce > Settings > Advanced > Analytics > Import historical data.
- Hidden and out-of-stock products are excluded by the loop queries.
- **Brand**: the plugin copies each product's `pa_brand` attribute to `_bcf_brand` and links
  it to the product category with the same name (`_bcf_brand_url`), falling back to a store
  search. Change `BRAND_ATTRIBUTE` if your attribute slug differs.
- Price uses `{{META:_price}}`: current price, no "was" price, lowest price for variable products.

Test the scoring math with `php greenshift-homepage/wp/test-rankings.php`.

## Product template

Uses WooCommerce's own blocks for breadcrumbs, gallery, stock, price, add-to-cart form
(handles variations) and details tabs. The template needs a single-product context,
e.g. a Blocksy Pro Content Block set to "Custom Template" on single products.
