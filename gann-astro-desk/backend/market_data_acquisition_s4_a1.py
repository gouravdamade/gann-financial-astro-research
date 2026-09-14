"""One-attempt, outcome-blind S4-A1 Dukascopy capture workflow.

The network boundary is deliberately small.  Imports, helper functions, and
ordinary tests do not create an AWS client or perform network I/O.  A real S3
request is possible only through the explicit CLI execution flag and after the
frozen authorization, parser, partition plan, and predecessor identities have
been verified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, Iterable, Mapping, Protocol

import dukascopy_tick_parser_s3r1_r3_r2 as frozen_parser


MILESTONE = "MO-R4A-S4-A1-P1-R1"
AUTHORIZATION_CONTRACT = "MO_R4A_S4_A1_ACQUISITION_AUTHORIZATION_V1"
RAW_MANIFEST_CONTRACT = "MO_R4A_S4_MARKET_DATA_RAW_ACQUISITION_MANIFEST_V1"
FREEZE_GATE_CONTRACT = "MO_R4A_S4_A1_ACQUISITION_FREEZE_GATE_V1"
OUTCOME_FIREWALL_CONTRACT = "MO_R4A_S4_A1_OUTCOME_FIREWALL_AUDIT_V1"
AUTHORIZED_PREOUTCOME_BASE_COMMIT = "47e557b1e573e661d6b3c0f2855d0044895bb12b"
PREACCESS_IMPLEMENTATION_PREDECESSOR_COMMIT = "3cbb175db05ba66714611cc451faf72358b3759f"
PREDECESSOR_IMPLEMENTATION_FREEZE_HASH = "42BF3BB9BB9A10A340DEFDC5FD29825B130DC4487D746537084604639486F170"

PROVIDER_IDENTITY = "DUKASCOPY_HISTORICAL_USDJPY_TICK_SERVICE"
PROVIDER_PRODUCT = "DUKASCOPY_HISTORICAL_PRICE_DATA_S3_REQUESTER_PAYS_DAILY_BI5_OBJECT_STORE"
INSTRUMENT = "USDJPY"
BUCKET = "cfg-public-proper-wallaby"
REGION = "eu-west-1"
REQUEST_PAYER = "requester"
MAX_ATTEMPTS = 1
SDK_RETRY_CONFIG = {"total_max_attempts": 1, "mode": "standard"}
CHUNK_SIZE_BYTES = 1024 * 1024

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "gann-astro-desk" / "backend"
CONFIG_ROOT = PROJECT_ROOT / "configs" / "research" / "machine_interpretation"
AUDIT_ROOT = PROJECT_ROOT / "status" / "audits"
ACCEPTANCE_ROOT = PROJECT_ROOT / "status" / "acceptance"

AUTHORIZATION_RELATIVE = Path("status/acceptance/mo_r4a_s4_a1_acquisition_authorization.json")
RAW_MANIFEST_RELATIVE = Path("status/audits/mo_r4a_s4_a1_market_data_raw_acquisition_manifest.json")
FIREWALL_AUDIT_RELATIVE = Path("status/audits/mo_r4a_s4_a1_outcome_firewall_audit.json")
FREEZE_GATE_RELATIVE = Path("status/acceptance/mo_r4a_s4_a1_acquisition_freeze_gate.json")
EXCEPTION_GATE_RELATIVE = Path("status/acceptance/mo_r4a_s4_a1_acquisition_exception_gate.json")
PREDECESSOR_IMPLEMENTATION_FREEZE_RELATIVE = Path("status/acceptance/mo_r4a_s4_a1_p1_pre_access_implementation_freeze.json")
IMPLEMENTATION_FREEZE_RELATIVE = Path("status/acceptance/mo_r4a_s4_a1_p1_r1_pre_access_implementation_freeze.json")
TEST_MODULE_RELATIVE = Path("gann-astro-desk/backend/test_market_data_acquisition_s4_a1.py")

PARSER_RELATIVE = Path("gann-astro-desk/backend/dukascopy_tick_parser_s3r1_r3_r2.py")
PARSER_CONTRACT_RELATIVE = Path("configs/research/machine_interpretation/dukascopy_tick_parser_contract_s3r1_r3_r2_v1.json")
ACQUISITION_CONTRACT_RELATIVE = Path("configs/research/machine_interpretation/market_data_acquisition_contract_s3r1_r3_r2_v1.json")
PARTITION_PLAN_RELATIVE = Path("status/audits/mo_r4a_s3r1_r2_provider_partition_plan.json")
PREREGISTRATION_RELATIVE = Path("configs/research/machine_interpretation/outcome_analysis_preregistration_s3r1_r3_r2_v1.json")
POPULATION_RELATIVE = Path("status/audits/mo_r4a_s3r1_r3_r2_primary_analysis_population.json")
CLUSTERS_RELATIVE = Path("status/audits/mo_r4a_s3r1_r3_r2_overlap_clusters.json")
INVARIANCE_RELATIVE = Path("status/audits/mo_r4a_s3r1_r3_r2_analysis_plan_invariance_audit.json")
CORE_RELATIVE = Path("status/acceptance/mo_r4a_s3r1_r3_r2_frozen_analysis_package.json")
ACCEPTANCE_RELATIVE = Path("status/acceptance/mo_r4a_s3r1_r3_r2_outcome_analysis_preregistration.json")
ROOT_GATE_RELATIVE = Path("status/acceptance/mo_r4a_s3r1_r3_r3_root_purity_gate.json")

EXPECTED_HASHES = {
    "parserContractHash": "18259325D9C8B245C05F4ECF596AD86395406A485E58DF3DF18C6B638C86BABE",
    "parserSourceSha256": "F3D49AFBC055D9C1CF2E513194C9A98C8D55769FF974343B99A4D00EE4A35BC8",
    "acquisitionContractHash": "BE4C378E368956F46F69D004D0C7522B32EA784C15894106B98DA8AA9A983CAC",
    "preregistrationHash": "23564E1F41C441EC1FB98B3FBD025F43643AEF75C27AD080550F7DCB7D64F272",
    "populationHash": "7F3CB6DE622A71FDA7F66E89BDAE2D0B7E3228E94BCAC403220DB17CF2686317",
    "clustersHash": "6D4968B9C7DB7B912FFF2567088AECFEE7AC00C5329BD0245E6BDE3A6613CC0E",
    "invarianceHash": "C53F5EB8C6ADAB19D090A834FBCFABA6D9207ADC9640C6E08CD8534D137748F9",
    "coreHash": "9B7D06C3F3BD7470478C75F9313EFBF9EB6C29E8BE766A74693FF77DA60A5C64",
    "acceptanceHash": "632D2B0C10D2F44287D8493495EC06E5CEDF6D7AD9DBC7374F2F2968327F9D8B",
    "rootPurityGateHash": "128F4E3F03CB7E5C190484CFB04796088FED15165B3AC81A867DA2B64F5606F2",
    "rootPurityAuditHash": "D1895250E16FFFBA988E18F3AD29836D7E9B132908D5743C883409938519C979",
    "astraFindingsDispositionHash": "8A32D3491C65801F392B5F6AB5453DA7B5115F34301851C089F5EB50F8437FD9",
    "partitionPlanHash": "5C39D983DD11288B24ABCF0E17F38C862A6B3B283CC68ABC3377C3324BBD738D",
    "analysisIntervalSetHash": "3A76939D2597AAE4742587738846987E82EBC73F1A47730F6809303634122465",
}

EXPECTED_UPSTREAM_HASHES = {
    "sourceOperatorLedgerHash": "2D4AD6E151602FBF2FC3E0ADDFDCDE7C7211CC52ED44D801AD3925AD9D5F3366",
    "sourceCoverageHash": "A4437C2A116EBD5D465339BCB0C9D81F8149CE65FAF37CF81C0F29D75B44F8B0",
    "hypothesisRegistryHash": "D76E208F52511BD8B5380BB32049B0C47275261443E587E3E09184E439FF3110",
    "usdHypothesisHash": "1C816B735FCCA52B84ED26C03D1755D251EADA7C2606B1D56533A06D71B713F9",
    "jpyHypothesisHash": "EF2D18CEA75BCC1A137D8687F332B5586FB62D8803D44819204AFDD6472ED24F",
    "predictionFreezeHash": "83F1456271B510468A0DF28C66AD705318CD06F5D5B5E0566F6DE05FA06CF71D",
}

EXPECTED_KEYS = (
    "USDJPY/2025/02/24_ticks.bi5", "USDJPY/2025/02/25_ticks.bi5",
    "USDJPY/2025/02/26_ticks.bi5", "USDJPY/2025/02/27_ticks.bi5",
    "USDJPY/2025/02/28_ticks.bi5", "USDJPY/2025/02/31_ticks.bi5",
    "USDJPY/2025/03/01_ticks.bi5", "USDJPY/2025/03/02_ticks.bi5",
    "USDJPY/2025/03/03_ticks.bi5", "USDJPY/2025/03/04_ticks.bi5",
    "USDJPY/2025/03/07_ticks.bi5", "USDJPY/2025/03/08_ticks.bi5",
    "USDJPY/2025/03/09_ticks.bi5", "USDJPY/2025/03/10_ticks.bi5",
    "USDJPY/2025/03/11_ticks.bi5",
)

ACCESS_FLAGS = (
    "PRICE_DATA_READ", "OUTCOME_DATA_READ", "FOUNDER_DECISION_READ", "REVIEW_STORE_READ",
    "SBC_READ", "CATALOGUE_ADMISSION", "EVIDENCE_ADMISSION", "SIGNED_WAVE_RENDERED",
    "PAIR_RESULTANT_CREATED", "MAGNITUDE_CONFIGURED", "AUTO_SUGGEST", "ML", "MT5",
    "EXECUTION_ALLOWED", "PRODUCTION_ADMISSION", "OUTCOME_UNLOCKED",
)


class AcquisitionError(RuntimeError):
    """Fail-closed acquisition or provenance error with a stable status code."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class TransportFailure(AcquisitionError):
    """A normalized provider response failure without credentials or body bytes."""

    def __init__(self, code: str, detail: str, *, status_code: int | None = None, missing: bool = False) -> None:
        super().__init__(code, detail)
        self.status_code = status_code
        self.missing = missing


