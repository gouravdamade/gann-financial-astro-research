from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

from .enums import StringEnum
from .grid import (
    CERTIFIED_LAYER_VALUES,
    SBC_NAKSHATRAS_28,
    CompiledGrid,
    GridCitation,
    GridEntry,
    compile_grid,
)
from .models import to_primitive


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VEDHA_PROFILE_ROOT = PROJECT_ROOT / "configs" / "sbc" / "vedha"

SELECTION_POLICY = "EXPLICIT_ONLY"
GUIDANCE_MODEL_ID = "EXPERIMENTAL_NORMALIZED_GUIDANCE_V1"
FINANCIAL_VALIDATION_STATUS = "NOT_VALIDATED"

PROFILE_KEYS = {
    "schema_version",
    "vedha_profile_id",
    "grid_profile_id",
    "status",
    "authority",
    "selection_policy",
    "compile_enabled",
    "citations",
    "target_layers",
    "direction_geometry",
    "motion_rules",
    "nature_rules",
    "guidance_model",
    "worked_examples",
    "blocked_capabilities",
    "notes",
}
CITATION_KEYS = {"source_id", "locator", "rule_scope"}
DIRECTION_GEOMETRY_KEYS = {"LEFT", "FRONT", "RIGHT"}
MOTION_RULE_KEYS = {
    "fixed_directions",
    "variable_bodies",
    "motion_to_direction",
}
NATURE_RULE_KEYS = {
    "natural_benefics",
    "natural_malefics",
    "conditional_bodies",
}
GUIDANCE_MODEL_KEYS = {
    "model_id",
    "base_evidence_unit",
    "benefic_sign",
    "malefic_sign",
    "conditional_sign",
    "modifiers",
    "modifier_combination_policy",
    "financial_validation_status",
    "guidance_only",
}
WORKED_EXAMPLE_KEYS = {"source_nakshatra", "expected_targets", "locator"}


class VedhaDirection(StringEnum):
    LEFT = "LEFT"
    FRONT = "FRONT"
    RIGHT = "RIGHT"


class MotionClass(StringEnum):
    DIRECT_SWIFT = "DIRECT_SWIFT"
    MEAN = "MEAN"
    RETROGRADE = "RETROGRADE"


class PlanetNature(StringEnum):
    BENEFIC = "BENEFIC"
    MALEFIC = "MALEFIC"
    CONDITIONAL = "CONDITIONAL"


class DignityState(StringEnum):
    ORDINARY = "ORDINARY"
    EXALTED = "EXALTED"
    DEBILITATED = "DEBILITATED"


class VedhaProfileBlockedError(ValueError):
    """Raised when a Vedha profile cannot pass its source fixtures."""


class VedhaMotionRequiredError(ValueError):
    """Raised when a variable-speed planet lacks an explicit motion class."""


@dataclass(frozen=True)
class VedhaCitation:
    source_id: str
    locator: str
    rule_scope: str


@dataclass(frozen=True)
class VedhaWorkedExample:
    source_nakshatra: str
    expected_targets: tuple[str, ...]
    locator: str


@dataclass(frozen=True)
class VedhaProfileDefinition:
    vedha_profile_id: str
    profile_hash: str
    grid_profile_id: str
    status: str
    authority: str
    selection_policy: str
    compile_enabled: bool
    citations: tuple[VedhaCitation, ...]
    target_layers: tuple[str, ...]
    direction_geometry: dict[str, str]
    fixed_directions: dict[str, tuple[VedhaDirection, ...]]
    variable_bodies: tuple[str, ...]
    motion_to_direction: dict[MotionClass, VedhaDirection]
    natural_benefics: tuple[str, ...]
    natural_malefics: tuple[str, ...]
    conditional_bodies: tuple[str, ...]
    base_evidence_unit: float
    benefic_sign: float
    malefic_sign: float
    modifiers: dict[str, float]
    modifier_combination_policy: str
    worked_examples: tuple[VedhaWorkedExample, ...]
    blocked_capabilities: tuple[str, ...]
    raw: dict[str, Any]


@dataclass(frozen=True)
class VedhaActor:
    body: str
    source_nakshatra: str
    motion_class: MotionClass | str | None = None
    nature: PlanetNature | str | None = None
    dignity: DignityState | str = DignityState.ORDINARY
    moon_is_waning: bool | None = None
    mercury_association_nature: PlanetNature | str | None = None


