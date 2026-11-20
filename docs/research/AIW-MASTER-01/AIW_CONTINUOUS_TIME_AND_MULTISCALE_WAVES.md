# Continuous time and waves within waves

An underlying state can be defined for every t and remain constant for days. Mercury's sign occupancy supplies an example. Its longitude generally varies between sign boundaries; the natal Moon-relative placement is discrete. Its timing in the Iyer translation extends throughout the sign. No inspected verse makes its strength proportional to distance from ingress. In another profile, a moving obstructing occupant can change the qualified result while Mercury stays in the same sign.

## Which timing object is present?

| Input or source statement | Defensible support | Open question |
|---|---|---|
| Mercury, gocara v50 | Whole transit sign; per-place base from vv4, 19–24 | Exact realization inside the interval and cumulative magnitude |
| Sun/Mars and Moon/Saturn, v49 | First or second half of a sign as designated | Degrees 0–15/15–30 are a geometric reading. Half elapsed residence time differs at nonuniform speed. Saturn v54 also warrants collation |
| Jupiter v51 | A specific middle-of-odd-sign qualification | Width of “middle” and relation to other verses require review |
| Phaladīpikā XXVI.6 | Occupancy of the paired place changes eligibility of the favorable Mercury result | Membership rules for clearing all possible obstructors, interval conventions across stations |
| Exact angular alignment, applying/separating | Astronomical event and direction of approach under a named angle and orb, if supplied | Source-specific efficacy, peak, after-effect and duration. A generic orb has no authority here |
| Trailokya motion and residence | Named categories and descriptive durations in R6 | Continuous speed thresholds, exact station handling, persistence and overlapping modifier precedence |
| Annual and subsidiary periods | Timing systems with parents and children in Tājika tradition | Which period system, which chart and how the parent qualifies a child. Different profile from transit occupancy |

## Reconstruct time before binning it

Fix UTC, reference frame, ephemeris version/effective flags, chart version and source profile. Unwrap longitudes around 360° before finding crossings. Search for sign boundaries in each contributing transit, splitting near turning points. Bracket roots on monotone sections or use a conservative speed bound plus adaptive refinement. A sign at both endpoints is insufficient: a retrograde loop can cross and return. At a tangential touch, distinguish an instant of equality from a positive-duration change. If position error spans the boundary, mark a boundary-time uncertainty bracket. Refine until a specified tolerance is achieved or expose the bracket. An instant exactly on a sign boundary follows the stated floor convention; do not assign an entire neighboring interval on its account.

Store time intervals in UTC with inclusive start and exclusive end between changes; handle isolated points and one-sided retrograde limits explicitly. At a decreasing crossing, the exact floor value can equal the pre-crossing state. Record that point independently if exact queries require it. Simultaneous boundaries enter one atomic update. Preserve event IDs for retrograde re-entry and the shared source rule ID. A station alone does not change Mercury's sign placement. Never extend an influence after separation without a persistence rule. Astronomy resolution and textual timing precision are separate limits.

## Six meanings of multi-resolution

1. **Natural duration hierarchy.** Sort intervals by actual length or containment to reveal slow occupancies and short obstruction windows. Overlap without containment is also allowed. Duration measures time, not efficacy.
2. **Additive bands.** Slow + medium + fast reconstruct a value only for an already additive measure and a disjoint partition. Band cutoffs are engineering choices. Overlapping moving averages double count content.
3. **Hierarchical modulation.** An explicit parent can govern a child, as in a chosen period-system profile or the qualified transit rule. There is no common multiplier merely because one interval contains another.
4. **Nested interaction.** Intersect a base and a guard. A narrow interval can change the qualified state for its duration while the base continues. A short interval with no connecting rule stays in its own lane.
5. **Signal analysis.** Fourier coefficients of a frozen scalar describe periodic content and suffer window/leakage effects. Wavelets localize changes across scales but require a basis, sampling grid and edge handling. A state-space model with hidden dynamics requires transition/observation assumptions. All three can describe an existing signal; none supplies a missing astrological observable. [Mallat, original multiresolution paper](https://www.di.ens.fr/stephane.mallat/papiers/MallatTheory89.pdf)
6. **Separate layers.** Draw raw intervals, modifier windows, effective categories and coverage. This is the preferred first view. The founder can follow an interval through M1, M5, H1, H4, D1 and W1 without recomputing its meaning.

## Two different meanings of a source maximum

Phaladīpikā IV.2, printed p34, identifies highest exaltation as a location of full exaltation strength. X.12, printed p109, selects the strongest of three named candidates for a particular natal indication. The first is an extremum of a measure and the second is a choice among candidates. Neither gives an extremum of chart-wide influence. Infinitely many curves can share the same maximum. A source-backed continuous candidate needs its own degree-to-strength formula, units, reference degree and rule transferring it to the timed result. A and B already produce stepped timelines. C can produce continuous magnitude only within a subdomain meeting those extra conditions.

## Sampling and waveform alternatives

For bin B and a given lane/state s, compute qₛ(B)=length({t∈B: state(t)=s})/length(B). Keep unknown in the denominator. Adjacent bins recompose by duration-weighted sums. A weekly chart should also store its transitions and constituent event IDs. For a 60-minute favorable base with a distinct 3-minute suppression and 2-minute unknown span, the reviewable states are 55/60 clear of that guard, 3/60 suppressed, 2/60 unknown. No magnitude of favorability follows. Point sampling at the hour can miss both short spans.

| Shape | Definition or use | Classification and problem |
|---|---|---|
| Rectangular presence | Indicator of sourced applicability interval | Appropriate for categorical support. A height of one encodes presence only |
| Triangular | max(0,1−abs(t−t₀)/d) | Experimental peak and linear rise/decay |
| Raised cosine / Hann | (1+cos(π(t−t₀)/d))/2 inside ±d, zero outside | Experimental finite taper with artificial peak and bandwidth |
| Gaussian | exp(−(t−t₀)²/(2σ²)) | Experimental width and nonzero tails extending outside the source interval |
| Exponential | exp(−(t−t₀)/τ) after t₀ | Assumes onset, time constant and remembered effect |
| Source-valued continuous measure | Recompute a certified degree-dependent quantity in native units | Continuous amplitude is possible only if the text gives the quantity, applicability and map to this particular outcome |
| State transition | Enter, exit, suspend or resume when a predicate changes | Preserves discontinuities with no interpolation. Source-defined extrema remain separate from geometric extrema |

A finite sum of steps is a step function; densely spaced changes can *look* smooth at low resolution. A display average is continuous in some sliding-window definitions, but its meaning is time occupancy. Neither procedure establishes source-defined continuous phala. Quasi-periodic orbital inputs do not prove periodicity of an interpreted state with chart-specific gates. On M boundaries, sorting is O(M log M) and scanning costs O(M) plus rule updates. Precomputed interval indexes allow zoom queries without re-running astronomy. Require pointwise equality across timeframes, exact rebinning of occupancy, and preserved union of event IDs.
