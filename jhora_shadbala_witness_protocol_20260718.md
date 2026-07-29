# Jagannatha Hora Shadbala Witness Protocol

Contract: `GANN_JHORA_SHADBALA_WITNESS_V1`

## Purpose

Jagannatha Hora is an independent interactive witness. It does not replace the
pinned PyJHora component comparator, and its output is not accepted without a
saved settings record and hashed visual evidence.

## Pinned Installation

- Official source: `https://vedicastrologer.org/jh/index.htm`
- Product: Jagannatha Hora 8.0
- Install root:
  `D:\GannFinancialAstro\external_validators\jagannatha_hora_8_0\app`
- Download SHA-256:
  `10A291F8F69FBB9AB8C4EC88F8D804FD227FB23E0F4375706C30BA0043B72339`
- Executable SHA-256:
  `3DDBE5FB0458AD1F0AD91B002C7EFB8BBA9F08891D3F46190ABA97D570B17908`

The official installer is unsigned. The hash above identifies the exact
download used; it is not a statement that the executable has a digital
signature.

## Locked Settings

- Drik Siddhanta
- Raman ayanamsa
- geocentric, apparent planetary positions
- true node
- Sripathi/Porphyry house system
- ascendant at the middle of the first house
- apparent rise of tip
- day boundary at sunrise
- Parasara special aspects
- compound relationships from the relevant divisional chart
- default Parasara Hora and Drekkana variants

Any sensitivity run must use a different profile identifier. Do not overwrite
this witness with Raman-special-aspect, 06:00 LMT, mean-node, topocentric, or
alternative divisional-chart settings.

## Capture Procedure

For each of the five fixtures in
`jhora_shadbala_witness_template_20260718.csv`:

1. Enter the exact civil date, civil time, timezone, latitude, longitude, and
   location from the row.
2. display current preference settings and save a screenshot;
3. open the full Shadbala component table;
4. save one uncropped screenshot containing the chart identity and table;
5. enter Sthana, Kaala, Dig, Chesta, Naisargika, Drik, and total values for all
   seven classical planets;
6. record the screenshot path, SHA-256, reviewer, and UTC capture time;
7. run `jhora_witness_protocol.py --validate <completed.csv>`.

The independent Drik gate can consume the 35 Drik rows after the completed
ledger validates. Full Shadbala remains diagnostic until all component
differences have an explicit doctrine/profile decision.

## Locked Capture Result

The five-fixture capture was completed on 2026-07-26 and assembled into:

- `status/evidence/jhora_shadbala_20260723/`
  `jhora_shadbala_witness_completed_20260726.csv`
- ledger SHA-256:
  `3DFF36A1415881522F152F690C3856C3F736BEE60ED202F7F5EDD100C055DF42`
- matrix validation: 245 of 245 required rows present, uniquely keyed, numeric,
  and linked to matching hashed visual evidence;
- rounded component consistency: maximum 0.01 virupa residual;
- rounded Rupa-to-Virupa consistency: maximum 0.29 virupa residual.

JHora displays a Chesta value for the Sun and Moon in the breakup table but
does not include those two displayed values in its reported Shadbala totals.
The assembler preserves the displayed values as evidence and explicitly
excludes only Sun/Moon Chesta when checking JHora's own reported total. It does
not silently alter any captured value.

The fixed 0.5-virupa comparison below is the separately named pinned
PyJHora-compatible diagnostic profile. It is not the BPHS-labeled production
source profile and must not be substituted into the production total:

| Measure | Pass | Fail |
| --- | ---: | ---: |
| Sthana | 33 | 2 |
| Kaala | 0 | 35 |
| Dig | 19 | 16 |
| Chesta | 12 | 23 |
| Naisargika | 35 | 0 |
| Drik | 9 | 26 |
| Total | 0 | 35 |
| **All rows** | **108** | **137** |

Therefore the independent witness is complete, but it does not certify the
current PyJHora/local doctrine profile. Drik is
`failed_independent_validation`, not pending. Formula/profile reconciliation
must explain the differences before certification; the tolerance remains
frozen.

The top-level JHora table does not identify which Sthana subcomponent causes a
residual. Any Sthana formula change now requires the separate visible-capture
contract in `jhora_sthana_subcomponent_witness_protocol_20260729.md`.

## Fail-Closed Rules

- no value without visual evidence;
- no evidence without a matching hash;
- no mixed settings inside one ledger;
- no unknown or duplicate fixture/planet/measure keys;
- no inferred values from PyJHora;
- no tolerance widening to hide a formula disagreement;
- no execution authorization from a research witness.
