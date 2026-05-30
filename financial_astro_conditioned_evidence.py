from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_FAMILIES = (
    "conjunction:JUPITER|MOON",
    "sextile:MARS|MOON",
    "trine:MOON|VENUS",
    "conjunction:MERCURY|MOON",
)

SIGN_ELEMENT = {
    "Aries": "fire",
    "Leo": "fire",
    "Sagittarius": "fire",
    "Taurus": "earth",
    "Virgo": "earth",
    "Capricorn": "earth",
    "Gemini": "air",
    "Libra": "air",
    "Aquarius": "air",
    "Cancer": "water",
    "Scorpio": "water",
    "Pisces": "water",
}

SIGN_MODALITY = {
    "Aries": "cardinal",
    "Cancer": "cardinal",
    "Libra": "cardinal",
    "Capricorn": "cardinal",
    "Taurus": "fixed",
    "Leo": "fixed",
    "Scorpio": "fixed",
    "Aquarius": "fixed",
    "Gemini": "mutable",
    "Virgo": "mutable",
    "Sagittarius": "mutable",
    "Pisces": "mutable",
}

SCAN_RECIPES = {
    "aspect_pair_tag": ["aspect", "pair_key", "shadbala_tag"],
    "aspect_pair_strength": ["aspect", "pair_key", "strength_pair"],
    "aspect_pair_retro": ["aspect", "pair_key", "retro_pair"],
    "aspect_pair_element": ["aspect", "pair_key", "element_pair"],
    "aspect_pair_modality": ["aspect", "pair_key", "modality_pair"],
    "aspect_pair_state": ["aspect", "pair_key", "state_pair"],
    "aspect_pair_aff": ["aspect", "pair_key", "aff_pair"],
    "aspect_pair_sign": ["aspect", "pair_key", "sign_pair"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Search for conditioned directional evidence in the astrology event log "
            "using pair-specific raw JSON fields plus a simple holdout check."
        )
    )
    parser.add_argument(
        "--data",
        default=r"D:\Trading_Algo\New folder\astro_training_data.parquet",
    )
    parser.add_argument(
        "--windows",
        default=(
            r"D:\Trading_Algo\New folder"
            r"\transit_impact_deep_report\event_windows_with_regimes.csv"
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=r"D:\PycharmProjects\astro_evidence_report",
    )
    parser.add_argument("--interval", default="1h")
    parser.add_argument("--direction-target", default="y_dir_1d")
    parser.add_argument("--min-total", type=int, default=20)
    parser.add_argument("--min-dir", type=int, default=18)
    parser.add_argument("--min-reversal", type=int, default=12)
    parser.add_argument("--min-holdout", type=int, default=8)
    parser.add_argument("--train-fraction", type=float, default=0.7)
    parser.add_argument("--reversal-threshold-pct", type=float, default=0.1)
    parser.add_argument(
        "--include-natal",
        action="store_true",
        default=False,
        help="Include natal events instead of dropping is_natal=true rows.",
    )
    parser.add_argument(
        "--families",
        nargs="*",
        default=list(DEFAULT_FAMILIES),
        help="Family priors in aspect:PAIR format. Example: conjunction:JUPITER|MOON",
    )
    return parser.parse_args()


def safe_json_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if value is None:
        return {}
    if isinstance(value, float) and not np.isfinite(value):
        return {}
    text = str(value).strip()
    if not text:
        return {}
    try:
        loaded = json.loads(text)
        return loaded if isinstance(loaded, dict) else {}
    except Exception:
        return {}


def canonical_pair(a: Any, b: Any) -> str:
    left = str(a).upper().strip()
    right = str(b).upper().strip()
    return "|".join(sorted((left, right)))


def parse_state_map(value: Any) -> dict[str, str]:
    states: dict[str, str] = {}
    if value is None:
        return states
    text = str(value).strip()
    if not text:
        return states
    for token in text.split("|"):
        token = token.strip()
        if not token or ":" not in token:
            continue
        planet_raw, state_raw = token.split(":", 1)
        states[planet_raw.strip().upper()] = state_raw.strip().upper().replace(" ", "_")
    return states


def strength_bucket(value: Any) -> str:
    try:
        strength = float(value)
    except Exception:
        return "NA"
    if not np.isfinite(strength):
        return "NA"
    if strength >= 75:
        return "VSTRONG"
    if strength >= 60:
        return "STRONG"
    if strength >= 45:
        return "NEUTRAL"
    return "WEAK"


def sign_element(sign_name: str) -> str:
    return SIGN_ELEMENT.get(str(sign_name).strip(), "NA")


def sign_modality(sign_name: str) -> str:
    return SIGN_MODALITY.get(str(sign_name).strip(), "NA")


def sign_with_threshold(value: Any, threshold_pct: float) -> int:
    try:
        number = float(value)
    except Exception:
        return 0
    if not np.isfinite(number) or abs(number) < threshold_pct:
        return 0
    return 1 if number > 0 else -1


def p_value_vs_baseline(successes: int, n: int, baseline_prob: float) -> float:
    if n <= 0:
        return float("nan")
    p0 = min(max(float(baseline_prob), 1e-9), 1.0 - 1e-9)
    variance = n * p0 * (1.0 - p0)
    if variance <= 0:
        return float("nan")
    z = (successes - n * p0) / math.sqrt(variance)
    cdf = 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0)))
    return float(max(0.0, min(1.0, 2.0 * (1.0 - cdf))))


