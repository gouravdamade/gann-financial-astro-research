# Chart-Conditioned Aspect Polarity: Milestone 1

Date: 2026-07-22
Status: experimental, isolated, execution locked

## Scope

This milestone implements the non-fitting foundation described in the revised
chart-conditioned stock-aspect specification. The goal is to answer a narrower
question than the legacy global aspect labels: how the same transit-to-natal
aspect changes structural meaning when the accepted organization chart changes.

It does not claim predictive validity and cannot place trades.

## Specification Custody

The two received specifications were moved off `C:` into durable research
storage:

| Source | D-drive path | SHA-256 |
|---|---|---|
| Chart-conditioned polarity revised v2 | `D:/GannFinancialAstro/sources/specifications/CHART_CONDITIONED_ASPECT_POLARITY_REVISED_V2_20260722.pdf` | `7812701297CA1430CF6BC3541F183208A9BC0279719A55600A0C4CD3FE33385D` |
| SBC/Shadbala/Drik certification guide | `D:/GannFinancialAstro/sources/specifications/SBC_SHADBALA_DRIK_CERTIFICATION_CODEX_GUIDE_20260722.pdf` | `ABFA2F9E7957D92381344B419F2217AC8762E1D90175083F6B8B63305DD00686` |

The specifications define architecture and research controls. They are not
treated as classical doctrine.

## Built

1. **Chart registry and accuracy gates**
   - Each chart has provenance, an effective interval, an astronomy contract,
     a time-accuracy class, and explicit research acceptance.
   - Multiple accepted hypotheses are evaluated separately; the registry
     refuses silent chart selection.
   - Date-only and unknown-time charts cannot use ascendants, houses, or
     functional lordship.

2. **Versioned static structure**
   - Functional lordship comes from `PARASHARI_ORG_V0`.
   - Corporate-domain translations come from a separate modern-extension
     profile and never supply price direction automatically.
   - The natal graph is immutable and hash-addressed.
   - Only conjunction geometry, dispositors, lordship, and house occupancy are
     active. Special drishti and yoga edges remain disabled.

3. **Explicit TN event contract**
   - Transit and natal roles must be explicitly supplied.
   - Sorted-pair recovery and ambiguous inferred roles are rejected.
   - Transit-to-transit events are rejected.
   - Event payloads containing outcomes, P/L, labels, targets, future returns,
     or other future-prefixed fields are rejected recursively.

4. **Three-axis output**
   - Direction: `SUPPORTIVE`, `ADVERSE`, `MIXED`, or `INDETERMINATE`.
   - Activation: `WEAK`, `MODERATE`, `STRONG`, `EXCEPTIONAL`, or `UNKNOWN`.
   - Volatility: `LOW`, `ELEVATED`, `HIGH`, or `UNKNOWN`.
   - Aspect geometry affects activation and volatility, never direction by
     itself.

5. **Timestamp-safe evaluation**
   - Evaluations cannot precede event time or evidence availability.
   - Future dynamic evidence is rejected.
   - Conflicting evidence becomes `MIXED` and receives an explicit conflict
     flag; it is not silently averaged away.

6. **FX reuse**
   - FX composition delegates to the existing instrument-relative
     base-minus-quote implementation.
   - Identity, inversion, and triangle invariants remain the governing tests.
   - Categorical chart priors are not secretly mapped to numbers.

## Intentionally Skipped

The following remain blocked because the complete source books are not present:

- `AGARWAL_FINANCIAL_COMPLETE_EDITION`
- `TRAILOKYA_DIPIKA_1972`

No substitute rules were invented. Full dignity/friendship doctrine, configured
special aspects, yoga interpretation, and domain-to-price polarity also remain
pending page-level certification.

## Verification Gates

- Focused unit and adversarial tests cover chart ambiguity, time-accuracy
  gating, chart-dependent Saturn roles, immutable graph hashes, bounded
  activation, TN-only ingestion, orb validation, recursive leakage rejection,
  blocked-source reporting, timestamp safety, conflict preservation, and FX
  invariants.
- Profiles and schemas keep `execution_allowed: false` and
  `promotion_allowed: false`.
- The layer is registered in `doctrine_config.yaml` as
  `chart_conditioned_aspect_polarity_v0_execution_locked`.

## Next Gate

After the two missing books are acquired and page-certified, add their rules as
new versioned profiles, never by mutating this baseline. Only then build a
registered purged walk-forward experiment with frozen hypotheses, negative
controls, chart-hypothesis sensitivity analysis, and untouched holdout data.