@dataclass(frozen=True)
class TransportObject:
    body: BinaryIO
    content_length: int | None
    provider_metadata: Mapping[str, object]


class ExactPartitionTransport(Protocol):
    def get_exact_partition(self, *, bucket: str, key: str, request_payer: str) -> TransportObject:
        """Perform exactly one GetObject-equivalent request for an already approved key."""


@dataclass(frozen=True)
class AcquisitionRun:
    records: tuple[dict[str, object], ...]
    provider_access_performed: bool
    price_data_mechanically_parsed: bool
    status: str
    terminal_error_code: str | None
    terminal_error_detail: str | None
    requested_key_count: int
    get_object_call_count: int
    acquisition_started_at_utc: str | None = None
    acquisition_completed_at_utc: str | None = None
    execution_commit: str | None = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical_hash(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _without_hash(value: Mapping[str, Any], hash_key: str) -> dict[str, Any]:
    return {name: item for name, item in value.items() if name != hash_key}


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AcquisitionError("PREACCESS_REQUIRED_ARTIFACT_MISSING", f"missing {label}") from exc
    except json.JSONDecodeError as exc:
        raise AcquisitionError("PREACCESS_REQUIRED_ARTIFACT_INVALID", f"invalid JSON for {label}") from exc
    if not isinstance(value, dict):
        raise AcquisitionError("PREACCESS_REQUIRED_ARTIFACT_INVALID", f"{label} is not an object")
    return value


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.pending-{os.getpid()}")
    if temporary.exists():
        raise AcquisitionError("EXTERNAL_STORAGE_TEMPORARY_CONFLICT", "pending external storage file already exists")
    try:
        with temporary.open("xb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        if temporary.exists():
            temporary.unlink(missing_ok=True)
        raise AcquisitionError("EXTERNAL_STORAGE_WRITE_FAILED", "atomic external storage write failed") from exc


def _atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    _atomic_write_bytes(path, json.dumps(value, ensure_ascii=True, indent=2).encode("utf-8") + b"\n")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def acquisition_module_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest().upper()


def _artifact_path(project_root: Path, relative: Path) -> Path:
    return Path(project_root).resolve() / relative


def _assert_self_hash(value: Mapping[str, Any], field: str, expected: str, label: str) -> None:
    if value.get(field) != expected or _canonical_hash(_without_hash(value, field)) != expected:
        raise AcquisitionError("PREACCESS_HASH_MISMATCH", f"{label} does not reproduce its frozen identity")


def _parse_utc_day(value: str) -> date:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError as exc:
        raise AcquisitionError("PREACCESS_PARTITION_PLAN_INVALID", "native partition timestamp is invalid") from exc


def _all_access_flags(*, price_data_read: bool) -> dict[str, bool]:
    return {flag: price_data_read if flag == "PRICE_DATA_READ" else False for flag in ACCESS_FLAGS}


def _verify_plan(plan: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    if plan.get("providerPartitionPlanHash") != EXPECTED_HASHES["partitionPlanHash"]:
        raise AcquisitionError("PREACCESS_PARTITION_PLAN_HASH_MISMATCH", "partition plan hash differs from the frozen authorization")
    if _canonical_hash(_without_hash(plan, "providerPartitionPlanHash")) != EXPECTED_HASHES["partitionPlanHash"]:
        raise AcquisitionError("PREACCESS_PARTITION_PLAN_HASH_MISMATCH", "partition plan canonical body differs from the frozen authorization")
    partitions = plan.get("partitions")
    if not isinstance(partitions, list) or len(partitions) != 15 or plan.get("uniqueProviderPartitionCount") != 15:
        raise AcquisitionError("PREACCESS_PARTITION_PLAN_INVALID", "frozen plan must contain exactly 15 partitions")
    keys = tuple(item.get("requestIdentity", {}).get("key") for item in partitions if isinstance(item, dict))
    if keys != EXPECTED_KEYS:
        raise AcquisitionError("PREACCESS_PARTITION_PLAN_INVALID", "frozen ordered request keys do not match the authorization")
    if plan.get("analysisIntervalCount") != 39 or plan.get("analysisIntervalSetHash") != EXPECTED_HASHES["analysisIntervalSetHash"]:
        raise AcquisitionError("PREACCESS_PARTITION_PLAN_INVALID", "frozen 39-interval contract is not bound to the plan")
    for partition in partitions:
        request = partition.get("requestIdentity")
        if not isinstance(request, dict) or request != {
            "transport": "AWS_S3_GET_OBJECT_REQUESTER_PAYS",
            "bucket": BUCKET,
            "region": REGION,
            "key": request.get("key"),
            "requestPayer": REQUEST_PAYER,
        }:
            raise AcquisitionError("PREACCESS_PARTITION_PLAN_INVALID", "provider request identity changed")
        if partition.get("instrument") != INSTRUMENT or partition.get("providerProduct") != PROVIDER_PRODUCT:
            raise AcquisitionError("PREACCESS_PARTITION_PLAN_INVALID", "provider partition identity changed")
    return tuple(partitions)


def build_acquisition_authorization(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Build the central S4-A1 authorization from immutable, pre-existing inputs."""

    plan = _read_json(_artifact_path(project_root, PARTITION_PLAN_RELATIVE), "provider partition plan")
    partitions = _verify_plan(plan)
    body: dict[str, Any] = {
        "contract": AUTHORIZATION_CONTRACT,
        "schemaVersion": 1,
        "milestone": MILESTONE,
        "authorizedPreOutcomeBaseCommit": AUTHORIZED_PREOUTCOME_BASE_COMMIT,
        "preAccessImplementationPredecessorCommit": PREACCESS_IMPLEMENTATION_PREDECESSOR_COMMIT,
        "astraVerdict": "PRE_OUTCOME_REAUDIT_PASS",
        "centralDecision": "ACQUISITION_UNLOCKED_ANALYSIS_LOCKED",
        "r3r3RootPurityGateHash": EXPECTED_HASHES["rootPurityGateHash"],
        "r3r3RootPurityAuditHash": EXPECTED_HASHES["rootPurityAuditHash"],
        "astraFindingsDispositionHash": EXPECTED_HASHES["astraFindingsDispositionHash"],
        "parserContractHash": EXPECTED_HASHES["parserContractHash"],
        "parserSourceSha256": EXPECTED_HASHES["parserSourceSha256"],
        "acquisitionContractHash": EXPECTED_HASHES["acquisitionContractHash"],
        "partitionPlanHash": EXPECTED_HASHES["partitionPlanHash"],
        "analysisIntervalSetHash": EXPECTED_HASHES["analysisIntervalSetHash"],
        "provider": {
            "identity": PROVIDER_IDENTITY,
            "product": PROVIDER_PRODUCT,
            "instrument": INSTRUMENT,
            "bucket": BUCKET,
            "region": REGION,
            "requestPayer": REQUEST_PAYER,
            "transport": "AWS_S3_GET_OBJECT_REQUESTER_PAYS",
        },
        "orderedPartitionKeys": [partition["requestIdentity"]["key"] for partition in partitions],
        "exactPartitionCount": 15,
        "maxAttempts": MAX_ATTEMPTS,
        "automaticRetry": False,
        "acquisitionModuleSha256": acquisition_module_sha256(),
        "sdkVersions": _sdk_versions(),
        "providerAccessAllowed": True,
        "rawCaptureAllowed": True,
        "frozenParserExecutionAllowed": True,
        "canonicalParsedCaptureAllowed": True,
        "intervalTickSelectionAllowed": False,
        "returnCalculationAllowed": False,
        "hitCalculationAllowed": False,
        "statisticalOutcomeAllowed": False,
        "S4OutcomeAnalysisAllowed": False,
        "outcomeUnlocked": False,
        "executionAllowed": False,
        "outcomeAccessFlags": _all_access_flags(price_data_read=False),
    }
    return {**body, "acquisitionAuthorizationHash": _canonical_hash(body)}


def write_acquisition_authorization(project_root: Path = PROJECT_ROOT) -> Path:
    """Write the non-network authorization artifact before an execution attempt."""

    path = _artifact_path(project_root, AUTHORIZATION_RELATIVE)
    if path.exists():
        existing = _read_json(path, "S4-A1 acquisition authorization")
        expected = build_acquisition_authorization(project_root)
        if existing != expected:
            raise AcquisitionError("AUTHORIZATION_ARTIFACT_CONFLICT", "existing authorization differs from the frozen S4-A1 authorization")
        return path
    _atomic_write_json(path, build_acquisition_authorization(project_root))
    return path


def _verify_frozen_predecessors(project_root: Path) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    root = Path(project_root).resolve()
    parser_contract = _read_json(_artifact_path(root, PARSER_CONTRACT_RELATIVE), "parser contract")
    acquisition = _read_json(_artifact_path(root, ACQUISITION_CONTRACT_RELATIVE), "acquisition contract")
    plan = _read_json(_artifact_path(root, PARTITION_PLAN_RELATIVE), "provider partition plan")
    preregistration = _read_json(_artifact_path(root, PREREGISTRATION_RELATIVE), "preregistration")
    population = _read_json(_artifact_path(root, POPULATION_RELATIVE), "primary population")
    clusters = _read_json(_artifact_path(root, CLUSTERS_RELATIVE), "overlap clusters")
    invariance = _read_json(_artifact_path(root, INVARIANCE_RELATIVE), "invariance audit")
    core = _read_json(_artifact_path(root, CORE_RELATIVE), "frozen analysis package")
    acceptance = _read_json(_artifact_path(root, ACCEPTANCE_RELATIVE), "outcome acceptance")
    root_gate = _read_json(_artifact_path(root, ROOT_GATE_RELATIVE), "root-purity gate")

    _assert_self_hash(parser_contract, "parserContractHash", EXPECTED_HASHES["parserContractHash"], "parser contract")
    _assert_self_hash(acquisition, "marketDataAcquisitionContractHash", EXPECTED_HASHES["acquisitionContractHash"], "acquisition contract")
    _assert_self_hash(preregistration, "preregistrationHash", EXPECTED_HASHES["preregistrationHash"], "preregistration")
    _assert_self_hash(population, "primaryPopulationHash", EXPECTED_HASHES["populationHash"], "population")
    _assert_self_hash(clusters, "overlapClustersHash", EXPECTED_HASHES["clustersHash"], "clusters")
    _assert_self_hash(invariance, "analysisPlanInvarianceAuditHash", EXPECTED_HASHES["invarianceHash"], "invariance audit")
    _assert_self_hash(core, "analysisCoreManifestHash", EXPECTED_HASHES["coreHash"], "analysis core")
    _assert_self_hash(acceptance, "acceptanceManifestHash", EXPECTED_HASHES["acceptanceHash"], "acceptance")
    _assert_self_hash(root_gate, "rootPurityGateHash", EXPECTED_HASHES["rootPurityGateHash"], "root-purity gate")

    if root_gate.get("rootPurityAuditHash") != EXPECTED_HASHES["rootPurityAuditHash"] or root_gate.get("astraFindingsDispositionHash") != EXPECTED_HASHES["astraFindingsDispositionHash"]:
        raise AcquisitionError("PREACCESS_ROOT_PURITY_GATE_MISMATCH", "Astra root-purity gate is not the accepted exact gate")
    if root_gate.get("scientificInvariants") != {
        "frozenEventCount": 24, "directionalCount": 14, "primaryCount": 13,
        "intervalCount": 39, "providerPartitionCount": 15, "clusterIds": ["C1", "C2", "C3", "C4"],
        "binaryVectorChecks": 8192, "timingCombinationChecks": 2744,
        "binaryVectorMismatches": 0, "timingMismatches": 0,
    }:
        raise AcquisitionError("PREACCESS_SCIENTIFIC_INVARIANT_MISMATCH", "the frozen 24/14/13 and verification counts changed")
    if population.get("populationCounts", {}).get("frozenEventCount") != 24 or population.get("populationCounts", {}).get("directionalCount") != 14 or population.get("populationCounts", {}).get("primaryMarketScorableCount") != 13:
        raise AcquisitionError("PREACCESS_SCIENTIFIC_INVARIANT_MISMATCH", "the frozen 24/14/13 population changed")
    if acquisition.get("frozenIntervalSet", {}).get("totalCount") != 39 or acquisition.get("providerPartitionPlanHash") != EXPECTED_HASHES["partitionPlanHash"]:
        raise AcquisitionError("PREACCESS_SCIENTIFIC_INVARIANT_MISMATCH", "the frozen interval set changed")
    if acquisition.get("compression", {}).get("evidenceStatus") != "PLAUSIBLE_CROSS_SOURCE_RECONCILIATION_NOT_DIRECT_PROVIDER_SPECIFICATION" or acquisition.get("providerProtocolFullyClosed") is not False or acquisition.get("providerFramingUniquelySourceClosed") is not False:
        raise AcquisitionError("PREACCESS_QUALIFIED_FORMAT_STATE_MISMATCH", "the qualified FORMAT_ALONE state changed")
    if acceptance.get("upstreamHashes") != EXPECTED_UPSTREAM_HASHES or core.get("upstreamHashes") != EXPECTED_UPSTREAM_HASHES:
        raise AcquisitionError("PREACCESS_UPSTREAM_HASH_MISMATCH", "one or more immutable upstream hashes changed")
    if any(acceptance.get("outcomeAccessFlags", {}).values()) or acceptance.get("outcomeUnlocked") or acceptance.get("executionAllowed"):
        raise AcquisitionError("PREACCESS_OUTCOME_FIREWALL_MISMATCH", "pre-existing outcome firewall is not closed")
    source_hash = hashlib.sha256(_artifact_path(root, PARSER_RELATIVE).read_bytes()).hexdigest().upper()
    if source_hash != EXPECTED_HASHES["parserSourceSha256"] or parser_contract.get("parserSourceSha256") != source_hash:
        raise AcquisitionError("PREACCESS_PARSER_SOURCE_MISMATCH", "frozen parser source hash changed")
    if parser_contract.get("contract") != frozen_parser.PARSER_CONTRACT or parser_contract.get("compression", {}).get("framing") != frozen_parser.COMPRESSION_FRAMING:
        raise AcquisitionError("PREACCESS_PARSER_CONTRACT_MISMATCH", "frozen parser contract no longer binds the imported parser")
    return acquisition, _verify_plan(plan)


def _verify_authorization(project_root: Path, authorization: Mapping[str, Any]) -> None:
    if authorization.get("acquisitionAuthorizationHash") != _canonical_hash(_without_hash(authorization, "acquisitionAuthorizationHash")):
        raise AcquisitionError("AUTHORIZATION_HASH_MISMATCH", "authorization canonical hash does not reproduce")
    expected = build_acquisition_authorization(project_root)
    if dict(authorization) != expected:
        raise AcquisitionError("AUTHORIZATION_MISMATCH", "authorization does not exactly match the central frozen authorization")


PROTECTED_PREACCESS_PATHS = (
    PARSER_RELATIVE,
    PARSER_CONTRACT_RELATIVE,
    ACQUISITION_CONTRACT_RELATIVE,
    PARTITION_PLAN_RELATIVE,
    ROOT_GATE_RELATIVE,
    AUTHORIZATION_RELATIVE,
    PREDECESSOR_IMPLEMENTATION_FREEZE_RELATIVE,
    IMPLEMENTATION_FREEZE_RELATIVE,
    TEST_MODULE_RELATIVE,
)


def _git_revision(project_root: Path, revision: str) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", revision],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise AcquisitionError("PREACCESS_GIT_LINEAGE_UNVERIFIABLE", "cannot resolve Git revision") from exc
    return result.stdout.strip()


def _verify_git_starting_lineage(project_root: Path) -> str:
    """Require the current synchronized branch to descend from the accepted base."""

    head = _git_revision(project_root, "HEAD")
    remote = _git_revision(project_root, "origin/master")
    if head != remote:
        raise AcquisitionError(
            "PREACCESS_GIT_LINEAGE_MISMATCH",
            "HEAD and origin/master must identify the same execution commit",
        )
    try:
        ancestry = subprocess.run(
            ["git", "merge-base", "--is-ancestor", AUTHORIZED_PREOUTCOME_BASE_COMMIT, head],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise AcquisitionError("PREACCESS_GIT_LINEAGE_UNVERIFIABLE", "cannot verify accepted Git ancestry") from exc
    if ancestry.returncode != 0:
        if ancestry.returncode == 1:
            raise AcquisitionError(
                "PREACCESS_GIT_LINEAGE_MISMATCH",
                "accepted pre-outcome base is not an ancestor of the synchronized execution commit",
            )
        raise AcquisitionError("PREACCESS_GIT_LINEAGE_UNVERIFIABLE", "Git ancestry verification failed")
    return head


def _verify_protected_paths_clean(project_root: Path) -> None:
    """Require protected bytes and both Git trees to agree with the current HEAD."""

    root = Path(project_root).resolve()
    for relative in PROTECTED_PREACCESS_PATHS:
        path = _artifact_path(root, relative)
        if not path.is_file():
            raise AcquisitionError("PREACCESS_PROTECTED_PATH_MISSING", f"missing protected path {relative.as_posix()}")
        git_path = relative.as_posix()
        try:
            worktree_object = subprocess.run(
                ["git", "hash-object", f"--path={git_path}", "--", git_path],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            committed_object = subprocess.run(
                ["git", "rev-parse", f"HEAD:{git_path}"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            worktree_diff = subprocess.run(
                ["git", "diff", "--quiet", "HEAD", "--", git_path],
                cwd=root,
                check=False,
                capture_output=True,
            )
            index_diff = subprocess.run(
                ["git", "diff", "--quiet", "--cached", "--", git_path],
                cwd=root,
                check=False,
                capture_output=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise AcquisitionError("PREACCESS_PROTECTED_PATH_UNVERIFIABLE", f"cannot verify protected path {git_path}") from exc
        if worktree_diff.returncode not in (0, 1) or index_diff.returncode not in (0, 1):
            raise AcquisitionError("PREACCESS_PROTECTED_PATH_UNVERIFIABLE", f"Git diff failed for protected path {git_path}")
        if worktree_diff.returncode == 1 or index_diff.returncode == 1:
            raise AcquisitionError("PREACCESS_PROTECTED_PATH_DIRTY", f"protected path differs from committed HEAD: {git_path}")
        if worktree_object.stdout.strip() != committed_object.stdout.strip():
            raise AcquisitionError("PREACCESS_PROTECTED_PATH_DIRTY", f"protected path content differs from committed HEAD: {git_path}")


def _verify_implementation_freeze(project_root: Path, authorization: Mapping[str, Any]) -> None:
    root = Path(project_root).resolve()
    predecessor = _read_json(
        _artifact_path(root, PREDECESSOR_IMPLEMENTATION_FREEZE_RELATIVE),
        "predecessor implementation freeze",
    )
    _assert_self_hash(
        predecessor,
        "preAccessFreezeArtifactHash",
        PREDECESSOR_IMPLEMENTATION_FREEZE_HASH,
        "predecessor implementation freeze",
    )
    successor = _read_json(
        _artifact_path(root, IMPLEMENTATION_FREEZE_RELATIVE),
        "successor implementation freeze",
    )
    successor_hash = successor.get("preAccessImplementationFreezeArtifactHash")
    if not isinstance(successor_hash, str):
        raise AcquisitionError("PREACCESS_HASH_MISMATCH", "successor implementation freeze has no self-hash")
    _assert_self_hash(successor, "preAccessImplementationFreezeArtifactHash", successor_hash, "successor implementation freeze")

    expected = {
        "contract": "MO_R4A_S4_A1_P1_R1_PRE_ACCESS_IMPLEMENTATION_FREEZE_V1",
        "schemaVersion": 1,
        "milestone": MILESTONE,
        "predecessorFreezeHash": PREDECESSOR_IMPLEMENTATION_FREEZE_HASH,
        "predecessorCommit": PREACCESS_IMPLEMENTATION_PREDECESSOR_COMMIT,
        "acceptedPreOutcomeBaseCommit": AUTHORIZED_PREOUTCOME_BASE_COMMIT,
        "acquisitionModulePath": "gann-astro-desk/backend/market_data_acquisition_s4_a1.py",
        "acquisitionModuleSha256": acquisition_module_sha256(),
        "testModulePath": "gann-astro-desk/backend/test_market_data_acquisition_s4_a1.py",
        "testModuleSha256": _sha256_file(_artifact_path(root, TEST_MODULE_RELATIVE)),
        "authorizationArtifactPath": AUTHORIZATION_RELATIVE.as_posix(),
        "authorizationHash": authorization["acquisitionAuthorizationHash"],
        "parserSourceSha256": EXPECTED_HASHES["parserSourceSha256"],
        "parserContractHash": EXPECTED_HASHES["parserContractHash"],
        "acquisitionContractHash": EXPECTED_HASHES["acquisitionContractHash"],
        "partitionPlanHash": EXPECTED_HASHES["partitionPlanHash"],
        "analysisIntervalSetHash": EXPECTED_HASHES["analysisIntervalSetHash"],
        "providerAccessPerformed": False,
        "priceDataRead": False,
        "marketOutcomeRead": False,
        "outcomeUnlocked": False,
        "executionAllowed": False,
        "scientificDesignChanged": False,
        "parserChanged": False,
        "acquisitionProtocolChanged": False,
        "status": "PRE_ACCESS_IMPLEMENTATION_HARDENED_PROVIDER_NOT_ACCESSED",
        "nextGate": "CENTRAL_REVIEW_FINAL_PRE_PROVIDER_EXECUTION_AUTHORIZATION",
    }
    for field, value in expected.items():
        if successor.get(field) != value:
            raise AcquisitionError("PREACCESS_IMPLEMENTATION_FREEZE_MISMATCH", f"successor freeze field {field} differs")


def validate_preaccess(project_root: Path = PROJECT_ROOT, authorization: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    """Verify all non-network inputs required before the first GetObject call."""

    root = Path(project_root).resolve()
    _verify_git_starting_lineage(root)
    if authorization is None:
        authorization = _read_json(_artifact_path(root, AUTHORIZATION_RELATIVE), "S4-A1 acquisition authorization")
    _verify_authorization(root, authorization)
    _verify_implementation_freeze(root, authorization)
    _verify_protected_paths_clean(root)
    acquisition, partitions = _verify_frozen_predecessors(root)
    return acquisition, partitions


def _require_private_root(project_root: Path, private_root: Path) -> Path:
    project = Path(project_root).resolve()
    root = Path(private_root).resolve()
    if root == project or root.is_relative_to(project):
        raise AcquisitionError("UNSAFE_PRIVATE_STORAGE_ROOT", "private acquisition storage must be outside the repository")
    root.mkdir(parents=True, exist_ok=True)
    probe = root / ".mo_r4a_s4_a1_write_probe"
    try:
        _atomic_write_bytes(probe, b"private-acquisition-root\n")
        probe.unlink()
    except OSError as exc:
        raise AcquisitionError("UNSAFE_PRIVATE_STORAGE_ROOT", "private acquisition storage is not writable") from exc
    return root


def default_private_storage_root(project_root: Path = PROJECT_ROOT) -> Path:
    configured = os.environ.get("GANN_MARKET_DATA_ROOT")
    if configured:
        return Path(configured)
    return Path(project_root).resolve().parent / "gann-financial-astro-private-market-data"


def deterministic_request_id(partition: Mapping[str, Any]) -> str:
    identifier = partition.get("providerPartitionId")
    if not isinstance(identifier, str) or not identifier:
        raise AcquisitionError("PREACCESS_PARTITION_PLAN_INVALID", "provider partition ID is missing")
    return f"{MILESTONE}::{identifier}::ATTEMPT-1"


def _safe_component(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _logical_capture_name(partition: Mapping[str, Any], suffix: str) -> str:
    day = _parse_utc_day(str(partition["nativeStartUtc"]))
    return f"USDJPY_{day:%Y%m%d}_{_safe_component(str(partition['providerPartitionId']))[:16]}.{suffix}"


def _safe_metadata(value: Mapping[str, object]) -> dict[str, object]:
    allowed = {"HTTPStatusCode", "ContentLength", "ETag", "LastModified", "ContentType", "VersionId", "RequestCharged"}
    safe: dict[str, object] = {}
    for name in allowed:
        captured = value.get(name)
        if captured is None:
            continue
        safe[name] = captured.isoformat() if isinstance(captured, datetime) else captured
    return safe


def _journal_path(private_root: Path, request_id: str) -> Path:
    return private_root / "mo_r4a_s4_a1" / "journal" / f"{_safe_component(request_id)}.json"


def _journal_start(private_root: Path, partition: Mapping[str, Any], authorization_hash: str) -> Path:
    request_id = deterministic_request_id(partition)
    path = _journal_path(private_root, request_id)
    if path.exists():
        prior = _read_json(path, "external acquisition journal")
        status = prior.get("status")
        if status == "ATTEMPT_STARTED":
            raise AcquisitionError("ATTEMPT_STATUS_UNKNOWN_REVIEW_REQUIRED", "an earlier attempt started but has no final status")
        raise AcquisitionError("PREEXISTING_FINALIZED_ATTEMPT_REVIEW_REQUIRED", "a previous final journal prevents a second attempt")
    request = partition["requestIdentity"]
    _atomic_write_json(path, {
        "requestId": request_id,
        "providerPartitionId": partition["providerPartitionId"],
        "key": request["key"],
        "attemptOrdinal": 1,
        "status": "ATTEMPT_STARTED",
        "startedAtUtc": _utc_now(),
        "requestParameters": {"bucket": BUCKET, "key": request["key"], "requestPayer": REQUEST_PAYER, "region": REGION},
        "authorizationHash": authorization_hash,
        "acquisitionCodeSha256": acquisition_module_sha256(),
    })
    return path


def _journal_finish(path: Path, *, status: str, record: Mapping[str, object], error: AcquisitionError | None = None) -> None:
    value = _read_json(path, "external acquisition journal")
    value.update({"status": status, "finishedAtUtc": _utc_now(), "record": dict(record)})
    if error is not None:
        value["error"] = {"code": error.code, "detail": error.detail}
    _atomic_write_json(path, value)


def _capture_raw(body: BinaryIO, raw_path: Path, expected_length: int | None) -> tuple[int, str]:
    if raw_path.exists():
        raise AcquisitionError("EXISTING_FINALIZED_RAW_CAPTURE_CONFLICT", "raw capture already exists for this request")
    digest = hashlib.sha256()
    length = 0
    temporary: Path | None = None
    try:
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = raw_path.with_name(f".{raw_path.name}.pending-{os.getpid()}")
        if temporary.exists():
            raise AcquisitionError("EXTERNAL_STORAGE_TEMPORARY_CONFLICT", "pending raw capture file already exists")
        with temporary.open("xb") as handle:
            while True:
                try:
                    chunk = body.read(CHUNK_SIZE_BYTES)
                except Exception as exc:
                    raise AcquisitionError("PROVIDER_BODY_STREAM_READ_FAILED", type(exc).__name__) from exc
                if not chunk:
                    break
                if not isinstance(chunk, bytes):
                    raise AcquisitionError("PROVIDER_BODY_INVALID", "provider body returned non-byte data")
                handle.write(chunk)
                digest.update(chunk)
                length += len(chunk)
            handle.flush()
            os.fsync(handle.fileno())
        if expected_length is not None and length != expected_length:
            raise AcquisitionError("PROVIDER_CONTENT_LENGTH_MISMATCH", "captured byte length differs from provider ContentLength")
        os.replace(temporary, raw_path)
    except AcquisitionError:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise
    except OSError as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise AcquisitionError("EXTERNAL_STORAGE_WRITE_FAILED", "exact raw capture could not be finalized") from exc
    finally:
        close = getattr(body, "close", None)
        if callable(close):
            close()
    return length, digest.hexdigest().upper()


def _partition_record_base(partition: Mapping[str, Any], authorization_hash: str) -> dict[str, object]:
    request = partition["requestIdentity"]
    return {
        "requestId": deterministic_request_id(partition),
        "attemptOrdinal": 1,
        "providerProduct": PROVIDER_PRODUCT,
        "instrument": INSTRUMENT,
        "providerPartitionId": partition["providerPartitionId"],
        "nativeStartUtc": partition["nativeStartUtc"],
        "nativeEndUtc": partition["nativeEndUtc"],
        "requestParameters": {"bucket": BUCKET, "key": request["key"], "requestPayer": REQUEST_PAYER, "region": REGION},
        "parserContractHash": EXPECTED_HASHES["parserContractHash"],
        "parserSourceSha256": EXPECTED_HASHES["parserSourceSha256"],
        "authorizationHash": authorization_hash,
        "storageClass": "EXTERNAL_PRIVATE_NOT_COMMITTED",
    }


def _with_retrieval_timestamps(
    record: Mapping[str, object],
    *,
    request_started_at_utc: str,
    retrieved_at_utc: str,
) -> dict[str, object]:
    return {
        **record,
        "requestStartedAtUtc": request_started_at_utc,
        "retrievedAtUtc": retrieved_at_utc,
    }


def _missing_record(
    partition: Mapping[str, Any],
    authorization_hash: str,
    failure: TransportFailure,
    *,
    request_started_at_utc: str,
    retrieved_at_utc: str,
) -> dict[str, object]:
    return {
        **_with_retrieval_timestamps(
            _partition_record_base(partition, authorization_hash),
            request_started_at_utc=request_started_at_utc,
            retrieved_at_utc=retrieved_at_utc,
        ),
        "transportStatus": "MISSING_DOCUMENTED_DAILY_KEY",
        "providerMetadata": {"HTTPStatusCode": failure.status_code} if failure.status_code else {},
        "byteLength": None,
        "rawSha256": None,
        "logicalRawCaptureName": None,
        "parsedRecordCount": 0,
        "parsedTicksSha256": None,
        "logicalParsedCaptureName": None,
        "firstTimestampUtc": None,
        "lastTimestampUtc": None,
        "acquisitionDisposition": "MISSING_DOCUMENTED_DAILY_KEY_NO_TICKS",
    }


def _failed_record(
    partition: Mapping[str, Any],
    authorization_hash: str,
    error: AcquisitionError,
    *,
    request_started_at_utc: str,
    retrieved_at_utc: str,
) -> dict[str, object]:
    return {
        **_with_retrieval_timestamps(
            _partition_record_base(partition, authorization_hash),
            request_started_at_utc=request_started_at_utc,
            retrieved_at_utc=retrieved_at_utc,
        ),
        "transportStatus": error.code,
        "providerMetadata": {},
        "byteLength": None,
        "rawSha256": None,
        "logicalRawCaptureName": None,
        "parsedRecordCount": 0,
        "parsedTicksSha256": None,
        "logicalParsedCaptureName": None,
        "firstTimestampUtc": None,
        "lastTimestampUtc": None,
        "acquisitionDisposition": "ACQUISITION_ATTEMPT_INCOMPLETE_CENTRAL_REVIEW_REQUIRED",
        "error": {"code": error.code, "detail": error.detail},
    }


def _parse_frozen_raw(partition: Mapping[str, Any], raw_path: Path, parsed_path: Path) -> tuple[int, str, str, str]:
    raw_bytes = raw_path.read_bytes()
    partition_day = _parse_utc_day(str(partition["nativeStartUtc"]))
    try:
        records = frozen_parser.parse_daily_bi5(raw_bytes, partition_date_utc=partition_day, symbol=INSTRUMENT)
    except frozen_parser.DukascopyTickParserError as exc:
        raise AcquisitionError("FROZEN_PARSER_REJECTED_REAL_PROVIDER_CAPTURE_REVIEW_REQUIRED", exc.code) from exc
    if not records:
        raise AcquisitionError("FROZEN_PARSER_REJECTED_REAL_PROVIDER_CAPTURE_REVIEW_REQUIRED", "parser returned no records")
    native_start = datetime.fromisoformat(str(partition["nativeStartUtc"]).replace("Z", "+00:00"))
    native_end = datetime.fromisoformat(str(partition["nativeEndUtc"]).replace("Z", "+00:00"))
    if any(not native_start <= item.timestamp_utc < native_end for item in records):
        raise AcquisitionError("FROZEN_PARSER_REJECTED_REAL_PROVIDER_CAPTURE_REVIEW_REQUIRED", "parser yielded a timestamp outside native partition")
    canonical = frozen_parser.canonical_parsed_tick_json_lines(records)
    expected_sha = frozen_parser.parsed_ticks_sha256(records)
    if parsed_path.exists():
        raise AcquisitionError("EXISTING_FINALIZED_PARSED_CAPTURE_CONFLICT", "parsed capture already exists for this request")
    _atomic_write_bytes(parsed_path, canonical)
    observed_sha = _sha256_file(parsed_path)
    if observed_sha != expected_sha:
        raise AcquisitionError("CANONICAL_PARSED_HASH_MISMATCH", "external parsed JSONL hash differs from frozen parser hash")
    return len(records), observed_sha, frozen_parser.format_timestamp_utc(records[0].timestamp_utc), frozen_parser.format_timestamp_utc(records[-1].timestamp_utc)


def acquire_authorized_partitions(
    *,
    project_root: Path = PROJECT_ROOT,
    private_root: Path,
    transport: ExactPartitionTransport,
    execute_authorized_acquisition: bool,
    authorization: Mapping[str, Any] | None = None,
) -> AcquisitionRun:
    """Run the exact plan once through the supplied transport, with no retry path."""

    if not execute_authorized_acquisition:
        raise AcquisitionError("EXECUTION_FLAG_REQUIRED", "provider calls require --execute-authorized-acquisition")
    acquisition_started_at_utc = _utc_now()
    root = Path(project_root).resolve()
    _, partitions = validate_preaccess(root, authorization)
    execution_commit = _git_revision(root, "HEAD")
    if tuple(partition["requestIdentity"]["key"] for partition in partitions) != EXPECTED_KEYS:
        raise AcquisitionError("UNEXPECTED_PARTITION_KEY", "execution request set is not the exact frozen ordered key set")
    private = _require_private_root(root, private_root)
    if authorization is None:
        authorization = _read_json(_artifact_path(root, AUTHORIZATION_RELATIVE), "S4-A1 acquisition authorization")
    authorization_hash = str(authorization["acquisitionAuthorizationHash"])
    base = private / "mo_r4a_s4_a1"
    records: list[dict[str, object]] = []
    calls = 0
    parsed_any = False

    def completed_run(status: str, error_code: str | None = None, error_detail: str | None = None) -> AcquisitionRun:
        return AcquisitionRun(
            tuple(records),
            True,
            parsed_any,
            status,
            error_code,
            error_detail,
            len(partitions),
            calls,
            acquisition_started_at_utc,
            _utc_now(),
            execution_commit,
        )

    for partition in partitions:
        raw_name = _logical_capture_name(partition, "bi5")
        parsed_name = _logical_capture_name(partition, "jsonl")
        raw_path = base / "raw" / raw_name
        parsed_path = base / "parsed" / parsed_name
        if raw_path.exists() or parsed_path.exists():
            raise AcquisitionError(
                "EXISTING_FINALIZED_CAPTURE_CONFLICT",
                "a final raw or parsed capture already exists for the exact frozen partition",
            )
        journal = _journal_start(private, partition, authorization_hash)
        request_started_at_utc = _utc_now()
        record = {
            **_partition_record_base(partition, authorization_hash),
            "requestStartedAtUtc": request_started_at_utc,
        }
        key = str(partition["requestIdentity"]["key"])
        try:
            calls += 1
            response = transport.get_exact_partition(bucket=BUCKET, key=key, request_payer=REQUEST_PAYER)
        except TransportFailure as exc:
            if exc.missing:
                completed = _missing_record(
                    partition,
                    authorization_hash,
                    exc,
                    request_started_at_utc=request_started_at_utc,
                    retrieved_at_utc=_utc_now(),
                )
                _journal_finish(journal, status="ATTEMPT_COMPLETED_MISSING_KEY", record=completed)
                records.append(completed)
                continue
            completed = _failed_record(
                partition,
                authorization_hash,
                exc,
                request_started_at_utc=request_started_at_utc,
                retrieved_at_utc=_utc_now(),
            )
            _journal_finish(journal, status="ATTEMPT_FAILED_TERMINAL", record=completed, error=exc)
            records.append(completed)
            return completed_run("ACQUISITION_ATTEMPT_INCOMPLETE_CENTRAL_REVIEW_REQUIRED", exc.code, exc.detail)
        except Exception as exc:  # Transport implementations may expose a non-provider failure.
            error = AcquisitionError("UNEXPECTED_TRANSPORT_EXCEPTION", type(exc).__name__)
            completed = _failed_record(
                partition,
                authorization_hash,
                error,
                request_started_at_utc=request_started_at_utc,
                retrieved_at_utc=_utc_now(),
            )
            _journal_finish(journal, status="ATTEMPT_FAILED_TERMINAL", record=completed, error=error)
            records.append(completed)
            return completed_run("ACQUISITION_ATTEMPT_INCOMPLETE_CENTRAL_REVIEW_REQUIRED", error.code, error.detail)

        try:
            record["providerMetadata"] = _safe_metadata(response.provider_metadata)
            length, raw_sha = _capture_raw(response.body, raw_path, response.content_length)
            record.update({
                "transportStatus": "GET_OBJECT_SUCCESS",
                "byteLength": length,
                "rawSha256": raw_sha,
                "logicalRawCaptureName": raw_name,
                "retrievedAtUtc": _utc_now(),
            })
            _journal_finish(journal, status="RAW_CAPTURE_FROZEN", record=record)
            if length == 0:
                record.update({
                    "parsedRecordCount": 0, "parsedTicksSha256": None, "logicalParsedCaptureName": None,
                    "firstTimestampUtc": None, "lastTimestampUtc": None,
                    "acquisitionDisposition": "SUCCESSFUL_ZERO_BYTE_RESPONSE_ACQUISITION_INCOMPLETE",
                })
                error = AcquisitionError("SUCCESSFUL_ZERO_BYTE_RESPONSE_ACQUISITION_INCOMPLETE", "successful object has zero exact bytes")
                _journal_finish(journal, status="ATTEMPT_FAILED_TERMINAL", record=record, error=error)
                records.append(record)
                return completed_run("ACQUISITION_ATTEMPT_INCOMPLETE_CENTRAL_REVIEW_REQUIRED", error.code, error.detail)
            count, parsed_sha, first, last = _parse_frozen_raw(partition, raw_path, parsed_path)
            record.update({
                "parsedRecordCount": count,
                "parsedTicksSha256": parsed_sha,
                "logicalParsedCaptureName": parsed_name,
                "firstTimestampUtc": first,
                "lastTimestampUtc": last,
                "acquisitionDisposition": "SUCCESSFUL_RAW_AND_FROZEN_PARSED_CAPTURE",
            })
            _journal_finish(journal, status="ATTEMPT_COMPLETED", record=record)
            records.append(record)
            parsed_any = True
        except AcquisitionError as exc:
            failed = dict(record)
            failed.update({
                "parsedRecordCount": 0, "parsedTicksSha256": None, "logicalParsedCaptureName": None,
                "firstTimestampUtc": None, "lastTimestampUtc": None,
                "retrievedAtUtc": _utc_now(),
                "acquisitionDisposition": "ACQUISITION_ATTEMPT_INCOMPLETE_CENTRAL_REVIEW_REQUIRED",
                "error": {"code": exc.code, "detail": exc.detail},
            })
            _journal_finish(journal, status="ATTEMPT_FAILED_TERMINAL", record=failed, error=exc)
            records.append(failed)
            return completed_run("ACQUISITION_ATTEMPT_INCOMPLETE_CENTRAL_REVIEW_REQUIRED", exc.code, exc.detail)

    return completed_run("ACQUISITION_CAPTURED_AND_PROVENANCE_FROZEN_ANALYSIS_LOCKED")


def _sdk_versions() -> dict[str, str | None]:
    try:
        import boto3  # Imported only for a final provenance label; never on module import.
        import botocore
    except ImportError:
        return {"boto3": None, "botocore": None}
    return {"boto3": boto3.__version__, "botocore": botocore.__version__}


def build_raw_manifest(run: AcquisitionRun, authorization: Mapping[str, Any]) -> dict[str, Any]:
    assert_same_request_raw_identity(run.records)
    body: dict[str, Any] = {
        "contract": RAW_MANIFEST_CONTRACT,
        "schemaVersion": 1,
        "milestone": MILESTONE,
        "authorizedPreOutcomeBaseCommit": AUTHORIZED_PREOUTCOME_BASE_COMMIT,
        "preAccessImplementationPredecessorCommit": PREACCESS_IMPLEMENTATION_PREDECESSOR_COMMIT,
        "executionCommit": run.execution_commit,
        "acquisitionStartedAtUtc": run.acquisition_started_at_utc,
        "acquisitionCompletedAtUtc": run.acquisition_completed_at_utc,
        "status": run.status,
        "authorizationHash": authorization["acquisitionAuthorizationHash"],
        "r3r2AcquisitionContractHash": EXPECTED_HASHES["acquisitionContractHash"],
        "providerPartitionPlanHash": EXPECTED_HASHES["partitionPlanHash"],
        "parserContractHash": EXPECTED_HASHES["parserContractHash"],
        "parserSourceSha256": EXPECTED_HASHES["parserSourceSha256"],
        "provider": PROVIDER_IDENTITY,
        "product": PROVIDER_PRODUCT,
        "instrument": INSTRUMENT,
        "bucket": BUCKET,
        "region": REGION,
        "attemptPolicy": {"maxAttempts": MAX_ATTEMPTS, "automaticRetry": False, "sdkRetryConfiguration": SDK_RETRY_CONFIG},
        "acquisitionCodeSha256": acquisition_module_sha256(),
        "sdkVersions": _sdk_versions(),
        "exactPartitionCount": run.requested_key_count,
        "getObjectCallCount": run.get_object_call_count,
        "providerAccessPerformed": run.provider_access_performed,
        "priceDataMechanicallyParsed": run.price_data_mechanically_parsed,
        "marketOutcomeRead": False,
        "outcomeUnlocked": False,
        "executionAllowed": False,
        "terminalError": None if run.terminal_error_code is None else {"code": run.terminal_error_code, "detail": run.terminal_error_detail},
        "partitionRecords": list(run.records),
    }
    return {**body, "rawAcquisitionManifestHash": _canonical_hash(body)}


def build_outcome_firewall_audit(run: AcquisitionRun, raw_manifest_hash: str) -> dict[str, Any]:
    body: dict[str, Any] = {
        "contract": OUTCOME_FIREWALL_CONTRACT,
        "schemaVersion": 1,
        "milestone": MILESTONE,
        "rawAcquisitionManifestHash": raw_manifest_hash,
        "providerAccessPerformed": run.provider_access_performed,
        "priceDataMechanicallyParsed": run.price_data_mechanically_parsed,
        "outcomeDataRead": False,
        "intervalTickSelectionPerformed": False,
        "returnCalculationPerformed": False,
        "expectedDirectionApplied": False,
        "hitMissCalculated": False,
        "statisticsCalculated": False,
        "timingControlCalculated": False,
        "S4OutcomeAnalysisPerformed": False,
        "marketOutcomeRead": False,
        "outcomeUnlocked": False,
        "executionAllowed": False,
        "outcomeAccessFlags": _all_access_flags(price_data_read=run.price_data_mechanically_parsed),
    }
    return {**body, "outcomeFirewallAuditHash": _canonical_hash(body)}


def _aggregate_capture_hash(records: Iterable[Mapping[str, object]]) -> str:
    items = [
        {
            "providerPartitionId": item["providerPartitionId"],
            "transportStatus": item["transportStatus"],
            "rawSha256": item["rawSha256"],
            "parsedTicksSha256": item["parsedTicksSha256"],
            "parsedRecordCount": item["parsedRecordCount"],
        }
        for item in records
    ]
    return _canonical_hash({"orderedPartitionRecords": items})


def assert_same_request_raw_identity(records: Iterable[Mapping[str, object]]) -> None:
    """Reject an attempted provider revision instead of selecting a second payload."""

    known: dict[str, str | None] = {}
    for record in records:
        request_id = record.get("requestId")
        raw_sha = record.get("rawSha256")
        if not isinstance(request_id, str):
            raise AcquisitionError("RAW_MANIFEST_INVALID", "capture record has no request ID")
        if request_id in known and known[request_id] != raw_sha:
            raise AcquisitionError("PROVIDER_REVISION_CONFLICT", "same request ID has different raw SHA-256 values")
        known[request_id] = raw_sha if isinstance(raw_sha, str) else None


def build_freeze_or_exception_gate(run: AcquisitionRun, manifest: Mapping[str, Any], firewall: Mapping[str, Any]) -> tuple[Path, dict[str, Any]]:
    successful = run.status == "ACQUISITION_CAPTURED_AND_PROVENANCE_FROZEN_ANALYSIS_LOCKED"
    successful_count = sum(record.get("acquisitionDisposition") == "SUCCESSFUL_RAW_AND_FROZEN_PARSED_CAPTURE" for record in run.records)
    missing_count = sum(record.get("acquisitionDisposition") == "MISSING_DOCUMENTED_DAILY_KEY_NO_TICKS" for record in run.records)
    if successful:
        body: dict[str, Any] = {
            "contract": FREEZE_GATE_CONTRACT,
            "schemaVersion": 1,
            "milestone": MILESTONE,
            "status": run.status,
            "authorizationHash": manifest["authorizationHash"],
            "rawAcquisitionManifestHash": manifest["rawAcquisitionManifestHash"],
            "outcomeFirewallAuditHash": firewall["outcomeFirewallAuditHash"],
            "r3r3RootPurityGateHash": EXPECTED_HASHES["rootPurityGateHash"],
            "r3r2AcquisitionContractHash": EXPECTED_HASHES["acquisitionContractHash"],
            "parserContractHash": EXPECTED_HASHES["parserContractHash"],
            "parserSourceSha256": EXPECTED_HASHES["parserSourceSha256"],
            "partitionPlanHash": EXPECTED_HASHES["partitionPlanHash"],
            "exactPartitionCount": 15,
            "successfulObjectCount": successful_count,
            "missingDocumentedKeyCount": missing_count,
            "totalParsedRecordCount": sum(int(record.get("parsedRecordCount") or 0) for record in run.records),
            "aggregateCaptureHash": _aggregate_capture_hash(run.records),
            "scientificDesignChanged": False,
            "providerProtocolFullyClosed": False,
            "providerAccessPerformed": True,
            "priceDataRead": run.price_data_mechanically_parsed,
            "marketOutcomeRead": False,
            "outcomeUnlocked": False,
            "executionAllowed": False,
            "S4OutcomeAnalysisAllowed": False,
            "nextGate": "CENTRAL_REVIEW_ACQUISITION_PROVENANCE_BEFORE_S4_OUTCOME_EVALUATION",
        }
        return FREEZE_GATE_RELATIVE, {**body, "acquisitionFreezeGateHash": _canonical_hash(body)}
    body = {
        "contract": "MO_R4A_S4_A1_ACQUISITION_EXCEPTION_GATE_V1",
        "schemaVersion": 1,
        "milestone": MILESTONE,
        "status": run.status,
        "authorizationHash": manifest["authorizationHash"],
        "rawAcquisitionManifestHash": manifest["rawAcquisitionManifestHash"],
        "outcomeFirewallAuditHash": firewall["outcomeFirewallAuditHash"],
        "providerAccessPerformed": run.provider_access_performed,
        "priceDataRead": run.price_data_mechanically_parsed,
        "marketOutcomeRead": False,
        "outcomeUnlocked": False,
        "executionAllowed": False,
        "terminalError": manifest["terminalError"],
        "nextGate": "CENTRAL_REVIEW_ACQUISITION_EXCEPTION",
    }
    return EXCEPTION_GATE_RELATIVE, {**body, "acquisitionExceptionGateHash": _canonical_hash(body)}


def write_committed_provenance(project_root: Path, run: AcquisitionRun, authorization: Mapping[str, Any] | None = None) -> dict[str, Path]:
    """Write metadata-only provenance artifacts.  Raw and parsed capture bytes stay external."""

    root = Path(project_root).resolve()
    if authorization is None:
        authorization = _read_json(_artifact_path(root, AUTHORIZATION_RELATIVE), "S4-A1 acquisition authorization")
    manifest = build_raw_manifest(run, authorization)
    firewall = build_outcome_firewall_audit(run, str(manifest["rawAcquisitionManifestHash"]))
    gate_relative, gate = build_freeze_or_exception_gate(run, manifest, firewall)
    paths = {
        "manifest": _artifact_path(root, RAW_MANIFEST_RELATIVE),
        "firewall": _artifact_path(root, FIREWALL_AUDIT_RELATIVE),
        "gate": _artifact_path(root, gate_relative),
    }
    for name, value in (("manifest", manifest), ("firewall", firewall), ("gate", gate)):
        if paths[name].exists():
            existing = _read_json(paths[name], f"existing {name}")
            if existing != value:
                raise AcquisitionError("COMMITTED_PROVENANCE_CONFLICT", f"existing {name} differs from this immutable acquisition record")
        else:
            _atomic_write_json(paths[name], value)
    return paths


def build_botocore_config() -> object:
    """Create an SDK config that permits one total attempt only."""

    try:
        from botocore.config import Config
    except ImportError as exc:
        raise AcquisitionError("ACQUISITION_ENVIRONMENT_BLOCKED_BOTO3_UNAVAILABLE", "botocore is unavailable") from exc
    return Config(region_name=REGION, retries=dict(SDK_RETRY_CONFIG))


class Boto3ExactPartitionTransport:
    """The only real provider boundary; it exposes no ListObject or HeadObject API."""

    def __init__(self, client: object) -> None:
        self._client = client

    def get_exact_partition(self, *, bucket: str, key: str, request_payer: str) -> TransportObject:
        try:
            response = self._client.get_object(Bucket=bucket, Key=key, RequestPayer=request_payer)
        except Exception as exc:
            response = getattr(exc, "response", None)
            error = response.get("Error", {}) if isinstance(response, dict) else {}
            metadata = response.get("ResponseMetadata", {}) if isinstance(response, dict) else {}
            code = str(error.get("Code", "UNEXPECTED_PROVIDER_ERROR"))
            status = metadata.get("HTTPStatusCode") if isinstance(metadata, dict) else None
            if code in {"NoSuchKey", "404", "NotFound"} or status == 404:
                raise TransportFailure("MISSING_DOCUMENTED_DAILY_KEY", code, status_code=status, missing=True) from exc
            raise TransportFailure(code, type(exc).__name__, status_code=status) from exc
        if not isinstance(response, dict) or "Body" not in response:
            raise TransportFailure("PROVIDER_RESPONSE_INVALID", "GetObject response has no Body")
        metadata = response.get("ResponseMetadata", {})
        metadata = dict(metadata) if isinstance(metadata, dict) else {}
        for field in ("ContentLength", "ETag", "LastModified", "ContentType", "VersionId", "RequestCharged"):
            if field in response:
                metadata[field] = response[field]
        content_length = response.get("ContentLength")
        if content_length is not None and (not isinstance(content_length, int) or content_length < 0):
            raise TransportFailure("PROVIDER_RESPONSE_INVALID", "ContentLength is invalid")
        return TransportObject(body=response["Body"], content_length=content_length, provider_metadata=_safe_metadata(metadata))


def resolve_boto3_transport_and_credential_source() -> tuple[Boto3ExactPartitionTransport, str]:
    """Resolve credentials through the standard AWS chain without exposing their values."""

    try:
        import boto3
    except ImportError as exc:
        raise AcquisitionError("ACQUISITION_ENVIRONMENT_BLOCKED_BOTO3_UNAVAILABLE", "boto3 is unavailable") from exc
    session = boto3.Session(region_name=REGION)
    credentials = session.get_credentials()
    if credentials is None:
        raise AcquisitionError("ACQUISITION_ENVIRONMENT_BLOCKED_NO_AWS_CREDENTIALS", "no usable AWS credentials resolved")
    method = str(getattr(credentials, "method", "unknown"))
    client = session.client("s3", config=build_botocore_config())
    return Boto3ExactPartitionTransport(client), method


def _cli_summary(run: AcquisitionRun, provenance_paths: Mapping[str, Path]) -> dict[str, object]:
    return {
        "milestone": MILESTONE,
        "status": run.status,
        "providerAccessPerformed": run.provider_access_performed,
        "priceDataMechanicallyParsed": run.price_data_mechanically_parsed,
        "getObjectCallCount": run.get_object_call_count,
        "terminalErrorCode": run.terminal_error_code,
        "provenanceArtifacts": {name: str(path.relative_to(PROJECT_ROOT)).replace("\\", "/") for name, path in provenance_paths.items()},
        "partitions": [
            {name: record.get(name) for name in (
                "providerPartitionId", "requestParameters", "transportStatus", "byteLength", "rawSha256",
                "parsedRecordCount", "parsedTicksSha256", "firstTimestampUtc", "lastTimestampUtc", "acquisitionDisposition",
            )}
            for record in run.records
        ],
    }


def main(argv: list[str] | None = None) -> int:
    argument_parser = argparse.ArgumentParser(description="MO-R4A-S4-A1 exact one-attempt acquisition")
    argument_parser.add_argument("--write-authorization", action="store_true")
    argument_parser.add_argument("--execute-authorized-acquisition", action="store_true")
    argument_parser.add_argument("--private-root", type=Path)
    arguments = argument_parser.parse_args(argv)
    if arguments.write_authorization and arguments.execute_authorized_acquisition:
        raise AcquisitionError("CLI_ARGUMENT_CONFLICT", "write authorization and provider execution are separate operations")
    if arguments.write_authorization:
        path = write_acquisition_authorization(PROJECT_ROOT)
        print(json.dumps({"authorization": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")}, sort_keys=True))
        return 0
    if not arguments.execute_authorized_acquisition:
        raise AcquisitionError("EXECUTION_FLAG_REQUIRED", "no provider operation is available without the explicit execution flag")
    private_root = arguments.private_root or default_private_storage_root(PROJECT_ROOT)
    validate_preaccess(PROJECT_ROOT)
    transport, credential_source = resolve_boto3_transport_and_credential_source()
    run = acquire_authorized_partitions(
        project_root=PROJECT_ROOT,
        private_root=private_root,
        transport=transport,
        execute_authorized_acquisition=True,
    )
    provenance = write_committed_provenance(PROJECT_ROOT, run)
    summary = _cli_summary(run, provenance)
    summary["credentialSourceType"] = credential_source
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0 if run.terminal_error_code is None else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AcquisitionError as error:
        print(json.dumps({"milestone": MILESTONE, "status": error.code, "detail": error.detail}, sort_keys=True))
        raise SystemExit(2)
