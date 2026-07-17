# SBC Repository Audit

Date: 2026-07-17

## Reused Contracts

- `doctrine_config.py` locks the main project to Raman sidereal astronomy and
  true nodes.
- `financial_astro_ephemeris.py` already locates the local Swiss Ephemeris data
  directory and provides the established timestamp conversion contract.
- `panchanga_doctrine.py` supplies deterministic 27-fold nakshatra, tithi,
  karana, yoga, and weekday formulas.
- `jyotish_agent/classical_source_editions.yaml` remains the edition registry
  for locally held classical texts.
- The Windows desktop app is Tauri-based, so future Chakra Lab calls should use
  native commands instead of another localhost service.

## Gaps Found

- Existing ephemeris helpers return longitude only and silently permit Moshier
  fallback. SBC needs latitude, distance, speed, returned flags, file hash, and
  an explicit fallback policy.
- Existing weekday logic uses civil IST midnight only. Sunrise Vara requires a
  separate, named calculation contract.
- Existing Panchanga has no source-profiled Abhijit policy.
- The implementation guide assumes an 81-cell design, while the source audit
  records both 64-cell and 81-cell textual traditions.
- The editor supplement contains three source-worked standard Vedha examples;
  these now gate the Phase 3A figure-relative ray compiler.
- No certified automatic threshold distinguishes mean from swift direct motion.
- No certified precedence rule combines retrograde with exalted/debilitated
  multipliers.
- No source-certified Latta fixture set exists.
- Swiss Ephemeris distribution licensing remains unresolved for the packaged
  Windows application.

## Result

The `sbc` package wraps deterministic facts without changing the main financial
astrology engine. Phase 1 snapshots still contain no price, market, score,
signal, Auto Suggest, or broker fields. Phase 3A is a separate guidance API:
it emits source targets plus an openly normalized favorable/adverse evidence
ledger, carries `financial_validation_status=NOT_VALIDATED`, and cannot emit
trade or broker fields.
