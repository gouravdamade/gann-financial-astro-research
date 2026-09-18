"""External one-shot authorization verifier; no authorization is issued in R3R2A."""

from __future__ import annotations

from typing import Any, Mapping


class ExternalAuthorizationError(PermissionError):
    """Raised before a real worker could start without a future immutable record."""


REQUIRED_BINDINGS = frozenset({
    "implementationCommit", "freezeCommit", "finalExecutionContractHash", "runtimeManifestHash",
    "bundleManifestHash", "canonicalGitBundleAggregateHash", "loaderViewBundleAggregateHash",
    "populationHash", "populationOrderHash", "rowUniverseHash", "realV2BridgeHash",
    "realV2BridgePopulationHash", "aProtectedIdentity", "bProtectedIdentity", "v2ProtectedIdentity",
    "scientificWorkerRetryCount", "oneShotExecutionIntent", "marketOutcomeAccess",
})


def validate_external_authorization(record: Mapping[str, Any] | None, expected: Mapping[str, Any]) -> None:
    if not isinstance(record, Mapping) or record.get("authorized") is not True:
        raise ExternalAuthorizationError("no immutable external authorization record permits real Candidate C execution")
    if set(record) < REQUIRED_BINDINGS | {"authorized"}:
        raise ExternalAuthorizationError("external authorization record lacks mandatory bindings")
    if record.get("scientificWorkerRetryCount") != 0 or record.get("marketOutcomeAccess") is not False:
        raise ExternalAuthorizationError("external authorization violates frozen execution constraints")
    for key in REQUIRED_BINDINGS - {"scientificWorkerRetryCount", "marketOutcomeAccess"}:
        if record.get(key) != expected.get(key):
            raise ExternalAuthorizationError(f"external authorization binding mismatch: {key}")
