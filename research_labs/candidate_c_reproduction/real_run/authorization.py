"""Non-issuable RUN1 execution capability with a fake-event-only test path."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


REAL_CANDIDATE_C_RUN_AUTHORIZED = False
RUN1_MILESTONE = "MO-R4A-CANDIDATE-C-RUN1-REAL-EXECUTION-HARNESS-PRERUN-FREEZE"
RUN1_CONTRACT_HASH = "0DD78FBA6FD347DB09778FFDD163FC76F6205070E92928D63A999D5D135B3A5A"
POPULATION_HASH = "A486D0045DC233207C0A2A50D50CFEFAC0B6493A6775630A068791B919F1F2A6"
A_IMPLEMENTATION_HASH = "93ECB7BDB684C9F9788F63BADAE8D297453F02557D7BB89DB2621CF9E257DCFB"
B_IMPLEMENTATION_HASH = "0A3266F754939D2408B4B7646A1E36A1CEC7338EDADE5844E831BCF6EB4CD199"
V2_PROJECTION_HASH = "1DDFC3B79EC30913254A2FEA117A97EA1761E42D8681EB5D2CB6B2D698187BED"
ONE_SHOT_EXECUTION_INTENT = "CANDIDATE_C_RUN1_ONE_SHOT_REAL_REPRODUCTION"
TEST_EVENT_PREFIX = "FAKE_REAL_RUN1_"


class RealCandidateCRunNotAuthorized(RuntimeError):
    """Raised before real events can reach any frozen scientific component."""


def _build_capability_boundary() -> tuple[type[Any], Any, Any]:
    issuer_nonce = object()

    @dataclass(frozen=True)
    class RealRunAuthorizationCapability:
        milestone: str
        execution_contract_hash: str
        population_hash: str
        a_implementation_hash: str
        b_implementation_hash: str
        v2_projection_hash: str
        one_shot_execution_intent: str
        event_id: str
        test_only: bool
        _issuer_nonce: object

    def issue_test_only_fake_event_capability(event_id: str) -> RealRunAuthorizationCapability:
        if not isinstance(event_id, str) or not event_id.startswith(TEST_EVENT_PREFIX):
            raise RealCandidateCRunNotAuthorized("test-only capability requires an explicitly fake RUN1 event ID")
        return RealRunAuthorizationCapability(
            milestone=RUN1_MILESTONE,
            execution_contract_hash=RUN1_CONTRACT_HASH,
            population_hash=POPULATION_HASH,
            a_implementation_hash=A_IMPLEMENTATION_HASH,
            b_implementation_hash=B_IMPLEMENTATION_HASH,
            v2_projection_hash=V2_PROJECTION_HASH,
            one_shot_execution_intent=ONE_SHOT_EXECUTION_INTENT,
            event_id=event_id,
            test_only=True,
            _issuer_nonce=issuer_nonce,
        )

    def validate_release_authorization(event_id: str, capability: object | None) -> None:
        if not isinstance(capability, RealRunAuthorizationCapability):
            raise RealCandidateCRunNotAuthorized("RUN1 release requires a valid authorization capability")
        if capability._issuer_nonce is not issuer_nonce:
            raise RealCandidateCRunNotAuthorized("RUN1 release capability was not issued by this boundary")
        frozen_identity = (
            capability.milestone,
            capability.execution_contract_hash,
            capability.population_hash,
            capability.a_implementation_hash,
            capability.b_implementation_hash,
            capability.v2_projection_hash,
            capability.one_shot_execution_intent,
        )
        expected_identity = (
            RUN1_MILESTONE,
            RUN1_CONTRACT_HASH,
            POPULATION_HASH,
            A_IMPLEMENTATION_HASH,
            B_IMPLEMENTATION_HASH,
            V2_PROJECTION_HASH,
            ONE_SHOT_EXECUTION_INTENT,
        )
        if frozen_identity != expected_identity:
            raise RealCandidateCRunNotAuthorized("RUN1 release capability does not bind the frozen execution contract")
        if not capability.test_only or capability.event_id != event_id or not event_id.startswith(TEST_EVENT_PREFIX):
            raise RealCandidateCRunNotAuthorized("RUN1 production authorization is not issuable in this milestone")

    # Keep the issuer nonce closure-bound. Importing this module must not give a
    # caller an ordinary constructor path around the test-only issuer.
    return RealRunAuthorizationCapability, issue_test_only_fake_event_capability, validate_release_authorization


(
    RealRunAuthorizationCapability,
    issue_test_only_fake_event_capability,
    validate_release_authorization,
) = _build_capability_boundary()


def issue_real_run_authorization(*_args: Any, **_kwargs: Any) -> RealRunAuthorizationCapability:
    """Production issuance is deliberately unavailable until a central successor authorizes RUN1."""

    raise RealCandidateCRunNotAuthorized(
        "REAL_CANDIDATE_C_RUN_AUTHORIZED=false; production RUN1 authorization cannot be issued"
    )
