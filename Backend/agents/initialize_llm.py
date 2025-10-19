from typing import Optional, Dict, Any
from langchain_openai import AzureChatOpenAI
from pydantic import ValidationError
from Backend.config.settings import settings
from Backend.utils.custom_message import LLMException
from Backend.utils.helpers import save_message



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

def handle_query(user_input: str):
    """Run an LLM query and log both user and agent messages."""
    try:
        # Save user input
        save_message(sender="user", content=user_input)

        llm = initialize_llm()
        response = llm.invoke(user_input)  # Run the LLM

        # Save LLM response
        save_message(sender="agent", content=response.content)

        print("Query handled successfully.")
        return response.content

    except Exception as e:
        print(f"Error handling query: {e}")
        return f"Error: {e}"
