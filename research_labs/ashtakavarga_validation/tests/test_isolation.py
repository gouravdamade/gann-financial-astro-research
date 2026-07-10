from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "ashtakavarga_lab"
FORBIDDEN = {
    "aspect_annotation_store",
    "build_aspect_sr_touch_log",
    "build_btc_weekly_astro_chart",
    "build_repeatation_review_pack",
    "codex_review_task_queue",
    "doctrine_config",
    "mt5_trade_executor",
    "serve_repeatation_pack",
}


class IsolationTests(unittest.TestCase):
    def test_package_does_not_import_main_project_or_mt5_modules(self):
        violations = []
        for source in PACKAGE.glob("*.py"):
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names.extend(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names.append(node.module.split(".")[0])
                for name in names:
                    if name in FORBIDDEN or name in {"MetaTrader5", "ollama", "openai"}:
                        violations.append(f"{source.name}: {name}")
        self.assertEqual(violations, [])

    def test_config_keeps_all_execution_integrations_disabled(self):
        import yaml

        config = yaml.safe_load((ROOT / "lab_config.yaml").read_text(encoding="utf-8"))
        isolation = config["isolation"]
        self.assertFalse(isolation["trading_enabled"])
        self.assertFalse(isolation["mt5_enabled"])
        self.assertFalse(isolation["auto_suggest_enabled"])
        self.assertFalse(isolation["llm_enabled"])


if __name__ == "__main__":
    unittest.main()
