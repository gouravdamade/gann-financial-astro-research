# Jagannatha Hora Shadbala Evidence Manifest

Contract: `GANN_JHORA_SHADBALA_WITNESS_V1`

Capture completed: 2026-07-26

## Pinned Witness

- Jagannatha Hora version: `8.0.0.0`
- executable SHA-256:
  `3DDBE5FB0458AD1F0AD91B002C7EFB8BBA9F08891D3F46190ABA97D570B17908`
- locked settings hash:
  `4CB3CDFDA7FC9A23C7CCD22332611D04047C2B4427EB7F1F03437F301E6539DB`
- reviewer: OpenAI Codex local GUI capture
- tolerance policy: frozen at 0.5 virupa; no widening

## Locked Settings Evidence

The following screenshots are the valid lock evidence:

- `jhora_locked_setting_siddhanta_drik.jpg`
- `jhora_locked_setting_ayanamsa_raman.jpg`
- `jhora_locked_setting_planet_options_apparent_true_nodes.jpg`
- `jhora_locked_setting_divisional_parasara_hora_drekkana.jpg`
- `jhora_locked_setting_sunrise_apparent_tip.jpg`
- `jhora_locked_setting_hora_weekday_sunrise.jpg`
- `jhora_locked_setting_house_sripathi_ascendant_middle.jpg`
- `jhora_locked_setting_parasara_special_aspects.jpg`
- `jhora_locked_setting_relationships_compound.jpg`
- `jhora_locked_setting_relationships_relevant_varga.jpg`

The lock means Drik Siddhanta, Raman ayanamsa, geocentric apparent positions,
true node, Sripathi/Porphyry houses, ascendant in the middle of the first
house, apparent rise of the solar tip, weekday at sunrise, Parasara special
aspects, compound relationships from the relevant divisional chart, and
default Parasara Hora/Drekkana.

## Fixture Evidence

Each fixture has:

- `<sample_id>_birthdata_locked_full.jpg`
- `<sample_id>_birthdata_locked_dialog.jpg`
- `<sample_id>_shadbala_breakup_locked.jpg`
- `<sample_id>_shadbala_breakup_locked.txt`
- `<sample_id>_shadbala_summary_locked.jpg`
- `<sample_id>_shadbala_summary_locked.txt`

Captured sample IDs:

- `case_8_event_start`
- `case_43_event_start`
- `case_103_event_start`
- `case_127_sr_touch_start`
- `gann_reference_tokyo`

JHora fixture time is packed `HH.MMSS`, not decimal hours. On 2026-07-29 the
case-8, case-43, and case-103 fixtures and all six associated summary/breakup
views were recaptured at exact civil times `19:30`, `02:30`, and `22:30`.
Prior `:50` files are retained only with an explicit
`superseded_time50_20260729` name and are excluded from the completed witness.

The four event fixtures deliberately use `Asia/Kolkata` civil time with the
Tokyo reference latitude/longitude from the frozen project fixtures. The Gann
reference fixture uses `Asia/Tokyo`. Numeric coordinates and timezone are
authoritative. JHora's free-text place field may display a geocoder-like
`Tokyo, Massachusetts, USA` label; that label was not used to derive
coordinates or timezone.

## Primary Artifacts

