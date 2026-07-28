# ADR-0009: Signed SBC Audit Package Catalogs

Date: 2026-07-28

Status: accepted for P5 implementation

## Context

P4 seals one canonical P3 projection, its interval comparisons, manual
bookmarks, and the full Chakra-to-P4 replay recipe. Researchers need to retain
and exchange more than one such package without losing package identity or
mistaking a collection for combined evidence.

A plain folder of JSON files cannot prove which bytes were signed by the local
research workspace. A signature alone also cannot prove that P1-P4 replay,
doctrine, or financial interpretation is correct.

## Decision

P5 introduces:

- `SBC_AUDIT_PACKAGE_CATALOG_V1`;
- `SBC_AUDIT_CATALOG_SIGNATURE_V1`;
- `SBC_SIGNED_AUDIT_CATALOG_BUNDLE_V1`;
- `SBC_AUDIT_CATALOG_VERIFICATION_V1`.

Before inclusion, every embedded P4 package must pass complete
Chakra -> P1 -> P2 -> P3 -> P4 replay. The catalog embeds each package in full,
preserves its package/source-audit/instrument/timestamp identities, and adds
portable SHA-256 identities for the package bytes, catalog entry, and complete
catalog.

The app signs canonical catalog bytes with Ed25519. On Windows, the private key
is protected by the current user's DPAPI context and stored below the existing
`D:` application-data root. The private key is never exported or committed.
The bundle contains the public key, key identity, signature, and signed
catalog.

## Two Verification Levels

Integrity verification checks:

1. exact P5 contracts, schemas, policies, and guardrails;
2. every embedded P4 structural identity;
3. package, entry, and catalog hashes;
4. the Ed25519 public-key identity and signature.

Full replay verification additionally recomputes every embedded P4 package
from its sealed replay recipe.

The standalone verifier deliberately performs integrity verification only and
reports semantic replay as `NOT_PERFORMED`. This prevents a file-signature
check from masquerading as evidence replay.

## Interpretation Boundary

Catalog order and membership have no evidentiary weight. P5 performs no
cross-package sum, average, comparison, rank, vote, confidence, phase,
market-direction inference, or financial promotion.

An Ed25519 PASS means only that the canonical catalog bytes match the public
signature. The default local key is a local research-provenance identity, not
an independently attested legal identity, doctrine certification, or
financial-validation authority.

## Guardrails

P5 remains:

- research-only and read-only;
- timestamp-safe and no-lookahead;
- source-profiled experimental;
- financially unvalidated;
- non-voting with directional contribution `0.0`;
- disconnected from FX subtraction, phase, confidence, market direction,
  Auto Suggest, live inference, official ML notes, shadow validation, trade
  output, and MT5 execution.

Any future cross-catalog arithmetic or independently attested signer registry
requires a separate contract, threat model, and acceptance gate.
