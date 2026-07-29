# Jagannatha Hora Sthana Subcomponent Witness Protocol

Contract: `GANN_JHORA_STHANA_SUBCOMPONENT_WITNESS_V1`

## Decision

Production Sthana Bala remains blocked. The locked JHora 8.0 evidence exposes
only the top-level Sthana value for each planet. It does not expose enough
visible evidence to decide whether the residual comes from Uchcha,
Saptavargaja, Ojayugma, Kendradi, or Drekkana.

The existing PyJHora-compatible Sthana profile is a Tier-B diagnostic. Its
stronger agreement must not replace the BPHS-labeled production source profile.
No formula or tolerance may change from an inferred component split.

## First-Party Evidence Boundary

- Official JHora source:
  `https://vedicastrologer.org/jh/index.htm`
- Official feature list:
  `https://vedicastrologer.org/jh/features.htm`
- The feature list confirms Shadabala calculations, multiple divisional-chart
  variants, and configurable relationship scopes.
- The public feature list does not publish numerical Sthana subcomponents.
- The pinned local help index contains a `Planetary strengths` topic, but the
  completed locked screenshots and clipboard tables contain only the top-level
  Sthana column.

Therefore JHora is accepted as an independent top-level witness, not as a
subcomponent witness, until a visible detailed table is captured.

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

## Current Result

Status: `blocked_pending_visible_sthana_subcomponent_witness`

The legacy JHora window did not expose a reliable capture/accessibility surface
in the current Codex desktop session. No values were copied, inferred, or
reverse-engineered. The production Sthana implementation remains unchanged and
fail-closed.
