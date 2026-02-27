ALLOWED_KEYWORDS = [
    "mineral",
    "minerals",
    "rock",
    "rocks",
    "geology",
    "geological",
    "hardness",
    "crystal",
    "element",
    "elements",
    "locality",
    "localities",
    "heatmap",
    "histogram",
    "plot",
    "chart",
    "graph",
    "network",
    "ima",
    "country",
    "mindat"
]


def is_domain_query(user_input: str) -> bool:
    lower = user_input.lower()
    if any(keyword in lower for keyword in ALLOWED_KEYWORDS):
        return True

    # Allow normal data-task phrasing to reduce false negatives.
    action_words = ("get", "show", "find", "list", "analyze", "analyse", "compare")
    token_count = len([t for t in lower.split() if t.strip()])
    return any(word in lower for word in action_words) and token_count >= 3
