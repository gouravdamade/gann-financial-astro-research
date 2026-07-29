# Shadbala Doctrine Corrections

Date: 2026-07-18

Status: research-source milestone; execution remains locked.

## 2026-07-29 Visible Sthana Witness Addendum

- Captured and hash-pinned all five visible Sthana subcomponents for five
  fixtures and seven classical planets: `175/175` rows under
  `GANN_JHORA_STHANA_SUBCOMPONENT_WITNESS_V1`.
- Every five-component sum reconciles to the locked top-level JHora Sthana
  value within the unchanged `0.5`-virupa tolerance.
- Uchcha, Ojayugma, Kendradi, and Drekkana match `35/35` under the production
  implementation.
- The BPHS-labeled source Saptavargaja profile matches `3/35`; complete source
  Sthana remains `1/35`. This is a doctrine-profile difference, not a reason to
  widen tolerance.
- The PyJHora-style profile matches `34/35`. Its one miss treats case-8 Saturn
  at about 28.7 degrees Aquarius as Moolatrikona.
- Added named diagnostic profile `jhora_8_visible_compatibility`, which uses
  the observed JHora relationship weights while retaining degree-bounded D1
  Moolatrikona. It matches every Saptavargaja and complete Sthana row `35/35`.
- The new profile is diagnostic only. Production remains on the cited source
  profile; source certification, financial validation, ML admission, and
  execution remain false.
- Evidence:
  `jhora_sthana_reconciliation_20260729.md` and
  `status/evidence/jhora_sthana_subcomponents_20260729/`.

## 2026-07-27 Visible Kaala Witness Addendum

- Captured and hash-pinned all ten visible Kaala columns for five fixtures and
  seven classical planets: `350/350` rows under
  `GANN_JHORA_KAALA_WITNESS_COMPARATOR_V1`.
- Promoted only dynamic Paksha nature under
  `STRICT_SHADBALA_V9_DYNAMIC_PAKSHA_JHORA_WITNESS_PROVISIONAL`. Moon nature
  follows the phase window; Mercury becomes malefic when it shares a whole
  sign with a malefic. The result passes `35/35` visible JHora Paksha rows with
  `0.003` virupa mean and `0.004` virupa maximum residual after exact-time
  recapture.
- Abda, Masa, Vara, Tribhaga, and Yuddha each pass `35/35` and are retained.
  This original checkpoint recorded Hora at `33/35`. It is superseded by the
  exact-time 2026-07-29 recapture: JHD time is packed `HH.MMSS`, and the
  corrected `19:30` case-8 witness gives Moon `60`, Saturn `0`. Hora now matches
  `35/35`; the hashed LMT packet visibly binds sunrise `6:22:22`, Moon lord,
  and all seven awards. This is narrow component evidence, not aggregate Kaala
  or full Shadbala certification.
- Nathonnatha, Ayana, and aggregate Kaala pass `11/35`, `13/35`, and `5/35`
  visible rows respectively and remain provisional.
- The corrected top-level Kaala mean absolute residual is now `2.763` virupa
  with `5/35` strict passes. Full-total mean absolute residual improves to
  `11.829` virupa, but full Shadbala still passes only `3/35`; certification and
  execution remain locked.
- JHora total arithmetic independently confirms Sun/Moon Chesta exclusion in
  all `10/10` luminary rows with at most `0.01` virupa display-rounding
  residual. Their displayed Chesta values remain provisional evidence rather
  than certified numeric features.
- Evidence: `jhora_kaala_reconciliation_20260727.md` and
  `status/evidence/jhora_kaala_witness_20260727/`.
## 2026-07-26 Independent Witness Addendum

- The locked Jagannatha Hora 8.0 witness is complete and internally valid:
  five fixtures, seven classical planets, six components plus total, and
  `245/245` required rows.
