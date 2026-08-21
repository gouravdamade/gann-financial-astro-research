# CGVO-S1B Source Audit Report

> Historical note, 2026-08-22: this V1 report is preserved as the then-current
> no-witness state. `CGVO_S1B_R1_SOURCE_ACQUISITION_REPORT.md` supersedes only
> its Panchasiddhantika acquisition and Swiss-flag conclusions; it does not
> rewrite the historical V1 finding.

Status: `READY_FOR_CENTRAL_REVIEW_WITH_SOURCE_GAPS`

## Scope and Boundary

CGVO-S1B is a read-only source reconstruction audit. It does not alter the
selected `VARAHAMIHIRA_CHITRA_180_RECONSTRUCTION_V1` calculation, market
features, scoring, Fields, SBC, Auto Suggest, ML, MT5, or execution. The three
new Chitra coordinate variants are audit records only and are not selectable
runtime frames.

## Witnesses and Evidence Layers

The held working witness examined for the phase and firmament questions is
N. Chidambaram Iyer's *Brihat Samhita* (1884), SHA-256
`9E0E8B4DD7D611F22B29ED65B7ED635D806D831407B27695D8128EB804983E27`.
It is used as a translation working witness, not as an unqualified replacement
for the existing root-source registry.

The fixed-star calculation variants are modern Swiss Ephemeris coordinate
definitions. They document the computation performed by the audit; they do not
turn any modern star convention into Varahamihira doctrine.

No checksum-identified, usable Pancasiddhantika witness containing a Magha
numerical anchor was found in the held local source set. Therefore the Magha
candidate is recorded as `SOURCE_SILENT_NOT_CALCULATED`, and no Chitra/Magha
difference or average is produced.

## Absolute Frame Audit

The source ledger now names four mutually exclusive candidates:

| Candidate | Modern handling | Current result |
| --- | --- | --- |
| `CHITRA_180_APPARENT_STAR` | geocentric apparent ecliptic of date | audit calculation; identical to the existing selected reconstruction's offset method |
| `CHITRA_180_TRUE_STAR` | geocentric true ecliptic of date | audit calculation only |
| `CHITRA_180_MEAN_ECLIPTIC` | apparent position referred to mean ecliptic of date | audit calculation only |
| `PANCHASIDDHANTIKA_MAGHA_ANCHOR` | no calculation without a held numerical anchor | source silent; not calculated |

Each modern Chitra row records event epoch, precession, nutation, aberration,
and proper-motion treatment. The audit spans 500, 550, 600, 1000, 1500, 1900,
2000, and 2025 CE. It deliberately exposes differences instead of averaging
them. A material future anchor conflict must remain `MULTI_ANCHOR_CONFLICT`.

The existing selected runtime profile remains non-default and source
reconstruction only. No audit profile can silently replace it.

## Eclipse Phase Findings

### Solar

Brihat Samhita V.18, Iyer printed p.24 / PDF image 44, says that eclipse-disc
points and times at commencement and termination are calculated from parallax,
angles, and new-moon timing. It does **not** identify commencement or conclusion
with C1, C2, maximum, C3, or C4. Both fields are therefore `UNKNOWN`, and
effect/Jupiter-mitigation activation remains `null`.

### Lunar

The held V.18 passage also does not identify a lunar commencement/conclusion
with P1/P4, U1/U4, or a historical-shadow boundary. The lunar mapping remains
independently `UNKNOWN`; it is not copied from the solar contract. Maximum time
continues to be an audit snapshot only.

## Firmament Finding

The translated root sequence in V.28-31 (Iyer printed pp.26-27 / PDF images
46-47) identifies first, second, third, mid-heaven, fifth, sixth, rising, and
setting positions. It does not state numerical sector boundaries or a modern
coordinate convention. Iyer's p.26 footnote calls the first-six sequence the
six sections of the visible hemispherical vault; that is commentary evidence,
not a source-closed classifier. The legacy Sastri/Bhat seven-division reference
was not re-inspected at page level in this bounded audit. The result stays
`COMMENTARY_CONFLICT_NOT_SOURCE_CLOSED`, with `classicalSection=UNKNOWN` and
raw observer geometry only.

## Remaining Gaps

- A historical source that supplies an auditable Magha numerical anchor.
- A source-closed solar contact mapping.
- A source-closed lunar penumbral/umbral/historical-shadow mapping.
- Firmament coordinate and boundary semantics sufficient for a classifier.

## Invariants

`executionAllowed=false`. No price or outcome read, market polarity, score,
financial validation, Fields, SBC, Auto Suggest, ML, MT5, or execution path was
introduced.
