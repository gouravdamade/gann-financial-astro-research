# Candidate C EMP2-R1 Low-Memory Execution Successor

## Purpose

EMP2-R1 is an additive engineering successor to the frozen R3-R1 EMP2 path.
The original in-memory market validator was operationally infeasible on the
available 16 GB host because it retained millions of Python quote objects and
datetime-indexed state. No real Candidate C source event had been joined to
market data when this successor was designed or tested.

The successor does not change the scientific contract. It streams one preserved
Dukascopy BI5 partition at a time, checks each raw object against the committed
EMP1 inventory, reconstructs the exact canonical market hash, and releases the
partition before reading the next one. Its future quote resolver retains only
first eligible quotes for caller-supplied anchors after a future authorization.

## Frozen Bindings

| Binding | Identity |
| --- | --- |
| EMP1 freeze commit | `5aaa58b09b4c2f10631fda32adde33a3593a06d1` |
| Market snapshot | `0F04578F8BB9FE08558889B3BBAC50F19DCE6702093856842B8A12ED32ACCEEC` |
| Market admission | `2EC34D56151E18CE17FC13F47CFB95007B9FDA86BF5F59B3416D65AF9455160A` |
| Raw artifact inventory | `B4D07BF5A960ADF4828271D1F009D769CBB2A3122D0CC172CAB80AC23A040534` |
| Source snapshot | `9EE0D825773D07306DD7B25E1AB26FE9384C6D278C1F95897199B6A6831AD284` |
| Source eligibility | `ADC3F5F527B1973C5D9493ECA8555E3EC3F94993A48B92A532EEF73F4F3A97B1` |
| Successor manifest | `8D558EEDA98C70CFA2C0235FA07AD3B63FBB85F518BBFFF20690A684C43A12F3` |
| Successor runtime contract | `6B150A756944D3500A05B193D7F759B0FC0C8E7F3B707FA8EE639D9D212184C8` |

## Semantics Preserved

The successor retains the frozen UTC coverage, 80 raw artifacts, 60-second
first-quote-at-or-after anchor rule, midpoint P0/PH construction, natural-log
return definition, three fixed horizons, separate USD/JPY strata, 24-row
ledger, 4,999-replicate temporal null, Holm primary family, and BH secondary
family. It does not create source signs, weights, a pair field, a score, or a
market direction.

Synthetic old/new equivalence checks cover exact-anchor, one-millisecond,
60-second, and 60.001-second selection boundaries; missing and weekend quotes;
identical and conflicting duplicates; chronology rejection; shared quote
selection; multiple events; and all three frozen horizons. The synthetic suite
also confirms that the successor uses the frozen admission validator with
metadata-only streaming output.

## Real Market-Only Reproduction

The permitted real run read only the durable private raw BI5 partitions. It did
not import Candidate C source-state records or event timestamps.

| Measure | Result |
| --- | --- |
| Raw artifacts SHA-256 verified | 80 / 80 |
| Raw parsed quotes | 7,888,953 |
| Canonical admitted quotes | 7,880,695 |
| Reproduced semantic hash | `0F04578F8BB9FE08558889B3BBAC50F19DCE6702093856842B8A12ED32ACCEEC` |
| Reproduced admission hash | `2EC34D56151E18CE17FC13F47CFB95007B9FDA86BF5F59B3416D65AF9455160A` |
| Exact duplicate quotes | 0 |
| Peak measured process RSS | 119,943,168 bytes |
| Engineering target | below 4 GiB: PASS |

The raw BI5 files and full quote snapshot remain outside Git under the existing
provider-license custody policy. Git contains only code, aggregate counts, and
cryptographic identities.

## Boundary

EMP2-R1 did not access real Candidate C event timestamps, availability counts,
P0, PH, returns, statistics, p-values, multiplicity outputs, or any direction.
It did not create EMP2 authorization or a canonical EMP2 result. Provider calls
were zero. `executionAllowed=false` remains unchanged.

Next gate:

`CENTRAL_REVIEW_CANDIDATE_C_EMP2_R1_OUTCOME_BLIND_LOW_MEMORY_EXECUTION_SUCCESSOR`
