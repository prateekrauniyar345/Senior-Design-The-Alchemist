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
    "mindat",
    "density",
    "lustre",
    "luster",
    "color",
    "colour",
    "cleavage",
    "transparency",
    "tenacity",
    "optical",
    "ima-approved",
    "geomaterial",
    "geomaterials"
]

GENERAL_KEYWORDS = [
    "hello",
    "hi",
    "hey",
    "how are you",
    "how are you doing",
    "how's it going",
    "how is it going",
    "good morning",
    "good afternoon",
    "good evening",
    "what can you do",
    "how do i use you",
    "what can i ask",
    "what should i ask",
    "example query",
    "example queries",
    "sample query",
    "sample queries",
    "queries that work",
    "give me some query",
    "give me some queries",
    "give me a query",
    "give me queries",
    "show me queries",
    "supported queries",
    "valid queries",
    "query examples",
    "help",
    "who are you",
    "thanks",
    "thank you"
]

OFF_TOPIC_KEYWORDS = [
    "weather",
    "sports",
    "stock price",
    "movie",
    "music",
    "recipe",
    "restaurant",
    "flight",
    "hotel",
    "homework",
    "math problem",
    "news",
]

QUERY_HELP_PATTERNS = [
    r"\b(?:give|show|list|suggest|provide)\b.*\b(?:example|sample|valid|supported|working)?\s*(?:query|queries|prompts)\b",
    r"\b(?:what|which)\b.*\b(?:query|queries|prompts)\b.*\b(?:ask|try|use|work)\b",
    r"\bhow\b.*\b(?:use|ask|query)\b.*\b(?:program|app|system|assistant|alchemist)\b",
]


import re

def classify_query(user_input: str) -> str:
    lower = user_input.lower().replace("-", " ")

    # Greeting / onboarding (STRICT word matching)
    for keyword in GENERAL_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", lower):
            return "general"

    if any(re.search(pattern, lower) for pattern in QUERY_HELP_PATTERNS):
        return "general"

    if any(keyword in lower for keyword in OFF_TOPIC_KEYWORDS):
        return "off_topic"

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

    mindat_context_words = [
        "data", "dataset", "field", "fields", "filter", "filters",
        "results", "records", "visualization", "visualisation"
    ]

    if (
        any(re.search(rf"\b{re.escape(word)}\b", lower) for word in action_words)
        and any(word in lower for word in mindat_context_words)
        and token_count >= 3
    ):
        return "mineral"

    return "off_topic"
