"""R3R2A batch-worker contract constants, intentionally outcome-blind."""

from __future__ import annotations

from .canonical import canonical_hash


IPC_SCHEMA_VERSION = "MO_R4A_CANDIDATE_C_RUN1_R3R2_WORKER_IPC_V1"
WORKER_POLICY = {
    "oneAWorkerForWholePopulation": True, "oneBWorkerForWholePopulation": True,
    "oneV2WorkerForWholeComparison": True, "scientificWorkerRetryCount": 0,
    "realProductionTicketsIssued": False,
}


def worker_contract_hash() -> str:
    return canonical_hash({"schemaVersion": IPC_SCHEMA_VERSION, **WORKER_POLICY})
