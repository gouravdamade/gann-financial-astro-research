from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def key_map_from_group(group_cols: list[str], key: Any) -> dict[str, Any]:
    key_values = list(key) if isinstance(key, tuple) else [key]
    return {c: key_values[i] if i < len(key_values) else np.nan for i, c in enumerate(group_cols)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze SR-anchored pair-aspect events for directional edge and reversal behavior."
        )
    )
    parser.add_argument(
        "--input",
        default=r"C:\Users\ADMIN\PycharmProjects\planetary_pair_aspect_market_log_sr.csv",
        help="Input SR event log CSV.",
    )
    parser.add_argument(
        "--output-dir",
        default=r"C:\Users\ADMIN\PycharmProjects\astro_sr_analysis_report",
        help="Folder to save evidence CSVs and summary.",
    )
    parser.add_argument("--min-n", type=int, default=25)
    parser.add_argument("--train-fraction", type=float, default=0.70)
    parser.add_argument(
        "--min-holdout",
        type=int,
        default=12,
        help="Minimum test rows for holdout groups.",
    )
    parser.add_argument(
        "--q-max",
        type=float,
        default=0.25,
        help="FDR threshold for shortlist.",
    )
    parser.add_argument(
        "--include-flat",
        action="store_true",
        help="Include FLAT movement rows in directional scan.",
    )
    return parser.parse_args()


def normal_two_sided_pvalue(successes: int, n: int, p0: float) -> float:
    if n <= 0 or p0 <= 0 or p0 >= 1 or not np.isfinite(p0):
        return float("nan")
    if not np.isfinite(successes) or successes < 0 or successes > n:
        return float("nan")
    var = n * p0 * (1.0 - p0)
    if var <= 0:
        return float("nan")
    z = (float(successes) - n * p0) / math.sqrt(var)
    tail = 0.5 * (1.0 + math.erf(abs(z) / math.sqrt(2.0)))
    return float(max(0.0, min(1.0, 2.0 * (1.0 - tail))))


def benjamini_hochberg(values: pd.Series) -> pd.Series:
    arr = values.to_numpy(dtype=float)
    m = np.isfinite(arr)
    out = pd.Series(np.full(len(arr), np.nan, dtype=float), index=values.index)
    if not m.any():
        return out

    idx = np.where(m)[0]
    vals = arr[idx]
    order = np.argsort(vals)
    sorted_idx = idx[order]
    sorted_vals = vals[order]
    total = len(sorted_vals)

    next_q = 1.0
    for rank in range(total - 1, -1, -1):
        q = min(next_q, sorted_vals[rank] * total / (rank + 1))
        next_q = q
        out.iloc[sorted_idx[rank]] = q
    return out


def make_target_columns(df: pd.DataFrame, include_flat: bool = False) -> pd.DataFrame:
    df = df.copy()
    for c in ["ret_after_24h_pct", "ret_after_72h_pct", "ret_during_pct"]:
        v = pd.to_numeric(df[c], errors="coerce")
        df[c] = v
        label = {
            "ret_after_24h_pct": "dir_after_24h",
            "ret_after_72h_pct": "dir_after_72h",
            "ret_during_pct": "dir_during",
        }[c]
        dir_series = pd.Series(np.nan, index=df.index, dtype="object")
        dir_series.loc[v > 0] = "UP"
        dir_series.loc[v < 0] = "DOWN"
        if include_flat:
            dir_series = dir_series.fillna("FLAT")
        df[label] = dir_series

    df["timestamp_utc"] = pd.to_datetime(df["event_time_utc"], errors="coerce", utc=True)
    return df


def group_scan(
    df: pd.DataFrame,
    group_cols: list[str],
    target_col: str,
    baseline: float,
    min_n: int,
) -> pd.DataFrame:
    valid = df[df[target_col].isin(["UP", "DOWN"])].copy()
    if valid.empty:
        return pd.DataFrame()

    rows: list[dict[str, Any]] = []
    for key, sub in valid.groupby(group_cols, dropna=False, sort=False):
        n = len(sub)
        if n < min_n:
            continue

        up_n = int((sub[target_col] == "UP").sum())
        up_prob = up_n / n
        # Additional metrics for ML usefulness.
        if target_col == "dir_after_24h":
            ret_key = "ret_after_24h_pct"
        elif target_col == "dir_after_72h":
            ret_key = "ret_after_72h_pct"
        else:
            ret_key = "ret_during_pct"
        ret = pd.to_numeric(sub[ret_key], errors="coerce")
        mean_ret = float(ret.mean())
        med_ret = float(ret.median())
        median_after = float(ret.median())

        key_map = key_map_from_group(group_cols, key)
        rows.append(
            {
                "target": target_col,
                "features": "|".join(group_cols),
                "n": n,
                "up_n": up_n,
                "up_prob": up_prob,
                "lift_vs_baseline": up_prob - baseline,
                "p_dir": normal_two_sided_pvalue(up_n, n, baseline),
                "mean_ret_pct": mean_ret,
                "median_ret_pct": med_ret,
                "median_after_pct": median_after,
                **key_map,
            }
        )

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    out["q_dir"] = benjamini_hochberg(out["p_dir"])
    out["direction"] = np.where(
        out["lift_vs_baseline"] > 0,
        "UP",
        np.where(out["lift_vs_baseline"] < 0, "DOWN", "FLAT"),
    )
    return out.sort_values(
        ["q_dir", "p_dir", "n"],
        ascending=[True, True, False],
    ).reset_index(drop=True)


def reversal_scan(df: pd.DataFrame, group_cols: list[str], min_n: int) -> pd.DataFrame:
    if "line_reversal_after" not in df.columns:
        return pd.DataFrame()

    rev = pd.to_numeric(df["line_reversal_after"], errors="coerce")
    rows: list[dict[str, Any]] = []
    baseline = float(rev.dropna().mean()) if rev.notna().any() else np.nan
    if not np.isfinite(baseline):
        return pd.DataFrame()

    for key, sub in df.groupby(group_cols, dropna=False, sort=False):
        n = len(sub)
        if n < min_n:
            continue
        sub_rev = sub["line_reversal_after"].fillna(0)
        up_n = int(sub_rev.sum())
        up_prob = up_n / n
        key_map = key_map_from_group(group_cols, key)
        rows.append(
            {
                "target": "line_reversal_after",
                "features": "|".join(group_cols),
                "n": n,
                "up_n": up_n,
                "up_prob": up_prob,
                "lift_vs_baseline": up_prob - baseline,
                "p_dir": normal_two_sided_pvalue(up_n, n, baseline),
                "mean_ret_pct": float(pd.to_numeric(sub["ret_after_24h_pct"], errors="coerce").mean()),
                "median_ret_pct": float(pd.to_numeric(sub["ret_after_24h_pct"], errors="coerce").median()),
                "median_after_pct": float(pd.to_numeric(sub["ret_after_24h_pct"], errors="coerce").median()),
                **key_map,
            }
        )

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["q_dir"] = benjamini_hochberg(out["p_dir"])
    out["direction"] = np.where(
        out["lift_vs_baseline"] > 0, "UP", np.where(out["lift_vs_baseline"] < 0, "DOWN", "FLAT")
    )
    return out.sort_values(["q_dir", "p_dir", "n"], ascending=[True, True, False]).reset_index(drop=True)


