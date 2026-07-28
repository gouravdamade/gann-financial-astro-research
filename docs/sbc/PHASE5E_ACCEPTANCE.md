# SBC Phase 5E Acceptance

Date: 2026-07-28

## Required Contract Behavior

- A catalog contains at least one unique canonical P4 package.
- Every member has a complete P4 replay `PASS` before catalog inclusion.
- Entries are sorted by package identity and preserve the embedded P4 bytes.
- Package, entry, catalog, key, and signature identities are portable.
- The Ed25519 signature covers exact canonical catalog bytes.
- Windows private-key bytes are protected with DPAPI and kept outside Git.
- Imported bundles can run integrity-only verification or complete semantic
  replay.
- The standalone verifier imports no application SBC module and reports
  semantic replay as `NOT_PERFORMED`.

## Required Fail-Closed Behavior

- Reject duplicate package identities.
- Reject missing, failed, or partial P4 replay evidence.
- Reject unknown contract fields, weakened guardrails, invalid hashes, changed
  embedded packages, mismatched key identities, and invalid signatures.
- Do not silently promote integrity verification to semantic replay.
- Do not expose cross-package arithmetic, voting, ranking, confidence,
  direction, official ML notes, live inference, trade output, or execution.

## Interface Acceptance

The Chakra audit workspace must allow a researcher to:

1. add only a replay-verified P4 package to a local catalog draft;
2. remove draft members without changing the sealed P4 package;
3. seal and sign one or more packages;
4. export and import the complete signed JSON bundle;
5. choose integrity-only or full-replay verification;
6. see the public key identity, signature algorithm, member identities, and
   separate structural/replay states;
7. see an explicit warning that packages are not added, averaged, voted,
   ranked, or converted into market direction.

## Promotion Boundary

Phase 5E is accepted only as a source-implemented, research-only exchange and
audit capability. It is not a packaged release, external identity
certification, doctrine certification, or prospective financial validation.
