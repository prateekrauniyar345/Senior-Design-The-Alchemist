import re

BLOCKED_REGEX = [
    (r"ignore.*instruction", "tries to ignore or bypass the assistant instructions"),
    (r"override.*system", "tries to override the system instructions"),
    (r"reveal.*(api|key|token|credential|secret)", "asks for private credentials or secrets"),
    (r"show.*(api|key|token|credential|secret)", "asks to show private credentials or secrets"),
    (r"(api|key|token|credential).*reveal", "asks to reveal private credentials or secrets"),
    (r"show.*system.*prompt", "asks to reveal hidden system instructions"),
    (r"(drop|delete).*(table|database)", "appears to request destructive database actions"),
    (r"rm\s*-rf", "appears to request destructive file-system actions"),
    (r"sudo\s+", "appears to request privileged system commands"),
]


def get_security_violation(user_input: str) -> str | None:
    lower = user_input.lower()

    for pattern, reason in BLOCKED_REGEX:
        if re.search(pattern, lower):
            return reason

    return None


def is_safe_input(user_input: str) -> bool:
    return get_security_violation(user_input) is None
