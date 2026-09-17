# Candidate C AB1-R1 Ordinary Drsti Representation Adjudication

AB1 V1 remains an immutable `SYNTHETIC_SEMANTIC_MISMATCH` observation: it compared 8,320 rows per evaluator over 1,040 fixtures and preserved 81 `SOURCE_VALUE_MISMATCH` records.

The controlling `SARAVALI_4_32_ORDINARY_DRSTI_V1` rule in `classical_source_operator_ledger_s1r1_v1.json` stores relative place 7 as the literal `FULL`. Its locator is Saravali 4.32-33 Sanskrit root, printed p.58 / scan p.62.

Evaluator A at `e581c499d3a3872cd88d6d17bf92c39a5c95185b` reads that frozen rule and deterministically formats every stated ordinary-Drsti value as `DRSTI_` plus `fraction.replace('/', '_')`: `1/4` becomes `DRSTI_1_4`, `1/2` becomes `DRSTI_1_2`, `3/4` becomes `DRSTI_3_4`, and `FULL` becomes `DRSTI_FULL`. Evaluator B at `267885b84e1d796b438b09d73f3fb9792235a41e` returns the literal ledger value, including `FULL`.

Comparator V1 already converted the three numeric A aliases to the ledger-fraction form, but its precise two-part numeric rule omitted `DRSTI_FULL`. The AB1 result contains exactly 81 mismatches: the 9 source bodies times 9 target bodies in the relationship-position matrix at relative place 7, all with A `DRSTI_FULL` and B `FULL`; there are no other mismatch classes or underlying ordinary-Drsti geometry differences.

Root cause: `REPRESENTATION_CANONICALIZATION_GAP`.

This record is committed before a successor projection is allowed. It does not modify A, B, or AB1 V1 artifacts; it does not authorize a real Candidate C run, market/outcome access, polarity, magnitude, scoring, or execution.
