# Repeatation Review Pack UI: case_id=11

Group: `AVG(ALL)|MOON :: square`

Local full chart pack with click-to-place marker UI:

`D:\GannFinancialAstro\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548`

Open the index first:

`D:\GannFinancialAstro\doc\repeatation_review_case_11_avg_all_moon_square_ui_20260516_030548\repeatation_review_index.html`

Each chart page includes a fixed `Repeatation Marker UI` panel. Use the panel buttons to choose trade start, trade end, ignore start, or ignore end, then click the chart to place the marker. The page overlays marker lines/ignore regions and generates Python commands for saving trade annotations, ignore regions, and rule notes.

Tracked here:

- `repeatation_marker_template.csv`: 18 repeatations with full-window pips, chart paths, factor tags, and marker command templates.
- `repeatation_review_index.html`: copied index page. Chart links expect the local full chart pack unless regenerated into this folder.

Regenerate full pack:

```powershell
python .\build_repeatation_review_pack.py --case-id 11 --export-max-lines 60 --case-context-hours 72
```
