"""
Base Agent Factory - Scalable agent creation system (LangChain v1+ compatible)
"""
from typing import List, Dict, Any
from langchain.agents import create_agent 
from langchain.tools import BaseTool
from langchain_openai import AzureChatOpenAI
from langchain_core.runnables import Runnable
import logging

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating standardized agents with modern LangChain APIs"""
    
    def __init__(self, llm: AzureChatOpenAI):
        self.llm = llm
    
    def create_agent(
        self, 
        name: str,
        tools: List[BaseTool],
        system_prompt: str,
    ) -> Runnable:
        """
        Create a standardized agent executor using latest create_agent
        
        Args:
            name: Agent identifier
            tools: List of tools available to this agent
            system_prompt: System instructions for the agent
            verbose: Whether to enable verbose logging
            
        Returns:
            Configured AgentExecutor (Runnable)
        """
        # Latest create_agent handles messages automatically - no prompt needed!
        # Just pass system_prompt as string or SystemMessage
        agent = create_agent(
            model=self.llm,
            tools=tools,
            system_prompt=system_prompt,
        )
        
        logger.info(f"Created agent: {name} with {len(tools)} tools")
        return agent


class AgentRegistry:
    """
    Registry for managing all agents in the system
    """
    
    def __init__(self, factory: AgentFactory):
        self.factory = factory
        self._agents: Dict[str, Runnable] = {}
    
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