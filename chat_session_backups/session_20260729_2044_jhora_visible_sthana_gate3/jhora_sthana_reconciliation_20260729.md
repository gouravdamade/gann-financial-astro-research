# JHora Sthana Bala Reconciliation

Contract: `GANN_JHORA_STHANA_SUBCOMPONENT_COMPARATOR_V1`

Status: visible-witness diagnostic; production and execution remain locked.

The numeric tolerance is frozen at 0.5 virupa. No tolerance was widened
and no component was inferred from a top-level residual.

## Profile Results

| Profile | Component | Pass | Fail | MAE | Maximum error |
| --- | --- | ---: | ---: | ---: | ---: |
| source | uchcha | 35 | 0 | 0.002290 | 0.005991 |
| source | saptavargaja | 3 | 32 | 6.296000 | 12.620000 |
| source | ojayugma | 35 | 0 | 0.000000 | 0.000000 |
| source | kendradi | 35 | 0 | 0.000000 | 0.000000 |
| source | drekkana | 35 | 0 | 0.000000 | 0.000000 |
| source | total | 1 | 34 | 6.295684 | 12.618362 |
| pyjhora | uchcha | 35 | 0 | 0.002290 | 0.005991 |
| pyjhora | saptavargaja | 34 | 1 | 0.429000 | 15.000000 |
| pyjhora | ojayugma | 35 | 0 | 0.000000 | 0.000000 |
| pyjhora | kendradi | 35 | 0 | 0.000000 | 0.000000 |
| pyjhora | drekkana | 35 | 0 | 0.000000 | 0.000000 |
| pyjhora | total | 34 | 1 | 0.431054 | 14.998314 |
| jhora_visible | uchcha | 35 | 0 | 0.002290 | 0.005991 |
| jhora_visible | saptavargaja | 35 | 0 | 0.000429 | 0.005000 |
| jhora_visible | ojayugma | 35 | 0 | 0.000000 | 0.000000 |
| jhora_visible | kendradi | 35 | 0 | 0.000000 | 0.000000 |
| jhora_visible | drekkana | 35 | 0 | 0.000000 | 0.000000 |
| jhora_visible | total | 35 | 0 | 0.002579 | 0.007808 |

## Interpretation

- Uchcha, Ojayugma, Kendradi, and Drekkana each match visible JHora in all 35 locked rows.
- The BPHS-labeled source Saptavargaja weight profile remains a distinct doctrine and does not match the JHora table.
- The PyJHora profile fails one Saturn row because it treats all Aquarius as Moolatrikona instead of respecting Saturn's degree-bounded Moolatrikona range.
- The named JHora-visible profile combines JHora's observed weights with degree-bounded D1 Moolatrikona and matches the complete visible matrix. It remains diagnostic only.

The visible JHora profile is a compatibility witness, not a claim
that JHora's Saptavargaja weights supersede the separately cited
classical source profile. Source certification, financial validation,
and live execution remain separate fail-closed gates.
