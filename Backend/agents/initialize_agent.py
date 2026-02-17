#################################################
# define the Agents for the multi-agent system
# And define the graph structure
#################################################
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
# from langchain.agents import create_agent
from Backend.agents.base_agent import AgentFactory, AgentRegistry
from Backend.agents.initialize_llm import initialize_llm
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain.messages import AnyMessage
import operator
from Backend.utils.custom_prompts import (
    system_prompt,
    geomaterial_collector_prompt, 
    histogram_plotter_prompt,
    locality_collector_prompt,
    network_plotter_prompt,
    heatmap_plotter_prompt
)
from typing_extensions import TypedDict, Annotated
from typing import List, Dict, Any, TypedDict, Union, Optional, Literal
from IPython.display import Image, display  



# ----------------------------------------------
# Load the tools from the MCP servers
# ----------------------------------------------
async def load_mcp_tools():
    """Asynchronously load tools from the MCP servers"""
    try:
        client = MultiServerMCPClient({
            "mindat": {
                "url": "http://localhost:8005/mcp",
                "transport": "http"  
            }
        })
        tools = await client.get_tools()
        print(f"Successfully loaded {len(tools)} MCP tools")
        return tools
    except Exception as e:
        print(f"Failed to load MCP tools: {e}")
        print(f"   Error type: {type(e).__name__}")




@traceable(run_type="chain", name="load_mcp_tools")
async def get_mcp_tools():
    """Load MCP tools for all agents."""
    return await load_mcp_tools()


# ----------------------------------------------
# Initialize the Factory and Registry
# ----------------------------------------------
factory = AgentFactory(llm=initialize_llm())
registry = AgentRegistry(factory)

# Global variables - will be initialized lazily
mcp_tools = None

async def initialize_agents():
    """Initialize all agents using the Registry."""
    global mcp_tools
    
    if mcp_tools is not None:
        return 
    
    mcp_tools = await get_mcp_tools()
    print(f"MCP tools loaded: {[tool.name for tool in mcp_tools]}")
    
    # Register all agents in one place
    agent_configs = [
        ("geomaterial_collector", geomaterial_collector_prompt),
        ("locality_collector", locality_collector_prompt),
        ("histogram_plotter", histogram_plotter_prompt),
        ("network_plotter", network_plotter_prompt),
        ("heatmap_plotter", heatmap_plotter_prompt),
    ]

    for name, prompt in agent_configs:
        registry.register(
            name=name,
            tools=mcp_tools,
            system_prompt=prompt
        )

# ----------------------------------------------
# Define the Graph Structure
# ----------------------------------------------

# Define ControllerDecision schema
class ControllerDecision(BaseModel):
    """Decision made by the controller about which agent to invoke next."""
    next_agent: Literal["geomaterial_collector", "locality_collector", "histogram_plotter", "network_plotter", "heatmap_plotter", "FINISH"] = Field(
        ...,
        description="Either 'FINISH' to end or the name of the agent to handle the query."
    )
    reasoning: Optional[str] = Field(
        None,
        description="Brief explanation of why this agent was selected."
    )


class State(TypedDict):
    # The Annotated type with operator.add ensures that new messages are appended to the existing list rather than replacing it.
    messages: Annotated[List[AnyMessage], operator.add]    
    next: Optional[str]


# ----------------------------------------------
# Supervisor Node (AI-Powered)
# ----------------------------------------------
@traceable(run_type="chain", name="supervisor_decision")
async def supervisor_node(state: State) -> dict:
    """
    AI-powered supervisor that decides which agent to route to next.
    Uses LLM with structured output to make intelligent routing decisions.
    """
    supervisor_with_structured_output = registry.register(
        name="supervisor_decision_llm",
        tools=[],  # No tools needed for decision making
        system_prompt=system_prompt
    ).with_structured_output(ControllerDecision)    

    # Extract messages from state
    messages = state["messages"]

    
    # Build the decision prompt
    decision_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    # Create and invoke the chain
    chain = decision_prompt | supervisor_with_structured_output
    decision: ControllerDecision = await chain.ainvoke({"messages": messages})
    
    # Log the decision
    print(f"\nSupervisor Decision: {decision.next}")
    if decision.reasoning:
        print(f"   Reasoning: {decision.reasoning}")
    
    # Return state update with routing decision
    return {
        "next": decision.next,
        "messages": [AIMessage(content=f"Supervisor routing to: {decision.next}")]
    }

# ----------------------------------------------
# Agent Wrapper Nodes
# ----------------------------------------------