@dataclass(frozen=True)
class VedhaTarget:
    source_nakshatra: str
    direction: VedhaDirection
    row: int
    column: int
    layer: str
    value: str
    semantic_role: str | None
    witness_set_id: str
    evidence_status: str
    citations: tuple[GridCitation, ...]

    @property
    def target_key(self) -> str:
        return f"{self.layer}:{self.value}"


@dataclass(frozen=True)
class VedhaActorResolution:
    body: str
    source_nakshatra: str
    direction: VedhaDirection
    direction_reason: str
    nature: PlanetNature
    nature_reason: str
    effective_multiplier: float | None
    multiplier_status: str
    multiplier_reason: str
    targets: tuple[VedhaTarget, ...]


@dataclass(frozen=True)
class VedhaContribution:
    body: str
    source_nakshatra: str
    direction: VedhaDirection
    target: VedhaTarget
    nature: PlanetNature
    effective_multiplier: float | None
    signed_guidance_units: float | None
    status: str
    explanation: str


@dataclass(frozen=True)
class VedhaGuidanceReport:
    schema_version: str
    vedha_profile_id: str
    vedha_profile_hash: str
    grid_profile_id: str
    grid_profile_hash: str
    guidance_model_id: str
    guidance_only: bool
    financial_validation_status: str
    actor_resolutions: tuple[VedhaActorResolution, ...]
    contributions: tuple[VedhaContribution, ...]
    favorable_guidance_units: float
    adverse_guidance_units: float
    net_guidance_units: float
    normalized_guidance_score: float
    guidance_band: str
    matched_target_count: int
    scored_match_count: int
    unresolved_match_count: int
    scoring_coverage_ratio: float
    blocked_capabilities: tuple[str, ...]
    citations: tuple[VedhaCitation, ...]

    def to_dict(self) -> dict[str, Any]:
        return to_primitive(self)


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return loaded