| Artifact | SHA-256 |
| --- | --- |
| `jhora_shadbala_witness_completed_20260726.csv` | `A0D5B7E3A0BDDDA54B7C47B80CEAA1DC2ADC16E3B33E632505A0554DC70FA02D` |
| `jhora_pyjhora_component_comparison_20260726.csv` | `FFF21FE38497138772435E77C0B77E19777DE619468ABA6FA90D384CC6DAC0F7` |
| `jhora_pyjhora_component_comparison_20260726.json` | `EDA7034C77113AFDBAAC69470612D55FD3D631B41ADDFF66274BFF7115A49541` |
| `jhora_drik_independent_validation_values_20260726.csv` | `50BC0BF7109266A2C8D201B5CA035018F08AE130A985A5B90B46CA7BB57775FE` |
| `jhora_local_doctrine_reconciliation_20260726.csv` | `6E5F8ACB7321291A440447D5D776B052BDAA4C9CDF8DB79A11D3F7CD1FB5259D` |
| `jhora_drik_candidate_residuals_20260726.csv` | `8ABBBB6BABF1EB0C5A8A22EEA8569FE69CA247ABECA5E937948EA02BEFDA9AA6` |
| `jhora_doctrine_reconciliation_20260726.json` | `B3A911C0F9290CDC2F1E6AFC7CDD579D910F7FA838EABD28DD97072AD61E5A9C` |
| `jhora_doctrine_reconciliation_20260726.md` | `60FFD9C9319525E215D0712FB38E09FA754F822217D5C771A0CE25CE69D67678` |
| `astro_external_validation_gate_20260729.json` | `3A06D316EEAEA5DB0557FC3D52E4A032DC3385B15D8CD2B07ADFDC8F07D4FBB6` |
| `astro_function_certification_report_20260729.md` | `1614DA33AFF8710B7C7477BE6480D6EF16E14F9DC6176EA276C3833F9BF58515` |

The ledger links every numeric row to the appropriate locked summary or breakup
screenshot and stores that screenshot's SHA-256. The raw text files preserve
the copied JHora tables independently of parsing.

## JHora Total Nuance

JHora displays Chesta values for the Sun and Moon in its breakup table, while
its reported total excludes those two displayed values. The witness retains
the display exactly. `jhora_witness_capture_assembler.py` excludes only
Sun/Moon Chesta from its internal total consistency check. The maximum rounded
component residual is 0.01 virupa and the maximum rounded Rupa conversion
residual is 0.29 virupa.

## Independent Result

The completed matrix validates at 245 of 245 rows. Against the pinned PyJHora
profile at 0.5 virupa:

- all measures: 108 pass, 137 fail;
- Drik: 9 pass, 26 fail;
- full total: 0 pass, 35 fail.

This is a completed independent witness and a failed certification comparison.
It is not permission to widen tolerance or authorize execution.

## Doctrine Reconciliation Result

The source-profile reconciliation applies two independently supported
corrections: displayed Sun/Moon Chesta remains visible but contributes zero to
the total because Ayana/Paksha already owns it, and dynamic Paksha is promoted
after passing all `35/35` visible rows in the separate 350-row Kaala witness.
Exact-time Hora is also independently witness-aligned at `35/35`, including a
hashed case-8 LMT sunrise/lord/award packet. Corrected local full-total mean
absolute error is `11.829` virupa versus
PyJHora's `71.742`, but the strict result remains `0/35` at the frozen
tolerance.

Top-level local Kaala passes `5/35` with `2.763` virupa mean absolute error.
Nathonnatha, Ayana, aggregate Kaala, non-luminary Chesta, and named Drik
sensitivity profiles remain non-production diagnostics. Hora's narrow
component alignment does not certify aggregate Kaala. Full Shadbala and Drik
therefore remain uncertified and execution-locked. The visible Kaala capture
is tracked under `status/evidence/jhora_kaala_witness_20260727`; completed
Hora/Ayana packets are under
`status/evidence/jhora_kaala_intermediate_20260729`.

## Legacy And Pre-Lock Evidence

These files are retained only as an audit trail and must not be used as locked
witness evidence:

- `case_8_event_start_shadbala_summary.jpg`
- `case_8_event_start_shadbala_breakdown.jpg`
- `jhora_locked_setting_house_cusps_ascendant_middle.jpg`
- every file prefixed `jhora_prelock_mismatch_`

The ambiguous house-cusp screenshot predates discovery of the equal-house
mismatch. The valid replacement is
`jhora_locked_setting_house_sripathi_ascendant_middle.jpg`.
