# Native Windows observational evidence

**Accept NATIVE_NUMERICAL_RESTART_REPRODUCED for the exact selected sample.** Direct comparison of run1-comparison.json and run2-comparison.json found identical selection, displayed values and reference receipt objects. Four native screenshots accompany those files. All six matched the recorded SHA-256 checksums. Each selection says EXACT COMPUTED SAMPLE at Unix 1748710800 with a zero-second offset. The comparison files record the same ten displayed transit longitudes at ten decimals. The observations establish the displayed precision.

| Display | Before restart | After restart |
|---|---:|---:|
| USD projection | 0.22132100 | 0.22132100 |
| JPY projection | 0.12471328 | 0.12471328 |
| Difference | 0.09660772 | 0.09660772 |
| R1 | 0.573789856612 | 0.573789856612 |
| R2 | 0.069145287935 | 0.069145287935 |

The manifest identifies distinct sidecar sessions 85b4e242d6d048188ea81300ed18cccb and 801e90aa4bee4aaa860b66a9a9c341c3. The first used the existing WebView2 profile, the second an isolated one. The manifest reports successful phase requests in the second session. Numerical mean longitude is in the supporting receipt; the UI provides no separate numeric mean-longitude card.

**Source identity.** The debug executable is recorded as 0.10.68, SHA-256 C09173820DDB16CC5DB52DEDA63A7AFE735D0A0DE9D960B7E8D8E3C96BDF370E. The URL's 0.10.61 query is a stale cache-buster. It is unreliable for attribution. The binary fingerprint, local Vite origin, candidate tree and recorded comparison of 12 source files establish a narrower identification. I separately compared the candidate copies of the phase builder, financial ephemeris, CGVO service, assessment and frontend validator with the inspected tree. All five matched byte-for-byte. The dirty worktree makes the Git HEAD alone insufficient.

The evidence supports the displayed PROVENANCE_INCOMPLETE and RECEIPTS_CONSISTENT_SWISS_FILE combination. NATIVE_PROVENANCE_INTEGRITY_VERIFIED remains open. Retain the two existing runs as the restart witness. Only if claiming a newly implemented positive native status, capture one exact sample showing the new status and its matching backend assessment. An additional pair of numerical restart runs is unnecessary for this decision.

Evidence directory: D:/GannFinancialAstro/qa/r7b-native-observational-20261120/evidence. Use evidence-manifest.json and both run comparison files with their four named screenshots. This later observation supersedes the pending numerical restart entry in R2B-R2.

