# PFR-V2B-R7-XE1 Existing Experimental Infrastructure Audit

## Purpose

XE1 introduces an isolated Evidence Role and Modifier Lab. This audit records
what it may reuse and, equally importantly, what it must leave alone.

## Reuse Decisions

| Existing area | XE1 decision | Boundary |
| --- | --- | --- |
| `src/productFirstTimingPhase.ts` | REFERENCE ONLY | Its event lifecycle geometry remains a non-voting product experiment. XE1 exposes a future timing-kernel slot but does not import, alter, or activate this code. |
| `src/pairRelativeField.ts` | ADAPT CONCEPT ONLY | XE1 may show a separate read-only base-minus-quote adapter in a later input-controlled experiment. It does not call or alter the Fields compiler. |
| Chart-conditioned event identities | REUSE AS FUTURE IDENTIFIERS | XE1 may retain opaque event and causal IDs, but no reviewed polarity, price, or catalogue admission is read in XE1. |
| `research_labs/instrument_relative_sbc` | ADAPT ISOLATION PATTERN | Its experimental-profile and execution-lock discipline informed XE1. Its scoring, source tiers, and FX machinery are not imported. |
| `backend/shadow_trial.py` and `backend/shadow_ledger.py` | ADAPT IMMUTABILITY PATTERN | XE1 has its own fixture ledger contract. It does not read outcomes or append to the trading shadow ledger. |
| `docs/sbc/ADR-0006-causal-cluster-and-ledger-deduplication.md` | REUSE CAUSAL SAFETY PRINCIPLE | Derived views cannot become extra causal votes. XE1 applies an independent, explicit causal-group contract. |

## Do Not Touch

- classical source fixtures, including Phaladeepika, Trailokya, Agarwal, and Argha source semantics;
- Mode 1 / source-only rendering and the SBC runtime;
- Fields, its USD/JPY formula, and its synchronized requests;
- Auto Suggest, official ML notes, local LLMs, MT5, live inference, orders, market price reads, and market outcome reads;
- BPHS calendar and founder review packets.

## Result

XE1 is new product code with a narrow frontend navigation reuse and the normal
private-backend transport only. It cannot become a hidden score source for an
existing surface.
