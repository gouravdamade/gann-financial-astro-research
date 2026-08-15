# PFR-V2B-R6-SBC-TD1R2 - Final Trailokya 1972 Source Glyph Correction

## Scope

TD1R2 is a surgical, source-only correction to the existing Trailokya native
Vedha contract. The controlling witness is the private 1972 original scan,
SHA-256 `1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194`.
The 2016 Khemraj reprint, SHA-256
`19CC2387C6C6B80E9A1F5A63BB9A71090A10FB17F3BD8BB56058210667F61ED8`, agrees
with both corrections but remains a same-lineage, non-controlling reading
witness. No private page bytes are committed.

## Historical Chain

- **TD1R** correctly retained `VISARGA` for the Jyeshtha left target row, but
  had unresolved native target/token defects elsewhere.
- **TD1R1** correctly introduced the lossless dental/retroflex/sibilant token
  system and corrected its broader table and locator defects. It nevertheless
  transcribed Verse 48's third pair as `PA <-> KHA` and changed Jyeshtha to
  `ANUSVARA`; both readings were wrong.
- **TD1R2** corrects only these two records. It neither reopens the 28-row
  audit nor changes the TD1 architecture.

## Corrected Source Records

### Verse 48 paired letters

The source line is `बवौ शसौ षखौ ...`. On 1972 scan p.27 / printed p.11,
Verse 48, the final pair is `ष <-> ख`:

`SSA_RETROFLEX <-> KHA`

The first two pairs remain `BA <-> VA` and `SHA_PALATAL <-> SA_DENTAL`.
`PA <-> KHA` is now a regression failure, not an accepted source reading.

### Jyeshtha target row

On 1972 scan p.25 / printed p.9, Verse 35, the Vama/left source sequence is:

`YA, SAGITTARIUS, VISARGA, PISCES, CHA, ASHVINI`

The literal vowel is `अः`. `ANUSVARA` remains distinct (`अं`) and continues
to appear only in the separately source-closed Verse 51 vowel-pair rule.

## Current Trust and Remaining Limits

`TRAILOKYA_NATIVE_TARGET_MAP_TRUSTED_FOR_SOURCE_CONTRACT=true` now belongs to
the TD1R2-corrected contract, not the TD1R1 historical snapshot alone. The
completed source map does not close the full Vedha operator: exact
swift/mean threshold, stationary handling, Shukla Panchami boundary,
modifier/precedence doctrine, Latta and reproducible Arghya arithmetic remain
fail closed.

No runtime or UI path changed. Polarity, score aggregation, price mapping,
Fields polarity, Auto Suggest, ML, MT5 and execution remain prohibited;
`executionAllowed=false`.

TD1 is closed for the present source-contract scope. A later, separately
authorized TD2 translation can begin at 1972 scan pp.52-62 / printed pp.36-46.
