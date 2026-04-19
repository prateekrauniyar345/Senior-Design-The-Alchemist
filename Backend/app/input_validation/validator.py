from .security import get_security_violation
from .domain import classify_query
from .parameters import validate_parameters

MAX_INPUT_LENGTH = 500


def validate_user_input(user_input: str) -> dict:
    """
    Central gateway validation before LLM execution.
    """

    # ---------- Structural Validation ----------
    if not user_input or not user_input.strip():
        return _error(
            "Input cannot be empty.",
            code="empty_input",
            detail="The request is empty, so there is no Mindat or mineral query to process."
        )

    if len(user_input) > MAX_INPUT_LENGTH:
        return _error(
            f"Input exceeds {MAX_INPUT_LENGTH} characters.",
            code="input_too_long",
            detail=f"The request is longer than the {MAX_INPUT_LENGTH}-character limit."
        )

    # ---------- Security Validation ----------
    security_reason = get_security_violation(user_input)
    if security_reason:
        return _blocked(
            "Unsafe or malicious input detected.",
            code="unsafe_input",
            detail=f"The request {security_reason}."
        )

    # ---------- Domain Classification ----------
    query_type = classify_query(user_input)

    if query_type == "general":
        return {
            "status": "general",
            "clean_query": user_input.strip()
        }

    if query_type == "off_topic":
        return _error(
            "Query is outside Mindat system capability.",
            code="off_topic",
            detail="The request does not appear to be about minerals, geology, Mindat data, or supported visualizations."
        )
    
    # ---------- Parameter Validation ----------
    param_result = validate_parameters(user_input)
    if param_result["status"] != "valid":
        return _error(
            param_result["message"],
            code=param_result.get("code", "invalid_parameter"),
            detail=param_result.get("detail", param_result["message"])
        )

    return {
        "status": "safe",
        "clean_query": user_input.strip()
    }


def _error(message: str, code: str = "validation_error", detail: str | None = None):
    return {
        "status": "error",
        "message": message,
        "code": code,
        "detail": detail or message,
    }


def _blocked(message: str, code: str = "blocked_input", detail: str | None = None):
    return {
        "status": "blocked",
        "message": message,
        "code": code,
        "detail": detail or message,
    }