- Jagannatha Hora displays Sun and Moon Chesta in the breakup table but excludes
  both values from its reported Shadbala totals. The uploaded Shadbala source
  also says their motion strength is already represented by Ayana/Paksha and
  should not be added again
  (`pdf_alignment_extracts/jyotish_best-way-to-use-shad-bala_k-jaya-sekhar.txt`,
  printed pages 81-82).
- `STRICT_SHADBALA_V8_LUMINARY_CHESTA_TOTAL_EXCLUSION_PROVISIONAL` therefore
  preserves those two values for inspection but gives them zero total
  contribution. This is a doctrine correction, not a tolerance adjustment.
- The corrected local full-total mean absolute residual against locked JHora
  falls from about `33.873` to `17.416` virupa. It still passes `0/35` rows at
  the frozen `0.5`-virupa tolerance, so full Shadbala remains uncertified and
  excluded from execution.
- Local Kaala is closer to locked JHora than PyJHora in all `35/35` rows
  (`7.983` virupa mean absolute residual), but only `4/35` pass strictly.
  A visible JHora Kaala subcomponent breakup is required before changing
  Abda, Masa, Hora, or categorical lord awards.
- Reconciliation evidence:
  `jhora_doctrine_reconciliation_20260726.md` and
  `status/evidence/jhora_shadbala_20260723/jhora_doctrine_reconciliation_20260726.json`.

## Source Lock

- Primary chapter text:
  `https://enjoylearningsanskrit.com/scriptures/parashara/chapter-27/`
- Santhanam BPHS scan:
  `https://vedic-astro.s3.amazonaws.com/books/bhrihat_parasara_hora_shastra.pdf`
- Secondary automated comparator: hash-pinned PyJHora 4.8.7.
- Independent witness: locked Jagannatha Hora 8.0 worksheet completed on
  2026-07-26 under `GANN_JHORA_SHADBALA_WITNESS_V1`.

The classical source profile is the production research profile. PyJHora
compatibility values are named diagnostics and cannot silently replace it.

## Corrected Components

### Sthana Bala

- Saptavargaja no longer awards exaltation/debilitation a second time; Uchcha
  Bala already owns that measurement.
- The source profile uses 45/30/20/15/10/4/2 virupa for Moolatrikona, own,
  great friend, friend, neutral, enemy, and great enemy.
- D1 Moolatrikona is degree-bounded. Other Vargas do not receive a
  Moolatrikona award.
- A separate PyJHora 4.8.7 compatibility profile retains its alternate
  45/30/22.5/15/7.5/3.75/1.875 table for diagnostic comparison only.
- Drekkana order is masculine first third, neuter middle third, feminine final
  third.

### Kaala Bala

- Jupiter receives permanent 60 virupa Tribhaga strength in addition to the
  current segment lord. This was already present in the implementation and is
  now locked by an explicit regression test.
- Tribhaga uses Swiss Ephemeris apparent sunrise/sunset at the configured
  longitude and latitude. A visible 06:00/18:00 fallback remains only when
  coordinates or a solar event are unavailable.
- Abda, Masa, and Dina lords use the published 1860-01-01 Ahargana anchor
  714404108573 and a sunrise day boundary.
- Hora uses one-hour local-mean-time periods from sunrise and the Chaldean
  sequence beginning with the Ahargana Dina lord.
- Seven-factor and conventional nine-factor totals are emitted under separate
  profile names.
- Ayana uses 23 degrees 27 minutes obliquity and the source north/south
  declination rules; Sun is doubled.
- A detected Graha Yuddha candidate now returns unknown and makes the
  nine-factor total incomplete. It no longer contributes a fabricated zero.

### Chesta Bala

- Speed-state buckets are no longer used as the base Chesta value.
- Sun Chesta equals Ayana and Moon Chesta equals doubled Paksha for visible
  breakup evidence, but both contribute zero to the implemented total because
  Ayana/Paksha already owns that strength.
