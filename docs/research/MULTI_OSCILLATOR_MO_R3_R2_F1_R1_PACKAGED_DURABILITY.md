# MO-R3-R2-F1-R1 Packaged Durability Evidence Closure

Status: complete. This record covers the bounded per-side Founder Review export
visibility repair and the actual packaged persistence proof. It does not begin
founder review and does not assign any real event decision.

Date: 2026-09-09

## Source And Scope

- Starting master: `58196dc8bf52765640b66bfb14ed653f21901312`
- Implementation commit: `9208a552cbed5ec0228e7811c9189393a1581797`
- New candidate: `0.10.64-pfr-v2b-mo-r3-r2-f1-r1`
- Historical baseline candidate: `0.10.63-pfr-v2b-mo-r3-r2-f1`

The implementation changes only the Founder Review client export outcome
reporting, structured API error typing used by that reporting, frontend tests,
and the immutable candidate version metadata. USD and JPY remain independently
revisioned. There is no cross-side transaction.

## Per-Side Export Outcomes

`FounderReviewWorkbench` submits USD and JPY sequentially, but records each
result independently. A successful side updates only that side's committed
revision ID/hash. A failed side remains dirty and visibly unsaved. A partial
result explicitly states that it is not an all-sides save. Structured stale
revision errors expose the conflict code and the authoritative current revision
ID/hash.

Focused frontend coverage is `23/23` across `src/api.test.ts` and
`src/founderReviewWorkbench.test.ts`, including:

- USD success followed by JPY failure;
- JPY failure followed by success on retry;
- stale-revision conflict visibility;
- structured API 409 error details.

## Packaged Durability Proof

Both probes launched the actual portable executable, discovered the managed
sidecar port, and called the real loopback API with the packaged token. The
durability root was unique per run and was deleted only after the checks passed.
No real review decision was submitted.

### Immutable 0.10.63 Baseline

Candidate:

```text
D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.63-pfr-v2b-mo-r3-r2-f1-tauri
```

Evidence report:

```text
D:\GannFinancialAstro\smoke\mo_r3_r2_f1_r1_durability_0_10_63-final_20260909_055853\durability_report.json
```

The baseline passed all checks. The initial GET returned two sides, 12 USD
rows, 12 JPY rows, 24 `SINGLE_PASS_VERIFIED` rows, zero decisions, zero
classifications, zero references, and null current revision hashes.

Revision chain observed on USD:

| Operation | Revision ID | Revision hash | Previous hash |
| --- | --- | --- | --- |
| blank export 1 | `rev-6ed29284af2c41ceae60203852d74586` | `CD1AB647EDA3F12233813B2C92D9B280C86A935229AD39D05CDA606E7B855F96` | null |
| blank export 2 | `rev-8b9da99a6e5040bd86d4b8154613c9b3` | `D9622356615629719DFDF8DA87527B7034FF7F69B3AF576209A8627800234440` | revision 1 hash |

The stale export returned HTTP `409`, `application/json`, and
`FOUNDER_REVIEW_REVISION_CONFLICT`, naming revision 2 as authoritative. Both
revision directories remained present. The candidate/backend resource tree
remained `C025E380552E4CF326E474EA491521B15CFC5231C8EBF153971C24504F8F9D9D`.

### New 0.10.64 Candidate

Candidate:

```text
D:\GannFinancialAstro\release_candidate\GannAstroDesk-0.10.64-pfr-v2b-mo-r3-r2-f1-r1-tauri
```

Evidence report:

```text
D:\GannFinancialAstro\smoke\mo_r3_r2_f1_r1_durability_0_10_64-pwsh_20260909_061015\durability_report.json
```

The new candidate passed the same sequence. Its initial GET again returned 12
USD plus 12 JPY verified rows and zero decisions/classifications/references.

Revision chain observed on USD:

