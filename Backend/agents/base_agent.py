"""
Base Agent Factory - Scalable agent creation system
"""
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain.tools import BaseTool
from langchain_openai import AzureChatOpenAI
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
        verbose: bool = True
    ) -> AgentExecutor:
        """
        Create a standardized agent executor
        
        Args:
            name: Agent identifier
            tools: List of tools available to this agent
            system_prompt: System instructions for the agent
            verbose: Whether to enable verbose logging
            
        Returns:
            Configured AgentExecutor
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=verbose,
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        logger.info(f"Created agent: {name} with {len(tools)} tools")
        return executor


class AgentRegistry:
    """
    Registry for managing all agents in the system
    Makes it easy to add new agents without modifying workflow logic
    """
    
    def __init__(self, factory: AgentFactory):
        self.factory = factory
        self._agents: Dict[str, AgentExecutor] = {}
    
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
    
    def get(self, name: str) -> AgentExecutor:
        """Get an agent by name"""
        if name not in self._agents:
            raise ValueError(f"Agent '{name}' not registered")
        return self._agents[name]
    
    def list_agents(self) -> List[str]:
        """List all registered agent names"""
        return list(self._agents.keys())
