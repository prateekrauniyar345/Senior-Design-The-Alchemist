from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI
from initialize_llm import initialize_llm


# initialize the llm
llm = initialize_llm()

def create_agent(llm:AzureChatOpenAI, tools:list, system_message:str)->AgentExecutor:
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_message),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            HumanMessage(content="{input}"),
        ]
    )
    agent = create_openai_tools_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
        verbose=True,
        max_iterations=3,
        early_stopping_method="generate",
    )
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor