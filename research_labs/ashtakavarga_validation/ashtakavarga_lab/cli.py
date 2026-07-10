from __future__ import annotations

import argparse
import json
from pathlib import Path

from .certification import certify
from .config import load_config, profile as get_profile, safe_output_path
from .ephemeris import configure
from .evaluation import (
    circular_shift_placebo,
    load_evidence,
    load_price,
    prepare_dataset,
    prepare_kas_dataset,
    walk_forward_report,
)
from .evidence import build_daily_evidence, natal_tables
from .external_check import compare_external_export, load_external_export
from .kas import corrected_event_worksheet
from .kas_evidence import build_daily_kas_evidence


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Isolated Ashtakavarga validation lab")
    root.add_argument("--config", default="lab_config.yaml")
    commands = root.add_subparsers(dest="command", required=True)

    certify_cmd = commands.add_parser("certify", help="Run internal arithmetic and published-fixture checks")
    certify_cmd.add_argument("--output", default="reports/certification_report.json")

    natal_cmd = commands.add_parser("natal", help="Build one reference profile's natal BAV/SAV report")
    natal_cmd.add_argument("--profile", required=True)
    natal_cmd.add_argument("--output", default="auto")

    evidence_cmd = commands.add_parser("evidence", help="Generate daily evidence rows")
    evidence_cmd.add_argument("--start", required=True)
    evidence_cmd.add_argument("--end", required=True)
    evidence_cmd.add_argument("--profiles", required=True)
    evidence_cmd.add_argument("--output", default="outputs/daily_evidence.parquet")

    external_cmd = commands.add_parser("compare-external", help="Compare all 96 values with an outside calculator export")
    external_cmd.add_argument("--input", required=True)
    external_cmd.add_argument("--output", default="auto")

    evaluate_cmd = commands.add_parser("evaluate", help="Run isolated USDJPY chronological evaluation")
    evaluate_cmd.add_argument("--price", required=True)
    evaluate_cmd.add_argument("--evidence", default="outputs/daily_evidence.parquet")
    evaluate_cmd.add_argument("--base-profile", default="usd_reference")
    evaluate_cmd.add_argument("--quote-profile", default="jpy_reference")
    evaluate_cmd.add_argument("--output", default="reports/usdjpy_walk_forward.json")

    kas_fixture_cmd = commands.add_parser("kas-fixture", help="Reproduce the corrected published Lesson 7 worksheet")
    kas_fixture_cmd.add_argument("--input", default="fixtures/kas_lesson7_marriage_corrected.json")
    kas_fixture_cmd.add_argument("--output", default="reports/kas_lesson7_fixture.json")

    kas_evidence_cmd = commands.add_parser("kas-evidence", help="Generate isolated corrected-KAS daily evidence")
    kas_evidence_cmd.add_argument("--start", required=True)
    kas_evidence_cmd.add_argument("--end", required=True)
    kas_evidence_cmd.add_argument("--profiles", required=True)
    kas_evidence_cmd.add_argument("--output", default="outputs/daily_kas_evidence.parquet")

    kas_evaluate_cmd = commands.add_parser("kas-evaluate", help="Evaluate all twelve frozen KAS event-house mappings")
    kas_evaluate_cmd.add_argument("--price", required=True)
    kas_evaluate_cmd.add_argument("--evidence", default="outputs/daily_kas_evidence.parquet")
    kas_evaluate_cmd.add_argument("--base-profile", default="usd_reference")
    kas_evaluate_cmd.add_argument("--quote-profile", default="jpy_reference")
    kas_evaluate_cmd.add_argument("--output", default="reports/usdjpy_kas_walk_forward.json")
    return root


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def main() -> None:
    args = parser().parse_args()
    config = load_config(args.config)
    configure(config)

    if args.command == "certify":
        output = safe_output_path(args.output, config)
        payload = certify()
        _write_json(output, payload)
        print(json.dumps({"output": str(output), **payload}, indent=2, default=str))
        return

    if args.command == "natal":
        get_profile(config, args.profile)
        output_name = f"reports/natal_{args.profile}.json" if args.output == "auto" else args.output
        output = safe_output_path(output_name, config)
        payload = natal_tables(config, args.profile)
        _write_json(output, payload)
        print(json.dumps({"output": str(output), "validation": payload["validation"]}, indent=2))
        return

    if args.command == "evidence":
        profiles = [item.strip() for item in args.profiles.split(",") if item.strip()]
        output = safe_output_path(args.output, config)
        frame = build_daily_evidence(config, profiles, args.start, args.end)
        if output.suffix.lower() in {".parquet", ".pq"}:
            frame.to_parquet(output, index=False)
        else:
            frame.to_csv(output, index=False)
        print(json.dumps({"output": str(output), "rows": len(frame), "profiles": profiles}, indent=2))
        return

    if args.command == "compare-external":
        payload = load_external_export(args.input)
        calculator = str(payload.get("calculator_name", "external")).strip().lower().replace(" ", "_")
        profile_id = str(payload.get("profile_id", "profile")).strip().lower().replace(" ", "_")
        output_name = f"reports/external_{calculator}_{profile_id}.json" if args.output == "auto" else args.output
        output = safe_output_path(output_name, config)
        report = compare_external_export(config, payload)
        _write_json(output, report)
        print(json.dumps({"output": str(output), **report}, indent=2))
        return

    if args.command == "evaluate":
        output = safe_output_path(args.output, config)
        evidence_path = Path(args.evidence)
        if not evidence_path.is_absolute():
            evidence_path = (Path(__file__).resolve().parents[1] / evidence_path).resolve()
        price = load_price(args.price)
        evidence = load_evidence(evidence_path)
        settings = config["evaluation"]
        dataset = prepare_dataset(
            price,
            evidence,
            args.base_profile,
            args.quote_profile,
            [int(value) for value in settings["horizons_trading_days"]],
        )
        report = walk_forward_report(
            dataset,
            [int(value) for value in settings["horizons_trading_days"]],
            int(settings["expanding_folds"]),
            float(settings["initial_train_fraction"]),
        )
        report.update(
            {
                "base_profile": args.base_profile,
                "quote_profile": args.quote_profile,
                "price_source": str(Path(args.price).resolve()),
                "evidence_source": str(evidence_path),
                "doctrine": config["doctrine"],
            }
        )
        _write_json(output, report)
        summary = [
            {
                "feature": item["feature"],
                "horizon_trading_days": item["horizon_trading_days"],
                "mapping": item["mapping"],
                "non_overlapping_observations": item["non_overlapping_observations"],
                "weighted_hit_rate": item["weighted_hit_rate"],
                "hit_rate_wilson_95": [item["hit_rate_wilson_95_low"], item["hit_rate_wilson_95_high"]],
                "hit_rate_normal_pvalue_vs_50": item["hit_rate_normal_pvalue_vs_50"],
                "positive_mean_return_folds": item["positive_mean_return_folds"],
            }
            for item in report["results"]
        ]
        print(json.dumps({"output": str(output), "dataset_rows": len(dataset), "summary": summary}, indent=2))
        return

    if args.command == "kas-fixture":
        source = Path(args.input)
        if not source.is_absolute():
            source = (Path(__file__).resolve().parents[1] / source).resolve()
        fixture = json.loads(source.read_text(encoding="utf-8"))
        report = corrected_event_worksheet(
            fixture["bav"], fixture["planet_signs"], fixture["lagna_sign"], fixture["house_b"]
        )
        checks = {
            "event_houses": report["event_houses"] == fixture["expected"]["event_houses"],
            "row3": report["row3_basic_strength"] == fixture["expected"]["row3"],
            "row5": report["row5_four_ten_transfer"] == fixture["expected"]["row5"],
            "row8": report["row8_de_bonus"] == fixture["expected"]["row8"],
            "row12": report["row12_house_aspects"] == fixture["expected"]["row12"],
            "row16": report["row16_planet_aspects"] == fixture["expected"]["row16"],
            "row17": report["row17_final_strength"] == fixture["expected"]["row17"],
            "ranking": report["ranking"] == fixture["expected"]["ranking"],
        }
        payload = {"passed": all(checks.values()), "checks": checks, "worksheet": report}
        output = safe_output_path(args.output, config)
        _write_json(output, payload)
        print(json.dumps({"output": str(output), "passed": payload["passed"], "checks": checks}, indent=2))
        return

    if args.command == "kas-evidence":
        profiles = [item.strip() for item in args.profiles.split(",") if item.strip()]
        output = safe_output_path(args.output, config)
        frame = build_daily_kas_evidence(config, profiles, args.start, args.end)
        if output.suffix.lower() in {".parquet", ".pq"}:
            frame.to_parquet(output, index=False)
        else:
            frame.to_csv(output, index=False)
        print(json.dumps({"output": str(output), "rows": len(frame), "profiles": profiles}, indent=2))
        return

    if args.command == "kas-evaluate":
        output = safe_output_path(args.output, config)
        evidence_path = Path(args.evidence)
        if not evidence_path.is_absolute():
            evidence_path = (Path(__file__).resolve().parents[1] / evidence_path).resolve()
        price = load_price(args.price)
        evidence = load_evidence(evidence_path)
        settings = config["evaluation"]
        horizons = [int(value) for value in settings["horizons_trading_days"]]
        feature_names = [
            "kas_ad_score_diff",
            "kas_ad_disposition_diff",
            "kas_sav_context_diff",
            "kas_js_context_diff",
            "kas_full_context_diff",
            "kas_full_sun_gated_diff",
            "kas_full_sector_1_diff",
            "kas_full_sector_2_diff",
            "kas_full_sector_3_diff",
            "kas_full_sun_sector_1_diff",
            "kas_full_sun_sector_2_diff",
            "kas_full_sun_sector_3_diff",
        ]
        house_reports = []
        datasets = {}
        for house_b in range(1, 13):
            dataset = prepare_kas_dataset(
                price, evidence, args.base_profile, args.quote_profile, house_b, horizons
            )
            datasets[house_b] = dataset
            report = walk_forward_report(
                dataset,
                horizons,
                int(settings["expanding_folds"]),
                float(settings["initial_train_fraction"]),
                features=feature_names,
            )
            report["house_b"] = house_b
            for result in report["results"]:
                result["circular_shift_placebo"] = circular_shift_placebo(
                    dataset,
                    result["feature"],
                    f"return_{result['horizon_trading_days']}d",
                    result["horizon_trading_days"],
                )
                gross = result["median_fold_mean_strategy_return_pct"]
                result["round_trip_cost_sensitivity"] = {
                    str(cost): (gross - cost / 100.0 if gross is not None else None)
                    for cost in settings.get("round_trip_cost_bps_sensitivity", [0, 1, 2, 5])
                }
            house_reports.append(report)
        tested_results = [result for report in house_reports for result in report["results"]]
        test_count = len(tested_results)
        for result in tested_results:
            raw = result["hit_rate_normal_pvalue_vs_50"]
            result["multiple_testing_family_size"] = test_count
            result["hit_rate_bonferroni_pvalue"] = min(1.0, raw * test_count) if raw is not None else None
        payload = {
            "status": "isolated_corrected_kas_experiment_no_promotion",
            "trade_signal_enabled": False,
            "base_profile": args.base_profile,
            "quote_profile": args.quote_profile,
            "price_source": str(Path(args.price).resolve()),
            "evidence_source": str(evidence_path),
            "house_selection_policy": "all_12_reported_no_post_outcome_selection",
            "methodology_ablations": feature_names,
            "multiple_testing_policy": "Bonferroni across every reported house, feature, horizon and mapping",
            "round_trip_cost_bps_sensitivity": settings.get("round_trip_cost_bps_sensitivity", [0, 1, 2, 5]),
            "house_reports": house_reports,
            "limitations": [
                "Raman adaptation is not exact Krushna ayanamsa reproduction",
                "event-house meaning for currency markets is unestablished, so all twelve are reported",
                "delay sector is observed, not outcome-fitted",
                "source-specific karaka rules are not mapped to financial markets",
                "outside-calculator certification remains incomplete",
                "no result can alter canonical trading or MT5",
            ],
        }
        _write_json(output, payload)
        print(json.dumps({"output": str(output), "houses": len(house_reports)}, indent=2))
        return

    raise RuntimeError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    main()
