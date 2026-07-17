# Sanskrit Letter Fixture Audit

Date: 2026-07-17 IST

## Evidence Boundary

Executable evidence is limited to two locally held, checksummed page witnesses:

- `PHALADEEPIKA_1937_SBC_EDITOR_SUPPLEMENT`, PDF pages 347-348, printed
  pages 310-311;
- `SANJAY_RATH_CRUX_1998_SBC_FIGURE`, PDF page 21, printed page 10,
  Figure 1.2.

The 1937 text supplies sequence and construction language. Rath supplies the
profile's figure-relative row/column frame. The 1937 plate is transformed with
the existing `ROTATE_CCW_90` comparison rule. Neither witness resolves absolute
cardinal orientation in the chosen profile frame.

## Certified Vowels

The 16 ASCII identity tokens, in source construction order, are:

```text
A AA I II U UU VOCALIC_R LONG_VOCALIC_R VOCALIC_L LONG_VOCALIC_L
E AI O AU ANUSVARA VISARGA
```

They correspond to:

```text
अ आ इ ई उ ऊ ऋ ॠ ऌ ॡ ए ऐ ओ औ अं अः
```

The profile stores them at the four corners of four nested squares, beginning
at `(1,1)` in the Rath figure-relative frame.

## Certified Name Initials

The 20 identity tokens, in source side order, are:

```text
A VA KA HA DDA | MA TTA PA RA TA | NA YA BHA JA KHA | GA SA DA CHA LA
```

They correspond to:

```text
अ व क ह ड | म ट प र त | न य भ ज ख | ग स द च ल
```

The first entry is a vowel even though the prose describes the ring using a
consonant label. The executable layer is therefore `NAME_INITIAL`, not
`CONSONANT`, and the exception is machine-visible.

## Validation Result

- 36 exact letter entries
- two page citations on every entry
- no duplicate values within either layer
- no missing transcription or semantic fields
- no cardinal-direction claim
- no Vedha, Latta, scoring, financial label, or trade output