| Operation | Revision ID | Revision hash | Previous hash |
| --- | --- | --- | --- |
| blank export 1 | `rev-86e378dacfc742538c879ef72293df6c` | `FD975E3B54E37522D4932A9711AC91D3A9A7EB5710A6CA57C01ADBA12C4584FA` | null |
| blank export 2 | `rev-5e3af8d14d7648c091f0c87c75b9b53a` | `7B18653E91131D2B3CA8B3B882425730273D0B5548402FA84651D7F9BA1E812A` | revision 1 hash |

The stale export returned HTTP `409`, `application/json`, and
`FOUNDER_REVIEW_REVISION_CONFLICT`, with revision 2's ID/hash in the conflict
payload. The revision 1 directory remained present after revision 2.

The candidate/backend resource tree was unchanged before and after the probe:

```text
0BBCE6E888974C28A59FA62589AE4604C8360675DC5FE3FA36F26FA82729F266
```

The packaged API calls were all JSON: Founder Review GET calls returned HTTP
`200 application/json`, blank export calls returned HTTP `200
application/json`, and the stale export returned HTTP `409 application/json`.
The final GET confirmed revision 2 remained authoritative.

Durable probe results for the new candidate:

- isolated durable files: `24`;
- catalogue entries: `0`;
- evidence admissions: `0`;
- decisions: `0`;
- classifications: `0`;
- source references: `0`;
- immutable Founder Review resources changed: no;
- isolated data root deleted after proof: yes;
- launch 1 and launch 2 descendant survivors: none.

The old candidate's immutable files and hashes were not overwritten. Its
portable SHA-256 is
`ABFD532DA6EAF01BA644BCF12374EF492A26B32A88E0719269BEC8781CD96908` and its
installer SHA-256 is
`82197273791FF26A986AF8C0E59224F4A871B2A8307D42D6F31DD48B90AD1B05`.

The new candidate artifact hashes are:

- portable: `A43ED1EF1CFD5CCFFDD7E7A14B5BCCB79538C5AF536638035B3C984D8D832545`;
- installer: `3DC5ED637DDEE4C0625BAA745C8CB06D19EF87700699228AFE1E8CE61883BADB`;
- sidecar: `B82F66D5A913232DB20BF081BF1328D18B77E9D872ED144A67DFC57A8A362852`;
- build receipt: `A570E42C5843CC70BDB5EE34F73F43D4DA9EA8C90F409511BEC23841C6454E13`;
- release manifest: `AC48605BFF0884D0F48F70719356D852C68EBBD12EC717977D353EAB49E19275`.

The new manifest binds source commit `9208a552cbed5ec0228e7811c9189393a1581797`,
declares `sourceGitDirty=false`, and declares `executionAllowed=false`.

## Verification

- Focused API and Founder Review frontend tests: `23/23`.
- Full frontend suite: `201/201` tests across `43` files.
- Full backend regression: `332` passed, `1` skipped.
- Oxlint: passed.
- Production frontend build: passed; `1878` modules transformed.
- `cargo fmt --check`: passed.
- `cargo check`: passed.
- Rust tests: `19` passed.
- `git diff --check`: passed.

An initial probe invocation under Windows PowerShell 5.1 stopped in the probe
harness because that shell does not support the temporary script's
`ConvertFrom-Json -Depth` option. It had observed healthy HTTP 200 responses
but had not entered the Founder Review sequence. The harness was corrected and
the final baseline proof passed. The new candidate proof was run with
PowerShell 7, matching the packaging environment used to calculate its
resource-tree digest.

## Locks

This closure made no changes to the 24 real identities, astronomy, unsigned MO
mathematics, source registries, catalogue/evidence registries, signed-wave
architecture, or execution locks. Founder Review remains unstarted:

- no real founder decisions;
- no outcome inspection;
- no polarity assignment;
- no price or return use;
- no SBC, ML, LLM, Auto Suggest, MT5, or order path;
- `executionAllowed=false`.

The temporary probe script was removed from the repository. Control returns to
the founder/central review process; no later milestone is started here.