def holdout_stability_scan(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    train_fraction: float,
    min_holdout: int,
) -> pd.DataFrame:
    valid = df[df[target_col].isin(["UP", "DOWN"])].copy()
    if valid.empty:
        return pd.DataFrame()

    cutoff = valid["timestamp_utc"].quantile(train_fraction)
    train = valid[valid["timestamp_utc"] < cutoff].copy()
    test = valid[valid["timestamp_utc"] >= cutoff].copy()
    if train.empty or test.empty:
        return pd.DataFrame()

    train_base = float((train[target_col] == "UP").mean())
    test_base = float((test[target_col] == "UP").mean())

    rows: list[dict[str, Any]] = []
    for key, sub_train in train.groupby(feature_cols, dropna=False, sort=False):
        n_train = len(sub_train)
        if n_train < max(2 * min_holdout, 30):
            continue
        if not isinstance(key, tuple):
            key = (key,)
        query = [(c, key[i] if i < len(key) else None) for i, c in enumerate(feature_cols)]

        sub_test = test.copy()
        for col, value in query:
            sub_test = sub_test[sub_test[col] == value]
        if len(sub_test) < min_holdout:
            continue

        train_up = float((sub_train[target_col] == "UP").mean())
        test_up = float((sub_test[target_col] == "UP").mean())
        key_map = key_map_from_group(feature_cols, key)
        rows.append(
            {
                "target": target_col,
                "features": "|".join(feature_cols),
                "n_train": int(n_train),
                "n_test": int(len(sub_test)),
                "train_up_prob": train_up,
                "test_up_prob": test_up,
                "train_lift": train_up - train_base,
                "test_lift": test_up - test_base,
                "sign_match": int(np.sign(train_up - train_base) == np.sign(test_up - test_base)),
                "p_test": normal_two_sided_pvalue(int((sub_test[target_col] == "UP").sum()), len(sub_test), test_base),
                "q_test": np.nan,
                **key_map,
            }
        )
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows)
    out["q_test"] = benjamini_hochberg(out["p_test"])
    out = out.sort_values(["sign_match", "p_test", "n_test"], ascending=[False, True, False]).reset_index(drop=True)
    return out


def render_table(df: pd.DataFrame, columns: list[str], limit: int = 10) -> list[str]:
    keep = [c for c in columns if c in df.columns]
    if not keep or df.empty:
        return ["- none"]
    return df[keep].head(limit).to_string(index=False).splitlines()


