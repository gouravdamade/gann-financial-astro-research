# Shadbala Doctrine Corrections

Date: 2026-07-18

Status: research-source milestone; execution remains locked.

## Source Lock

- Primary chapter text:
  `https://enjoylearningsanskrit.com/scriptures/parashara/chapter-27/`
- Santhanam BPHS scan:
  `https://vedic-astro.s3.amazonaws.com/books/bhrihat_parasara_hora_shastra.pdf`
- Secondary automated comparator: hash-pinned PyJHora 4.8.7.
- Independent witness: installed Jagannatha Hora 8 worksheet remains pending.

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
- Sun Chesta equals Ayana; Moon Chesta equals doubled Paksha.
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

1. Capture the installed Jagannatha Hora 8 component worksheet with screenshots
   and reviewer metadata.
2. Cross-check the Swiss osculating mean-longitude Chesta model against those
   visible values.
3. Resolve Graha Yuddha with a source-verified apparent-disc method.
4. Add Ishta/Kashta Phala only after its own source and witness gate.
5. Keep all corrected Bala features research-only until purged prospective
   validation passes.
