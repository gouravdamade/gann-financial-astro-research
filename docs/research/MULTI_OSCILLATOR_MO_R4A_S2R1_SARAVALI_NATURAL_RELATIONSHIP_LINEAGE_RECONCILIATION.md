# MO-R4A-S2R1 Saravali Natural-Relationship Lineage Reconciliation

## Scope

This source-only correction resolves a same-family lineage defect in the
historical S2 pilot. Historical S2 composed a Trailokya natural relationship
with Saravali/Brihat Jataka temporary and Saravali compound rules. The
successor records the distinct Saravali natural matrix and rebinding explicitly.
It does not change the historical source records, event identities, astronomy,
temporary relationship mathematics, five-state compound mathematics, market
state map, or any product runtime.

Starting master: `8367908818c488fe92e4de8e0f86fb0b816c0462`.

## Held Witness and Source Layers

The controlling source is
`SARAVALI_RANJAN_SANTHANAM_1983_HELD_PARTIAL`, SHA-256
`3BFD4F7F717798F87B7EFD6FA5A3DE2E28E7E09FC2520F0F05AE12B2E1BF9A58`.
Direct inspection of PDF image 60 / printed p.56 closes Chapter 4, verses
28-29.

- `SARAVALI_ROOT`: the Sanskrit root supplies the seven-planet matrix.
- `SANTHANAM_TRANSLATION`: the English rendering on the same page is retained
  as a separately-labelled lexical and row-rendering cross-check.
- No commentary is substituted for the root, and the translation is not
  relabelled as root evidence.

The page explicitly makes every omitted non-self relationship neutral, while it
does not state a self relationship or a node relationship. Self pairs and
Rahu/Ketu remain `UNKNOWN`; no source is borrowed to complete them.

## Saravali Matrix

Rows are source body and columns are target body. Diagonal cells are unstated
and therefore `UNKNOWN`.

| Source | SUN | MOON | MARS | MERCURY | JUPITER | VENUS | SATURN |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SUN | UNKNOWN | FRIEND | FRIEND | NEUTRAL | FRIEND | ENEMY | ENEMY |
| MOON | FRIEND | UNKNOWN | NEUTRAL | FRIEND | NEUTRAL | NEUTRAL | NEUTRAL |
| MARS | FRIEND | FRIEND | UNKNOWN | ENEMY | FRIEND | NEUTRAL | NEUTRAL |
| MERCURY | FRIEND | ENEMY | ENEMY | UNKNOWN | NEUTRAL | FRIEND | NEUTRAL |
| JUPITER | FRIEND | FRIEND | FRIEND | ENEMY | UNKNOWN | ENEMY | NEUTRAL |
| VENUS | ENEMY | ENEMY | NEUTRAL | FRIEND | NEUTRAL | UNKNOWN | FRIEND |
| SATURN | ENEMY | ENEMY | ENEMY | FRIEND | NEUTRAL | FRIEND | UNKNOWN |

`SARAVALI_NATURAL_RELATIONSHIP_V1` is the new source operator. It returns only
`FRIEND`, `NEUTRAL`, `ENEMY`, or fail-closed `UNKNOWN`; it authorizes neither a
market direction nor magnitude.

## Trailokya Comparison and Branch

The complete 49-cell comparison preserves seven self-pairs as
`NOT_COMPARABLE`, has 42 non-self comparable directed cells, 41 agreements,
and one conflict:

| Source | Target | Historical Trailokya | Saravali | Status |
| --- | --- | --- | --- | --- |
| MERCURY | MARS | NEUTRAL | ENEMY | CONFLICT |

The frozen pilot contains no `MERCURY -> MARS` transit-to-natal event. The
conflict is therefore source-material but not pilot-relevant. Branch **B** was
taken: Saravali is source-closed and differs in one directed cell, so a new
lineage ledger, source coverage, two successor hypotheses, and blinded freeze
were created. Historical artifacts remain immutable.

## Successor Binding

The successor reads the final S1R1-R1 source coverage snapshot rather than
calling the ephemeris or regenerating astronomy. Every successor source event
retains its event ID/hash, UTC timestamp, chart identity, chart-hypothesis
identity, order, and astronomy snapshot. It continues to state
`NO_APPROVED_ASTROLOGICAL_COMPOSITION_CONTRACT` and `UNKNOWN_ASTRO_STATE`.

