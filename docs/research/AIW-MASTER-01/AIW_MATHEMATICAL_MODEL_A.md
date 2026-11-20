# Model A · A categorical influence field

**Decision variable.** For a chart c and a time t let k identify (source edition, subject, target, result domain, stage). A(c,k,t) is a set of qualified claims. Each claim carries its source rule, the input values that fired it, coverage, and its effective interval. Distinguish stages such as placement, qualification and realization. Reporting a sign on the first stage does not fill the last stage.

For known evidence encode the *presence of assertions* by two bits (f,a). The idempotent join is (f₁ OR f₂, a₁ OR a₂). Thus two reports of the same benefit still give (1,0), and support for benefit and loss is (1,1). This operation forms a small product lattice ordered by information inclusion. It does not rank how fortunate a chart is. When the source genuinely assigns two effects within scope, the label can be MIXED. When witnesses offer mutually exclusive readings of the same proposition, retain CONFLICTED with alternatives. Neither licenses a net zero.

Store explicit neutral as a separate positive assertion of indifference. The pair (0,0) alone means no directional assertion and can accompany EMPTY, NOT_APPLICABLE, UNCOVERED or UNKNOWN. Missing requested factors set coverage PARTIAL even when known claims already give (1,0). A suppressed benefit retains its baseline and an inactive conclusion with the suppressing rule ID. Losing a favorable effect supplies no independent assertion of harm.

## First evaluator specified on paper

Take ecliptic sidereal longitude λ in [0,360). Let r(λ)=floor(λ/30) and h=1+mod(r(transit Mercury)−r(natal Moon),12). Require one chart ID, one frame and independently recorded times. Mercury in h∈{2,4,6,8,10,11} has a favorable general base in Iyer v4. For h=12, v24 lists adverse personal outcomes. Expose each domain separately if requested. For an unreviewed h, report uncovered pending its specific verse. Mercury in h=2 illustrates why a favorable general base and more qualified detailed outcomes need separate rows. Verse 50 gives sign-wide applicability. A sign change with an identical output label is still an evidence boundary.

At a positive base, evaluate the four alternatives in v53 using three-valued predicates. Any true alternative suffices to mark this particular benefit suppressed. If all are false, report “no v53 suppression identified”; if none is true and one is unknown, report unresolved. Verse 46 still conditions realization. A source-specific graph can implement this gate later. The person-domain interpretation remains distinct from the Mode 2 operation of putting a currency chart in the person's place.

## Composition and display

Facts may have many citations, and outcomes can share a planet without sharing a target. Aggregate independent cells as a Cartesian product keyed by k. One optional visualization counts unique favorable and adverse claims separately. That projection depends on how the researcher defines a claim and its universe. It has units of claim records. Do not infer that the chart with more records is more fortunate. For a time window B report the fractions of time in each state, with an explicit unknown fraction. Summing over overlapping target lanes can exceed 100% and has no single-chart probability meaning.

## Cost and first implementation

At one instant the Mercury lookup is constant-time after retrieving two longitudes. Evaluating n independent keyed claims is O(n), with O(n) records in the worst case. Sort m boundary times once in O(m log m) and store changes per target. Materialize the placement table with separate general and particular rows, compute the sides independently, and verify the real fixture before enabling interval queries. An indexed point query needs a logarithmic boundary lookup plus the returned records.

## Assumptions, checks and limits

Indexing and joining are MATHEMATICAL_ENGINEERING. The placement list and whole-sign timing are SOURCE_EXPLICIT in this profile. Whole-sign counting does not imply an ascendant, a bhāva cusp or an orb. Test sign wrap Pisces→Aries, a reversed transit, a mixed domain, one fact with two locators, explicit neutral vs unknown, and two certified source profiles with different readings. Duplicating a citation and changing display timeframe must preserve A. The model cannot estimate intensity or settle an undocumented conflict. Its first admissible output is an inspectable series of categorical placements.
