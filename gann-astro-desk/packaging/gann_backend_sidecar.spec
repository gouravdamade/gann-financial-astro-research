# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


app_root = Path(SPECPATH).parent.resolve()
project_root = app_root.parent
node_root = app_root / "node_modules" / "@openai"
sweph_root = Path(r"D:\Trading_Algo\Desktop_Trading_Algo_root_legacy_20260530\sweph")

required_files = [
    project_root / "astro_events_usdjpy_tn_raman_v2_20250301_20260310.parquet",
    project_root / "aspect_sr_touch_log_usdjpy_tn_raman_v2_20250301_20260310.csv",
    project_root / "usd_jpy_h1_mt5_metaquotes_demo_full.parquet",
    project_root / "usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet",
    project_root / "gann_aspect_annotations_raman_v2.sqlite",
    app_root / "server" / "codexBridge.mjs",
    project_root / "jyotish_agent" / "corpus_chunks.jsonl",
    project_root / "candlestick_agent" / "corpus_chunks.jsonl",
    Path(r"D:\node.exe"),
    sweph_root / "sepl_18.se1",
    sweph_root / "semo_18.se1",
]
missing = [str(path) for path in required_files if not path.exists()]
if missing:
    raise FileNotFoundError("Missing backend sidecar package inputs:\n" + "\n".join(missing))

datas = [
    (str(project_root / "astro_events_usdjpy_tn_raman_v2_20250301_20260310.parquet"), "."),
    (str(project_root / "aspect_sr_touch_log_usdjpy_tn_raman_v2_20250301_20260310.csv"), "."),
    (str(project_root / "usd_jpy_h1_mt5_metaquotes_demo_full.parquet"), "."),
    (str(project_root / "usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet"), "."),
    (str(project_root / "gann_aspect_annotations_raman_v2.sqlite"), "."),
    (str(sweph_root / "sepl_18.se1"), "sweph"),
    (str(sweph_root / "semo_18.se1"), "sweph"),
    (str(app_root / "server" / "codexBridge.mjs"), "codex/server"),
    (str(project_root / "jyotish_agent" / "corpus_chunks.jsonl"), "jyotish"),
    (str(project_root / "candlestick_agent" / "corpus_chunks.jsonl"), "candlestick"),
    (r"D:\node.exe", "codex"),
    (str(node_root / "codex-sdk"), "codex/node_modules/@openai/codex-sdk"),
    (str(node_root / "codex"), "codex/node_modules/@openai/codex"),
    (str(node_root / "codex-win32-x64"), "codex/node_modules/@openai/codex-win32-x64"),
]

hiddenimports = [
    "server",
    "repository",
    "chart_layouts",
    "generation",
    "mt5_gateway",
    "shadow_ledger",
    "prospective_refresh",
    "local_jyotish",
    "local_candlestick",
    "candlestick_analysis",
    "decision_engine",
    "build_trade_candidates_from_touches",
    "doctrine_config",
    "build_corrected_natal_event_source",
    "build_aspect_sr_touch_log",
]

a = Analysis(
    [str(app_root / "backend_sidecar.py")],
    pathex=[str(app_root / "backend"), str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "IPython",
        "clr_loader",
        "cv2",
        "lightgbm",
        "matplotlib",
        "notebook",
        "numba",
        "pygments",
        "pytest",
        "pythonnet",
        "scipy",
        "sklearn",
        "statsmodels",
        "sympy",
        "tensorflow",
        "torch",
        "transformers",
        "webview",
        "xgboost",
    ],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GannAstroBackend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="GannAstroBackend",
)
