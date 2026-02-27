from typing import Optional
from langchain_openai import AzureChatOpenAI
from pydantic import ValidationError
from Backend.config.settings import settings
from Backend.utils.custom_message import LLMException

DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.7

def initialize_llm() -> AzureChatOpenAI:
    """
    Builds an AzureChatOpenAI client using strongly-typed app settings.
    Raises LLMException if configuration is missing or initialization fails.
    """
    try:
        # 1. Validate settings exist
        if not all([settings.azure_api_version, settings.azure_endpoint, settings.azure_api_key, settings.azure_deployment]):
            raise LLMException("Missing one or more Azure OpenAI configuration settings.")

        # 2. Construct LLM client
        llm = AzureChatOpenAI(
            api_version=settings.azure_api_version,
            azure_endpoint=settings.azure_endpoint,
            api_key=settings.azure_api_key,
            azure_deployment=settings.azure_deployment,
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
        )
        return llm

    except ValidationError as ve:
        # Handle Pydantic validation errors specifically
        raise LLMException(f"Configuration validation failed: {str(ve)}")
    except Exception as e:
        # Catch-all for connection or authentication errors
        # Logging the actual error 'e' is better than just printing
        raise LLMException(f"Failed to initialize AzureChatOpenAI: {str(e)}")