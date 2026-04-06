import re

BLOCKED_REGEX = [
    r"ignore.*instruction",
    r"override.*system",
    r"reveal.*(api|key|token|credential|secret)",
    r"show.*(api|key|token|credential|secret)",
    r"(api|key|token|credential).*reveal",
    r"show.*system.*prompt",
    r"(drop|delete).*(table|database)",
    r"rm\s*-rf",
    r"sudo\s+",
]


def is_safe_input(user_input: str) -> bool:
    lower = user_input.lower()

    for pattern in BLOCKED_REGEX:
        if re.search(pattern, lower):
            return False

    return True