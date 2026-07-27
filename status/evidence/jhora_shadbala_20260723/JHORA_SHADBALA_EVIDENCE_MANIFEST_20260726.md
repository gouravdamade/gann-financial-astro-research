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

The four event fixtures deliberately use `Asia/Kolkata` civil time with the
Tokyo reference latitude/longitude from the frozen project fixtures. The Gann
reference fixture uses `Asia/Tokyo`. Numeric coordinates and timezone are
authoritative. JHora's free-text place field may display a geocoder-like
`Tokyo, Massachusetts, USA` label; that label was not used to derive
coordinates or timezone.

## Primary Artifacts

| Artifact | SHA-256 |
| --- | --- |
| `jhora_shadbala_witness_completed_20260726.csv` | `3DFF36A1415881522F152F690C3856C3F736BEE60ED202F7F5EDD100C055DF42` |
| `jhora_pyjhora_component_comparison_20260726.csv` | `DDA6C65606D167041B6C7707FF1A6EF20663C56E2C076C1A46D233EBE9763776` |
| `jhora_pyjhora_component_comparison_20260726.json` | `8B690D2BBD753AC1ABBD9E59BC707B9D49FE82BD2403D1A6C778D385A2BF0F47` |
| `jhora_drik_independent_validation_values_20260726.csv` | `DECDB00B58E0B4C4D3E6A14295DCAFE72D72E2D91584B8F3050C587D6000F1BF` |
| `jhora_local_doctrine_reconciliation_20260726.csv` | `8D7A7509C900B5AED1EA988F783CD4E55932426C3632A71CBA3AA663A03C5B14` |
| `jhora_drik_candidate_residuals_20260726.csv` | `0476F39034E742069CD4D57032AB91704375915F863AC5012D219CC33C6D3541` |
| `jhora_doctrine_reconciliation_20260726.json` | `1C048D4BD2FA269604B4CEB10D0CE2F52F6681A3F4AE58B940D4FDC7E2257E4B` |
| `jhora_doctrine_reconciliation_20260726.md` | `36C5799957487C329E144D90DD3D2151846213E38B4E6CD9B1C0198A15BAD2A3` |
| `astro_external_validation_gate_20260726.json` | `1B6470F3756A4F078D33C14647992F4A5EC0F7C500261052CAC0C177F4B0B352` |
| `astro_function_certification_report_20260726.md` | `F8C77930401CEF82D1A8C1D628A6FE1105AF454A8315637F15D1995F7C304319` |

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
Corrected local full-total mean absolute error is `12.626` virupa versus
PyJHora's `71.742`, but the strict result remains `0/35` at the frozen
tolerance.

Top-level local Kaala passes `5/35` with `2.763` virupa mean absolute error.
Hora, Nathonnatha, Ayana, aggregate Kaala, non-luminary Chesta, and named Drik
sensitivity profiles remain non-production diagnostics. Full Shadbala and
Drik therefore remain uncertified and execution-locked. The visible Kaala
capture is tracked separately under
`status/evidence/jhora_kaala_witness_20260727`.

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
