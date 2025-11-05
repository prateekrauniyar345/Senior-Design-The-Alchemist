"""
Base Agent Factory - Scalable agent creation system
"""
from typing import List, Dict, Any
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain.tools import BaseTool
from langchain_openai import AzureChatOpenAI
from langchain_core.runnables import Runnable 
import logging

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating standardized agents"""
    
    def __init__(self, llm: AzureChatOpenAI):
        self.llm = llm
    
    def create_agent(
        self, 
        name: str,
        tools: List[BaseTool],
        system_prompt: str,
        verbose: bool = False
    ) -> Runnable: # return the runnable type so that it can be executed
        """
        Create a standardized agent executor
        
        Args:
            name: Agent identifier
            tools: List of tools available to this agent
            system_prompt: System instructions for the agent
            verbose: Whether to enable verbose logging
            
        Returns:
            Configured Agent (A LangChain Runnable object)
        """
        # Note: The LangChain utility `create_agent` accepts a SystemMessage 
        # or string for the system_prompt argument, but its internal logic 
        # is often easier to control with a simple prompt object like this:
        
        # We modify the prompt to ensure it's a ChatPromptTemplate 
        # object as expected by LangChain agent utilities.
        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt_template, 
        )
        
        logger.info(f"Created agent: {name} with {len(tools)} tools")
        return agent


class AgentRegistry:
    """
    Registry for managing all agents in the system
    Makes it easy to add new agents without modifying workflow logic
    """
    
    def __init__(self, factory: AgentFactory):
        self.factory = factory
        self._agents: Dict[str, Runnable] = {} # ⬅returns Runnable type
    
    def register(
        self, 
        name: str, 
        tools: List[BaseTool], 
        system_prompt: str
    ) -> None:
        """Register a new agent"""
        agent = self.factory.create_agent(name, tools, system_prompt)
        self._agents[name] = agent
        logger.info(f"Registered agent: {name}")
    
    def get(self, name: str) -> Runnable:
        """Get an agent by name"""
        if name not in self._agents:
            raise ValueError(f"Agent '{name}' not registered")
        return self._agents[name]
    
    def list_agents(self) -> List[str]:
        """List all registered agent names"""
        return list(self._agents.keys())