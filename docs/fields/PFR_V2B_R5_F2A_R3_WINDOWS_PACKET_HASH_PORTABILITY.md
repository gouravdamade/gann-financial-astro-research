# PFR-V2B-R5-F2A-R3 Windows Packet Hash Portability

## Scope

This is a narrow integrity repair discovered while repeating the full backend
regression from the clean Windows founder-candidate checkout. It changes no
astronomy event, blank packet, founder decision, polarity catalogue, field
rendering, BPHS calculation, SBC profile, price input, or execution lock.

## Finding

The canonical April 2025 blank founder-review packets and their identity
manifests were generated with LF line endings. Git's configured Windows
checkout converted the same tracked JSON packet to CRLF. The workbench hashed
raw on-disk bytes, so it rejected the unchanged packet before any founder
review could begin:

- manifest canonical hash: `08DB3837B89866519B7E0B24388537A2064F9EFE059D4FD5E6BCB77F82CA3D76`
- Windows raw checkout hash before the repair:
  `0484DA85FB7D78DF88EB154C0EE40963FC54AD2B97E11CA7A5EC53475F426609`

This was a transport representation difference, not an event-identity or
packet-content difference.

## Repair

`founder_review_workbench._sha256_file` now normalizes only `CRLF` to `LF`
before calculating a text-packet hash. It does not parse and reserialize the
JSON, remove whitespace generally, or modify files. Therefore an actual
content edit, including an appended newline, remains a hash mismatch and fails
closed.

The original V1 blank JSON packets, manifests, event IDs, event hashes and
founder fields remain untouched.

## Verification

- The full backend suite was first run from a fresh clean Windows checkout and
  reproduced the seven expected Founder Review hash errors.
- A focused fixture now converts a copied valid packet from CRLF to LF and
  verifies that it remains review-eligible.
- The existing mismatch test still appends a newline and verifies that the
  workbench rejects the packet.

No founder decision is created or admitted by this repair.
