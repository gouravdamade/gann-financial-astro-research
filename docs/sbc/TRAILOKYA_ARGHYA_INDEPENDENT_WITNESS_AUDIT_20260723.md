# Trailokya Arghya Independent Witness Audit - 2026-07-23

## Decision

The Arghya lab now has useful independent evidence, but it still does not have
a reproducible price forecast formula. The new evidence is therefore admitted
only as guarded research metadata:

- one disputed table value has an independent correction witness;
- the other disputed value is independently repeated and remains unresolved;
- two sources independently state that one reference-price unit is one
  twentieth, or 5 percent;
- a dated 1951 silver example supports the qualitative direction in one
  historical case, but its final score-to-price working page is unavailable.

Direct price, bullish/bearish labels, modern instrument mapping, Auto Suggest,
live inference, official ML-note evidence, validation promotion, and MT5
execution remain blocked.

## Sources Examined

### Krishna Rau and Choudhary booklet

Private artifact:

`D:\GannFinancialAstro\sources\private\KRISHNA_RAU_CHOUDHARY_SBC_CHISTABO_2013_786A2041.pdf`

SHA-256:

`786A20415DAFC791CA7374C33458B30465EA5B93DD7F2856B1969FB7374A8F6A`

This is a 2013 ChiStaBo edited transcription of a booklet attributed to N. N.
Krishna Rau and V. B. Choudhary and dated 20 January 1962. It is independent
of the Mithalal Vyas Trailokya editions, but it is not the original 1962 scan.
It is therefore a secondary transcription witness rather than a primary
edition witness.

Visually checked evidence:

- PDF page 25, printed page 24, Table XV prints `11|15` for the
  relationship/three-quarter/malefic-neutral cell. This agrees with the
  proportional expectation and supports `11|15` as a correction candidate for
  the Trailokya editions' `11|45`. The Trailokya source rows remain unchanged.
- PDF page 26, printed page 25, Table XVI prints `2|18` for
  five-class/three-quarter/four-malefics. This repeats Trailokya's
  non-proportional value rather than resolving it.
- PDF pages 26-27, printed pages 25-26, say to divide the ruling price by 20
  and treat each one-twentieth as a unit.
- PDF page 34, printed page 33, calls one slab 5 percent or one-twentieth in an
  iron/steel illustration. The text begins from an observed increase and does
  not show a complete numerical subtotal-to-slab derivation, so it is
  retrospective evidence only.

### Agarwal financial chapter

The already-audited incomplete Agarwal image scan independently repeats the
one-twentieth price unit on PDF page 115, printed page 118. Its surrounding
text also says benefic and malefic effects should be differenced. This supports
the unit definition, not a complete forecasting formula, and does not repair
the scan's missing pages or provenance limitations.

### Dated Bombay silver page photographs

The public SBC quantification FAQ links page photographs for a silver example
dated 12 and 14 May 1951:

- FAQ and worksheet index:
  `https://howisyourdaytoday.com/faq/Courses_%26_Classes/Sarvatobhadra_Chakra/FAQ_SBC_Quantification_of_Gains_and_Losses.htm`
- 12 May pages:
  `https://share.evernote.com/note/b10e26c1-d24d-4d55-80fc-a174efe8d99f`
- 14 May pages:
  `https://share.evernote.com/note/9c2bccf7-2bdf-4b83-a9e9-1a3497ac46b7`

The seven downloaded page images are preserved outside Git at:

`D:\GannFinancialAstro\sources\private\derived\arghya_1951_silver`

Image hashes:

| File | SHA-256 |
| --- | --- |
| `1951-05-12_page_1.jpg` | `D0E013CF15B610DA394CB832D02BB722CEB36654F575B8451621E37ECEABE1E9` |
| `1951-05-12_page_2.jpg` | `EF4DE3CED7F3F5CFEF9E9B04122898401C512F08BB2C760201E564CCB6370687` |
| `1951-05-12_page_3.jpg` | `031F5A715F4282DB0CB042F976728677E7D61D269F38E5A86B2EE0BE22DE2B0A` |
| `1951-05-12_page_4.jpg` | `B84C4F5F9978F4693298B9C921950E6522B6349E8593C9795C0EBE2C34CD53FB` |
| `1951-05-14_page_1.jpg` | `4D85177E4009ED5FF7DE234D6299E7317BC9BD43483769ED4641C955B456FAC5` |
| `1951-05-14_page_2.jpg` | `9A6C9939A6386354F13B4314CF2F16EEB2839D2915D51E31CABDC6A8C6255C96` |
| `1951-05-14_page_3.jpg` | `7BF8C133FE806ED6D9A1B3E769BEA8EAFB4F6CA75E7EA44FD8AF37C012B16714` |

Visible facts from the pages:

- Bombay, silver forward contract, 3 p.m. standard time.
- The question records 12 May 1951 price `2041` and asks for 14 May 1951.
- The 12 May calculation identifies two benefic and one malefic contributor,
  totals the two sides separately, and shows a net benefic remainder
  `0|32|15`, annotated on the page as decimal `0.5375`.
- The 14 May page records price `2011`, a decrease of 30 points or about
  1.47 percent from `2041`.
- The 14 May calculation identifies both contributors as benefic and shows
  total `1|3|45`, annotated as decimal `1.0625`.

This single case is directionally consistent with the source rule that a net
benefic influence can mean greater availability and lower price. It is not a
prospective validation record: the pages are historical, the edition identity
is not established from the images alone, and the linked final working note
that should connect score to price redirects to an authenticated Evernote
screen. The visible pages do not explain why the observed move is about 1.47
percent rather than one or more 5-percent units.

## Machine Guardrails

`configs/sbc/arghya/trailokya_arghya_reconciliation_v1.yaml` now records:

- the independent table readings and their authority level;
- the witnessed `1/20 = 5%` reference unit;
- the two historical examples and their missing evidence;
- `correction_applied: false` for both disputed cells;
- `certifies_price_formula: false` and
  `reusable_prediction_allowed: false` for every worked example.

The original 1972 and 2016 CSV transcriptions are unchanged. The research lab
can calculate the size of one reference unit, such as `2041 / 20 = 102.05`, but
returns no target price, market label, or trading signal. The price API still
fails closed.

## Certification State

Supported now:

1. Stable same-lineage readings for all 108 Trailokya cells.
2. Independent secondary support for `11|15` as the first anomaly's correction
   candidate, without applying the correction.
3. Independent repetition of `2|18`, which leaves the second anomaly open.
4. Independent support for the one-twentieth or 5-percent reference unit.
5. One historical example consistent with benefic/abundance/lower-price
   direction.

Still required before any promotion:

1. An original independent table edition or another page-controlled witness.
2. The missing final 1951 score-to-price working page, or a different complete
   worked example that can be reproduced line by line.
3. A certified rule converting the computed score into a count or fraction of
   one-twentieth units.
4. Certified strongest-lord and combination precedence.
5. A documented mapping from commodity availability language to each modern
   instrument, especially FX pairs where supply and price direction are not a
   one-variable relationship.
6. Timestamp-safe prospective tests with rules frozen before outcomes are
   known.

Until all six gates pass, this remains an execution-locked historical research
layer.
