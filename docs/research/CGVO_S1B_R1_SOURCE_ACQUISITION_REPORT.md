# CGVO-S1B-R1 Source Acquisition and Absolute-Frame Audit Correction

## Scope

This is a read-only correction to the S1B source audit. It does not alter
`VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_V1`, select an audit profile at
runtime, or connect any CGVO source record to price, polarity, Fields, SBC,
Auto Suggest, ML, MT5, or execution.

## Witness Acquisition

The initially downloaded RBSI copy was rejected as incomplete: it contains 29
PDF images. The accepted working witness is the 330-image public-domain copy
downloaded from Wilbour Hall on 2026-08-22.

| Field | Value |
| --- | --- |
| Local source ID | `PANCHASIDDHANTIKA_THIBAUT_DVIVEDI_1889_WILBOURHALL` |
| Work | *The Panchasiddhantika: The Astronomical Work of Varaha Mihira* |
| Editors | G. Thibaut and Mahamahopadhyaya Sudhakara Dvivedi |
| Edition | 1889, E. J. Lazarus and Co., Medical Hall Press, Benares |
| Acquisition URL | `https://www.wilbourhall.org/pdfs/pancha_dli.pdf` |
| PDF images | 330 |
| SHA-256 | `626E14CA14F16D6A2ECE0D51E0F7063052C376715D63CA64737C734F2EB0EF8A` |
| Storage | private local source store; bytes are neither tracked nor packaged |

## Fixed-Star Table

The introduction's comparison table, printed page XL / PDF image 38,
transcribes both `MAGHA` and `CHITRA`. It calls the relevant fields polar
longitude and polar latitude:

| Record | Position in nakshatra | Polar longitude | Polar latitude |
| --- | ---: | ---: | --- |
| Magha | 6 degrees | 126 degrees | zero |
| Chitra | 7 degrees 30 minutes | 180 degrees 50 minutes | 2 degrees 43 minutes S |

The table's raw Chitra-minus-Magha polar-longitude difference is 3,290 arc
minutes (54 degrees 50 minutes). This is a literal historical-table
difference only. It is not a modern ecliptic offset, a current-epoch
calculation, a zero-Mesha value, or an averaged anchor.

The next printed page (XLI / PDF image 39) says that the text does not define
how these longitudes and latitudes are measured, and presents the editorial
interpretation only as a presumption. The ledger consequently records a
source-acquired Magha table value but leaves its transformation to a modern
coordinate convention unresolved. No modern star identity is assigned to
Magha by this source ledger.

## Swiss Ephemeris Audit Profiles

The V1 record incorrectly represented `TRUEPOS` as suppressing nutation. The
official Swiss Ephemeris programming documentation defines `TRUEPOS` as true
geometric position without light-time; `NONUT`, `NOABERR`, and `NOGDEFL` have
their own distinct meanings. In this installed `pyswisseph 2.10.03`, the
returned flag word for `SWIEPH | TRUEPOS` also contains `NOABERR | NOGDEFL`,
but not `NONUT`.

| Profile | Requested flags | Coordinate description | Nutation |
| --- | --- | --- | --- |
| `CHITRA_180_APPARENT_TRUE_EQUINOX` | `SWIEPH` | apparent geocentric ecliptic, true equinox of date | included |
| `CHITRA_180_APPARENT_MEAN_EQUINOX` | `SWIEPH | NONUT` | apparent geocentric ecliptic, mean equinox of date | excluded |
| `CHITRA_180_TRUE_GEOMETRIC_TRUE_EQUINOX` | `SWIEPH | TRUEPOS` | true geometric geocentric ecliptic, true equinox of date | included |
| `CHITRA_180_TRUE_NOABERR_NODEFL` | `SWIEPH | TRUEPOS | NOABERR | NOGDEFL` | true geometric geocentric ecliptic, true equinox of date | included |
| `CHITRA_180_TRUE_NOABERR_NODEFL_MEAN_EQUINOX` | previous plus `NONUT` | true geometric geocentric ecliptic, mean equinox of date | excluded |

Each candidate is audit-only. The service reports requested and returned flags
for every sampled epoch. The existing apparent-Spica reconstruction is
unchanged and remains non-default.

## Eclipse and Firmament Recheck

The acquired witness establishes that the work contains distinct eclipse
calculation chapters, but it does not close a mapping from the product's
modern C1/C4 solar or P1/U4 lunar labels to a historical activation phase.
The separate solar and lunar V1 phase fixtures therefore remain unchanged and
unknown. The firmament V2 adjudication is likewise unchanged:
`COMMENTARY_CONFLICT_NOT_SOURCE_CLOSED`.

## Active Safety State

`sourceCertifiedAyanamsha=false`; no audit profile is runtime-selectable;
Chitra and Magha are never averaged; price/outcome reads, market direction,
score aggregation, execution, Fields, SBC, Auto Suggest, ML, and MT5 paths
remain disabled.
