# CGVO-S1B Implementation Notes

The source audit is exposed from the existing read-only CGVO status contract as
`s1bSourceAudit`. `build_cgvo_s1b_source_audit()` provides the epoch table for
inspection without granting runtime selection of an audit candidate.

The existing Chitra-180 runtime function deliberately remains unchanged:
`swe.fixstar2_ut("Spica", jd, swe.FLG_SWIEPH)` minus 180 degrees. The audit
records use separate flag combinations solely to make the apparent, true, and
mean-ecliptic reconstruction assumptions inspectable.

Solar and lunar phase ledgers are chosen by eclipse type before source-adapter
output is constructed. They expose distinct label families and preserve all
activation values as `null` while the source mappings remain unresolved.
