# Nightly Research — Trailokya 1972 Moon-Nature Shukla Panchami Boundary

Date: 2026-10-05  
Status: RESEARCH_ONLY  
Branch baseline verified: `11eafce8aa16c1a80a3b4587f62f76f78766969d`  
Scope: one bounded source adjudication only; no production/operator/runtime/scoring/polarity/Fields/Candidate-C/EMP3/provider/outcome/MT5/execution changes.

## Question / task

Adjudicate the single remaining Trailokya 1972 natural-planet-class edge:

```text
TD1972_MOON_NATURE

purnaSaumyaRange =
  SHUKLA_PANCHAMI_THROUGH_KRISHNA_DASHAMI

kshinaKruraRange =
  KRISHNA_EKADASHI_THROUGH_SHUKLA_PANCHAMI

overlap =
  SHUKLA_PANCHAMI
```

Determine whether Shukla Panchami itself is source-defined as SAUMYA, KRURA, a transition state, or remains UNKNOWN.

## Why it matters

The existing research contract correctly fails closed at the overlap. A timestamp-safe planet-nature classifier cannot choose one side without source authority. Repairing the overlap from modern convention, sunrise rules, fractional tithi progress, lunar elongation, or software behavior would silently add doctrine.

## Repository context verified

At start of this run, `research/nightly-project-work` was identical to baseline:

`11eafce8aa16c1a80a3b4587f62f76f78766969d`

Controlling contract:

`configs/sbc/trailokya/trailokya_1972_planet_nature_conditions_v1.yaml`

Current repository state already records:

- primary authority: `TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN`, SHA-256 `1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194`;
- same-lineage reading witness: `TRAILOKYA_DIPIKA_VYAS_KHEMRAJ_2016_REPRINT`, SHA-256 `19CC2387C6C6B80E9A1F5A63BB9A71090A10FB17F3BD8BB56058210667F61ED8`;
- verse 55 locators: 1972 scan pp.29–30 / printed pp.13–14;
- current fail-closed state: `UNKNOWN_AT_OVERLAP_BOUNDARY`;
- prior two-pass audit: `DIRECT_AGREEMENT`.

The 1972 page images remain the citation authority. In this run the Archive PDF delivery host was not directly accessible, so no claim is made that those page images were freshly reopened. The existing repository page-image certification is preserved, and the matching Internet Archive OCR plus the 2016 same-lineage text were independently rechecked.

## Sources checked

### A. Controlling 1972 Trailokya witness

Bibliographic identity:

- *Sarvatobhadra Chakra* with *Trailokya Dipika* commentary;
- Pt. Mithalal Vyas;
- Tej Kumar Book Depot, Lucknow;
- 1972 original scan;
- Internet Archive identifier: `eJNJ_sarvatobhadra-chakra-sanskrit-and-hindi-text-with-trailokya-dipika-commentary-by`.

Repository locator:

- scan pp.29–30;
- printed pp.13–14;
- verse 55;
- root verse plus Hindi commentary.

Current-run access:

- Internet Archive item metadata: accessible;
- full-text OCR: accessible and page-aligned enough for textual corroboration;
- original PDF/page-image delivery: inaccessible from current web runtime because Archive redirects to a blocked delivery host.

### B. 2016 same-lineage reading witness

Bibliographic identity from repository and accessible text:

- Khemraj Shri Krishnadas edition/reprint;
- June 2016;
- same Mithalal Vyas work;
- 100-page witness;
- role: same-lineage reading witness, not independent doctrine.

Accessible Scribd text reproduces verses 53–58 and the Hindi commentary around verse 55.

## Direct wording

### Sanskrit root, verse 55

A bounded reading from the 1972 OCR, agreeing with the 2016 witness:

`daśamyavadhi kṛṣṇe tu pakṣe pūrṇo hi candramāḥ / tataḥ paraṃ kṣīṇacandraḥ ...`

The root directly establishes:

1. in Krishna pakṣa, the Moon is treated as `pūrṇa` **through Dashami**;
2. `tataḥ param` — **after that** — the Moon is `kṣīṇa`.

This cleanly supports the Krishna Dashami → Krishna Ekadashi transition.

The root does **not** mention Shukla Panchami, does not state the beginning of the pūrṇa range, and does not define how the kṣīṇa period terminates on the waxing side.

### 1972 Hindi commentary

The commentary says, in substance:

