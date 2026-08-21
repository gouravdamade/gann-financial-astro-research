# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


app_root = Path(SPECPATH).parent.resolve()
project_root = app_root.parent
node_root = app_root / "node_modules" / "@openai"
sweph_root = Path(r"D:\Trading_Algo\Desktop_Trading_Algo_root_legacy_20260530\sweph")
chart_conditioned_profile_root = (
    project_root / "research_labs" / "chart_conditioned_aspects" / "profiles"
)
founder_review_root = (
    project_root / "research_labs" / "chart_conditioned_aspects" / "founder_review"
)
founder_review_identity_audit = (
    project_root / "status" / "audits" / "pfr_v2b_r5_f2a_r1_event_identity_integrity.json"
)
bphs_classical_timing_root = project_root / "research_labs" / "bphs_1899_classical_timing"
bphs_muhurta_fixture = bphs_classical_timing_root / "bphs_1899_packet_1w_muhurta_fixture.json"
xe1_experimental_evidence_root = project_root / "research_labs" / "experimental_evidence"
cgvo_root = project_root / "configs" / "research" / "cgvo"

required_files = [
    project_root / "astro_events_usdjpy_tn_raman_v2_20250301_20260310.parquet",
    project_root / "aspect_sr_touch_log_usdjpy_tn_raman_v2_20250301_20260310.csv",
    project_root / "usd_jpy_h1_mt5_metaquotes_demo_full.parquet",
    project_root / "usd_jpy_m30_mt5_metaquotes_demo_20250310_20260310.parquet",
    project_root / "gann_aspect_annotations_raman_v2.sqlite",
    app_root / "server" / "codexBridge.mjs",
    project_root / "configs" / "sbc" / "sources.yaml",
    app_root / "mt5" / "GannClockProbe.mq5",
    app_root / "mt5" / "GannClockProbe.ex5",
    Path(r"D:\node.exe"),
    sweph_root / "sepl_18.se1",
    sweph_root / "semo_18.se1",
    chart_conditioned_profile_root / "target_aware_polarity_catalogue_v1.json",
    chart_conditioned_profile_root / "target_aware_polarity_evidence_packets_v1.json",
    chart_conditioned_profile_root / "founder_chart_hypotheses_v1.json",
    founder_review_root / "USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json",
    founder_review_root / "USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json",
    founder_review_root / "JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json",
    founder_review_root / "JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json",
    founder_review_identity_audit,
    bphs_muhurta_fixture,
    cgvo_root / "varahamihira_eclipse_source_profile_v1.json",
    cgvo_root / "trailokya_geography_argha_context_v1.json",
    cgvo_root / "kurma_gazetteer_seed_v1.json",
    cgvo_root / "VARAHAMIHIRA_ASTRONOMICAL_FRAME_V1.yaml",
    cgvo_root / "VARAHAMIHIRA_LUNAR_MONTH_PROFILE_V1.yaml",
    cgvo_root / "VARAHAMIHIRA_ECLIPSE_ASPECT_PROFILE_V1.yaml",
    cgvo_root / "VARAHAMIHIRA_FIRMAMENT_GEOMETRY_V1.yaml",
    cgvo_root / "CGVO_S1_READINESS_MATRIX_V1.yaml",
    xe1_experimental_evidence_root / "fixtures" / "xe1_evidence_observations_v1.json",
    xe1_experimental_evidence_root / "fixtures" / "xe1_trial_ledger_v1.json",
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
    (str(project_root / "configs" / "sbc"), "configs/sbc"),
    (str(app_root / "mt5" / "GannClockProbe.mq5"), "mt5"),
    (str(app_root / "mt5" / "GannClockProbe.ex5"), "mt5"),
    # The chart-conditioned modules resolve their immutable JSON profiles
    # relative to the collected package root at runtime.
    (str(chart_conditioned_profile_root), "profiles"),
    # XE3 admits only the existing, hash-verified founder-review packets and
    # their independent identity audit. The writable review ledger remains in
    # the D: application-data store and is never bundled.
    (str(founder_review_root), "research_labs/chart_conditioned_aspects/founder_review"),
    (str(founder_review_identity_audit), "status/audits"),
    # The BPHS inspector resolves this explicit source fixture beneath
    # sys._MEIPASS when running in the collected Python sidecar.
    (str(bphs_muhurta_fixture), "research_labs/bphs_1899_classical_timing"),
    # CGVO keeps modern astronomy output separate from its source-ledger and
    # raw Kurma seed fixtures. They are read-only research inputs.
    (str(cgvo_root), "configs/research/cgvo"),
    # XE1 reads a compact, price-free fixture and immutable ledger from the
    # collected package. It never bundles source doctrine or market data here.
    (str(xe1_experimental_evidence_root), "research_labs/experimental_evidence"),
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
    "mt5_clock",
    "shadow_ledger",
    "candlestick_shadow",
    "prospective_refresh",
    "local_jyotish",
    "local_candlestick",
    "candlestick_analysis",
    "chakra_lab_service",
    "agarwal_source_inspector",
    "experimental_evidence_service",
    "founder_review_workbench",
    "xe2_scoped_evidence_service",
    "xe3_sign_admission_service",
    "cgvo_service",
    "decision_engine",
    "build_trade_candidates_from_touches",
    "doctrine_config",
    "panchanga_doctrine",
    "sbc",
    "sbc.audit_catalog",
    "sbc.audit_packages",
    "sbc.chakra_lab",
    "sbc.config",
    "sbc.ephemeris",
    "sbc.enums",
    "sbc.grid",
    "sbc.models",
    "sbc.nakshatra",
    "sbc.panchanga",
    "sbc.snapshot",
    "sbc.vedha",
    "research_labs.trailokya_arghya",
    "research_labs.trailokya_arghya.reconcile",
    "swisseph",
    "build_corrected_natal_event_source",
    "build_aspect_sr_touch_log",
    "planetary_lines",
    "collective_geometry",
    "collective_influence",
    "collective_motion",
    "collective_refinement",
    "chart_conditioned_aspects",
    "chart_conditioned_aspects.models",
    "chart_conditioned_aspects.polarity_catalogue",
    "chart_conditioned_aspects.polarity_evidence",
    "chart_conditioned_aspects.polarity_series",
    "instrument_relative_sbc",
    "instrument_relative_sbc.connector",
    "instrument_relative_sbc.models",
    "instrument_relative_sbc.profiles",
    "instrument_relative_sbc.scoring",
    "strict_shadbala_doctrine",
    "drik_bala_engine",
    "cryptography",
    "cryptography.hazmat.primitives.asymmetric.ed25519",
]

a = Analysis(
    [str(app_root / "backend_sidecar.py")],
    pathex=[
        str(app_root / "backend"),
        str(project_root),
        str(project_root / "research_labs" / "chart_conditioned_aspects"),
        str(project_root / "research_labs" / "instrument_relative_sbc"),
    ],
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
