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


def validate_parameters(user_input: str) -> dict:
    lower = user_input.lower()

    # Hardness validation
    if "hardness" in lower:
        numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", lower)]
        for n in numbers:
            if n < 0 or n > 10:
                return {
                    "status": "invalid",
                    "message": "Hardness must be between 0 and 10."
                }

    # Crystal system validation
    for system in VALID_CRYSTAL_SYSTEMS:
        if system in lower:
            return {"status": "valid"}

    return {"status": "valid"}
