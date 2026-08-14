# Agarwal Scan Acquisition Audit

Audit date: 2026-07-22

## Scope

This audit compares three user-provided private research PDFs of M. K. Agarwal's
`Mystics of Sarvato Bhadra Chakra and Astrological Predictions`. It establishes
file identity, completeness, provenance, and the permitted evidence role. It
does not certify doctrine or authorize redistribution.

## Files

| Candidate | PDF pages | Size | SHA-256 | Evidence role |
| --- | ---: | ---: | --- | --- |
| Image scan | 191 | 3,603,273 bytes | `5644DFC44DEC730A26111CA2EEA9C2A005A4291555B71A6A32F0B7B7BCF26050` | Incomplete primary page-image candidate |
| ChiStaBo edited version, January 2012 | 94 | 1,476,522 bytes | `8AF0045A44BBFF8F81F470F996D7949887BEC1A63C1641586EFC579EED4ED6CA` | Earlier derivative search and comparison aid only |
| ChiStaBo edited version v3 | 95 | 4,410,319 bytes | `D93B9B97D2B8C902168FE83C1E6796FE22AD644C55903BA85154D1C6D610E38D` | Derivative search and comparison aid only |

The private files are stored outside Git under
`D:/GannFinancialAstro/sources/private/`, using hash-suffixed filenames recorded
in the machine-readable source register.

## Provenance Finding

The files are not independent copies. Both ChiStaBo PDFs are Word-generated
edited derivatives of the Internet scan. The January 2012 file identifies its
editor and date in the page header and contains explicit missing-page
placeholders. The 2013 foreword additionally discloses changed planet names
and abbreviations, replicated or redrawn pictures, and editor additions in
square brackets. Their reflow and full text layers are derivative
transcriptions, not separately scanned editions.

The image scan preserves the original typography, pagination, tables, and page
images. Its metadata records OmniPage and Adobe paper-capture processing, but
the scan itself contains no extractable ISBN, copyright, publisher, or edition
statement. The presumed publication year and edition therefore remain
unverified from these files.

## Completeness Finding

The image scan reaches printed page 194 but is not complete. Page-header and
chapter-boundary inspection establishes these omissions:

| Neighboring evidence in image scan | Missing printed pages |
| --- | --- |
| PDF page 50 is printed page 45; PDF page 51 starts Chapter 6 at printed page 48 | 46-47 |
| PDF page 56 is printed page 53; PDF page 57 is printed page 56 | 54-55 |
| PDF page 62 is printed page 61; PDF page 63 starts Chapter 9 at printed page 64 | 62-63 |
| PDF page 131 starts Chapter 16 at printed page 132; PDF page 132 starts Chapter 17 at printed page 134 | 133 |
| PDF page 141 is printed page 143; PDF page 142 starts Chapter 18 at printed page 145 | 144 |

The ChiStaBo derivatives explicitly acknowledge missing pages 54-55 and two
pages after its Shadbala summary, corresponding to printed pages 62-63. It also
flags smaller missing-text uncertainties. It does not supply an independent
image witness for any omitted source page and must not be used to reconstruct
those gaps as if they were Agarwal's verified words.

OCR is incomplete in the image scan: 51 PDF pages have little or no extractable
text. Visual inspection of page images is therefore mandatory for every future
citation.

## Decision

1. Keep both PDFs private and outside Git.
2. Use the image scan only to nominate visible passages for page-level visual
   certification.
3. Use the ChiStaBo derivative only for search, navigation, and comparison.
4. Never treat editor-added bracketed text, changed terminology, or redrawn
   figures as an independent doctrinal witness.
5. Do not enable an executable Agarwal profile from either file as a whole.
6. Acquire an imprint-bearing complete edition or an independent complete scan
   before certifying the missing pages, edition identity, or complete method.

## Bounded Financial-Chapter Retrieval

PDF pages 177-191 of the image scan are consecutive printed pages 180-194,
Chapter 20, `Astrological Norms for Financial Gain in Share Market`. A contact
sheet and representative full-resolution renders were manually inspected on
2026-07-22; all fifteen page images are present and readable.

That intact sequence may be extracted privately with PDF and printed-page
markers and exposed to the local LLM only as an opt-in
`hypothesis_reference`. It remains modern practitioner commentary from an
edition-unidentified, incomplete scan. Its bullish/bearish combinations are
not classical doctrine, not certified financial rules, and cannot be consumed
by deterministic SBC scoring, Auto Suggest, live inference, prospective
validation, official ML notes, or execution. Their proper use is to nominate
explicit hypotheses for later timestamp-safe testing.

This boundary does not prevent later use of a visible, intact page. Such a page
still requires the repository's normal edition, page-range, content-layer,
quotation, and manual visual-certification gates before it can support a
derived fixture or executable rule.

## 2026-08-14 Closure Addendum - Superseding Acquisition Evidence

This July audit remains historically correct for the three files then held: the
old image-scan file is still incomplete, and the ChiStaBo derivatives are still
non-independent edited search aids. On 2026-08-13, founder-supplied front matter
and private photographs of a physical Sagar Publications, New Delhi, `First
Edition 2000` copy established the book identity and recovered the eight
previously absent printed pages. See
`docs/sbc/AGARWAL_HARDCOPY_GAP_CLOSURE_20260813.md` and
`configs/sbc/agarwal_hardcopy_20260813.yaml`.

The later evidence closes the project acquisition gap, not the old scan's file
identity and not any individual executable-rule gate. A1 source reconciliation
records the two facts separately: a composite source map may cite the hardcopy
as controlling evidence, but literal transcription remains blocked until its
checksum-identified private capture files are locally materialized.