def _reject_unknown(mapping: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise ValueError(f"Unknown {label} fields: {', '.join(unknown)}")


def _required_text(mapping: Mapping[str, Any], key: str, label: str) -> str:
    value = str(mapping.get(key, "")).strip()
    if not value:
        raise ValueError(f"{label} requires {key}")
    return value


def _canonical_hash(value: dict[str, Any]) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def _unique_upper_strings(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty list")
    normalized = tuple(str(item).strip().upper() for item in value)
    if any(not item for item in normalized) or len(normalized) != len(set(normalized)):
        raise ValueError(f"{label} must contain unique non-empty values")
    return normalized


def _enum_value(enum_type: type[StringEnum], value: Any, label: str) -> StringEnum:
    try:
        return enum_type(str(value).strip().upper())
    except ValueError as exc:
        allowed = ", ".join(item.value for item in enum_type)
        raise ValueError(f"{label} must be one of: {allowed}") from exc


def validate_vedha_profile(
    raw: dict[str, Any],
    known_source_ids: Iterable[str],
) -> VedhaProfileDefinition:
    _reject_unknown(raw, PROFILE_KEYS, "Vedha profile")
    if int(raw.get("schema_version", 0)) != 1:
        raise ValueError("Vedha profile schema_version must be 1")

    profile_id = _required_text(raw, "vedha_profile_id", "Vedha profile")
    grid_profile_id = _required_text(raw, "grid_profile_id", profile_id)
    selection_policy = _required_text(raw, "selection_policy", profile_id)
    if selection_policy != SELECTION_POLICY:
        raise ValueError("Vedha profiles must use EXPLICIT_ONLY selection")
    if not bool(raw.get("compile_enabled", False)):
        raise VedhaProfileBlockedError(f"{profile_id} is not compile-enabled")

    citations_raw = raw.get("citations")
    if not isinstance(citations_raw, list) or not citations_raw:
        raise ValueError("Vedha profile citations must be a non-empty list")
    known = set(known_source_ids)
    citations: list[VedhaCitation] = []
    for item in citations_raw:
        if not isinstance(item, dict):
            raise ValueError("every Vedha citation must be a mapping")
        _reject_unknown(item, CITATION_KEYS, "Vedha citation")
        source_id = _required_text(item, "source_id", "Vedha citation")
        if source_id not in known:
            raise ValueError(f"Vedha profile has unresolved source ID: {source_id}")
        citations.append(
            VedhaCitation(
                source_id=source_id,
                locator=_required_text(item, "locator", source_id),
                rule_scope=_required_text(item, "rule_scope", source_id),
            )
        )

    target_layers = _unique_upper_strings(raw.get("target_layers"), "target_layers")
    if not set(target_layers) <= set(CERTIFIED_LAYER_VALUES):
        raise ValueError("target_layers contains an uncertified grid layer")
    if "WEEKDAY" in target_layers:
        raise ValueError("WEEKDAY is not a target layer in the cited worked examples")

    geometry_raw = raw.get("direction_geometry")
    if not isinstance(geometry_raw, dict):
        raise ValueError("direction_geometry must be a mapping")
    _reject_unknown(geometry_raw, DIRECTION_GEOMETRY_KEYS, "direction geometry")
    if set(geometry_raw) != DIRECTION_GEOMETRY_KEYS:
        raise ValueError("direction_geometry requires LEFT, FRONT, and RIGHT")
    direction_geometry = {
        key: _required_text(geometry_raw, key, "direction geometry")
        for key in sorted(DIRECTION_GEOMETRY_KEYS)
    }
    expected_geometry = {
        "LEFT": "INWARD_PLUS_FIGURE_LEFT_DIAGONAL",
        "FRONT": "OPPOSITE_OUTER_NAKSHATRA_ONLY",
        "RIGHT": "INWARD_PLUS_FIGURE_RIGHT_DIAGONAL",
    }
    if direction_geometry != expected_geometry:
        raise ValueError("unsupported or silently changed Vedha geometry")

    motion_raw = raw.get("motion_rules")
    if not isinstance(motion_raw, dict):
        raise ValueError("motion_rules must be a mapping")
    _reject_unknown(motion_raw, MOTION_RULE_KEYS, "motion rules")
    fixed_raw = motion_raw.get("fixed_directions")
    mapping_raw = motion_raw.get("motion_to_direction")
    if not isinstance(fixed_raw, dict) or not isinstance(mapping_raw, dict):
        raise ValueError("fixed_directions and motion_to_direction must be mappings")
    fixed_directions: dict[str, tuple[VedhaDirection, ...]] = {}
    for raw_body, raw_directions in fixed_raw.items():
        body = str(raw_body).strip().upper()
        values = raw_directions if isinstance(raw_directions, list) else [raw_directions]
        directions = tuple(
            VedhaDirection(str(direction).strip().upper()) for direction in values
        )
        if not directions or len(set(directions)) != len(directions):
            raise ValueError(f"fixed Vedha directions for {body} must be unique and non-empty")
        fixed_directions[body] = directions
    expected_single = {
        "SUN": (VedhaDirection.LEFT,),
        "MOON": (VedhaDirection.LEFT,),
        "RAHU": (VedhaDirection.RIGHT,),
        "KETU": (VedhaDirection.RIGHT,),
    }
    all_three = (
        VedhaDirection.LEFT,
        VedhaDirection.FRONT,
        VedhaDirection.RIGHT,
    )
    expected_all_three = {body: all_three for body in expected_single}
    if fixed_directions != expected_single and fixed_directions != expected_all_three:
        raise ValueError("fixed Vedha directions drifted from a cited source profile")
    variable_bodies = _unique_upper_strings(
        motion_raw.get("variable_bodies"), "variable_bodies"
    )
    if set(variable_bodies) != {"MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"}:
        raise ValueError("variable_bodies must be the five planets from Mars onward")
    motion_to_direction = {
        MotionClass(str(motion).strip().upper()): VedhaDirection(
            str(direction).strip().upper()
        )
        for motion, direction in mapping_raw.items()
    }
    expected_motion = {
        MotionClass.DIRECT_SWIFT: VedhaDirection.LEFT,
        MotionClass.MEAN: VedhaDirection.FRONT,
        MotionClass.RETROGRADE: VedhaDirection.RIGHT,
    }
    if motion_to_direction != expected_motion:
        raise ValueError("motion-to-direction rules drifted from the cited profile")

    nature_raw = raw.get("nature_rules")
    if not isinstance(nature_raw, dict):
        raise ValueError("nature_rules must be a mapping")
    _reject_unknown(nature_raw, NATURE_RULE_KEYS, "nature rules")
    natural_benefics = _unique_upper_strings(
        nature_raw.get("natural_benefics"), "natural_benefics"
    )
    natural_malefics = _unique_upper_strings(
        nature_raw.get("natural_malefics"), "natural_malefics"
    )
    conditional_bodies = _unique_upper_strings(
        nature_raw.get("conditional_bodies"), "conditional_bodies"
    )
    if set(natural_benefics) != {"JUPITER", "VENUS"}:
        raise ValueError("natural_benefics drifted from the cited profile")
    if set(natural_malefics) != {"SATURN", "SUN", "RAHU", "KETU", "MARS"}:
        raise ValueError("natural_malefics drifted from the cited profile")
    if set(conditional_bodies) != {"MERCURY", "MOON"}:
        raise ValueError("conditional_bodies must contain Mercury and Moon")

    guidance_raw = raw.get("guidance_model")
    if not isinstance(guidance_raw, dict):
        raise ValueError("guidance_model must be a mapping")
    _reject_unknown(guidance_raw, GUIDANCE_MODEL_KEYS, "guidance model")
    if _required_text(guidance_raw, "model_id", profile_id) != GUIDANCE_MODEL_ID:
        raise ValueError(f"guidance model must be {GUIDANCE_MODEL_ID}")
    if (
        _required_text(guidance_raw, "financial_validation_status", profile_id)
        != FINANCIAL_VALIDATION_STATUS
    ):
        raise ValueError("financial validation must remain NOT_VALIDATED")
    if guidance_raw.get("guidance_only") is not True:
        raise ValueError("Vedha profile must remain guidance_only")
    conditional_sign = guidance_raw.get("conditional_sign")
    if conditional_sign is not None:
        raise ValueError("conditional_sign must be null so uncertainty is not scored")
    modifiers_raw = guidance_raw.get("modifiers")
    if not isinstance(modifiers_raw, dict):
        raise ValueError("guidance modifiers must be a mapping")
    modifiers = {
        str(name).strip().upper(): float(value) for name, value in modifiers_raw.items()
    }
    expected_modifiers = {
        "ORDINARY": 1.0,
        "RETROGRADE": 2.0,
        "EXALTED": 3.0,
        "DEBILITATED": 0.5,
    }
    if modifiers != expected_modifiers:
        raise ValueError("guidance modifiers drifted from the cited source")
    modifier_policy = _required_text(
        guidance_raw, "modifier_combination_policy", profile_id
    )
    if modifier_policy != "BLOCK_RETROGRADE_WITH_NON_ORDINARY_DIGNITY":
        raise ValueError("modifier combination policy must fail closed")

    examples_raw = raw.get("worked_examples")
    if not isinstance(examples_raw, list) or len(examples_raw) < 3:
        raise ValueError("at least three worked examples are required")
    worked_examples: list[VedhaWorkedExample] = []
    for item in examples_raw:
        if not isinstance(item, dict):
            raise ValueError("every worked example must be a mapping")
        _reject_unknown(item, WORKED_EXAMPLE_KEYS, "worked example")
        source_nakshatra = _required_text(
            item, "source_nakshatra", "worked example"
        ).upper()
        if source_nakshatra not in SBC_NAKSHATRAS_28:
            raise ValueError(f"unknown worked-example nakshatra: {source_nakshatra}")
        expected_targets = _unique_upper_strings(
            item.get("expected_targets"), f"{source_nakshatra} expected_targets"
        )
        worked_examples.append(
            VedhaWorkedExample(
                source_nakshatra=source_nakshatra,
                expected_targets=expected_targets,
                locator=_required_text(item, "locator", source_nakshatra),
            )
        )
    if len({item.source_nakshatra for item in worked_examples}) != len(worked_examples):
        raise ValueError("worked_examples contains duplicate source nakshatras")

    blocked_capabilities = _unique_upper_strings(
        raw.get("blocked_capabilities"), "blocked_capabilities"
    )
    required_blocks = {
        "AUTOMATIC_DIRECT_SPEED_CLASSIFICATION",
        "SPECIAL_CORNER_JUNCTION_RULES",
        "MODIFIER_STACKING",
        "CLASSICAL_NATAL_SEVERITY_TRANSLATION",
        "FINANCIAL_LABELS",
        "TRADES",
        "MT5_EXECUTION",
    }
    if not required_blocks <= set(blocked_capabilities):
        raise ValueError("Vedha profile is missing required research locks")

    return VedhaProfileDefinition(
        vedha_profile_id=profile_id,
        profile_hash=_canonical_hash(raw),
        grid_profile_id=grid_profile_id,
        status=_required_text(raw, "status", profile_id),
        authority=_required_text(raw, "authority", profile_id),
        selection_policy=selection_policy,
        compile_enabled=True,
        citations=tuple(citations),
        target_layers=target_layers,
        direction_geometry=direction_geometry,
        fixed_directions=fixed_directions,
        variable_bodies=variable_bodies,
        motion_to_direction=motion_to_direction,
        natural_benefics=natural_benefics,
        natural_malefics=natural_malefics,
        conditional_bodies=conditional_bodies,
        base_evidence_unit=float(guidance_raw["base_evidence_unit"]),
        benefic_sign=float(guidance_raw["benefic_sign"]),
        malefic_sign=float(guidance_raw["malefic_sign"]),
        modifiers=modifiers,
        modifier_combination_policy=modifier_policy,
        worked_examples=tuple(worked_examples),
        blocked_capabilities=blocked_capabilities,
        raw=raw,
    )


def load_vedha_profile(
    profile_id: str,
    profile_root: Path | None = None,
) -> VedhaProfileDefinition:
    root = profile_root or VEDHA_PROFILE_ROOT
    raw = _load_yaml(root / f"{profile_id}.yaml")
    if str(raw.get("vedha_profile_id", "")) != profile_id:
        raise ValueError("Vedha profile filename/id mismatch")
    from .config import load_source_register

    register = load_source_register()
    return validate_vedha_profile(
        raw, (str(item["source_id"]) for item in register["sources"])
    )


def _normalize_enum(
    enum_type: type[StringEnum],
    value: StringEnum | str | None,
    label: str,
) -> StringEnum | None:
    if value is None:
        return None
    return _enum_value(enum_type, value, label)


def _source_cell(grid: CompiledGrid, source_nakshatra: str) -> tuple[int, int]:
    matches = [
        (cell.row, cell.column)
        for cell in grid.cells
        for entry in cell.entries
        if entry.layer == "NAKSHATRA" and entry.value == source_nakshatra
    ]
    if len(matches) != 1:
        raise VedhaProfileBlockedError(
            f"source nakshatra must resolve to one outer cell: {source_nakshatra}"
        )
    row, column = matches[0]
    if (row in {1, grid.rows}) == (column in {1, grid.columns}):
        raise VedhaProfileBlockedError(
            f"source nakshatra is not on one non-corner edge: {source_nakshatra}"
        )
    return row, column


def _inward_vector(row: int, column: int, rows: int, columns: int) -> tuple[int, int]:
    if row == 1 and 1 < column < columns:
        return 1, 0
    if row == rows and 1 < column < columns:
        return -1, 0
    if column == 1 and 1 < row < rows:
        return 0, 1
    if column == columns and 1 < row < rows:
        return 0, -1
    raise VedhaProfileBlockedError(
        f"Vedha source must be on one non-corner outer edge: ({row}, {column})"
    )


def _target_from_entry(
    source_nakshatra: str,
    direction: VedhaDirection,
    row: int,
    column: int,
    entry: GridEntry,
) -> VedhaTarget:
    return VedhaTarget(
        source_nakshatra=source_nakshatra,
        direction=direction,
        row=row,
        column=column,
        layer=entry.layer,
        value=entry.value,
        semantic_role=entry.semantic_role,
        witness_set_id=entry.witness_set_id,
        evidence_status=entry.evidence_status,
        citations=entry.citations,
    )


class VedhaGuidanceEngine:
    def __init__(
        self,
        profile: str | VedhaProfileDefinition,
        *,
        profile_root: Path | None = None,
    ) -> None:
        self.profile = (
            load_vedha_profile(profile, profile_root)
            if isinstance(profile, str)
            else profile
        )
        self.grid = compile_grid(self.profile.grid_profile_id)
        if not set(self.profile.target_layers) <= set(self.grid.certified_layers):
            raise VedhaProfileBlockedError(
                "Vedha target layers are not certified by the selected grid"
            )
        self._validate_worked_examples()

    def targets_for_direction(
        self,
        source_nakshatra: str,
        direction: VedhaDirection | str,
    ) -> tuple[VedhaTarget, ...]:
        source = str(source_nakshatra).strip().upper()
        if source not in SBC_NAKSHATRAS_28:
            raise ValueError(f"unsupported SBC nakshatra: {source}")
        direction_value = VedhaDirection(str(direction).strip().upper())
        row, column = _source_cell(self.grid, source)
        dr, dc = _inward_vector(row, column, self.grid.rows, self.grid.columns)

        if direction_value == VedhaDirection.FRONT:
            current_row, current_column = row, column
            while True:
                next_row = current_row + dr
                next_column = current_column + dc
                if not (
                    1 <= next_row <= self.grid.rows
                    and 1 <= next_column <= self.grid.columns
                ):
                    break
                current_row, current_column = next_row, next_column
            entries = [
                entry
                for entry in self.grid.cell(current_row, current_column).entries
                if entry.layer == "NAKSHATRA"
            ]
            if len(entries) != 1:
                raise VedhaProfileBlockedError(
                    f"front Vedha did not end on one nakshatra for {source}"
                )
            return (
                _target_from_entry(
                    source,
                    direction_value,
                    current_row,
                    current_column,
                    entries[0],
                ),
            )

        # In screen row/column coordinates, (-dc, dr) is figure-left while
        # facing inward from any edge.
        left_dr, left_dc = -dc, dr
        if direction_value == VedhaDirection.LEFT:
            step_row, step_column = dr + left_dr, dc + left_dc
        else:
            step_row, step_column = dr - left_dr, dc - left_dc

        targets: list[VedhaTarget] = []
        current_row, current_column = row + step_row, column + step_column
        while (
            1 <= current_row <= self.grid.rows
            and 1 <= current_column <= self.grid.columns
        ):
            for entry in self.grid.cell(current_row, current_column).entries:
                if entry.layer in self.profile.target_layers:
                    targets.append(
                        _target_from_entry(
                            source,
                            direction_value,
                            current_row,
                            current_column,
                            entry,
                        )
                    )
            current_row += step_row
            current_column += step_column
        return tuple(targets)

    def all_direction_targets(self, source_nakshatra: str) -> tuple[VedhaTarget, ...]:
        return tuple(
            target
            for direction in (
                VedhaDirection.LEFT,
                VedhaDirection.FRONT,
                VedhaDirection.RIGHT,
            )
            for target in self.targets_for_direction(source_nakshatra, direction)
        )

    def _validate_worked_examples(self) -> None:
        for example in self.profile.worked_examples:
            actual = {
                target.target_key
                for target in self.all_direction_targets(example.source_nakshatra)
            }
            expected = set(example.expected_targets)
            if actual != expected:
                missing = sorted(expected - actual)
                extra = sorted(actual - expected)
                raise VedhaProfileBlockedError(
                    f"{example.source_nakshatra} worked-example mismatch; "
                    f"missing={missing}, extra={extra}"
                )

    def _resolve_directions(
        self, actor: VedhaActor
    ) -> tuple[tuple[VedhaDirection, ...], MotionClass | None, str]:
        body = actor.body.strip().upper()
        fixed = self.profile.fixed_directions.get(body)
        supplied_motion = _normalize_enum(
            MotionClass, actor.motion_class, f"{body} motion_class"
        )
        if fixed is not None:
            if body in {"RAHU", "KETU"}:
                effective_motion = MotionClass.RETROGRADE
                expected_motion = MotionClass.RETROGRADE
            else:
                effective_motion = None
                expected_motion = None
            if supplied_motion is not None and supplied_motion != expected_motion:
                raise ValueError(
                    f"{body} uses fixed {'/'.join(item.value for item in fixed)} "
                    "Vedha in this profile; "
                    f"motion_class {supplied_motion.value} conflicts"
                )
            return (
                fixed,
                effective_motion,
                f"{body} has fixed {'/'.join(item.value for item in fixed)} Vedha "
                "in the selected source profile",
            )
        if body not in self.profile.variable_bodies:
            raise ValueError(f"body is outside the certified Vedha profile: {body}")
        if supplied_motion is None:
            raise VedhaMotionRequiredError(
                f"{body} requires explicit DIRECT_SWIFT, MEAN, or RETROGRADE; "
                "automatic direct-speed thresholds are not certified"
            )
        return (
            (self.profile.motion_to_direction[supplied_motion],),
            supplied_motion,
            f"{supplied_motion.value} maps to "
            f"{self.profile.motion_to_direction[supplied_motion].value}",
        )

    def _resolve_nature(self, actor: VedhaActor) -> tuple[PlanetNature, str]:
        body = actor.body.strip().upper()
        supplied = _normalize_enum(PlanetNature, actor.nature, f"{body} nature")
        if supplied is not None:
            return supplied, "caller supplied explicit source-context nature"
        if body in self.profile.natural_benefics:
            return PlanetNature.BENEFIC, "natural benefic in the selected profile"
        if body in self.profile.natural_malefics:
            return PlanetNature.MALEFIC, "natural malefic in the selected profile"
        if body == "MOON":
            if actor.moon_is_waning is None:
                return (
                    PlanetNature.CONDITIONAL,
                    "Moon nature needs waxing/waning context",
                )
            if actor.moon_is_waning:
                return PlanetNature.MALEFIC, "waning Moon is malefic in this profile"
            return PlanetNature.BENEFIC, "non-waning Moon is benefic in this profile"
        if body == "MERCURY":
            association = _normalize_enum(
                PlanetNature,
                actor.mercury_association_nature,
                "Mercury association nature",
            )
            if association in {PlanetNature.BENEFIC, PlanetNature.MALEFIC}:
                return (
                    association,
                    f"Mercury inherits {association.value.lower()} association context",
                )
            return (
                PlanetNature.CONDITIONAL,
                "Mercury nature needs certified association context",
            )
        raise ValueError(f"body is outside the certified nature rules: {body}")

    def _resolve_multiplier(
        self,
        actor: VedhaActor,
        effective_motion: MotionClass | None,
    ) -> tuple[float | None, str, str]:
        dignity = _normalize_enum(DignityState, actor.dignity, f"{actor.body} dignity")
        assert isinstance(dignity, DignityState)
        is_retrograde = effective_motion == MotionClass.RETROGRADE
        if is_retrograde and dignity != DignityState.ORDINARY:
            return (
                None,
                "UNRESOLVED_MULTIPLIER_PRECEDENCE",
                "the source gives separate retrograde and dignity multipliers "
                "without a certified stacking or precedence rule",
            )
        if is_retrograde:
            return (
                self.profile.modifiers["RETROGRADE"],
                "SCORED",
                "retrograde source multiplier",
            )
        return (
            self.profile.modifiers[dignity.value],
            "SCORED",
            f"{dignity.value.lower()} source multiplier",
        )

    def resolve_actor_directions(
        self, actor: VedhaActor
    ) -> tuple[VedhaActorResolution, ...]:
        body = actor.body.strip().upper()
        source = actor.source_nakshatra.strip().upper()
        directions, effective_motion, direction_reason = self._resolve_directions(actor)
        nature, nature_reason = self._resolve_nature(actor)
        multiplier, multiplier_status, multiplier_reason = self._resolve_multiplier(
            actor, effective_motion
        )
        return tuple(
            VedhaActorResolution(
                body=body,
                source_nakshatra=source,
                direction=direction,
                direction_reason=direction_reason,
                nature=nature,
                nature_reason=nature_reason,
                effective_multiplier=multiplier,
                multiplier_status=multiplier_status,
                multiplier_reason=multiplier_reason,
                targets=self.targets_for_direction(source, direction),
            )
            for direction in directions
        )

    def resolve_actor(self, actor: VedhaActor) -> VedhaActorResolution:
        resolutions = self.resolve_actor_directions(actor)
        if len(resolutions) != 1:
            directions = "/".join(item.direction.value for item in resolutions)
            raise ValueError(
                f"{actor.body.strip().upper()} resolves to {directions}; "
                "use resolve_actor_directions() or evaluate() for this source profile"
            )
        return resolutions[0]

    def _normalize_target_context(
        self, target_context: Mapping[str, Iterable[str]]
    ) -> dict[str, frozenset[str]]:
        normalized: dict[str, frozenset[str]] = {}
        for raw_layer, raw_values in target_context.items():
            layer = str(raw_layer).strip().upper()
            if layer not in self.profile.target_layers:
                raise ValueError(f"unsupported Vedha target layer: {layer}")
            if isinstance(raw_values, str):
                values = frozenset({raw_values.strip().upper()})
            else:
                values = frozenset(str(item).strip().upper() for item in raw_values)
            if not values or any(not value for value in values):
                raise ValueError(f"target context for {layer} must not be empty")
            unknown = values - CERTIFIED_LAYER_VALUES[layer]
            if unknown:
                raise ValueError(f"unknown {layer} target values: {sorted(unknown)}")
            normalized[layer] = values
        return normalized

    def evaluate(
        self,
        actors: Iterable[VedhaActor],
        target_context: Mapping[str, Iterable[str]],
    ) -> VedhaGuidanceReport:
        context = self._normalize_target_context(target_context)
        resolutions = tuple(
            resolution
            for actor in actors
            for resolution in self.resolve_actor_directions(actor)
        )
        if not resolutions:
            raise ValueError("at least one Vedha actor is required")

        contributions: list[VedhaContribution] = []
        for resolution in resolutions:
            for target in resolution.targets:
                if target.value not in context.get(target.layer, frozenset()):
                    continue
                if resolution.nature == PlanetNature.CONDITIONAL:
                    signed_units = None
                    status = "UNRESOLVED_PLANET_NATURE"
                    explanation = resolution.nature_reason
                elif resolution.effective_multiplier is None:
                    signed_units = None
                    status = resolution.multiplier_status
                    explanation = resolution.multiplier_reason
                else:
                    sign = (
                        self.profile.benefic_sign
                        if resolution.nature == PlanetNature.BENEFIC
                        else self.profile.malefic_sign
                    )
                    signed_units = (
                        self.profile.base_evidence_unit
                        * sign
                        * resolution.effective_multiplier
                    )
                    status = "SCORED"
                    explanation = (
                        f"one matched layer x {resolution.nature.value.lower()} sign "
                        f"x {resolution.effective_multiplier:g} source modifier"
                    )
                contributions.append(
                    VedhaContribution(
                        body=resolution.body,
                        source_nakshatra=resolution.source_nakshatra,
                        direction=resolution.direction,
                        target=target,
                        nature=resolution.nature,
                        effective_multiplier=resolution.effective_multiplier,
                        signed_guidance_units=signed_units,
                        status=status,
                        explanation=explanation,
                    )
                )

        scored = [
            item for item in contributions if item.signed_guidance_units is not None
        ]
        favorable = sum(
            item.signed_guidance_units
            for item in scored
            if item.signed_guidance_units > 0
        )
        adverse = sum(
            item.signed_guidance_units
            for item in scored
            if item.signed_guidance_units < 0
        )
        net = favorable + adverse
        absolute = favorable + abs(adverse)
        normalized_score = net / absolute if absolute else 0.0
        if normalized_score > 0:
            band = "FAVORABLE_EVIDENCE_DOMINANT"
        elif normalized_score < 0:
            band = "ADVERSE_EVIDENCE_DOMINANT"
        else:
            band = "BALANCED_OR_NO_SCORED_HITS"
        unresolved_count = len(contributions) - len(scored)
        coverage = len(scored) / len(contributions) if contributions else 0.0

        return VedhaGuidanceReport(
            schema_version="SBC_VEDHA_GUIDANCE_V1",
            vedha_profile_id=self.profile.vedha_profile_id,
            vedha_profile_hash=self.profile.profile_hash,
            grid_profile_id=self.grid.grid_profile_id,
            grid_profile_hash=self.grid.profile_hash,
            guidance_model_id=GUIDANCE_MODEL_ID,
            guidance_only=True,
            financial_validation_status=FINANCIAL_VALIDATION_STATUS,
            actor_resolutions=resolutions,
            contributions=tuple(contributions),
            favorable_guidance_units=favorable,
            adverse_guidance_units=adverse,
            net_guidance_units=net,
            normalized_guidance_score=normalized_score,
            guidance_band=band,
            matched_target_count=len(contributions),
            scored_match_count=len(scored),
            unresolved_match_count=unresolved_count,
            scoring_coverage_ratio=coverage,
            blocked_capabilities=self.profile.blocked_capabilities,
            citations=self.profile.citations,
        )
