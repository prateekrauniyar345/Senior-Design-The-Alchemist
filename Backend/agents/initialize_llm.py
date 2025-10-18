# app/llm/factory.py
from typing import Optional, Dict, Any
from langchain_openai import AzureChatOpenAI
from pydantic import ValidationError
from config.settings import settings
from utils.custom_message import LLMException


DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.7

def _required(name: str, value: Optional[str]) -> str:
    """Ensure a required setting exists and is non-empty."""
    if not value or not str(value).strip():
        raise LLMException(
            message=f"Missing required Azure OpenAI setting: {name}",
            status_code=500,
            details={"setting": name},
        )
    return value

def initialize_llm(
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: Optional[int] = None,
    timeout: Optional[float] = None,
    warmup: bool = False,           # set True if you want a quick health check call
) -> AzureChatOpenAI:
    """
    Build an AzureChatOpenAI client using strongly-typed app settings.
    Raises LLMException with structured details on failure.
    """
    try:
        # Validate presence of required settings (fail fast, clear message)
        api_version   = _required("AZURE_OPENAI_API_VERSION", settings.azure_api_version)
        azure_endpoint= _required("AZURE_OPENAI_API_ENDPOINT", settings.azure_endpoint)
        api_key       = _required("AZURE_OPENAI_API_KEY", settings.azure_api_key)
        deployment    = _required("AZURE_DEPLOYMENT_NAME", settings.azure_deployment_name)

        # Construct LLM client
        llm = AzureChatOpenAI(
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            azure_deployment=deployment,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout or settings.request_timeout,  # reuse your settings default
        )

        return llm 
    except ValidationError as ve:
        raise LLMException(
            message="Invalid Azure OpenAI configuration.",
            status_code=500,
            details={"validation_errors": ve.errors()},
        ) from ve
    except Exception as e:
        raise LLMException(
            message="Failed to initialize Azure OpenAI client.",
            status_code=500,
            details={"error": str(e)},
        ) from e