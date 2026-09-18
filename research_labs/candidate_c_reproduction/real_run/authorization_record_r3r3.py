"""Self-hashed, data-driven external authorization for the future one-shot run."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .canonical import self_hash


class ExternalAuthorizationError(PermissionError):
    """Raised before a real Candidate C worker can be issued a ticket."""


REQUIRED = frozenset({
    "schemaVersion", "authorizationId", "authorized", "authorizationRecordHash",
    "R3R3ImplementationCommit", "R3R3FreezeCommit", "R3R3FinalExecutionContractHash",
    "R3R3RuntimeManifestHash", "bundleManifestHash", "canonicalGitBundleAggregateHash",
    "loaderViewBundleAggregateHash", "dependencyInventoryHash", "renderedPathsHash",
    "populationHash", "populationOrderHash", "rowUniverseHash", "realV2BridgeHash",
    "realV2BridgePopulationHash", "aProtectedIdentity", "bProtectedIdentity",
    "v2ProtectedIdentity", "scientificWorkerRetryCount", "oneShotExecutionIntent",
    "marketOutcomeAccess",
})


@dataclass(frozen=True)
class ValidatedRealRunAuthorization:
    """Private construction proves that bindings and the canonical self-hash passed."""

    record: Mapping[str, Any]

    @property
    def authorization_hash(self) -> str:
        return str(self.record["authorizationRecordHash"])


def validate_external_authorization(record: Mapping[str, Any] | None, expected: Mapping[str, Any]) -> ValidatedRealRunAuthorization:
    if not isinstance(record, Mapping) or record.get("authorized") is not True:
        raise ExternalAuthorizationError("no immutable external authorization record permits real Candidate C execution")
    if not REQUIRED.issubset(record):
        raise ExternalAuthorizationError("external authorization record lacks mandatory bindings")
    if record.get("authorizationRecordHash") != self_hash(dict(record), "authorizationRecordHash"):
        raise ExternalAuthorizationError("external authorization self-hash mismatch")
    if record.get("scientificWorkerRetryCount") != 0 or record.get("marketOutcomeAccess") is not False:
        raise ExternalAuthorizationError("external authorization violates frozen execution constraints")
    for key in REQUIRED - {"schemaVersion", "authorizationId", "authorized", "authorizationRecordHash", "scientificWorkerRetryCount", "oneShotExecutionIntent", "marketOutcomeAccess"}:
        if record.get(key) != expected.get(key):
            raise ExternalAuthorizationError(f"external authorization binding mismatch: {key}")
    if record.get("oneShotExecutionIntent") is not True:
        raise ExternalAuthorizationError("external authorization is not one-shot")
    return ValidatedRealRunAuthorization(dict(record))