@traceable(run_type="chain", name="geomaterial_collector_agent")
async def geomaterial_collector_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    print(f"[DEBUG] geomaterial_collector_node called with {len(state['messages'])} messages")
    agent = registry.get("geomaterial_collector")
    if agent is None:
        raise Exception("Geomaterial Collector agent not found in registry")
    try:
        result = await agent.ainvoke(state)  # ainvoke!
        print(f"[DEBUG] geomaterial_collector result: {result}")
        return {
            "messages": result["messages"],
            "next": "supervisor"
        }
    except Exception as e:
        print(f"[ERROR] geomaterial_collector_node failed: {e}")
        import traceback
        traceback.print_exc()
        raise

@traceable(run_type="chain", name="locality_collector_agent")
async def locality_collector_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    agent = registry.get("locality_collector")
    if agent is None:
        raise Exception("Locality Collector agent not found in registry")
    result = await agent.ainvoke(state)  # ainvoke!
    return {
        "messages": result["messages"],
        "next": "supervisor"
    }

@traceable(run_type="chain", name="histogram_plotter_agent")
async def histogram_plotter_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    agent = registry.get("histogram_plotter")
    if agent is None:
        raise Exception("Histogram Plotter agent not found in registry")
    result = await agent.ainvoke(state)  # ainvoke!
    return {
        "messages": result["messages"],
        "next": "supervisor"
    }

@traceable(run_type="chain", name="network_plotter_agent")
async def network_plotter_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    agent = registry.get("network_plotter")
    if agent is None:
        raise Exception("Network Plotter agent not found in registry")
    result = await agent.ainvoke(state)  # ainvoke!
    return {
        "messages": result["messages"],
        "next": "supervisor"
    }

@traceable(run_type="chain", name="heatmap_plotter_agent")
async def heatmap_plotter_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    agent = registry.get("heatmap_plotter")
    if agent is None:
        raise Exception("Heatmap Plotter agent not found in registry")
    result = await agent.ainvoke(state)  # ainvoke!
    return {
        "messages": result["messages"],
        "next": "supervisor"
    }

def finish_node(state: State) -> dict:
    """Terminal node that ends the workflow"""
    return {
        "messages": [AIMessage(content="Workflow completed successfully!")],
        "next": "FINISH"
    }

# ----------------------------------------------
# Graph Construction
# ----------------------------------------------

# Create the graph with State
workflow = StateGraph(State)

# Add all nodes
workflow.add_node("supervisor", supervisor_node)  
workflow.add_node("geomaterial_collector", geomaterial_collector_node)
workflow.add_node("locality_collector", locality_collector_node) 
workflow.add_node("histogram_plotter", histogram_plotter_node)
workflow.add_node("network_plotter", network_plotter_node)
workflow.add_node("heatmap_plotter", heatmap_plotter_node)
workflow.add_node("FINISH", finish_node)

# Define the workflow edges
# START -> Supervisor
workflow.add_edge(START, "supervisor")

# Supervisor routes to agents based on decision
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state.get("next", "FINISH"),
    {
        "geomaterial_collector": "geomaterial_collector",
        "locality_collector": "locality_collector",
        "histogram_plotter": "histogram_plotter",
        "network_plotter": "network_plotter",
        "heatmap_plotter": "heatmap_plotter",
        "FINISH": "FINISH"
    }
)

# All agents return to supervisor
workflow.add_edge("geomaterial_collector", "supervisor")
workflow.add_edge("locality_collector", "supervisor")
workflow.add_edge("histogram_plotter", "supervisor")
workflow.add_edge("network_plotter", "supervisor")
workflow.add_edge("heatmap_plotter", "supervisor")

# FINISH ends the workflow
workflow.add_edge("FINISH", END)

# Compile the graph
agent_graph = workflow.compile()


# ----------------------------------------------
# Visualization Helper
# ----------------------------------------------

def display_graph():
    """Display the compiled graph structure"""
    try:
        graph_image = agent_graph.get_graph().draw_mermaid_png()
        display(Image(graph_image))
        print("Graph displayed successfully!")
        return True
    except Exception as e:
        print(f"Could not display graph: {e}")
        # Save to file as fallback
        try:
            with open("Backend/contents/agent_workflow_graph.png", "wb") as f:
                f.write(graph_image)
            print("Graph saved to Backend/contents/agent_workflow_graph.png")
        except Exception as save_error:
            print(f"Could not save graph: {save_error}")
        return False
    

async def run_graph(input_messages: List[AnyMessage]):
    """Run the agent graph. Initializes agents on first call."""
    print(f"[DEBUG] run_graph called with {len(input_messages)} messages")
    await initialize_agents()  # Ensure agents are initialized
    print(f"[DEBUG] Agents initialized, invoking graph...")
    result = await agent_graph.ainvoke({"messages": input_messages})
    print(f"[DEBUG] Graph execution complete. Result keys: {result.keys()}")
    print(f"[DEBUG] Result messages count: {len(result.get('messages', []))}")
    return result