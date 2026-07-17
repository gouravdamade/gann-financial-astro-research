# Sarvatobhadra Research Foundation

This package is an isolated, source-profiled research foundation. Phase 1
calculates astronomy, nakshatra membership, and Panchanga facts. Phase 2 adds
one explicit-only, figure-relative 81-cell topology and Sanskrit-letter
fixture. Phase 3A adds standard figure-relative Vedha rays and a transparent
research guidance ledger. It does not emit a market opinion or trade decision.

Primary profile: `sbc_raman_foundation_v1`.

Comparison profile: `sbc_lahiri_comparison_v1`. This profile exists only to
measure sensitivity to ayanamsha and must not replace Raman silently.

Phase 2 research profiles:

- `sbc_81_rotation_normalized_partial_v1`: compiles nakshatra, rashi, tithi,
  weekday, 16-vowel, and 20-name-initial layers. It is incomplete and has no
  absolute cardinal binding. The machine layer is `NAME_INITIAL`, not
  `CONSONANT`, because the source sequence begins with vowel `अ` (`A`).
- `sbc_64_blocked_v1`: metadata only; compilation fails closed.

Phase 3A research profile:

- `phaladeepika_editor_vedha_guidance_v1`: derives left, front, and right
  targets from the 81-cell board, validates the geometry against the printed
  Krittika, Rohini, and Mrigashira examples, and scores only context values
  actually struck by the selected ray.

The guidance score is deliberately simple and visible:

- each matched target layer contributes one experimental evidence unit;
- a resolved benefic makes the unit positive and a resolved malefic negative;
- source multipliers are `2x` retrograde, `3x` exalted, and `0.5x`
  debilitated;
- conditional Mercury/Moon nature and ambiguous multiplier combinations are
  reported as unresolved and excluded from the net;
- normalized guidance is `net / (favorable + absolute adverse)`, bounded from
  `-1` to `+1`.

This normalization is an engineering comparison aid, not a classical
numerical score and not a financially validated signal.

Minimal use:

```python
from sbc import MotionClass, VedhaActor, VedhaGuidanceEngine

engine = VedhaGuidanceEngine("phaladeepika_editor_vedha_guidance_v1")
report = engine.evaluate(
    (
        VedhaActor("JUPITER", "KRITTIKA", MotionClass.MEAN),
        VedhaActor("SATURN", "KRITTIKA", MotionClass.RETROGRADE),
    ),
    {"NAKSHATRA": {"SHRAVANA", "BHARANI"}},
)
```

Locked until later certification:

- default choice between 64-cell and 81-cell forms
- absolute cardinal orientation
- Abhijit insertion interval
- automatic direct-versus-swift speed classification
- special corner/junction Vedha rules, association inference, and Latta
- classical natal-severity translation
- financial scoring or directional market labels
- Auto Suggest and MT5 execution
- main chart integration

The first user-facing surface will be a read-only Chakra Lab. It will use
native Tauri IPC rather than a localhost REST service. Phase 3A is a tested
Python research backend and is not yet wired into the packaged app.
