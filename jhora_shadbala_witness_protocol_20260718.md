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

## Fail-Closed Rules

- no value without visual evidence;
- no evidence without a matching hash;
- no mixed settings inside one ledger;
- no unknown or duplicate fixture/planet/measure keys;
- no inferred values from PyJHora;
- no tolerance widening to hide a formula disagreement;
- no execution authorization from a research witness.