| Artifact | Historical | Successor |
| --- | --- | --- |
| Source ledger | `00A63DFA1ED2154D9935D9502191D5574C5D1BF38E924ABD8BDA95FD9E6C1379` | `E9DB0C92B449045FB2ED35D482E3F7063C547CD2562305EEF778064C2F5558E6` |
| Source coverage | `359C905C6CF7792F6782E53552CEBCC9D43A63E93EC375E8314ABE795445A2AD` | `B22F42E78D20858045AE98F0010355E1E8895C60F1DD49570230ECC5B2C7F62A` |
| S2 registry | `E2FD1EA6B570F35E07F06259A64A19E181B06610F0659B1B333800F7688EBA66` | `4655316D94188E9B4187E24D67DC9466124C977002F129508F62B518F4786CDE` |
| USD hypothesis | `FD4E4F3B125EB8254569F8EA6E70FB50ECD2D4B30E4CD9119F7E9CB5BE8A5BF6` | `E9605930B63F89EED49A0CE0F25A11D7EC9AD7FE3B25BD8F2466D4BF2D6C89E1` |
| JPY hypothesis | `FC7A2CFD3930FBBAD41A4995C4697A8B31A50F409DDBE66ED4BE2902C4AE233A` | `040676DC1CF10E197427CF88ED96EDAAB8B7235D74B03BF8F45ECCAC2E5E0B3C` |
| Prediction freeze | `5A7D318D22D27637F2A253D362258648F40CF12DB6016B6743D166A1C010C27A` | `68E7FEDB23EBD3CF52367DF7DEAB241977C7EA8B1720BCF4F01C07F89CB34F7C` |

The successor invariance audit is
`A282DC181591B1F7BA11457E3F86A3FBBDCF54290BF7A3C0E98CDB3140AD07BC`,
the source-lineage reconciliation is
`8C973561EC72B5FF00AA057C1353946B9792F85E13CFBA8EFF6972C356E39B01`,
and the acceptance manifest is
`72404E54ECC169107AD5C5CDB3932D5827D3319D19D29EF252F2C60C64416C75`.

Both successor entries preserve the exact historical S2 hypothesis ID/hash they
supersede. Their decision hashes differ because their upstream source lineage
is different, even though their conceptual side-local state map remains
unchanged.

## Pilot Diff

The deterministic diff contains all 24 rows in
`status/audits/mo_r4a_s2r1_saravali_relationship_lineage_reconciliation.json`
and the generated review table contains all 24 historical-to-successor compound
and pressure states in
`docs/research/MULTI_OSCILLATOR_MO_R4A_S2R1_REAL_24_EVENT_PREDICTION_FREEZE.md`.

Result: 24 unchanged predictions, 0 changed predictions, and 0 changed compound
states. The source lineage operator changes on every row from Trailokya to
Saravali; no actual input cell changes in the frozen event universe.

The successor retains 24 total events: 17 bridge-applicable, 14 directional
(9 SUPPORTIVE and 5 ADVERSE), 3 categorical NEUTRAL, and 7 abstentions as
`UNKNOWN_MORE_EVIDENCE_REQUIRED`. Bridge-applicable and directional remain
distinct categories.

## Boundaries and Next Gate

This is an outcome-blind experimental successor. It reads no price data,
outcomes, candles, returns, PnL, Founder Review content/store, polarity
catalogue, reviewed evidence registry, SBC, Auto Suggest, ML, MT5, or execution
data. It creates no pair resultant, signed wave, source magnitude, or numeric
signed unit. Every successor prediction has `signedUnit=null` and
`magnitudeConfigured=false`; `executionAllowed=false`.

Unrelated source gaps remain open: Saravali positional and naisargika strength,
Trailokya multi-modifier stacking, generic multi-planet precedence, continuous
motion thresholds, generic context resolution, Lattā expansion, Arghya closure,
and every magnitude transform. They were not used to resolve this lineage.

No remaining natural-relationship source-lineage defect blocks S3. The only
authorized next step is `INDEPENDENT_CENTRAL_REVIEW_BEFORE_MO_R4A_S3`; S3 itself
has not been started and no outcome protocol has been selected.