- from Shukla Panchami through Krishna Dashami, the Moon is pūrṇa/saumya;
- from Krishna Ekadashi through Shukla Panchami, the Moon is kṣīṇa/krūra.

The two Hindi range expressions therefore both include **Shukla Panchami** on their face.

The page break occurs inside the second commentary sentence: verse 55 begins on printed p.13 and its Hindi explanation continues onto printed p.14, matching the repository locator.

### 2016 same-lineage reading

The 2016 text reproduces the same structure:

- `शुक्ल पक्ष की ५ से लेके कृष्णपक्ष की १० ...`
- `कृष्णपक्ष की ११ से लेके शुक्लपक्ष की ५ ...`

No additional qualifier appears for:

- beginning of Shukla Panchami;
- completion/end of Shukla Panchami;
- sunrise;
- tithi transition instant;
- fractional tithi progress;
- ghati;
- lunar longitude;
- a separate transition class.

Therefore the 2016 witness **confirms the overlap rather than resolving it**.

## Boundary interpretation

### What is source-closed

```text
KRISHNA_DASHAMI = within pūrṇa/saumya range
AFTER_KRISHNA_DASHAMI = kṣīṇa/krūra range begins
```

Because verse 55 itself says `daśamyavadhi` and then `tataḥ param`, Krishna Ekadashi is the first named tithi after the source-closed Dashami boundary.

### What is not source-closed

```text
SHUKLA_PANCHAMI = ?
```

The Hindi commentary simultaneously uses Shukla Panchami as:

- the beginning endpoint of the pūrṇa/saumya range; and
- the ending endpoint of the kṣīṇa/krūra range.

Neither the root nor the commentary states an inclusive/exclusive convention capable of disambiguating the shared endpoint.

## Competing readings considered

### Reading 1 — Shukla Panchami = SAUMYA

Possible only if “from Shukla Panchami” is taken as governing the whole tithi while “through Shukla Panchami” is treated as ending immediately before that tithi.

**Problem:** the source does not state such an exclusive interpretation for the kṣīṇa range.

Status: `UNSUPPORTED_RESOLUTION`.

### Reading 2 — Shukla Panchami = KRURA

Possible only if “through Shukla Panchami” is read inclusively for kṣīṇa while “from Shukla Panchami” is treated as beginning after completion of Panchami.

**Problem:** the source does not state such a delayed-start interpretation for the pūrṇa range.

Status: `UNSUPPORTED_RESOLUTION`.

### Reading 3 — Shukla Panchami = SOURCE_DEFINED_TRANSITION_STATE

No distinct transition-state term, half-day rule, tithi-fraction rule, or split-state procedure appears in verse 55 or the checked same-lineage commentary.

Status: `NOT_ESTABLISHED`.

### Reading 4 — genuine unresolved overlap

This is the only reading that preserves both source statements without adding an unstated boundary convention.

Status: `SUPPORTED_FAIL_CLOSED_INTERPRETATION`.

## Adjacent material checked

Verses 54–58 were reviewed around the target passage.

- Verse 54 establishes base natural classes and conditionally kṣīṇa Moon.
- Verse 56 handles Mercury's krūra association.
- Verse 57 handles categorical retrograde/swift intensification.
- Verse 58 directs precise motion/state work to mathematical/panchanga sources, but does not define a Shukla-Panchami Moon-nature split.

Later Trailokya material distinguishes pūrṇa-Moon and kṣīṇa-Moon effects, but does not supply a new Panchami boundary rule.

A later passage also states a broad Shukla/Krishna distinction for a different aspect/result context. It is **not** imported into verse 55's natural-class boundary and therefore does not repair the overlap.

## OCR / punctuation / transcription assessment

The overlap is not plausibly explained by a one-off 1972 OCR error:

- the repository's earlier direct page-image two-pass audit records the same ranges;
- the 2016 same-lineage witness independently reproduces the same numerical endpoints;
- both range clauses are coherent Hindi; the problem is their shared endpoint, not a garbled numeral.

No punctuation mark in the accessible readings establishes exclusive boundary semantics.

Disposition:

`NOT_AN_OCR_ONLY_ARTIFACT`

`NOT_RESOLVED_BY_PUNCTUATION`

## Final verdict

```text
TRAILOKYA_MOON_SHUKLA_PANCHAMI_BOUNDARY
= UNKNOWN_AFTER_BOUNDED_SOURCE_REVIEW
```

