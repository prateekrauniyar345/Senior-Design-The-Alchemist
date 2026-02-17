from .security import is_safe_input
from .domain import is_domain_query
from .parameters import validate_parameters

MAX_INPUT_LENGTH = 500


def validate_user_input(user_input: str) -> dict:
    """
    Central gateway validation before LLM execution.
    """

    # ---------- Structural Validation ----------
    if not user_input or not user_input.strip():
        return _error("Input cannot be empty.")

    if len(user_input) > MAX_INPUT_LENGTH:
        return _error(f"Input exceeds {MAX_INPUT_LENGTH} characters.")

    # ---------- Security Validation ----------
    if not is_safe_input(user_input):
        return _blocked("Unsafe or malicious input detected.")

    # ---------- Domain Validation ----------
    if not is_domain_query(user_input):
        return _error("Query is outside Mindat system capability.")

    # ---------- Parameter Validation ----------
    param_result = validate_parameters(user_input)
    if param_result["status"] != "valid":
        return _error(param_result["message"])

    return {
        "status": "safe",
        "clean_query": user_input.strip()
    }


def _error(message: str):
    return {"status": "error", "message": message}


def _blocked(message: str):
    return {"status": "blocked", "message": message}
