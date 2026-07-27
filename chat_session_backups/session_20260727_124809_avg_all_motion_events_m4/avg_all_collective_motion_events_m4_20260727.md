# AVG(ALL) Reliability-Safe Motion And Sampled Events M4

Date: 2026-07-27

## Scope

This milestone extends the synthetic ten-body `AVG(ALL)` collective geometry
with:

- reliability-aware circular unwrapping;
- velocity in degrees per elapsed day;
- acceleration in degrees per elapsed day squared;
- sampled mean-rashi ingress markers;
- sampled R1 coherence-threshold crossings;
- sampled cluster-state transitions;
- a causal-cluster identity tying related geometry descriptors together.

It does not promote AVG(ALL) into Jyotisha doctrine, SBC Vedha, a market
direction, an Auto Suggest input, a shadow-ledger feature, an official ML
feature, or an execution input.

## Reliability-Safe Unwrapping

For two adjacent reliable mean longitudes:

```text
delta = atan2(
  sin(current - previous),
  cos(current - previous)
)

unwrapped_current = unwrapped_previous + delta
```

The signed circular difference uses the shortest path in the range
`[-180, 180]`.

An AVG sample participates only when:

- its mean longitude is finite; and
- `longitudeReliable` is true.

An unreliable sample ends the active segment. The next reliable sample starts
a new segment from its own wrapped longitude. Motion and ingress calculations
never bridge such a gap.

## Velocity And Acceleration

All derivatives use the real Unix timestamp difference converted to elapsed
days. They do not assume equally spaced samples.

- Velocity uses a centered slope for interior points in a reliable segment.
- Velocity uses a one-sided slope at a segment endpoint.
- A one-sample segment has no velocity.
- Acceleration uses the slope between neighboring computed velocities and is
  emitted only for interior points of segments containing at least three
  samples.
- No smoothing, resampling, or future-window fit is applied.

The response contract is:

```text
GANN_PLANETARY_COLLECTIVE_MOTION_V1
RELIABILITY_SAFE_CIRCULAR_MOTION_V1
```

Every sample exposes:

- `segmentId`;
- `unwrappedLongitudeDeg`;
- `velocityDegPerDay`;
- `accelerationDegPerDay2`.

Unavailable values are `null`, never a fabricated zero.

## Sampled Research Events

The detector contract is:

```text
GANN_PLANETARY_COLLECTIVE_EVENT_V1
AVG_ALL_SAMPLED_EVENTS_V1
```

It currently emits:

1. `MEAN_RASHI_INGRESS`
   - Finds a crossed 30-degree boundary inside one reliable motion segment.
   - Estimates the time by linear interpolation of unwrapped longitude.
   - Handles forward and backward motion.
   - Uses an endpoint convention that emits a boundary exactly once.

2. `COHERENCE_THRESHOLD_CROSSING`
   - Detects upward or downward crossing of the versioned low-coherence and
     concentrated R1 thresholds.
   - Estimates the time by linear interpolation of R1.

3. `CLUSTER_STATE_TRANSITION`
   - Records a changed geometry state at the right-hand observed sample.

The input bar timestamps are exact observations. The derived event time is not
an exact astronomical event time. Every event therefore carries:

```text
timing.exact = false
timing.precision = BETWEEN_EXACT_BAR_SAMPLES
```

Exact ephemeris-refined ingress, nakshatra/pada ingress, apparent station,
polarisation peak, and natal contact detection remain future work.

## Causal Clustering

R1, R2, mean longitude, motion, and events are linked descriptors of the same
planetary-geometry source. They must not be counted as independent votes.

Events derived from the same source bracket share a deterministic
`causalClusterId`. The cluster policy fixes directional contribution at
exactly `0.0`.

## Safety Boundary

Backend, TypeScript, and runtime validation all require:

- research only;
- visual marker only for events;
- approximate sampled timing only;
- no traditional authority claim;
- no SBC Vedha;
- no directional contribution;
- no live-inference consumption;
- no Auto Suggest consumption;
- no shadow-ledger consumption;
- no official ML-note consumption;
- no execution.

The desktop rejects a response that violates any of these locks.

## Verification

Verification completed on 2026-07-27:

- focused backend geometry, motion, evidence, and overlay tests: `21/21`;
- focused frontend panel and response-contract tests: `4/4`;
- complete desktop backend suite: `136/136`;
- complete desktop frontend suite: `75/75`;
- complete repository Python suite: `379/379`;
- Python Ruff checks for all changed backend files: passed;
- frontend Oxlint: passed;
- project status validation: passed;
- TypeScript and Vite production build: passed.

The existing Vite advisory for a main chunk larger than 500 kB remains
non-blocking and is unchanged in character.

## Packaging Status

This is a source milestone. No Windows installer or Android package is
promoted by this change. Packaging and physical-device status remain
unchanged.
