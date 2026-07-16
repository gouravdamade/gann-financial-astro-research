from __future__ import annotations

from enum import Enum


class StringEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class ZodiacMode(StringEnum):
    SIDEREAL = "SIDEREAL"
    TROPICAL = "TROPICAL"


class Ayanamsha(StringEnum):
    RAMAN = "RAMAN"
    LAHIRI = "LAHIRI"


class Center(StringEnum):
    GEOCENTRIC = "GEOCENTRIC"
    TOPOCENTRIC = "TOPOCENTRIC"


class NodeType(StringEnum):
    TRUE_NODE = "TRUE_NODE"
    MEAN_NODE = "MEAN_NODE"


class EphemerisFallbackPolicy(StringEnum):
    ALLOW_RECORDED = "ALLOW_RECORDED"
    ERROR_IF_NOT_SWISSEPH = "ERROR_IF_NOT_SWISSEPH"


class AbhijitPolicy(StringEnum):
    IGNORE_FOR_PLANET_PLACEMENT = "IGNORE_FOR_PLANET_PLACEMENT"
    OVERLAP_FLAG = "OVERLAP_FLAG"
    REPLACE_SEGMENT = "REPLACE_SEGMENT"


class VaraBoundary(StringEnum):
    CIVIL_MIDNIGHT = "CIVIL_MIDNIGHT"
    SUNRISE_BASED = "SUNRISE_BASED"


CLASSICAL_BODIES = (
    "SUN",
    "MOON",
    "MARS",
    "MERCURY",
    "JUPITER",
    "VENUS",
    "SATURN",
)

NODE_BODIES = ("RAHU", "KETU")
OUTER_BODIES = ("URANUS", "NEPTUNE", "PLUTO")
SUPPORTED_BODIES = CLASSICAL_BODIES + NODE_BODIES + OUTER_BODIES