Decisive outcome:

```text
SHUKLA_PANCHAMI = UNKNOWN_AFTER_BOUNDED_ADJUDICATION
```

The current repository fail-closed behavior is therefore **correct and should remain unchanged**.

## Contract implication

The existing research contract should **not** later be revised to force SAUMYA or KRURA at Shukla Panchami based on presently available evidence.

A future human-reviewed contract refinement may improve provenance by distinguishing:

```text
root_source_closed:
  Krishna Dashami inclusive as pūrṇa
  after Krishna Dashami = kṣīṇa

commentary_source_closed:
  two named ranges reproduced exactly

boundary_state:
  Shukla Panchami = UNKNOWN_SHARED_ENDPOINT
```

But this run does not modify the contract or any runtime/operator.

## What remains UNKNOWN

1. Whether Mithalal Vyas intended Shukla Panchami itself to be saumya.
2. Whether he intended it to remain krūra through completion of Panchami.
3. Whether an unstated traditional convention was assumed for inclusive/exclusive tithi endpoints.
4. Whether an earlier manuscript/commentary source behind this compilation contains an explicit boundary instruction.
5. Whether a precise transition instant inside Shukla Panchami exists in the source tradition.

None of these may be supplied from modern convention without a separately identified source profile.

## Secondary objective / next Trailokya-SBC mechanics target

Because the Moon boundary **did not close**, no broader mechanical inventory was performed.

The existing TD1R repository recommendation remains the appropriate next bounded Trailokya/SBC source task:

`TD1_MODIFIER_PRECEDENCE`

Target scope already identified by the repository:

- 1972 scan pp.52–62 / printed pp.36–46;
- modifier/precedence doctrine;
- separate Latta context;
- no financial or scoring promotion.

This target is merely carried forward; it was **not researched in this pass**.

## Status

`RESEARCH_ONLY`

Proposed research conclusion:

`UNRESOLVED` for the Shukla-Panchami boundary itself.

The broader planet-nature contract remains source-closed except for this explicit boundary gap.

## Guards against overclaiming

- Do not assign the whole Shukla Panchami tithi to SAUMYA.
- Do not assign the whole Shukla Panchami tithi to KRURA.
- Do not invent a half-tithi, sunrise, ghati, degree, elongation, or percentage threshold.
- Do not use BPHS, Sārāvalī, Bṛhat Jātaka, modern software, or popular panchanga convention to overwrite Trailokya.
- Do not reopen Mercury's same-pada/same-navamsa rule absent genuinely contradictory primary evidence.
- Do not convert this nature classification into market direction, market magnitude, oscillator amplitude, score, or execution behavior.

```text
MARKET_DIRECTION = WITHHELD
MARKET_MAGNITUDE = WITHHELD
OSCILLATOR_AMPLITUDE = WITHHELD
executionAllowed = false
```

## Dated source log — 2026-10-05

- Pt. Mithalal Vyas, *Sarvatobhadra Chakra* with *Trailokya Dipika*, Tej Kumar Book Depot, Lucknow, 1972. Internet Archive identifier `eJNJ_sarvatobhadra-chakra-sanskrit-and-hindi-text-with-trailokya-dipika-commentary-by`. Target: scan pp.29–30 / printed pp.13–14 / vv.54–58. Current run: full-text OCR and metadata accessible; PDF delivery host inaccessible; prior repository direct-page certification retained.
- Khemraj Shri Krishnadas, June 2016 same-lineage reprint of Mithalal Vyas, 100 pages. Accessible text witness: Scribd document `742095906/Sarvatobhadra-Chakra-Khemraj-Publishers-text`. Target: vv.53–58 around printed p.12–13 transition.
- Repository source contract: `configs/sbc/trailokya/trailokya_1972_planet_nature_conditions_v1.yaml`.
- Repository translation ledger: `configs/sbc/trailokya/trailokya_1972_translation_coverage_ledger_v1.yaml`.
- Repository TD1R source-closure report: `docs/sbc/PFR_V2B_R6_SBC_TD1R_TRAILOKYA_1972_NATIVE_VEDHA_SOURCE_CLOSURE.md`.

## Stop condition

The controlling wording and same-lineage reading witness both preserve the overlap and provide no boundary semantics. Further generic Moon-nature searching would violate the bounded directive unless genuinely new primary/same-lineage source material becomes available.

Stop here.
