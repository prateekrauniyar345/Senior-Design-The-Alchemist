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

GENERAL_KEYWORDS = [
    "hello",
    "hi",
    "hey",
    "what can you do",
    "how do i use you",
    "help",
    "who are you"
]


import re

def classify_query(user_input: str) -> str:
    lower = user_input.lower().replace("-", " ")

    # Greeting / onboarding (STRICT word matching)
    for keyword in GENERAL_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", lower):
            return "general"

    # Mineral domain
    if any(keyword in lower for keyword in ALLOWED_KEYWORDS):
        return "mineral"

    # Fallback action detection
    action_words = [
        "get", "show", "find", "list",
        "plot", "generate", "create",
        "analyze", "analyse"
    ]

    token_count = len(lower.split())

    if any(word in lower for word in action_words) and token_count >= 3:
        return "mineral"

    return "off_topic"