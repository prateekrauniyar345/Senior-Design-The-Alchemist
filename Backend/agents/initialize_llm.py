from typing import Optional, Dict, Any
from langchain_openai import AzureChatOpenAI
from pydantic import ValidationError
from ..config.settings import settings
from ..utils.custom_message import LLMException
from ..utils.helpers import save_message, save_agent_task


DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.7


def initialize_llm() -> AzureChatOpenAI:
    """
    Build an AzureChatOpenAI client using strongly-typed app settings.
    Raises LLMException with structured details on failure.
    """
    try:
        # Validate presence of required settings (fail fast, clear message)
        api_version   = settings.azure_api_version
        azure_endpoint=  settings.azure_endpoint
        api_key       =  settings.azure_api_key
        deployment    = settings.azure_deployment

        # Construct LLM client
        llm = AzureChatOpenAI(
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            azure_deployment=deployment,
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
        )
        return llm 
    except Exception as e:
        print(f"Error initializing LLM: {e}")
