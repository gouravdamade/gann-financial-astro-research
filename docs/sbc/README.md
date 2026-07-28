# Sarvatobhadra Research Foundation

This package is an isolated, source-profiled research foundation. Phase 1
calculates astronomy, nakshatra membership, and Panchanga facts. Phase 2 adds
one explicit-only, figure-relative 81-cell topology and Sanskrit-letter
fixture. Phase 3A adds standard figure-relative Vedha rays and a transparent
research guidance ledger. Phase 4A binds those layers to one immutable,
timestamp-safe Chakra Lab snapshot. Phase 5A compiles explicit state
boundaries into deterministic half-open atomic intervals. Phase 5B organizes
those interval facts into reconciled, non-voting causal-cluster ledger views.
Phase 5C projects the same ledger into linked, read-only Timeline, Ledger, Ray
audit, Lineage, Reconciliation, and Validation views. It does not emit a market
opinion or trade decision.

Primary profile: `sbc_raman_foundation_v1`.

Comparison profile: `sbc_lahiri_comparison_v1`. This profile exists only to
measure sensitivity to ayanamsha and must not replace Raman silently.

Phase 2 research profiles:

- `sbc_81_rotation_normalized_partial_v1`: compiles nakshatra, rashi, tithi,
  weekday, 16-vowel, and 20-name-initial layers. It is incomplete and has no
  absolute cardinal binding. The machine layer is `NAME_INITIAL`, not
  `CONSONANT`, because the source sequence begins with vowel `अ` (`A`).
- `sbc_64_blocked_v1`: metadata only; compilation fails closed.

Phase 3A research profile:

- `phaladeepika_editor_vedha_guidance_v1`: derives left, front, and right
  targets from the 81-cell board, validates the geometry against the printed
  Krittika, Rohini, and Mrigashira examples, and scores only context values
  actually struck by the selected ray.

The guidance score is deliberately simple and visible:

- each matched target layer contributes one experimental evidence unit;
- a resolved benefic makes the unit positive and a resolved malefic negative;
- source multipliers are `2x` retrograde, `3x` exalted, and `0.5x`
  debilitated;
- conditional Mercury/Moon nature and ambiguous multiplier combinations are
  reported as unresolved and excluded from the net;
- normalized guidance is `net / (favorable + absolute adverse)`, bounded from
  `-1` to `+1`.

This normalization is an engineering comparison aid, not a classical
numerical score and not a financially validated signal.

Phase 4A Chakra Lab contract:

- the request timestamp must contain a UTC offset;
- astronomy, Panchanga, current placements, target context, and Vedha actors
  share one evidence cutoff;
- current nakshatra, rashi, and tithi-group context is derived from that
  snapshot rather than accepted as caller-provided facts;
- direct/swift versus mean motion is never inferred for Mars through Saturn;
- fixed-direction actors can be evaluated immediately, while a selected
  variable actor without explicit motion is returned as `MOTION_REQUIRED`;
- market data, Auto Suggest, financial labels, orders, and MT5 execution are
  absent and explicitly locked.

Phase 5A atomic interval contract:

- boundaries are explicit, timezone-aware state transitions;
- each interval is `[startUtc, endUtc)` with one no-lookahead evidence cutoff;
- one series cannot mix foundation, grid, Vedha, or guidance profiles;
- source lineage and evaluated-contribution identities remain separate;
- favorable, adverse, net, true gross activation, unknown count, unknown
  magnitude, and coverage remain separately visible;
- reversed boundary input produces the same canonical series;
- phase, confidence, market direction, Auto Suggest, live inference, official
  ML notes, validation votes, trades, and MT5 execution remain blocked.

Phase 5B multidimensional ledger contract:

- one source lineage inside one interval is one causal fact;
- exact repeats are deduplicated and conflicting evaluations sharing one
  lineage fail closed;
- causal-cluster identity contains instrument, interval, cutoff, source and
  profile lineage, actor, target, and exact derivation role;
- total, actor, target-layer, nature, Vedha-direction, and source-lineage views
  reference the same primary cluster IDs;
- every view reconciles to the Phase 5A favorable, adverse, net, true-gross,
  scored, unknown, missing, total, and coverage ledger;
- unavailable dimensions remain visibly `UNAVAILABLE`;
- figure-relative Vedha direction is not market direction;
- FX subtraction, phase, confidence, all trading consumers, and execution
  remain blocked.

Phase 5C linked audit-view contract:

- the projection accepts only a canonical, reconciled Phase 5B ledger;
- interval, cell, cluster, and lineage links use the existing canonical IDs;
- Timeline, Ledger, Ray audit, Lineage, Reconciliation, and Validation expose
  the same facts without multiplying them into extra votes;
- ray direction remains figure-relative Vedha direction, with no phase angle
  or market direction;
- explicit missing evidence, null unknown magnitude, incomplete coverage, and
  absent financial or phase validation remain visible;
- browser development uses private HTTP while packaged desktop transport uses
  a dedicated execution-locked Tauri command;
- FX subtraction, phase, confidence, Auto Suggest, live inference, official ML
  notes, shadow votes, trades, packaging promotion, and execution remain
  blocked.

Minimal use:

```python
from sbc import MotionClass, VedhaActor, VedhaGuidanceEngine

engine = VedhaGuidanceEngine("phaladeepika_editor_vedha_guidance_v1")
report = engine.evaluate(
    (
        VedhaActor("JUPITER", "KRITTIKA", MotionClass.MEAN),
        VedhaActor("SATURN", "KRITTIKA", MotionClass.RETROGRADE),
    ),
    {"NAKSHATRA": {"SHRAVANA", "BHARANI"}},
)
```

Locked until later certification:

- default choice between 64-cell and 81-cell forms
- absolute cardinal orientation
- Abhijit insertion interval
- automatic direct-versus-swift speed classification
- special corner/junction Vedha rules, association inference, and Latta
- classical natal-severity translation
- financial scoring or directional market labels
- Auto Suggest and MT5 execution
- main chart integration

The first user-facing surface is a read-only Chakra Lab. Packaged UI requests
cross native Tauri IPC; Tauri forwards them only to its supervised private
sidecar. Browser development keeps a private API fallback for testability.
