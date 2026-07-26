# Drik Bala V2 Reconciliation

Date: 2026-07-18

## 2026-07-26 Independent Witness Addendum

The locked Jagannatha Hora 8.0 witness is now complete. At the frozen
`0.5`-virupa tolerance the production V2 profile passes only `9/35` Drik rows
and fails `26/35`, so its status is:

`tier_b_pyjhora_aligned_failed_independent_jhora_reconciliation_in_progress`

The named sensitivity matrix in `jhora_doctrine_reconciliation_20260726.md`
shows that removing the current range-special bonus and applying a bright-half
Moon classification improves descriptive agreement. Its best tested profile
passes `20/35` with `2.372` virupa mean absolute residual, but it assumes
malefic Mercury globally and still leaves large residuals. These profiles are
diagnostic leads only; production Drik was not silently replaced.

## Scope

This milestone reconciles the project's directed planetary Drik Bala calculation
with the pinned PyJHora 4.8.7 Tier B comparator. It does not certify full
Shadbala and does not unlock execution.

Rule IDs:

- `PARASHARA_DRIK_BALA_RECONCILIATION_V2`
- `DRIK_NET_DIVIDE_BY_FOUR_V1`
- `PVR_TITHI_SIGN_ASSOCIATION_NATURE_V1`
- `PYJHORA_4_8_7_ACTIVE_SPECIAL_ASPECT_RANGES_V1`

Status:

`tier_b_pyjhora_aligned_failed_independent_jhora_reconciliation_in_progress`

## What Changed

1. The directed angle still runs from the aspecting planet to the target planet.
2. The six-piece base aspect curve is evaluated from 30 through 300 degrees.
3. Jupiter, Mars, and Saturn special strength is applied across the active
   PyJHora 4.8.7 angle ranges instead of only at one exact degree.
4. Waxing Moon is benefic and waning Moon is malefic.
5. Mercury is benefic when alone or associated with more benefics, malefic when
   associated with more malefics, and uses the nearest same-sign planet as the
   tie breaker.
6. Benefic and malefic contributions are summed separately, the signed raw net
   is retained, and the published Drik value is the signed net divided by four.
7. Every target has six persisted contribution records with angle, nature,
   nature reason, base strength, special bonus, gross strength, raw signed
   strength, and normalized signed strength.

The compatibility-facing fields
`event_*_strict_drik_bala_virupa`,
`event_*_strict_drik_benefic_virupa`, and
`event_*_strict_drik_malefic_virupa` now contain normalized V2 values. New raw
fields retain the pre-normalization net and split. The full contribution and
nature ledgers are stored as JSON.

## Comparator Result

Pinned comparator:

- PyJHora `4.8.7`
- Raman ayanamsa
- exact fixture civil time, UTC offset, and Tokyo coordinates
- wheel SHA-256:
  `D8D8014573A38DDEFEDCAE57D3B8D84687CAC2AD31BB5B1DD70D945906A4D54D`
- saved total matrix SHA-256:
  `29A88901CEE0821F3F20C75777D2BDDACDB9524EB253939D9263E693CBDEE9C9`
- saved contribution matrix SHA-256:
  `6FDB30D6CF082B017436093F7F81CFB8BAB303A6B7426A4B4414BF47DCA2D342`

| Measure | V1 | V2 |
| --- | ---: | ---: |
| Drik rows within 0.5 virupa | 0 / 35 | 35 / 35 |
| Mean absolute Drik residual | 17.4336 | 0.0011 |
| Maximum absolute Drik residual | 49.4942 | 0.0100 |
| Directed contribution rows checked | 0 | 210 |
| Contribution nature mismatches | n/a | 0 |
| Maximum directed-angle residual | n/a | 0.02 deg |
| Maximum gross/raw contribution residual | n/a | 0.02 virupa |
| Maximum normalized-contribution residual | n/a | 0.005 virupa |

The 210-row comparison is enforced by tests; it is not a visual spot check.

## Gate Result

The regenerated Gate 3 result is deliberately:

`failed_external_validation`

Counts:

- astronomy/Panchanga: 25 pass
- Drik Bala: 35 pass
- implemented Shadbala totals: 35 fail
- total: 60 pass, 35 fail, 0 pending

The implemented Shadbala-total residuals still have mean absolute error about
94.996 virupa and maximum absolute error about 296.482 virupa. Those differences
must be decomposed by Sthana, Dig, Kaala, Chesta, Yuddha, and other components;
the Drik fix must not be used to imply full Shadbala agreement.

## Independent Witness

PyJHora is a secondary comparator, not the final authority. The certification
runner emits:

`jhora_drik_independent_validation_template_YYYYMMDD.csv`

It contains 35 required rows. The completed locked JHora matrix passes `9/35`
and fails `26/35`. The API gate correctly refuses certification.

Jagannatha Hora explicitly offers a choice between Raman and Parasara
special-aspect quantification. The locked witness records Parasara special
aspects and every required setting. No independent values were invented or
copied from PyJHora.

## Source Notes

- Local source extract `SHADBALA_JAYA` describes the six-piece aspect-energy
  curve and benefic/malefic signed net. Its OCR has an internal 120-degree
  inconsistency (`30` in prose and `20` in one table), so that text alone is not
  enough to certify the range implementation.
- PyJHora documents association-aware benefic/malefic classification and also
  warns that its Shadbala totals can differ from Jagannatha Hora.
- Official Jagannatha Hora release notes state that special-aspect
  quantification is selectable by doctrine. This is why V2 is labeled by its
  exact comparator policy instead of being called universally canonical.

Primary online references:

- https://github.com/naturalstupid/PyJHora
- https://www.vedicastrologer.org/jh/
- https://www.vedicastrologer.org/jh/update_7.6.htm

## Safety Decision

- Keep Drik V2 available as a transparent provisional research feature.
- Do not relabel full Shadbala as certified.
- Do not migrate legacy case outcomes silently; corrected case data needs a
  versioned rebuild.
- Do not unlock order execution from this result.
