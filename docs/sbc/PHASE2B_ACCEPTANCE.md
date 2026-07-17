# Phase 2B Acceptance Gates

Phase 2B is accepted only when all of the following pass:

1. Vowel gate: all 16 source vowels occur exactly once at the nested-corner
   coordinates, with exact Devanagari glyphs and ASCII transliterations.
2. Name-initial gate: all 20 source name-initial entries occur exactly once in
   source order and figure-relative position.
3. Semantic-exception gate: the initial `अ` is not misclassified as a
   consonant; it carries `VOWEL_EXCEPTION_IN_NAME_INITIAL_RING`.
4. Citation gate: each of the 36 letter entries resolves to both held page
   witnesses and the recorded rotation transform.
5. Schema gate: missing glyph, transliteration, or semantic role fails closed;
   structural layers reject letter-only fields.
6. Regression gate: Phase 2A structural positions remain unchanged.
7. Incompleteness gate: cardinal orientation remains the only unresolved layer,
   so `complete=false`.
8. 64-cell gate: the metadata profile loads, but compilation still fails
   closed because no acquired page-certified mapping exists.
9. Isolation gate: no Vedha, Latta, market opinion, Auto Suggest, order, or
   execution payload is emitted.

Passing these gates certifies a page transcription fixture only. It does not
certify absolute orientation, a universal grid form, interpretation, financial
utility, or live execution.
