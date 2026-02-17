ALLOWED_KEYWORDS = [
    "mineral",
    "hardness",
    "crystal",
    "element",
    "locality",
    "heatmap",
    "histogram",
    "network",
    "ima",
    "country",
    "mindat"
]


def is_domain_query(user_input: str) -> bool:
    lower = user_input.lower()

    return any(keyword in lower for keyword in ALLOWED_KEYWORDS)