def make_summary(out: pd.DataFrame, scan_24: pd.DataFrame, scan_72: pd.DataFrame, rev_scan: pd.DataFrame, holdout_24: pd.DataFrame, holdout_72: pd.DataFrame, min_n: int, q_max: float) -> str:
    dir_base_24 = out["dir_after_24h"].isin(["UP", "DOWN"])
    base24 = float((out.loc[dir_base_24, "dir_after_24h"] == "UP").mean())
    base72 = float((out.loc[out["dir_after_72h"].isin(["UP", "DOWN"]), "dir_after_72h"] == "UP").mean())

    lines = [
        "=== SR Pair/Aspect Evidence Report ===",
        f"Input rows: {len(out)}",
        f"Target sample size (24h): {int(dir_base_24.sum())}, baseline UP: {base24:.4f}",
        f"Target sample size (72h): {int((out['dir_after_72h'].isin(['UP','DOWN']).sum()))}, baseline UP: {base72:.4f}",
        f"Groups scanned (24h): {len(scan_24)}",
        f"Groups scanned (72h): {len(scan_72)}",
        f"Reversal groups scanned: {len(rev_scan)}",
        f"Holdout groups (24h): {len(holdout_24)}",
        f"Holdout groups (72h): {len(holdout_72)}",
        "",
        f"Top 24h directional findings with q < {q_max}:",
    ]

    for qcol, scan_df, label in [
        ("q_dir", scan_24, "24h directional"),
        ("q_dir", scan_72, "72h directional"),
        ("q_dir", rev_scan, "24h reversal-after"),
    ]:
        subset = scan_df[scan_df[qcol] < q_max].copy()
        if subset.empty:
            lines.append(f"- {label}: none")
            continue
        lines.append(f"- {label}: {len(subset)} groups")
        lines.extend(
            render_table(
                subset,
                [
                    "features",
                    "target",
                    "n",
                    "up_prob",
                    "lift_vs_baseline",
                    "p_dir",
                    "q_dir",
                    "pair_key",
                    "aspect",
                    "anchor_planet",
                    "anchor_mode",
                    "line_touch_after",
                    "line_touch_during",
                    "nearest_side_line",
                ],
            )
        )

    lines.extend(["", f"Top pure pair/aspect groups with q < {q_max}:"])
    pair_24 = scan_24[(scan_24["features"] == "pair_key|aspect") & (scan_24["q_dir"] < q_max)]
    pair_72 = scan_72[(scan_72["features"] == "pair_key|aspect") & (scan_72["q_dir"] < q_max)]
    pair_rev = rev_scan[(rev_scan["features"] == "pair_key|aspect") & (rev_scan["q_dir"] < q_max)]
    lines.append("- 24h pair/aspect")
    lines.extend(render_table(pair_24, ["pair_key", "aspect", "n", "up_prob", "lift_vs_baseline", "p_dir", "q_dir"]))
    lines.append("- 72h pair/aspect")
    lines.extend(render_table(pair_72, ["pair_key", "aspect", "n", "up_prob", "lift_vs_baseline", "p_dir", "q_dir"]))
    lines.append("- reversal pair/aspect")
    lines.extend(render_table(pair_rev, ["pair_key", "aspect", "n", "up_prob", "lift_vs_baseline", "p_dir", "q_dir"]))

    lines.extend(
        [
            "",
            f"Holdout-stable directional groups (24h, p<0.20, n_test>={min_n}):",
        ]
    )
    stable_24 = holdout_24[(holdout_24["p_test"] < 0.20) & (holdout_24["n_test"] >= min_n)]
    if stable_24.empty:
        lines.append("- none")
    else:
        lines.extend(
            render_table(
                stable_24,
                [
                    "features",
                    "pair_key",
                    "aspect",
                    "anchor_planet",
                    "anchor_mode",
                    "line_touch_after",
                    "line_touch_during",
                    "n_train",
                    "n_test",
                    "train_up_prob",
                    "test_up_prob",
                    "train_lift",
                    "test_lift",
                    "sign_match",
                    "p_test",
                ],
                limit=20,
            )
        )

    lines.extend(
        [
            "",
            f"Holdout-stable directional groups (72h, p<0.20, n_test>={min_n}):",
        ]
    )
    stable_72 = holdout_72[(holdout_72["p_test"] < 0.20) & (holdout_72["n_test"] >= min_n)]
    if stable_72.empty:
        lines.append("- none")
    else:
        lines.extend(
            render_table(
                stable_72,
                [
                    "features",
                    "pair_key",
                    "aspect",
                    "anchor_planet",
                    "anchor_mode",
                    "line_touch_after",
                    "line_touch_during",
                    "n_train",
                    "n_test",
                    "train_up_prob",
                    "test_up_prob",
                    "train_lift",
                    "test_lift",
                    "sign_match",
                    "p_test",
                ],
                limit=20,
            )
        )

    lines.extend(
        [
            "",
            "Interpretation notes:",
            "- Prefer groups with q<0.25 and reasonable test support (>=12).",
            "- Use these as candidate features, not standalone entry rules.",
            "- Weak out-of-sample stability suggests keeping this in ML feature space rather than hard filters.",
        ]
    )
    return "\n".join(lines)


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    expected = {
        "pair_key",
        "aspect",
        "anchor_planet",
        "anchor_mode",
        "line_touch_after",
        "line_touch_during",
        "line_reversal_after",
        "ret_after_24h_pct",
        "ret_after_72h_pct",
        "ret_during_pct",
    }
    missing = sorted(expected - set(df.columns))
    if missing:
        raise RuntimeError(f"Missing required columns in input: {missing}")
    # Normalize bool-like columns that can be strings in CSV exports.
    for col in ["line_touch_after", "line_touch_during", "line_reversal_after"]:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].map(lambda x: str(x).strip().lower() in {"1", "true", "yes"})
    return df


