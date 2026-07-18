# Trusted External Sources For Astro Certification

Last updated: 2026-07-18

This project uses a four-gate certification process. These sources are for Gate 2 and Gate 3
external checks. They are not training labels by themselves. They become training-safe only after
values are entered into the current `astro_external_validation_template_YYYYMMDD.csv`, pass the
certification comparison, and belong to a supported astronomy contract.

The May 2026 USDJPY case records are quarantined as legacy double-sidereal research history.
Do not use their case IDs as certification samples. Start with a corrected versioned rebuild.

## Source Tiers

### Tier A - Astronomy / Ephemeris

Use these for planetary longitude, Raman ayanamsa, true node / Rahu, Ketu derivation, and timezone sanity.

1. Swiss Ephemeris documentation
   - URL: https://www.astro.com/swisseph/swisseph_acrobat.pdf
   - Use for: method-level validation, ayanamsa mode names, sidereal longitude formula, true/mean node flags.
   - Limitation: documentation confirms method and flags, but does not by itself give every sample value.

2. Raman ephemeris sample / Raman New Millennium Ephemeris
   - URL: https://astroamerica.com/ramannew.pdf
   - Use for: Raman ayanamsa sidereal planetary positions, especially date-level sanity checks.
   - Limitation: many ephemeris tables are daily/midnight values, so intraday values may need interpolation or software export.

### Tier B - Jyotish Software

Use these for Shadbala, Drik-style strength, divisional chart sanity, and Panchanga cross-checks.

1. Jagannatha Hora, official site
   - URL: https://vedicastrologer.org/jh/index.htm
   - Use for: primary Shadbala cross-check, Panchanga and classical Jyotish output comparison, chart export/screenshot references.
   - Settings required:
     - ayanamsa should be Raman when possible;
     - true node versus mean node must be recorded;
     - timezone and location must match the sample;
     - export/screenshot should be saved with the certification sample id.
   - Limitation: tradition/settings can change outputs. Record settings, not only values.

2. PyJHora
   - Official repository: https://github.com/naturalstupid/PyJHora
   - URL: https://pypi.org/project/pyjhora/
   - Use for: secondary automated cross-checks and repeatable Python comparisons.
   - Pinned local comparator: PyJHora `4.8.7`, wheel SHA-256
     `D8D8014573A38DDEFEDCAE57D3B8D84687CAC2AD31BB5B1DD70D945906A4D54D`.
   - Required settings: call `drik.set_ayanamsa_mode("RAMAN")`, preserve the
     fixture's civil-time UTC offset, and record that `strength.shad_bala(...)[6]`
     and the private `strength._drik_bala(...)` API supplied the compared
     classical-planet virupa values.
   - Limitation: not the final authority; use it as a second opinion against
     Jagannatha Hora and saved book examples. Package availability or a source
     claim is not certification. Only a saved numeric export admitted by the
     fail-closed gate counts.

### Tier C - Panchanga Sites

Use these for Tithi, Vara, Nakshatra, Yoga, Karana, and sometimes Rahu Kalam / Gulika / Yamaganda.

1. Drik Panchang
   - URL: https://www.drikpanchang.com/?lang=en
   - Use for: Panchanga limbs and date/time rollover checks.
   - Limitation: defaults may be Lahiri or local sunrise based. Record city, timezone, ayanamsa if shown, and whether the value is at exact event time or sunrise day.

2. Secondary Panchanga calculators
   - Examples: VedaMarg, Tithi.app, other Drik Ganita calculators.
   - Use for: disagreement detection, not final certification by themselves.
   - Limitation: settings are often hidden. Treat as weak evidence unless settings are explicit.

## Intake Workflow

1. Run the certification script:

```powershell
python astro_function_certification.py
```

2. Open:

```text
D:\PycharmProjects\astro_external_validation_template_20260718.csv
```

The runner now writes numeric rows for every classical planet instead of the old
`needs local row-specific event context` placeholder. Strength keys use:

```text
shadbala_implemented_total_virupa.SUN
drik_bala_virupa.SUN
...
shadbala_implemented_total_virupa.SATURN
drik_bala_virupa.SATURN
```

3. For each externally verified row, fill:

- `external_expected_value`
- `external_source`
- optionally add settings/details in `notes`

Do not edit `gate`, `sample_id`, `feature_key`, or `local_value`.

4. Rerun:

```powershell
python astro_function_certification.py
```

The script preserves your entered external values and updates `pass_fail`:

- `pass`: local value matches external value within tolerance.
- `fail`: local value does not match external value.
- `pending`: no external value entered yet.
- `pending_manual_context`: the row needs a row-specific event context before it can be compared.

It also writes:

```text
D:\PycharmProjects\astro_external_validation_gate_20260718.json
D:\PycharmProjects\jhora_drik_independent_validation_template_20260718.csv
```

That machine gate is fail-closed. It passes only when all 70 declared strength
rows (five fixtures x seven classical planets x Shadbala/Drik) have sourced,
numeric, in-tolerance external values. Duplicate keys, unknown keys, missing
source labels, non-numeric strength values, failures, and pending rows all block
certification. Drik has an additional 35-row independent-source witness gate:
PyJHora values must not be copied into that file. A passed research gate still
leaves execution disabled.

As of the Drik V2 reconciliation on 2026-07-18, 25 astronomy/Panchanga rows and
all 35 PyJHora Drik rows pass. The largest Drik residual is `0.01` virupa.
All 35 implemented Shadbala-total rows still fail, so Gate 3 remains
`failed_external_validation`. The admitted PyJHora 4.8.7 export is
`pyjhora_external_strength_values_20260718.csv` (SHA-256
`29A88901CEE0821F3F20C75777D2BDDACDB9524EB253939D9263E693CBDEE9C9`).

Drik V2 now records all six contributions, divides the signed net by four,
classifies Moon from waxing/waning phase, classifies Mercury from same-sign
associations, and applies the active Mars/Jupiter/Saturn special-aspect ranges.
The old raw pre-normalization net remains available as an audit value. PyJHora
is still only a secondary comparator: the generated independent template has
35 pending rows and must be completed from Jagannatha Hora or a cited saved
worked classical example before Drik can be called independently certified.

To admit that second source, copy the generated independent template to a
separate evidence CSV, fill only `external_expected_value`, `external_source`,
and evidence details in `notes`, then run:

```powershell
python astro_function_certification.py `
  --external-values pyjhora_external_strength_values_20260718.csv `
  --independent-drik-values <saved-independent-drik-values.csv>
```

## Current Tolerances

- Sidereal longitude rows: `<= 0.02 deg`
- Shadbala / Drik / Virupa rows: `<= 0.5 virupa`
- Categorical Panchanga rows: exact case-insensitive text match

If a source gives rounded values, record the rounding in `notes`. Do not loosen tolerances silently; create a new documented tolerance rule instead.

## Certification Promotion Rules

Promote a feature to `externally_validated` only when:

1. At least one Tier A or Tier B trusted source agrees within tolerance.
2. The source settings match the project settings or the difference is explicitly documented.
3. The value is reproducible from a saved export, screenshot, PDF, or script output.
4. The same feature value can be traced through:
   - touch-log CSV,
   - reviewer drawer,
   - ML notes / deterministic evidence,
   - local RAG evidence.
5. `astro_external_validation_gate_YYYYMMDD.json` reports
   `passed_external_validation`.

For the current USDJPY fixtures, use Tokyo latitude/longitude
(`35.6762`, `139.6503`) with the event timestamp shown in the CSV. Record Raman
ayanamsa, true node, Porphyry houses, exact timezone, location, software version,
and a durable export/screenshot path. Do not compare a planet-total row against
an `AVG(ALL)` or pair-average value.

## Do Not Train Rules

Do not train ML on:

- raw local LLM prose;
- Shadbala/Drik numbers promoted only by assumption;
- Panchanga rows where the source is sunrise-day based but the local value is event-time based, unless the distinction is explicitly encoded;
- Rahu/Ketu Shadbala strength unless a separate node-strength doctrine is deliberately created and validated.

## First Values To Collect

Start with these high-value checks:

1. `raman_node_regression_2025_05_28`
   - Sun/Moon/Rahu Raman longitude
   - confirm true-node calculation is sidereal exactly once.

2. `corrected_tn_smoke_2025_03_07`
   - Sun/Moon/Rahu Raman longitude
   - Tithi/Paksha/Nakshatra/Pada/Yoga/Karana.

3. `reference_chart_tokyo_1889`
   - Raman positions from an external ephemeris source
   - use this as a long-range historical sanity check.

4. A rebuilt event fixture with explicit transit/natal roles
   - JHora Shadbala and Drik outputs if available;
   - exported role, orb, house system, node type, timezone, and ephemeris backend.