def bh_qvalues(values: pd.Series) -> pd.Series:
    arr = values.to_numpy(dtype=float)
    finite_mask = np.isfinite(arr)
    out = np.full(len(arr), np.nan, dtype=float)
    if not finite_mask.any():
        return pd.Series(out, index=values.index)
    finite_idx = np.where(finite_mask)[0]
    finite_vals = arr[finite_mask]
    order = np.argsort(finite_vals)
    ranked_idx = finite_idx[order]
    ranked_vals = finite_vals[order]
    prev = 1.0
    total = len(ranked_vals)
    for i in range(total - 1, -1, -1):
        pv = ranked_vals[i]
        rank = i + 1
        qv = min(prev, pv * total / rank)
        prev = qv
        out[ranked_idx[i]] = qv
    return pd.Series(out, index=values.index)


def build_feature_columns(df: pd.DataFrame) -> pd.DataFrame:
    sign_pair: list[str] = []
    element_pair: list[str] = []
    modality_pair: list[str] = []
    retro_pair: list[str] = []
    strength_pair: list[str] = []
    state_pair: list[str] = []
    aff_pair: list[str] = []

    for _, row in df.iterrows():
        pair_a, pair_b = str(row["pair_key"]).split("|", 1)
        signs = safe_json_dict(row.get("planet_signs_json"))
        retro = safe_json_dict(row.get("planet_retro_json"))
        strengths = safe_json_dict(row.get("planet_strengths_json"))
        afflictions = safe_json_dict(row.get("planet_afflictions_json"))
        states = parse_state_map(row.get("planet_states"))

        sign_a = str(signs.get(pair_a, "NA")).strip() or "NA"
        sign_b = str(signs.get(pair_b, "NA")).strip() or "NA"
        sign_pair.append(f"{sign_a}|{sign_b}")
        element_pair.append(f"{sign_element(sign_a)}|{sign_element(sign_b)}")
        modality_pair.append(f"{sign_modality(sign_a)}|{sign_modality(sign_b)}")

        retro_a = int(float(retro.get(pair_a, 0)) > 0.5) if str(retro.get(pair_a, 0)).strip() else 0
        retro_b = int(float(retro.get(pair_b, 0)) > 0.5) if str(retro.get(pair_b, 0)).strip() else 0
        retro_pair.append(f"{retro_a}|{retro_b}")

        strength_pair.append(
            f"{strength_bucket(strengths.get(pair_a))}|{strength_bucket(strengths.get(pair_b))}"
        )
        state_pair.append(f"{states.get(pair_a, 'NA')}|{states.get(pair_b, 'NA')}")

        aff_a = str(afflictions.get(pair_a, "None")).strip().upper()
        aff_b = str(afflictions.get(pair_b, "None")).strip().upper()
        aff_pair.append(
            f"{'AFF' if aff_a and aff_a != 'NONE' else 'NONE'}|"
            f"{'AFF' if aff_b and aff_b != 'NONE' else 'NONE'}"
        )

    out = df.copy()
    out["sign_pair"] = sign_pair
    out["element_pair"] = element_pair
    out["modality_pair"] = modality_pair
    out["retro_pair"] = retro_pair
    out["strength_pair"] = strength_pair
    out["state_pair"] = state_pair
    out["aff_pair"] = aff_pair
    return out