def main() -> None:
    args = parse_args()
    df = load_data(args.input)
    df = make_target_columns(df, include_flat=args.include_flat)

    # Baseline rates for directional targets.
    base24_valid = df["dir_after_24h"].isin(["UP", "DOWN"])
    base72_valid = df["dir_after_72h"].isin(["UP", "DOWN"])
    base24 = float((df.loc[base24_valid, "dir_after_24h"] == "UP").mean())
    base72 = float((df.loc[base72_valid, "dir_after_72h"] == "UP").mean())

    feature_sets = [
        ["pair_key", "aspect"],
        ["pair_key", "aspect", "line_touch_after"],
        ["pair_key", "aspect", "line_touch_during"],
        ["pair_key", "aspect", "anchor_planet", "anchor_mode"],
        ["anchor_planet", "anchor_mode"],
        ["anchor_planet", "anchor_mode", "line_touch_after"],
        ["anchor_planet", "anchor_degree", "anchor_mode"],
        ["pair_key", "aspect", "anchor_planet", "anchor_mode", "line_touch_after"],
    ]
    reversal_feature_sets = [
        ["pair_key", "aspect"],
        ["pair_key", "aspect", "line_touch_after"],
        ["pair_key", "aspect", "line_touch_during"],
        ["pair_key", "aspect", "anchor_planet", "anchor_mode"],
        ["anchor_planet", "anchor_mode"],
        ["anchor_planet", "anchor_mode", "line_touch_after"],
    ]

    scans: list[pd.DataFrame] = []
    for cols in feature_sets:
        scans.append(group_scan(df, cols, "dir_after_24h", base24, args.min_n))
        scans.append(group_scan(df, cols, "dir_after_72h", base72, args.min_n))

    for cols in reversal_feature_sets:
        scans.append(reversal_scan(df, cols, args.min_n))
    all_scans = pd.concat([s for s in scans if not s.empty], ignore_index=True)

    holdout_24 = pd.concat(
        [
            holdout_stability_scan(df, cols, "dir_after_24h", args.train_fraction, args.min_holdout)
            for cols in feature_sets[:6]
        ],
        ignore_index=True,
    )
    holdout_72 = pd.concat(
        [
            holdout_stability_scan(df, cols, "dir_after_72h", args.train_fraction, args.min_holdout)
            for cols in feature_sets[:6]
        ],
        ignore_index=True,
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not all_scans.empty:
        all_scans.to_csv(out_dir / "sr_broad_scan.csv", index=False)
        all_scans[all_scans["q_dir"] < 0.05].to_csv(
            out_dir / "sr_broad_scan_q05.csv", index=False
        )
        all_scans[all_scans["q_dir"] < args.q_max].to_csv(
            out_dir / "sr_broad_scan_qmax.csv", index=False
        )
        scan_24 = all_scans[all_scans["target"] == "dir_after_24h"].copy()
        scan_72 = all_scans[all_scans["target"] == "dir_after_72h"].copy()
        rev_scan = all_scans[all_scans["target"] == "line_reversal_after"].copy()
        scan_24[scan_24["features"] == "pair_key|aspect"].to_csv(out_dir / "sr_pair_aspect_24h.csv", index=False)
        scan_72[scan_72["features"] == "pair_key|aspect"].to_csv(out_dir / "sr_pair_aspect_72h.csv", index=False)
        scan_24[scan_24["features"] == "pair_key|aspect|line_touch_after"].to_csv(
            out_dir / "sr_pair_aspect_touch_after_24h.csv", index=False
        )
        scan_72[scan_72["features"] == "pair_key|aspect|line_touch_after"].to_csv(
            out_dir / "sr_pair_aspect_touch_after_72h.csv", index=False
        )
        rev_scan[rev_scan["features"] == "pair_key|aspect"].to_csv(out_dir / "sr_pair_aspect_reversal.csv", index=False)
    if not holdout_24.empty:
        holdout_24.to_csv(out_dir / "sr_holdout_24h.csv", index=False)
    if not holdout_72.empty:
        holdout_72.to_csv(out_dir / "sr_holdout_72h.csv", index=False)

    scan_24 = all_scans[all_scans["target"] == "dir_after_24h"].copy()
    scan_72 = all_scans[all_scans["target"] == "dir_after_72h"].copy()
    rev_scan = all_scans[all_scans["target"] == "line_reversal_after"].copy()
    summary = make_summary(df, scan_24, scan_72, rev_scan, holdout_24, holdout_72, args.min_holdout, args.q_max)
    (out_dir / "sr_evidence_summary.txt").write_text(summary, encoding="utf-8")

    print(summary)
    print(f"\nSaved report dir: {out_dir}")
    print(f"Saved: {out_dir / 'sr_broad_scan.csv'}")
    print(f"Saved: {out_dir / 'sr_evidence_summary.txt'}")


if __name__ == "__main__":
    main()
