# Backend/app/input_validation/parameters.py
import re

VALID_CRYSTAL_SYSTEMS = [
    "amorphous",
    "hexagonal",
    "icosahedral",
    "isometric",
    "monoclinic",
    "orthorhombic",
    "tetragonal",
    "triclinic",
    "trigonal"
]

NUMBER_PATTERN = r"(?<![\w.])-?\d+(?:\.\d+)?"


def _extract_hardness_values(user_input: str) -> list[float]:
    """
    Extract only numbers that are part of an explicit Mohs hardness filter.

    Queries can mention hardness as a chart field and include unrelated numbers,
    such as discovery years. Those unrelated numbers should not be validated as
    Mohs hardness values.
    """
    lower = user_input.lower()
    values: list[float] = []

    patterns = [
        # "hardness between 5 and 7", "hardness from 5 to 7", "hardness 3-5"
        rf"\bhardness\b\s*(?:between|from)?\s*({NUMBER_PATTERN})\s*(?:-|–|—|to|and)\s*({NUMBER_PATTERN})",
        # "hardness greater than 10", "hardness <= 7", "hardness of 5"
        rf"\bhardness\b\s*(?:of|is|=|>|<|>=|<=|above|below|under|over|at\s+least|at\s+most|greater\s+than|less\s+than)?\s*({NUMBER_PATTERN})",
        # "minimum hardness of 5", "max hardness 7"
        rf"\b(?:minimum|min|maximum|max|lower|upper)\s+hardness\b\s*(?:of|is|=)?\s*({NUMBER_PATTERN})",
        # "hardness minimum 5", "hardness max 7"
        rf"\bhardness\s+(?:minimum|min|maximum|max|lower|upper)\b\s*(?:of|is|=)?\s*({NUMBER_PATTERN})",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, lower):
            for group in match.groups():
                if group is not None:
                    values.append(float(group))

    return values


def validate_parameters(user_input: str) -> dict:
    lower = user_input.lower()

    # Hardness validation
    if "hardness" in lower:
        for n in _extract_hardness_values(user_input):
            if n < 0 or n > 10:
                return {
                    "status": "invalid",
                    "code": "invalid_hardness_range",
                    "message": "Hardness must be between 0 and 10.",
                    "detail": (
                        f"The request includes a Mohs hardness value of {n:g}, "
                        "but Mindat hardness filters must stay between 0 and 10."
                    ),
                }

    # Crystal system validation
    for system in VALID_CRYSTAL_SYSTEMS:
        if system in lower:
            return {"status": "valid"}

    return {"status": "valid"}