def load_dataset(args: argparse.Namespace) -> pd.DataFrame:
    df = pd.read_parquet(args.data)
    if "is_natal" in df.columns and not args.include_natal:
        df = df[~df["is_natal"].astype(bool)].copy()
    if "interval" in df.columns:
        df = df[df["interval"].astype(str).str.lower() == args.interval.lower()].copy()
    if df.empty:
        raise RuntimeError("No rows left after transit/interval filtering.")

    df["pair_key"] = [canonical_pair(a, b) for a, b in zip(df["b1"], df["b2"], strict=False)]
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    windows = pd.read_csv(args.windows)
    windows["event_id"] = windows["event_id"].astype(str)
    df["event_id"] = df["event_id"].astype(str)
    needed_cols = [
        "event_id",
        "ret_pre_24h_pct",
        "ret_post_24h_pct",
        "ret_post_72h_pct",
        "trend_regime",
        "vol_regime",
    ]
    df = df.merge(windows[needed_cols], on="event_id", how="left")

    df = build_feature_columns(df)

    pre_sign = df["ret_pre_24h_pct"].map(lambda v: sign_with_threshold(v, args.reversal_threshold_pct))
    post24_sign = df["ret_post_24h_pct"].map(lambda v: sign_with_threshold(v, args.reversal_threshold_pct))
    post72_sign = df["ret_post_72h_pct"].map(lambda v: sign_with_threshold(v, args.reversal_threshold_pct))
    df["reversal_valid_24h"] = ((pre_sign != 0) & (post24_sign != 0)).astype(int)
    df["reversal_valid_72h"] = ((pre_sign != 0) & (post72_sign != 0)).astype(int)
    df["reversal_24h"] = ((pre_sign != 0) & (post24_sign != 0) & (pre_sign != post24_sign)).astype(int)
    df["reversal_72h"] = ((pre_sign != 0) & (post72_sign != 0) & (pre_sign != post72_sign)).astype(int)
    return df


def broad_scan(df: pd.DataFrame, args: argparse.Namespace) -> tuple[pd.DataFrame, dict[str, float]]:
    direction_target = args.direction_target
    dir_df = df[df[direction_target].astype(str).str.upper().isin(["UP", "DOWN"])].copy()
    dir_df["_up"] = dir_df[direction_target].astype(str).str.upper().eq("UP").astype(int)
    baseline_up = float(dir_df["_up"].mean())
    baseline_rev24 = float(df.loc[df["reversal_valid_24h"] == 1, "reversal_24h"].mean())
    baseline_rev72 = float(df.loc[df["reversal_valid_72h"] == 1, "reversal_72h"].mean())

    rows: list[dict[str, Any]] = []
    for recipe_name, group_cols in SCAN_RECIPES.items():
        grouped = df.groupby(group_cols, dropna=False, sort=False)
        for key, group in grouped:
            total_n = len(group)
            min_total = args.min_total if recipe_name != "aspect_pair_sign" else max(15, args.min_total - 5)
            min_dir = args.min_dir if recipe_name != "aspect_pair_sign" else max(12, args.min_dir - 6)
            if total_n < min_total:
                continue

            dir_group = group[group[direction_target].astype(str).str.upper().isin(["UP", "DOWN"])]
            dir_n = len(dir_group)
            if dir_n < min_dir:
                continue

            rev24_group = group[group["reversal_valid_24h"] == 1]
            rev72_group = group[group["reversal_valid_72h"] == 1]
            if max(len(rev24_group), len(rev72_group)) < args.min_reversal:
                continue

            key_values = list(key) if isinstance(key, tuple) else [key]
            key_map = dict(zip(group_cols, key_values, strict=False))

            up_n = int(dir_group[direction_target].astype(str).str.upper().eq("UP").sum())
            up_prob = float(up_n / dir_n)
            rev24_rate = float(rev24_group["reversal_24h"].mean()) if len(rev24_group) else float("nan")
            rev72_rate = float(rev72_group["reversal_72h"].mean()) if len(rev72_group) else float("nan")

            rows.append(
                {
                    "recipe": recipe_name,
                    **key_map,
                    "samples_total": total_n,
                    "samples_dir": dir_n,
                    "up_prob": up_prob,
                    "up_lift": up_prob - baseline_up,
                    "p_dir": p_value_vs_baseline(up_n, dir_n, baseline_up),
                    "mean_delta_1d": float(pd.to_numeric(group.get("delta_1d"), errors="coerce").mean()),
                    "samples_rev24": len(rev24_group),
                    "rev24_rate": rev24_rate,
                    "rev24_lift": rev24_rate - baseline_rev24 if len(rev24_group) else float("nan"),
                    "p_rev24": (
                        p_value_vs_baseline(
                            int(rev24_group["reversal_24h"].sum()),
                            len(rev24_group),
                            baseline_rev24,
                        )
                        if len(rev24_group)
                        else float("nan")
                    ),
                    "samples_rev72": len(rev72_group),
                    "rev72_rate": rev72_rate,
                    "rev72_lift": rev72_rate - baseline_rev72 if len(rev72_group) else float("nan"),
                    "p_rev72": (
                        p_value_vs_baseline(
                            int(rev72_group["reversal_72h"].sum()),
                            len(rev72_group),
                            baseline_rev72,
                        )
                        if len(rev72_group)
                        else float("nan")
                    ),
                }
            )

    scan = pd.DataFrame(rows)
    if scan.empty:
        raise RuntimeError("Broad scan produced no eligible groups. Lower support thresholds.")
    scan["q_dir"] = bh_qvalues(scan["p_dir"])
    scan["q_rev24"] = bh_qvalues(scan["p_rev24"])
    scan["q_rev72"] = bh_qvalues(scan["p_rev72"])
    scan = scan.sort_values(["q_dir", "p_dir", "samples_dir"], ascending=[True, True, False]).reset_index(drop=True)

    baselines = {
        "baseline_up": baseline_up,
        "baseline_rev24": baseline_rev24,
        "baseline_rev72": baseline_rev72,
    }
    return scan, baselines


