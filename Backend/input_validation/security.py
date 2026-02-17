BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "disregard above",
    "override system",
    "reveal api key",
    "show system prompt",
    "delete database",
    "drop table",
    "rm -rf",
    "sudo",
]


def is_safe_input(user_input: str) -> bool:
    lower = user_input.lower()

    for pattern in BLOCKED_PATTERNS:
        if pattern in lower:
            return False

    return True



