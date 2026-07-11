import pandas as pd

from astro_event_contract import (
    directional_family_key,
    entity_longitude,
    enrich_event_roles_frame,
    resolve_event_roles,
    scoped_family_key,
)


def test_resolves_transiting_moon_against_natal_average() -> None:
    transit = {
        "SUN": 324.5741841334,
        "MOON": 66.9654361436,
        "MERCURY": 342.7204848292,
        "VENUS": 347.4168738275,
        "MARS": 85.0361982356,
        "JUPITER": 50.0986429036,
        "SATURN": 328.6431882274,
        "URANUS": 31.0342433671,
        "NEPTUNE": 336.3486223339,
        "PLUTO": 280.2782873531,
    }
    natal = {
        "SUN": 280.4109054180,
        "MOON": 40.2254460038,
        "MERCURY": 289.2961038583,
        "VENUS": 326.8159879621,
        "MARS": 313.1355368934,
        "JUPITER": 229.1339696199,
        "SATURN": 94.7753664284,
        "URANUS": 160.1539928283,
        "NEPTUNE": 17.7922443680,
        "PLUTO": 22.2800202105,
    }
    result = resolve_event_roles(
        {
            "b1": "AVG(ALL)",
            "b2": "MOON",
            "aspect": "square",
            "is_natal": True,
            "planet_longitudes_json": transit,
            "natal_longitudes_json": natal,
        }
    )
    assert result["event_scope"] == "TN"
    assert result["event_transit_body"] == "MOON"
    assert result["event_natal_body"] == "AVG(ALL)"
    assert result["event_role_best_orb_deg"] < 0.5
    assert result["event_role_alternate_orb_deg"] > 40.0


def test_average_is_circular_not_arithmetic() -> None:
    snapshot = {member: value for member, value in zip(
        ("SUN", "MOON", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "URANUS", "NEPTUNE", "PLUTO"),
        (359.0, 1.0, 359.0, 1.0, 359.0, 1.0, 359.0, 1.0, 359.0, 1.0),
        strict=True,
    )}
    value = entity_longitude(snapshot, "AVG(ALL)")
    assert value is not None
    assert min(abs(value), abs(value - 360.0)) < 1e-9


def test_frame_enrichment_and_scoped_family() -> None:
    frame = pd.DataFrame(
        [
            {
                "b1": "MARS",
                "b2": "JUPITER",
                "aspect": "trine",
                "is_natal": False,
                "planet_longitudes_json": "{}",
                "natal_longitudes_json": "{}",
            }
        ]
    )
    out = enrich_event_roles_frame(frame)
    assert out.loc[0, "event_scope"] == "TT"
    assert out.loc[0, "event_role_resolution_status"] == "not_applicable_transit_transit"
    assert scoped_family_key("MARS|JUPITER", "trine", "TT") == "TT::MARS|JUPITER::trine"


def test_directional_family_keeps_transit_natal_orientation() -> None:
    moon_transit = directional_family_key("TN", "MOON", "MERCURY", "trine")
    mercury_transit = directional_family_key("TN", "MERCURY", "MOON", "trine")

    assert moon_transit == "TN::MOON->MERCURY::trine"
    assert mercury_transit == "TN::MERCURY->MOON::trine"
    assert moon_transit != mercury_transit