def holdout_family_check(df: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    direction_target = args.direction_target
    dir_df = df[df[direction_target].astype(str).str.upper().isin(["UP", "DOWN"])].copy()
    dir_df["_up"] = dir_df[direction_target].astype(str).str.upper().eq("UP").astype(int)
    cut_idx = int(len(dir_df) * args.train_fraction)
    split_time = dir_df["timestamp"].sort_values().iloc[cut_idx]
    train = dir_df[dir_df["timestamp"] < split_time].copy()
    test = dir_df[dir_df["timestamp"] >= split_time].copy()
    base_train = float(train["_up"].mean())
    base_test = float(test["_up"].mean())

    condition_cols = ["shadbala_tag", "strength_pair", "retro_pair", "element_pair", "state_pair", "sign_pair"]
    rows: list[dict[str, Any]] = []
    for family in args.families:
        if ":" not in family:
            raise ValueError(f"Invalid family prior: {family}")
        aspect, pair_key = family.split(":", 1)
        train_family = train[(train["aspect"] == aspect) & (train["pair_key"] == pair_key)].copy()
        test_family = test[(test["aspect"] == aspect) & (test["pair_key"] == pair_key)].copy()
        if train_family.empty or test_family.empty:
            continue

        rows.append(
            {
                "family_scope": "base_family",
                "aspect": aspect,
                "pair_key": pair_key,
                "condition_col": "",
                "condition_value": "",
                "train_n": len(train_family),
                "train_up_prob": float(train_family["_up"].mean()),
                "train_lift": float(train_family["_up"].mean() - base_train),
                "test_n": len(test_family),
                "test_up_prob": float(test_family["_up"].mean()),
                "test_lift": float(test_family["_up"].mean() - base_test),
                "test_p": p_value_vs_baseline(int(test_family["_up"].sum()), len(test_family), base_test),
                "same_sign": bool(
                    np.sign(train_family["_up"].mean() - base_train)
                    == np.sign(test_family["_up"].mean() - base_test)
                ),
            }
        )

        for column in condition_cols:
            candidates: list[tuple[float, str, int, float]] = []
            for value, group in train_family.groupby(column, dropna=False):
                if len(group) < max(15, args.min_dir - 3):
                    continue
                train_prob = float(group["_up"].mean())
                score = abs(train_prob - base_train) * math.sqrt(len(group))
                candidates.append((score, str(value), len(group), train_prob))
            candidates.sort(reverse=True)

            kept = 0
            for score, value, train_n, train_prob in candidates:
                if kept >= 5:
                    break
                test_group = test_family[test_family[column].astype(str) == value]
                if len(test_group) < args.min_holdout:
                    continue
                kept += 1
                test_prob = float(test_group["_up"].mean())
                rows.append(
                    {
                        "family_scope": "conditioned_family",
                        "aspect": aspect,
                        "pair_key": pair_key,
                        "condition_col": column,
                        "condition_value": value,
                        "train_n": train_n,
                        "train_up_prob": train_prob,
                        "train_lift": train_prob - base_train,
                        "test_n": len(test_group),
                        "test_up_prob": test_prob,
                        "test_lift": test_prob - base_test,
                        "test_p": p_value_vs_baseline(
                            int(test_group["_up"].sum()),
                            len(test_group),
                            base_test,
                        ),
                        "same_sign": bool(np.sign(train_prob - base_train) == np.sign(test_prob - base_test)),
                    }
                )

    holdout = pd.DataFrame(rows)
    if not holdout.empty:
        holdout = holdout.sort_values(
            ["same_sign", "test_p", "test_n"],
            ascending=[False, True, False],
        ).reset_index(drop=True)
    return holdout


def write_summary(
    out_dir: Path,
    df: pd.DataFrame,
    baselines: dict[str, float],
    scan: pd.DataFrame,
    holdout: pd.DataFrame,
) -> None:
    direction_nominal = scan[scan["p_dir"] < 0.05].copy()
    reversal_nominal = scan[scan["p_rev24"] < 0.05].copy()
    direction_fdr = scan[scan["q_dir"] < 0.25].copy()
    reversal_fdr = scan[scan["q_rev24"] < 0.25].copy()
    stable_holdout = holdout[(holdout["same_sign"]) & (holdout["test_p"] < 0.10)].copy()

    lines = [
        "=== Conditioned Financial Astrology Evidence ===",
        f"Rows scanned: {len(df)}",
        f"Direction baseline UP rate: {baselines['baseline_up']:.4f}",
        f"Reversal baseline 24h rate: {baselines['baseline_rev24']:.4f}",
        f"Reversal baseline 72h rate: {baselines['baseline_rev72']:.4f}",
        "",
        f"Broad direction groups tested: {len(scan)}",
        f"Direction groups with nominal p < 0.05: {len(direction_nominal)}",
        f"Direction groups with q < 0.25: {len(direction_fdr)}",
        f"Reversal groups with nominal p < 0.05: {len(reversal_nominal)}",
        f"Reversal groups with q < 0.25: {len(reversal_fdr)}",
        "",
        "Best holdout-stable directional families:",
    ]

    if stable_holdout.empty:
        lines.append("None passed the simple holdout filter.")
    else:
        preview = stable_holdout.head(10)[
            [
                "family_scope",
                "aspect",
                "pair_key",
                "condition_col",
                "condition_value",
                "train_n",
                "test_n",
                "train_lift",
                "test_lift",
                "test_p",
            ]
        ]
        lines.extend(preview.to_string(index=False).splitlines())

    lines.extend(
        [
            "",
            "Interpretation:",
            "- Use holdout-stable groups as priors, not proof of causality.",
            "- If broad scan q-values stay weak, the edge is narrow and should flow into ML, not hard-coded rules.",
            "- Reversal evidence should be treated as aggregate unless a family remains stable out-of-sample.",
        ]
    )

    (out_dir / "summary.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_dataset(args)
    scan, baselines = broad_scan(df, args)
    holdout = holdout_family_check(df, args)

    scan.to_csv(out_dir / "broad_scan.csv", index=False)
    scan[scan["p_dir"] < 0.05].to_csv(out_dir / "direction_nominal_candidates.csv", index=False)
    scan[scan["p_rev24"] < 0.05].to_csv(out_dir / "reversal24_nominal_candidates.csv", index=False)
    holdout.to_csv(out_dir / "holdout_family_direction.csv", index=False)
    write_summary(out_dir, df, baselines, scan, holdout)

    print((out_dir / "summary.txt").read_text(encoding="utf-8"))
    print()
    print("Saved:", out_dir / "broad_scan.csv")
    print("Saved:", out_dir / "direction_nominal_candidates.csv")
    print("Saved:", out_dir / "reversal24_nominal_candidates.csv")
    print("Saved:", out_dir / "holdout_family_direction.csv")


if __name__ == "__main__":
    main()