- Mars through Saturn use the source-structured separation between seegrocha
  and the midpoint of mean and true longitude. The current deterministic model
  obtains osculating mean longitudes from Swiss Ephemeris and remains
  provisional pending a visible JHora witness.
- Motion-state strength remains available as a separately labeled diagnostic.
  Alternate doubled and motion-added values are also retained as research
  diagnostics, not production totals.

### Dig And Minimum Totals

- Local Dig already used the bounded circular-distance formula. The PyJHora
  export now selects its canonical `_dig_bala(method=2)` variant because its
  default method can exceed the classical 0-60 range.
- The Sun minimum total is corrected from 300 to 390 virupa. The complete
  minimum sequence is Sun 390, Moon 360, Mars 300, Mercury 420, Jupiter 390,
  Venus 330, and Saturn 300.

## Comparator Result

The comparator now reports three separate matrices at 0.5 virupa tolerance.
This prevents source-profile disagreements from being mistaken for formula
implementation defects.

The end-to-end six-component matrix has 145 pass, 55 fail, and 10 structural
N/A rows:

| Component | Comparable | Pass | Fail | Structural N/A |
| --- | ---: | ---: | ---: | ---: |
| Sthana | 35 | 34 | 1 | 0 |
| Kaala | 35 | 0 | 35 | 0 |
| Dig | 35 | 35 | 0 | 0 |
| Chesta | 25 | 6 | 19 | 10 |
| Naisargika | 35 | 35 | 0 | 0 |
| Drik | 35 | 35 | 0 | 0 |

Sun and Moon Chesta are structural N/A rows, not numeric failures. The source
profile uses Sun Chesta = Ayana and Moon Chesta = Paksha, while PyJHora's
epoch-table Chesta vector returns zero for both.

The 350-row Kaala decomposition localizes the disagreement:

| Kaala measure | Pass | Fail |
| --- | ---: | ---: |
| Abda | 35 | 0 |
| Masa | 35 | 0 |
| Vara | 35 | 0 |
| Tribhaga | 31 | 4 |
| Yuddha | 31 | 4 |
| Hora | 25 | 10 |
| Ayana | 13 | 22 |
| Paksha | 6 | 29 |
| Nathonnatha | 5 | 30 |
| Total | 0 | 35 |

Most importantly, the shared-input matrix passes all 60 comparable rows:
Sthana passes 35/35 and Mars-Saturn epoch-table Chesta compatibility passes
25/25. This proves that the compatibility formulas are implemented correctly
when ephemeris inputs are held constant. It does not prove that PyJHora's
formula variant is the correct classical doctrine.

The sole Sthana failure is a retained divisional-boundary witness. At the 1889
Tokyo fixture, Swiss Ephemeris places Jupiter at 249.992006 degrees and
PyJHora at 250.002277 degrees. The 0.010271-degree difference crosses an exact
Varga boundary and changes D3, D9, D12, and D30.

Kaala and end-to-end Chesta failures do not authorize copying PyJHora
behavior. The residuals now identify time-basis, Paksha classification,
Ayana, Hora-indexing, mean-longitude, and Yuddha-policy differences instead of
hiding them inside one total. These rows remain diagnostic until a visible
Jagannatha Hora or worked-example witness is saved.

## Remaining Certification Gates

1. Reconcile the case-8 Hora sunrise boundary and the remaining Nathonnatha
   and Ayana formula/time-basis residuals without widening tolerance.
2. Cross-check the Swiss osculating mean-longitude Chesta model for
   non-luminaries against visible JHora subcomponent values.
3. Resolve the remaining Sthana and Dig profile differences without copying a
   comparator implementation blindly.
4. Reconcile Drik nature and special-aspect policy with the independent
   contribution evidence.
5. Resolve Graha Yuddha with a source-verified apparent-disc method.
6. Add Ishta/Kashta Phala only after its own source and witness gate.
7. Keep all corrected Bala features research-only until purged prospective
   validation passes.
