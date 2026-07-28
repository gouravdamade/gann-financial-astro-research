# SBC Signed Audit Catalogs P5

Date: 2026-07-28

Classification: `SOURCE_PROFILED_EXPERIMENTAL`

Status: implemented in source, read-only, execution-locked

## Purpose

P5 groups one or more fully replay-verified P4 packages into a portable signed
catalog. It lets the researcher exchange and later verify exact research
artifacts while keeping every package independent.

## Contracts

- catalog: `SBC_AUDIT_PACKAGE_CATALOG_V1`
- signature: `SBC_AUDIT_CATALOG_SIGNATURE_V1`
- bundle: `SBC_SIGNED_AUDIT_CATALOG_BUNDLE_V1`
- verification: `SBC_AUDIT_CATALOG_VERIFICATION_V1`
- schema version: `1`
- policy: `SEALED_PACKAGE_CATALOG_NO_CROSS_AUDIT_INFERENCE_V1`
- signature algorithm: `ED25519`

## Catalog Rules

The compiler accepts only unique canonical P4 packages with complete
Chakra-to-P4 replay `PASS` records. It embeds each package, orders members by
package identity, and seals package, entry, and catalog bytes with portable
SHA-256 identities.

Catalog members are records, not votes. The engine exposes no operation that
adds, averages, ranks, compares, or converts packages into market direction.

## Signing Identity

The backend generates one Ed25519 research key on first use. Windows protects
the private 32-byte key with DPAPI and stores the protected blob under
`D:\GannFinancialAstro\app_data\sbc_audit_catalog` by default. Tauri passes the
same existing `D:` app-data root to the packaged backend.

Only the public key and signature are exported. The key identifies the local
research workspace for integrity checking; it is not an externally attested
person or organization certificate.

## Verification

The app offers:

- integrity-only verification: contracts, guardrails, portable hashes, and
  Ed25519 signature;
- full replay verification: integrity checks plus complete replay of every
  embedded P4 package.

`tools/verify_sbc_audit_catalog.py` is intentionally standalone. It does not
import the application SBC implementation, so it can independently check the
portable file and signature. It explicitly reports P1-P4 semantic replay as
`NOT_PERFORMED`.

## Desktop Integration

The Chakra audit workspace adds a P5 catalog section and Catalog tab. A P4
package cannot be added until the app has replay-verified it. The tab shows:

- catalog and public-key identities;
- signature algorithm and timestamp;
- embedded package identities and instruments;
- separate structural-integrity and semantic-replay states;
- the immutable no-cross-package-inference warning;
- signed JSON export/import, integrity check, and full replay controls.

The native Tauri bridge keeps catalog build and verification behind the
private loopback sidecar and read-only runtime lock.

## Deliberate Exclusions

P5 does not:

- perform cross-audit arithmetic, voting, ranking, or direction;
- infer confidence, phase, performance, or financial usefulness;
- alter Auto Suggest, live inference, official ML notes, or shadow validation;
- create trades or call MT5;
- externally attest the local signing identity;
- rebuild a Windows or Android package.

## Next Boundary

An independently attested signer registry, detached multi-party signatures,
or cross-catalog research statistics would be separate milestones. Any
cross-package analysis must first define a timestamp-safe comparable-unit
contract and pass prospective validation; P5 does not authorize it.
