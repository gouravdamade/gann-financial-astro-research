"""Deterministic, neutral Candidate C synthetic state-space corpus."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .canonical import HASH_CONVENTION, canonical_hash
from .models import NeutralFixture


GENERATION_ALGORITHM_VERSION = "MO_R4A_CANDIDATE_C_AB1_NEUTRAL_STATE_SPACE_V1"
BODIES = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU")


def _sign_from_relative(source_sign_index: int, relative_place: int) -> int:
    return ((source_sign_index - 1 + relative_place - 1) % 12) + 1


def _fixture(
    fixture_id: str,
    fixture_family: str,
    source_body: str,
    target_body: str,
    source_sign_index: int,
    target_sign_index: int,
    sun_sign_index: int,
    coverage_tags: tuple[str, ...],
    optional_aspect_type: str | None = None,
) -> NeutralFixture:
    provisional = NeutralFixture(
        fixture_id=fixture_id,
        fixture_family=fixture_family,
        source_body=source_body,
        target_body=target_body,
        source_sign_index=source_sign_index,
        target_sign_index=target_sign_index,
        sun_sign_index=sun_sign_index,
        coverage_tags=coverage_tags,
        optional_aspect_type=optional_aspect_type,
    )
    return NeutralFixture(**(provisional.__dict__ | {"semantic_fixture_identity_hash": canonical_hash(provisional.semantic_input())}))


def generate_neutral_fixtures() -> list[NeutralFixture]:
    fixtures: list[NeutralFixture] = []
    source_sign = 1
    for source_body in BODIES:
        for target_body in BODIES:
            for relative_place in range(1, 13):
                target_sign = _sign_from_relative(source_sign, relative_place)
                sun_sign = source_sign if source_body == "SUN" else 6
                fixtures.append(
                    _fixture(
                        f"REL_{source_body}_{target_body}_P{relative_place:02d}",
                        "RELATIONSHIP_POSITION_MATRIX",
                        source_body,
                        target_body,
                        source_sign,
                        target_sign,
                        sun_sign,
                        ("C01", "C02", "C03", "C04", "C05", "C07", f"RELATIVE_PLACE_{relative_place}"),
                    )
                )
    for source_body in ("MARS", "JUPITER", "SATURN", "MERCURY", "VENUS"):
        for relative_sun_place in range(1, 13):
            sun_sign = _sign_from_relative(source_sign, relative_sun_place)
            fixtures.append(
                _fixture(
                    f"MOTION_{source_body}_SUNP{relative_sun_place:02d}",
                    "MOTION_MATRIX",
                    source_body,
                    "JUPITER",
                    source_sign,
                    4,
                    sun_sign,
                    ("C01", "C06", f"RELATIVE_SUN_PLACE_{relative_sun_place}"),
                )
            )
    for source_body in ("SUN", "MOON", "RAHU", "KETU"):
        fixtures.append(
            _fixture(
                f"MOTION_UNSUPPORTED_{source_body}",
                "MOTION_MATRIX",
                source_body,
                "MARS",
                source_sign,
                4,
                source_sign if source_body == "SUN" else 6,
                ("C01", "C06", "UNSUPPORTED_MOTION_SOURCE"),
            )
        )
    canary_base = ("MARS", "JUPITER", 2, 5, 3)
    for index, aspect_type in enumerate(("CONJUNCTION", "OPPOSITION", "TRINE", "SQUARE"), start=1):
        fixtures.append(
            _fixture(
                f"CANARY_ASPECT_{index:02d}",
                "REPRESENTATION_INVARIANCE_CANARIES",
                *canary_base,
                ("REPRESENTATION_INVARIANCE", "C03", "C05"),
                optional_aspect_type=aspect_type,
            )
        )
    return fixtures


def build_fixture_corpus() -> dict[str, Any]:
    fixtures = generate_neutral_fixtures()
    family_counts: dict[str, int] = {}
    for fixture in fixtures:
        family_counts[fixture.fixture_family] = family_counts.get(fixture.fixture_family, 0) + 1
    corpus = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_AB1_SYNTHETIC_FIXTURE_CORPUS_V1",
        "generationAlgorithmVersion": GENERATION_ALGORITHM_VERSION,
        "hashConvention": HASH_CONVENTION + " Exclude corpusHash.",
        "fixtureCount": len(fixtures),
        "fixtureFamilyCounts": family_counts,
        "fixtures": [fixture.to_dict() for fixture in fixtures],
    }
    corpus["corpusHash"] = canonical_hash(corpus)
    return corpus


def load_fixture_corpus(path: Path) -> list[NeutralFixture]:
    corpus = json.loads(path.read_text(encoding="utf-8"))
    stored_hash = corpus.pop("corpusHash")
    if canonical_hash(corpus) != stored_hash:
        raise ValueError("neutral fixture corpus hash does not validate")
    fixtures = []
    for item in corpus["fixtures"]:
        fixture = NeutralFixture(
            fixture_id=item["fixtureId"],
            fixture_family=item["fixtureFamily"],
            source_body=item["sourceBody"],
            target_body=item["targetBody"],
            source_sign_index=item["sourceSignIndex"],
            target_sign_index=item["targetSignIndex"],
            sun_sign_index=item["sunSignIndex"],
            coverage_tags=tuple(item["coverageTags"]),
            optional_aspect_type=item.get("optionalAspectType"),
            semantic_fixture_identity_hash=item["semanticFixtureIdentityHash"],
        )
        if canonical_hash(fixture.semantic_input()) != fixture.semantic_fixture_identity_hash:
            raise ValueError(f"neutral fixture identity does not validate: {fixture.fixture_id}")
        fixtures.append(fixture)
    return fixtures


def write_fixture_corpus(path: Path) -> dict[str, Any]:
    corpus = build_fixture_corpus()
    path.write_text(json.dumps(corpus, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return corpus
