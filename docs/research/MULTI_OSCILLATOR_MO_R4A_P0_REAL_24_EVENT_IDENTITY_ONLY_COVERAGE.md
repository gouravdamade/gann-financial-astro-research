# MO-R4A-P0 Real 24 Event Identity-Only Coverage

The authoritative machine-readable report is
`status/audits/mo_r4a_p0_real_24_identity_only_coverage.json`.

It reads only immutable blank-packet identities, identity manifests, and the
accepted event-identity audit. It does not read Founder Review decisions, a
durable review store, price, outcomes, SBC, the production catalogue, or the
reviewed-evidence registry.

- Events: `24` (`12` USD and `12` JPY)
- Identity status: all `SINGLE_PASS_VERIFIED`
- Source operator coverage: all `OPERATOR_NOT_YET_AVAILABLE`
- Unresolved operator count: `1` for each row
- Market bridge: all `NO_AUTHORIZED_MARKET_BRIDGE`
- Current direction: all `UNKNOWN_MORE_EVIDENCE_REQUIRED`
- Mode: all `EXPLORATORY_UNSIGNED`
- Magnitude: all `MAGNITUDE_NOT_CONFIGURED`
- Coverage hash: `884F6709E29DE2F7CD4F64B4953C9098142A0AC120E3FDD0C678034EA3B82532`

| Side | Event IDs |
| --- | --- |
| USD | `TN_CE5F70C72FD13CC479740159`, `TN_397A2B053BC76D9D788E5E5E`, `TN_5F09789EC41603F5659F0310`, `TN_91CFE5711918203A037CE751`, `TN_593EA6B234B87E0EDF2918F7`, `TN_B8750233DA923D431E121862`, `TN_29BCE2386E5DB19625921587`, `TN_F20AD1B4AC4094C8222AE7F9`, `TN_574C7A7407B855CD78DF8E0D`, `TN_A32A6104A917D4918B269910`, `TN_A3AE3253EF31ACAFF08CD9AA`, `TN_BD340A6100B173B5F254EDC1` |
| JPY | `TN_4A15CCC7D126313A14BCB562`, `TN_493252F9AB112FC2408987DD`, `TN_B70B60AB8E4057EAE10B62EE`, `TN_6E2DD561FB40D45D406F808E`, `TN_7CCC78DA82BDAC13D3CF60B0`, `TN_B24B1690FD8612329198D379`, `TN_8C3582F7101F4F14BC4ECC4F`, `TN_529E2CBC72B405EAD0990350`, `TN_CA3C82509E5C1C1BCB64ABD0`, `TN_0B97DA4310F43CF2F3803720`, `TN_6F48D71F91F1382FAA720581`, `TN_97C9294ED13CD6C36FB0840B` |

The report is not a sign-admission artifact. It records the present absence of
an event-bound source-operator contract and approved market bridge, preserving
the real pilot for later source/hypothesis population.
