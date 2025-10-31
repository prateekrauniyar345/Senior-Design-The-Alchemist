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
        deployment    = settings.azure_deployment_name

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

# def handle_query(user_input: str, session_id=None) -> str:
#     """Run an LLM query and log both user and agent messages."""
#     # Save user query
#     session_id, user_msg_id = save_message(sender="user", content=user_input, session_id=session_id)

#     # Simulate or get agent response
#     response = "Here's the AI response for your question."
#     save_message(sender="agent", content=response, session_id=session_id)

#     return response, session_id


def handle_query(user_input: str, session_id=None):
    # Save user message
    session_id, user_msg_id = save_message(sender="user", content=user_input, session_id=session_id)

    # Initialize the LLM client (Azure GPT-4o)
    llm = initialize_llm()

    # Run the actual model prediction
    response = llm.invoke(user_input)  # Call the model to generate a real reply

    # Extract the text from the response
    ai_text = response.content if hasattr(response, "content") else str(response)

    # Save the AI’s response
    save_message(sender="agent", content=ai_text, session_id=session_id)

    return ai_text, session_id

# Example usage after agent response
# task_id = save_agent_task(
#     agent_name="Collector",
#     session_id=session_id,
#     input_message_id=user_msg_id,
#     output_message_id=agent_msg_id,
#     status="completed"
# )



# def handle_query(user_input: str, session_id=None):
#     # 1️⃣ Save user message
#     session_id, user_msg_id = save_message(sender="user", content=user_input, session_id=session_id)

#     # 2️⃣ Mark task start
#     task_id = save_agent_task("Collector", session_id, input_message_id=user_msg_id, status="running")

#     # 3️⃣ Run your LLM or agent process
#     response = "Here’s what I found about minerals in Idaho."  # Replace with real LLM response

#     # 4️⃣ Save AI message
#     _, agent_msg_id = save_message(sender="agent", content=response, session_id=session_id)

#     # 5️⃣ Mark task complete
#     save_agent_task("Collector", session_id, input_message_id=user_msg_id, output_message_id=agent_msg_id, status="completed")

#     return response, session_id

# from Backend.agents.initialize_llm import handle_query
# response, session_id = handle_query("What minerals are found in Idaho?")
