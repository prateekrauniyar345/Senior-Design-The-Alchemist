from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()


AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")   


# define the llm
def initialize_llm() -> AzureChatOpenAI:
    llm = AzureChatOpenAI(
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_API_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY, 
        azure_deployment=AZURE_DEPLOYMENT_NAME,
        model="gpt-4o",
        temperature=0.7,
        max_tokens=None,
        timeout=None,
    )
    return llm