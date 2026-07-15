from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from usdjpy_walk_forward import (
    DEFAULT_CONTRACT_PATH,
    PATTERN_FEATURE_COLUMNS,
    PROJECT_ROOT,
    RAW_FEATURE_COLUMNS,
    build_decision_dataset,
    file_sha256,
    load_contract,
    load_price_source,
    resolve_source_path,
)


ARTIFACT_CONTRACT = "GANN_CANDLESTICK_FROZEN_MODEL_ARTIFACT_V1"
MODEL_CONTRACT = "GANN_CANDLESTICK_TRANSPARENT_LOGISTIC_MODEL_V1"
DEFAULT_OUTPUT_PATH = Path(__file__).with_name("usdjpy_shadow_model_v1.json")


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest().upper()


def frozen_logistic_model(
    dataset: Any,
    features: tuple[str, ...],
    name: str,
    contract: dict[str, Any],
) -> dict[str, Any]:
    models = contract["models"]
    pipeline = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    C=float(models["logisticC"]),
                    class_weight=str(models["classWeight"]),
                    max_iter=2000,
                    random_state=int(models["randomSeed"]),
                    solver="liblinear",
                ),
            ),
        ]
    )
    pipeline.fit(dataset.loc[:, features], dataset["target_up"].to_numpy(dtype=int))
    scaler = pipeline.named_steps["scale"]
    model = pipeline.named_steps["model"]
    if model.coef_.shape != (1, len(features)) or model.intercept_.shape != (1,):
        raise ValueError(f"Unexpected binary model shape for {name}")
    payload = {
        "contract": MODEL_CONTRACT,
        "name": name,
        "features": list(features),
        "scalerMean": np.asarray(scaler.mean_, dtype=float).tolist(),
        "scalerScale": np.asarray(scaler.scale_, dtype=float).tolist(),
        "coefficients": np.asarray(model.coef_[0], dtype=float).tolist(),
        "intercept": float(model.intercept_[0]),
        "classes": [int(value) for value in model.classes_],
        "shortProbability": float(models["shortProbability"]),
        "longProbability": float(models["longProbability"]),
        "trainingRows": int(len(dataset)),
        "positiveRows": int(dataset["target_up"].sum()),
        "negativeRows": int(len(dataset) - dataset["target_up"].sum()),
    }
    payload["modelId"] = fingerprint(payload)
    probabilities = pipeline.predict_proba(dataset.loc[:, features])[:, 1]
    payload["trainingProbabilityRange"] = {
        "minimum": float(probabilities.min()),
        "maximum": float(probabilities.max()),
    }
    return payload


def freeze_model(contract_path: Path, output_path: Path) -> dict[str, Any]:
    contract_path = contract_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()
    contract = load_contract(contract_path)
    source_path = resolve_source_path(contract, PROJECT_ROOT)
    frame = load_price_source(source_path, contract)
    dataset = build_decision_dataset(frame, contract)
    primary = frozen_logistic_model(
        dataset,
        PATTERN_FEATURE_COLUMNS,
        "named_pattern_logistic_v1",
        contract,
    )
    diagnostic = frozen_logistic_model(
        dataset,
        RAW_FEATURE_COLUMNS,
        "raw_geometry_logistic_v1",
        contract,
    )
    artifact: dict[str, Any] = {
        "contract": ARTIFACT_CONTRACT,
        "status": "prospective_shadow_research_only",
        "frozenAtUtc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "symbol": str(contract["symbol"]),
        "timeframe": str(contract["timeframe"]),
        "geometryMethodologyVersion": str(contract["geometryMethodologyVersion"]),
        "evaluationContract": str(contract["contract"]),
        "evaluationContractSha256": file_sha256(contract_path),
        "source": {
            "pathLabel": source_path.name,
            "sha256": file_sha256(source_path),
            "immutableForStudy": True,
        },
        "training": {
            "rows": int(len(dataset)),
            "firstFeatureAvailableAtUtc": dataset["feature_available_time"].iloc[0].isoformat(),
            "lastFeatureAvailableAtUtc": dataset["feature_available_time"].iloc[-1].isoformat(),
            "lastLabelAvailableAtUtc": dataset["label_available_time"].max().isoformat(),
            "fitRule": "all frozen historical rows with the six-bar label present in the immutable source",
            "retuningAllowed": False,
        },
        "decision": {
            **contract["decision"],
            "captureGraceMinutes": 15,
            "lateDecisionBackfillAllowed": False,
        },
        "costs": contract["costs"],
        "primaryModel": primary,
        "diagnosticModels": [diagnostic],
        "retrospectiveGate": {
            "status": "failed",
            "primaryCandidate": "named_pattern_logistic_v1",
            "reason": "The frozen retrospective walk-forward primary produced zero threshold-qualified trades.",
            "promotionAuthorized": False,
        },
        "guardrails": {
            "consumedByAstrologyRules": False,
            "consumedByAutoSuggest": False,
            "consumedByOfficialMlNotes": False,
            "consumedByCoordinator": False,
            "executionAllowed": False,
            "mt5ReadOnly": True,
        },
    }
    identity = dict(artifact)
    identity.pop("frozenAtUtc", None)
    artifact["artifactId"] = fingerprint(identity)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Freeze the failed V1 USDJPY candle candidates for prospective shadow observation."
    )
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    arguments = parser.parse_args()
    artifact = freeze_model(arguments.contract, arguments.output)
    print(
        json.dumps(
            {
                "output": str(arguments.output.expanduser().resolve()),
                "artifactId": artifact["artifactId"],
                "trainingRows": artifact["training"]["rows"],
                "primaryModelId": artifact["primaryModel"]["modelId"],
                "diagnosticModelId": artifact["diagnosticModels"][0]["modelId"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
