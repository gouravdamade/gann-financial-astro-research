# Jagannatha Hora Sthana Subcomponent Witness Protocol

Contract: `GANN_JHORA_STHANA_SUBCOMPONENT_WITNESS_V1`

## Decision

The visible JHora 8.0 Sthana table has now been captured for all five locked
fixtures. It exposes Uchcha, Saptavargaja, Ojayugma, Kendradi, and Drekkana
beside the displayed total for every classical planet.

The completed `175/175` row packet validates and reconciles to the locked
top-level Sthana values. The named JHora-visible compatibility profile matches
all `35/35` planet-fixture totals. Production still uses the separately cited
BPHS-labeled source profile; compatibility agreement does not silently replace
that doctrine or authorize financial/ML/execution use.

## First-Party Evidence Boundary

- Official JHora source:
  `https://vedicastrologer.org/jh/index.htm`
- Official feature list:
  `https://vedicastrologer.org/jh/features.htm`
- The feature list confirms Shadabala calculations, multiple divisional-chart
  variants, and configurable relationship scopes.
- The public feature list does not publish numerical Sthana subcomponents.
- The pinned desktop application exposes the required table through:
  `Strengths` -> `Other strengths` -> right-click the Shadbala summary ->
  `Sthana Bala`.
- Each capture includes the visible table, accessibility text, fixture
  identity, and a normalized JSON transcription.

JHora is now accepted as an independent visible compatibility witness for this
locked matrix. It is not treated as the textual authority for selecting the
production doctrine profile.

## Required Capture Matrix

The template contains exactly `175` required values:

- five locked fixtures;
- seven classical planets;
- five Sthana subcomponents:
  Uchcha, Saptavargaja, Ojayugma, Kendradi, and Drekkana.

Every value must be copied from a visible JHora breakdown under the same locked
settings as `GANN_JHORA_SHADBALA_WITNESS_V1`.

## Acceptance Rules

1. Save an uncropped image that shows chart identity and all five named
   subcomponents.
2. Record the exact JHora value in virupa; do not infer it by subtracting other
   components or by copying PyJHora/local output.
3. Hash the image and bind every copied row to that image.
4. Record reviewer and timezone-aware UTC capture time.
5. Require all `175/175` unique rows.
6. For each fixture and planet, the five visible values must sum to the locked
   top-level JHora Sthana value within `0.5` virupa.
7. Keep source certification, financial validation, and execution false even
   after matrix completion; those remain separate gates.

## Commands

Create the pending template:

```powershell
python jhora_sthana_subcomponent_witness_protocol.py
```

Validate a completed visible ledger:

```powershell
python jhora_sthana_subcomponent_witness_protocol.py --validate <completed.csv>
```

Build the three-profile reconciliation:

```powershell
python jhora_sthana_subcomponent_comparator.py
```

## Current Result

Status: `visible_witness_reconciled_diagnostic_only`

- Witness ledger:
  `status/evidence/jhora_sthana_subcomponents_20260729/`
  `jhora_sthana_subcomponent_witness_completed_20260729.csv`.
- Witness validation: `175/175`, no issues.
- Source profile: Saptavargaja `3/35`; complete Sthana `1/35`.
- PyJHora profile: Saptavargaja and complete Sthana `34/35`.
- JHora-visible profile: every subcomponent and complete Sthana `35/35`.
- The sole PyJHora-profile miss is case-8 Saturn. Its longitude is outside
  Saturn's degree-bounded Aquarius Moolatrikona range, so visible JHora awards
  own-sign strength instead.
- Production change, source certification, financial validation, and execution
  permission remain false.
