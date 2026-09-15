import re

BLOCKED_REGEX = [
    {
        "pattern": r"ignore.*instruction",
        "code": "prompt_injection",
        "detail": "tries to ignore or bypass the assistant instructions",
    },
    {
        "pattern": r"override.*system",
        "code": "prompt_injection",
        "detail": "tries to override the system instructions",
    },
    {
        "pattern": r"reveal.*(api|key|token|credential|secret)",
        "code": "credential_request",
        "detail": "asks for private credentials or secrets",
    },
    {
        "pattern": r"show.*(api|key|token|credential|secret)",
        "code": "credential_request",
        "detail": "asks to show private credentials or secrets",
    },
    {
        "pattern": r"(api|key|token|credential).*reveal",
        "code": "credential_request",
        "detail": "asks to reveal private credentials or secrets",
    },
    {
        "pattern": r"show.*system.*prompt",
        "code": "system_prompt_request",
        "detail": "asks to reveal hidden system instructions",
    },
    {
        "pattern": r"(drop|delete).*(table|database)",
        "code": "destructive_database_action",
        "detail": "appears to request destructive database actions",
    },
    {
        "pattern": r"rm\s*-rf",
        "code": "destructive_file_action",
        "detail": "appears to request destructive file-system actions",
    },
    {
        "pattern": r"sudo\s+",
        "code": "privileged_command",
        "detail": "appears to request privileged system commands",
    },
]

SAFE_REDIRECT_SUGGESTION = (
    "Ask a Mindat-related question, such as finding minerals by hardness, "
    "plotting a histogram, or showing locality data for a country."
)


def get_security_violation(user_input: str) -> dict | None:
    lower = user_input.lower()

    for rule in BLOCKED_REGEX:
        if re.search(rule["pattern"], lower):
            return {
                "code": rule["code"],
                "detail": f"The request {rule['detail']}.",
                "suggestion": SAFE_REDIRECT_SUGGESTION,
            }

    return None


def is_safe_input(user_input: str) -> bool:
    return get_security_violation(user_input) is None
