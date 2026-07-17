# Sarvatobhadra Research Foundation

This package is an isolated, source-profiled research foundation. Phase 1
calculates astronomy, nakshatra membership, and Panchanga facts. Phase 2 adds
one explicit-only, figure-relative 81-cell topology and Sanskrit-letter
fixture. It does not emit a market opinion or trade decision.

Primary profile: `sbc_raman_foundation_v1`.

Comparison profile: `sbc_lahiri_comparison_v1`. This profile exists only to
measure sensitivity to ayanamsha and must not replace Raman silently.

Phase 2 research profiles:

- `sbc_81_rotation_normalized_partial_v1`: compiles nakshatra, rashi, tithi,
  weekday, 16-vowel, and 20-name-initial layers. It is incomplete and has no
  absolute cardinal binding. The machine layer is `NAME_INITIAL`, not
  `CONSONANT`, because the source sequence begins with vowel `अ` (`A`).
- `sbc_64_blocked_v1`: metadata only; compilation fails closed.

Locked until later certification:

- default choice between 64-cell and 81-cell forms
- absolute cardinal orientation
- Abhijit insertion interval
- Vedha and Latta mappings
- directional or financial scoring
- Auto Suggest and MT5 execution
- main chart integration

The first user-facing surface, after the remaining source questions are
resolved, will be a read-only Chakra Lab. It will use native Tauri IPC rather
than a localhost REST service. Phase 2 is not wired into the packaged app.
