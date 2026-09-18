# Candidate C RUN1 AUTH1-R1 PID Evidence Clarification

AUTH1 passed central scientific and execution review. The frozen one-shot run
produced 5,160 rows from each independent evaluator and preserved a V2
comparison with `REAL_SOURCE_REPRODUCTION_SEMANTIC_AGREEMENT`, zero mismatch
records, and zero mismatch classifications.

The historical AUTH1 execution record correctly retains `null` for each worker
PID, but its explanation was too strong. It said
`NOT_EXPOSED_BY_FROZEN_CONTROLLER`. Frozen worker responses in fact contained
`runtimeRootIdentity.pid`, `verificationPid`, and `executionPid`, each sourced
from `os.getpid()`. The frozen controller returned the full A, B, and V2 worker
responses from `_execute()`.

The corrected interpretation is
`AVAILABLE_IN_EPHEMERAL_CONTROLLER_RETURN_BUT_NOT_RETAINED_IN_AUTH1_EVIDENCE`.
The PID values were available during the ephemeral controller return, but were
not persisted in the immutable AUTH1 artifacts. They are therefore not
recoverable now and remain `null`; this record does not reconstruct them.

This is an additive observability clarification only. It does not alter the
authorization, first-result artifacts, comparison, scientific conclusion, or
replay block. No AUTH1 rerun is required or authorized. The allowed conclusion
remains deterministic source-contract agreement on the frozen real Candidate C
population, not market or forecast validation.

Candidate C source reproduction is `CLOSED_PENDING_CENTRAL_CONFIRMATION`.
Next gate: `CENTRAL_REVIEW_CANDIDATE_C_RUN1_AUTH1_R1_PID_EVIDENCE_CLARIFICATION`.
