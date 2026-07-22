# Canonical Project Status

This directory is the small machine-readable status layer for Gann Astro.
It complements, but does not replace, the recovery handoff and detailed audit
reports.

The status vocabulary is deliberately explicit:

- `IMPLEMENTED_IN_SOURCE`: code and focused tests exist.
- `PACKAGED_CANDIDATE`: a hash-addressed distributable exists.
- `PHYSICALLY_TESTED`: the exact candidate passed its physical-device matrix.
- `PROMOTED_STABLE`: an accepted candidate was deliberately promoted.
- `SOURCE_CERTIFIED`: the relevant doctrine or formula passed its source gate.
- `FINANCIALLY_VALIDATED`: a frozen out-of-sample trial passed its registered gate.

These labels are not synonyms. A capability may be implemented without being
packaged, source certified, or financially validated. `unknown` and `pending`
must remain visible rather than becoming zero, neutral, or passed.

Canonical documents:

- `release_status.json`: exact distributable identities and promotion blockers.
- `capability_status.json`: status dimensions for major capabilities.
- `research_trials.json`: frozen and planned prospective cohorts.
- `source_certification.json`: doctrine and comparator gates.
- `mobile_acceptance_plan.json`: MOB-01 through MOB-08 for the selected pair.

Run validation from the repository root:

```powershell
python status\validate_status.py
python -m unittest status.test_validate_status status.test_mobile_acceptance
```

Physical evidence is intentionally kept outside Git under
`D:\GannFinancialAstro\acceptance`. The collector hashes every evidence file
and binds the result to the exact tracked acceptance plan.
