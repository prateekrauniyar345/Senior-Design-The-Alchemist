import re

from .security import get_security_violation
from .domain import classify_query
from .parameters import validate_parameters

MAX_INPUT_LENGTH = 500
MIN_MEANINGFUL_CHARS = 2

DEFAULT_MINDAT_SUGGESTIONS = [
    "Find minerals with hardness between 5 and 7.",
    "Plot a histogram of hardness for IMA-approved minerals.",
    "Show mineral localities in Canada.",
]


def validate_user_input(user_input: str) -> dict:
    """
    Central gateway validation before LLM execution.
    """

    # ---------- Structural Validation ----------
    if not user_input or not user_input.strip():
        return _error(
            "Input cannot be empty.",
            code="empty_input",
            detail="The request is empty, so there is no Mindat or mineral query to process.",
            suggestion="Try asking for minerals, localities, or a chart from Mindat data.",
        )

    stripped_input = user_input.strip()
    meaningful_chars = re.sub(r"[^A-Za-z0-9]", "", stripped_input)

    if not meaningful_chars:
        return _error(
            "Input cannot be empty.",
            code="empty_input",
            detail="The request only contains whitespace or punctuation, so there is no Mindat or mineral query to process.",
            suggestion="Try asking a complete question, such as finding minerals by hardness or plotting a histogram.",
        )

    if len(meaningful_chars) < MIN_MEANINGFUL_CHARS:
        return _error(
            "Input is too short to understand.",
            code="unclear_input",
            detail="The request is too short to classify as a greeting, Mindat query, or supported visualization task.",
            suggestion="Ask a complete Mindat-related question, such as 'Find minerals with hardness between 5 and 7.'",
        )

    if len(user_input) > MAX_INPUT_LENGTH:
        return _error(
            f"Input exceeds {MAX_INPUT_LENGTH} characters.",
            code="input_too_long",
            detail=f"The request is longer than the {MAX_INPUT_LENGTH}-character limit.",
            suggestion="Shorten the request and keep the mineral filters or visualization goal.",
        )

    # ---------- Security Validation ----------
    security_reason = get_security_violation(user_input)
    if security_reason:
        return _blocked(
            "Unsafe or malicious input detected.",
            code=security_reason["code"],
            detail=security_reason["detail"],
            suggestion=security_reason["suggestion"],
        )

    # ---------- Domain Classification ----------
    query_type = classify_query(user_input)

    if query_type == "general":
        return {
            "status": "general",
            "clean_query": stripped_input,
            "code": "general_query",
        }

    if query_type == "off_topic":
        return _error(
            "Query is outside Mindat system capability.",
            code="off_topic",
            detail="The request does not appear to be about minerals, geology, Mindat data, or supported visualizations.",
            suggestion="Ask about minerals, elements, localities, hardness, crystal systems, or supported charts.",
        )
    
    # ---------- Parameter Validation ----------
    param_result = validate_parameters(user_input)
    if param_result["status"] != "valid":
        return _error(
            param_result["message"],
            code=param_result.get("code", "invalid_parameter"),
            detail=param_result.get("detail", param_result["message"]),
            suggestion=param_result.get("suggestion"),
        )

    return {
        "status": "safe",
        "clean_query": stripped_input,
        "code": "safe_query",
    }


def _error(
    message: str,
    code: str = "validation_error",
    detail: str | None = None,
    suggestion: str | None = None,
):
    return {
        "status": "error",
        "message": message,
        "code": code,
        "detail": detail or message,
        "suggestion": suggestion,
        "examples": DEFAULT_MINDAT_SUGGESTIONS,
    }


def _blocked(
    message: str,
    code: str = "blocked_input",
    detail: str | None = None,
    suggestion: str | None = None,
):
    return {
        "status": "blocked",
        "message": message,
        "code": code,
        "detail": detail or message,
        "suggestion": suggestion,
        "examples": DEFAULT_MINDAT_SUGGESTIONS,
    }
