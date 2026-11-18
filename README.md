# Streams Into Wealth — Six-page integration (18 November 2026)

This package consolidates the newest six-page website from the **Teaching Finance – P6** discussion. It is the Streams Into Wealth website, not the previous Stockcheck branding. The interactive five-point economic cycle checklist and eight-stage sector guide live under **Markets & Sectors**, not a separate Cycles page.

## Pages
- `index.html` — Home / search / green banner and river logo.
- `research.html` — company search and research.
- `opportunities.html` — SWOT / government-policy questions.
- `econ.html` — economic indicators and releases.
- `leaders.html` — political-leader information and search.
- `markets.html` — sector overview, five-number cycle checklist and eight-stage sector research tool.
- `data.js` — supporting company/reference data used by the six pages (included here; was missing in the source six-HTML ZIP).

## The five signals
Real GDP growth, unemployment, Core PCE inflation, ISM Manufacturing and Services, and the Fed policy rate. Enter earlier and latest observations. The signal summaries and estimate are generated in the browser; no API key is used. The model is educational and needs independent verification.

## INSTALL — important
1. DOWNLOAD the ZIP. RIGHT-CLICK and choose **Extract All** before uploading.
2. Open the extracted folder and upload **all seven website files** (six HTML + data.js) together to the GitHub repository **root**, where `index.html` lives. Keep the flat folder structure intact.
3. Commit; check Settings → Pages → main branch / root; reload with Ctrl + Shift + R once GitHub Pages finishes deploying.
4. On the website open Markets & Sectors → Find the Economic Stage. Press **Try a sample scenario**, verify results and moving marker, then replace example values with official economic readings.
5. The old `cycles.html` page, if still in GitHub, is not linked from the six-page navigation; do not merge old JavaScript files into this package.

## Source/accuracy
Official indicator links appear within the checklist; Fidelity's cycle-sector guide is linked for historical context. Market-sector tendencies are not forecasts or recommendations. Research with current economic releases before reaching conclusions. This package does not include live financial-price APIs or membership tools.
