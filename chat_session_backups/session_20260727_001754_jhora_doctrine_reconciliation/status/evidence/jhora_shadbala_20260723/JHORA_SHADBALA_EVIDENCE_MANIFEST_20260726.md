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
| `jhora_local_doctrine_reconciliation_20260726.csv` | `99E5D6C2BF026C9AF12248DFC0A986E4C99A0F8013857A3E8C57FC0043F3E156` |
| `jhora_drik_candidate_residuals_20260726.csv` | `819E20B5013D199A89520BF3541D92DAD83DB860F687D7162B782C89A5EA3D38` |
| `jhora_doctrine_reconciliation_20260726.json` | `561C6FC2243397B74BECE411A89B5176CC0577511B2D78B6465D2A1F7DDA8B85` |
| `jhora_doctrine_reconciliation_20260726.md` | `34B5036FE1A07D60A491CF82C438F389A0009324492BE8D4675C5F9B4AC04476` |
| `astro_external_validation_gate_20260726.json` | `29F00E959986C709816A790280D0C577A09B87B24FBDF897B96E81E36E17CDD4` |
| `astro_function_certification_report_20260726.md` | `EFA3072BDB64F22A710AEAADA122FEE7ADD63702A639E13C30D87EB19EC88589` |

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

The source-profile reconciliation applies one independently supported
correction: displayed Sun/Moon Chesta remains visible but contributes zero to
the total because Ayana/Paksha already owns it. Corrected local full-total mean
absolute error is `17.416` virupa versus PyJHora's `71.742`, but the strict
result remains `0/35` at the frozen tolerance.

Local Kaala is closer than PyJHora in `35/35` rows but passes only `4/35`.
Named Drik sensitivity profiles remain non-production diagnostics. Full
Shadbala and Drik therefore remain uncertified and execution-locked.

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
