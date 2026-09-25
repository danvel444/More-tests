// Draws the Locations page overview map as a self-contained inline SVG (no map service,
// no API key). Province outlines come from Natural Earth via Plotly's sane-topojson.
//
// One-time setup:  npm i sane-topojson topojson-client d3-geo
// Run:             node build_locations_map.js   (writes locations-page/map.svg)
const fs = require("fs");
const path = require("path");
const topo = require("sane-topojson/dist/north-america_50m.json");
const { feature } = require("topojson-client");
const { geoConicConformal, geoPath } = require("d3-geo");

const HERE = __dirname;
const data = JSON.parse(fs.readFileSync(path.join(HERE, "locations-page", "stores.json"), "utf8"));

const W = 1100, H = 640, PAD = 24;
const OURS = ["BC", "AB", "SK", "MB"];
const PROVINCE_NAMES = { BC: "British Columbia", AB: "Alberta", SK: "Saskatchewan", MB: "Manitoba" };

const all = feature(topo, topo.objects.subunits).features;
const ours = all.filter((f) => f.properties.gu === "CAN" && OURS.includes(f.id));
const context = all.filter((f) => !(f.properties.gu === "CAN" && OURS.includes(f.id)));

const projection = geoConicConformal().parallels([49, 58]).rotate([112, 0])
  .fitExtent([[PAD, PAD], [W - PAD, H - PAD]], { type: "FeatureCollection", features: ours })
  .clipExtent([[0, 0], [W, H]]);  // neighbours are cut at the frame, which keeps the file small
const draw = geoPath(projection).digits(1);
const visible = (f) => { const d = draw(f); return d && d.length > 0; };

// Hand-tuned label offsets (dx, dy, anchor) where cities sit close together.
const LABEL = {
  Courtenay: [-12, -4, "end"], Nanaimo: [-12, 12, "end"], Burnaby: [12, -10, "start"],
  Surrey: [12, 16, "start"], Kamloops: [-12, -2, "end"], Vernon: [12, -2, "start"],
  Kelowna: [12, 6, "start"], Penticton: [12, 14, "start"],
};

const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-");
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");

// One pin per city, placed at the mean of its stores.
const cities = new Map();
for (const p of data.provinces) for (const s of p.stores) {
  const c = cities.get(s.city) || { city: s.city, stores: [] };
  c.stores.push(s);
  cities.set(s.city, c);
}

let pins = "";
for (const c of cities.values()) {
  const lon = c.stores.reduce((a, s) => a + s.lon, 0) / c.stores.length;
  const lat = c.stores.reduce((a, s) => a + s.lat, 0) / c.stores.length;
  const [x, y] = projection([lon, lat]).map((v) => Math.round(v * 10) / 10);
  const n = c.stores.length;
  const [dx, dy, anchor] = LABEL[c.city] || [12, 5, "start"];
  const label = n > 1 ? `${c.city} (${n})` : c.city;
  pins += `<a class="tfgr-map-pin" href="#store-${slug(c.city)}">` +
    `<title>${esc(c.city)}: ${n} store${n > 1 ? "s" : ""}</title>` +
    `<circle cx="${x}" cy="${y}" r="${n > 1 ? 8 : 6}"/>` +
    `<text x="${x + dx}" y="${y + dy}" text-anchor="${anchor}">${esc(label)}</text></a>`;
}

let provinceLabels = "";
for (const f of ours) {
  const [x, y] = projection(f.properties.ct);
  provinceLabels += `<text x="${Math.round(x)}" y="${Math.round(y)}">${PROVINCE_NAMES[f.id]}</text>`;
}

const svg =
  `<svg class="tfgr-map" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" ` +
  `aria-label="Map of our 20 stores across British Columbia, Alberta, Saskatchewan and Manitoba">` +
  `<style>` +
  `.tfgr-map{display:block;width:100%;height:auto;background:#ffffff;}` +
  `.tfgr-map-context path{fill:#f7f5f0;stroke:#ffffff;stroke-width:1;}` +
  `.tfgr-map-prov path{fill:#f1ede5;stroke:#cfc8bb;stroke-width:1.2;stroke-linejoin:round;}` +
  `.tfgr-map-prov-labels text{fill:#8f877b;font-size:13px;font-weight:700;letter-spacing:0.12em;` +
  `text-transform:uppercase;text-anchor:middle;}` +
  `.tfgr-map-pin circle{fill:var(--wp--preset--color--palette-color-1, var(--theme-palette-color-1, #b11f24));stroke:#ffffff;stroke-width:2;transition:r .15s;}` +
  `.tfgr-map-pin text{fill:#1d1f21;font-size:14px;font-weight:700;paint-order:stroke;` +
  `stroke:#ffffff;stroke-width:4px;stroke-linejoin:round;}` +
  `.tfgr-map-pin:hover circle,.tfgr-map-pin:focus circle{fill:#1d1f21;}` +
  `.tfgr-map-pin:hover text,.tfgr-map-pin:focus text{text-decoration:underline;}` +
  `.tfgr-map-pin:focus{outline:none;}.tfgr-map-pin:focus-visible circle{stroke:#1d1f21;stroke-width:3;}` +
  // On narrow screens the city labels would be unreadably small; the cards below list them.
  `@media (max-width: 767.98px){.tfgr-map-pin text{display:none;}.tfgr-map-prov-labels text{font-size:22px;}` +
  `.tfgr-map-pin circle{r:12px;stroke-width:3;}}` +
  `</style>` +
  `<g class="tfgr-map-context">${context.filter(visible).map((f) => `<path d="${draw(f)}"/>`).join("")}</g>` +
  `<g class="tfgr-map-prov">${ours.map((f) => `<path d="${draw(f)}"/>`).join("")}</g>` +
  `<g class="tfgr-map-prov-labels">${provinceLabels}</g>` +
  `<g class="tfgr-map-pins">${pins}</g>` +
  `</svg>`;

fs.writeFileSync(path.join(HERE, "locations-page", "map.svg"), svg + "\n");
console.log("map.svg", (svg.length / 1024).toFixed(1), "KB,", cities.size, "pins");
