# CGVO-S1A Varahamihira Source-Architecture Integration

Status: `IMPLEMENTED_FOR_CENTRAL_REVIEW`
Scope: read-only CGVO source architecture only.

## Implemented source contracts

| Contract | Status | Product role |
| --- | --- | --- |
| `VARAHAMIHIRA_RASI_NAKSHATRA_PARTITION_V1` | `CLOSED_ROOT_SOURCE` | fixed stellar rasi/nakshatra partition |
| `VARAHAMIHIRA_PRECESSIONAL_DISTINCTION_V1` | `CLOSED_ROOT_SOURCE` | distinguishes the stellar framework from observed solar turning points; no numeric constant |
| `VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_V1` | `SOURCE_RECONSTRUCTION_CANDIDATE` | explicit optional absolute-frame selector; never default |
| `VARAHAMIHIRA_LUNAR_MONTH_PROFILE_V1` | `HIGH_CONFIDENCE_SOURCE_INTERNAL_INFERENCE` | ordinary unambiguous purnimanta month only |
| `VARAHAMIHIRA_ECLIPSE_ASPECT_PROFILE_V1` | `CLOSED_SAME_AUTHOR_DELEGATED_SOURCE` | categorical sign-relative eclipse aspect records |
| `VARAHAMIHIRA_FIRMAMENT_GEOMETRY_V1` | `COMMENTARY_CONFLICT_NOT_SOURCE_CLOSED` | raw horizontal geometry only; no classical classifier |

## Required boundaries

- No implicit Raman, Lahiri, tropical, or other absolute frame is selected.
- Lunar intercalation, kshaya, double-month, and unresolved boundary cases return `UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED`.
- Aspect tokens have no numerical multiplier, mitigation coefficient, score, polarity, or market meaning.
- Firmament comparison candidates are visible as non-voting provenance only.
- The source adapters do not read price, outcomes, Fields, SBC, Auto Suggest, ML, MT5, orders, or execution state.

`executionAllowed=false` is invariant.
