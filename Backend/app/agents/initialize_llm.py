# Backend/app/agents/initialize_llm.py
import os
from typing import Optional
# from langchain_openai import AzureChatOpenAI  # DEPRECATED - Using standard OpenAI instead
from langchain_openai import ChatOpenAI
from pydantic import ValidationError
from app.config.settings import settings
from app.utils.custom_message import LLMException

DEFAULT_TEMPERATURE = 0.7

# ============================================
# DEPRECATED: Azure OpenAI Implementation
# ============================================
# def initialize_llm() -> AzureChatOpenAI:
#     """
#     Builds an AzureChatOpenAI client using strongly-typed app settings.
#     Raises LLMException if configuration is missing or initialization fails.
#     """
#     try:
#         # 1. Validate settings exist
#         if not all([settings.azure_api_version, settings.azure_endpoint, settings.azure_api_key, settings.azure_deployment]):
#             raise LLMException("Missing one or more Azure OpenAI configuration settings.")
#
#         # 2. Construct LLM client
#         llm = AzureChatOpenAI(
#             api_version=settings.azure_api_version,
#             azure_endpoint=settings.azure_endpoint,
#             api_key=settings.azure_api_key,
#             azure_deployment=settings.azure_deployment,
#             model=DEFAULT_MODEL,
#             temperature=DEFAULT_TEMPERATURE,
#         )
#         return llm
#
#     except ValidationError as ve:
#         # Handle Pydantic validation errors specifically
#         raise LLMException(f"Configuration validation failed: {str(ve)}")
#     except Exception as e:
#         # Catch-all for connection or authentication errors
#         # Logging the actual error 'e' is better than just printing
#         raise LLMException(f"Failed to initialize AzureChatOpenAI: {str(e)}")


# ============================================
# OpenAI ChatOpenAI Implementation
# ============================================
def initialize_llm() -> ChatOpenAI:
    """
    Builds a ChatOpenAI client using OpenAI API.
    Reads model name and API key from environment variables.
    Raises LLMException if configuration is missing or initialization fails.
    """
    try:
        # 1. Read from environment
        api_key = os.getenv("OPENAI_API_KEY")
        model_name = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")  # Default to gpt-4o if not specified
        
        # 2. Validate configuration
        if not api_key:
            raise LLMException("Missing OPENAI_API_KEY in environment variables.")
        
        # 3. Construct LLM client
        llm = ChatOpenAI(
            api_key=api_key,
            model=model_name,
            temperature=DEFAULT_TEMPERATURE,
        )
        return llm

    except ValidationError as ve:
        # Handle Pydantic validation errors specifically
        raise LLMException(f"Configuration validation failed: {str(ve)}")
    except Exception as e:
        # Catch-all for connection or authentication errors
        raise LLMException(f"Failed to initialize ChatOpenAI: {str(e)}")