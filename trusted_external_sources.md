# Trusted External Sources For Astro Certification

Last updated: 2026-05-27

This project uses a four-gate certification process. These sources are for Gate 2 and Gate 3 external checks. They are not training labels by themselves; they become training-safe only after values are entered into `astro_external_validation_template_20260527.csv` and pass the certification comparison.

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
   - URL: https://pypi.org/project/pyjhora/
   - Use for: secondary automated cross-checks and repeatable Python comparisons.
   - Limitation: not the final authority; use it as a second opinion against JHora/book examples.

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
D:\PycharmProjects\astro_external_validation_template_20260527.csv
```

3. For each row you can verify externally, fill:

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

## Do Not Train Rules

Do not train ML on:

- raw local LLM prose;
- Shadbala/Drik numbers promoted only by assumption;
- Panchanga rows where the source is sunrise-day based but the local value is event-time based, unless the distinction is explicitly encoded;
- Rahu/Ketu Shadbala strength unless a separate node-strength doctrine is deliberately created and validated.

## First Values To Collect

Start with these high-value checks:

1. `case_8_event_start`
   - Sun/Moon/Rahu Raman longitude
   - Tithi/Paksha/Nakshatra/Pada/Yoga/Karana

2. `case_43_event_start`
   - Sun/Moon/Rahu Raman longitude
   - JHora Shadbala and Drik outputs if available

3. `case_127_sr_touch_start`
   - Sun/Moon/Rahu Raman longitude
   - Panchanga limb values
   - confirm whether the 22:00 selected-window SR touch sits under the same astronomical context as the generated review pack

4. `gann_reference_tokyo`
   - Raman positions from an external ephemeris source
   - use this as a long-range historical sanity check
