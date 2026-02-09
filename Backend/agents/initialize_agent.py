#################################################
# define the Agents for the multi-agent system
# And define the graph structure
#################################################
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
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
from IPython.display import Image, display       # for visualizing the graph


# get the llm initialized
llm = initialize_llm()



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


# Global variables - will be initialized lazily
mcp_tools = None
mindat_geomaterial = None
mindat_locality = None
histogram_plotter = None
network_plotter = None
heatmap_plotter = None


async def initialize_agents():
    """Initialize all agents with MCP tools. Must be called before using the graph."""
    global mcp_tools, mindat_geomaterial, mindat_locality, histogram_plotter, network_plotter, heatmap_plotter
    
    if mcp_tools is not None:
        return  # Already initialized
    
    # Load MCP tools once
    mcp_tools = await get_mcp_tools()
    
    # ----------------------------------------------
    # Mindat Geomaterial Collector Agent
    # ----------------------------------------------
    mindat_geomaterial = create_agent(
        model=llm, 
        tools=mcp_tools,
        system_prompt=geomaterial_collector_prompt
    )

    # ----------------------------------------------
    # Mindat Locality Collector Agent
    # ----------------------------------------------
    mindat_locality = create_agent(
        model=llm,
        tools=mcp_tools,
        system_prompt=locality_collector_prompt
    )

    # ----------------------------------------------
    # Histogram Plotter Agent
    # ----------------------------------------------
    histogram_plotter = create_agent(
        model=llm,
        tools=mcp_tools,
        system_prompt=histogram_plotter_prompt
    )

    # ----------------------------------------------
    # Network Plotter Agent
    # ----------------------------------------------
    network_plotter = create_agent(
        model=llm,
        tools=mcp_tools,
        system_prompt=network_plotter_prompt
    )

    # ----------------------------------------------
    # Heatmap Plotter Agent
    # ----------------------------------------------
    heatmap_plotter = create_agent(
        model=llm,
        tools=mcp_tools,
        system_prompt=heatmap_plotter_prompt
    )   

# ----------------------------------------------
# Define the Graph Structure
# ----------------------------------------------

# Define ControllerDecision schema
class ControllerDecision(BaseModel):
    """Decision made by the controller about which agent to invoke next."""
    action: Literal["geomaterial_collector", "locality_collector", "histogram_plotter", "network_plotter", "heatmap_plotter", "FINISH"] = Field(
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
    messages = state["messages"]
    
    # Create LLM with structured output capability
    decision_llm = llm.with_structured_output(ControllerDecision) 
    
    # Build the decision prompt
    decision_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    # Create and invoke the chain
    chain = decision_prompt | decision_llm
    decision: ControllerDecision = await chain.ainvoke({"messages": messages})
    
    # Log the decision
    print(f"\nSupervisor Decision: {decision.action}")
    if decision.reasoning:
        print(f"   Reasoning: {decision.reasoning}")
    
    # Return state update with routing decision
    return {
        "next": decision.action,
        "messages": [AIMessage(content=f"Supervisor routing to: {decision.action}")]
    }

# ----------------------------------------------
# Agent Wrapper Nodes
# ----------------------------------------------

@traceable(run_type="chain", name="geomaterial_collector_agent")
async def geomaterial_collector_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    print(f"[DEBUG] geomaterial_collector_node called with {len(state['messages'])} messages")
    if mindat_geomaterial is None:
        raise RuntimeError("Agents not initialized! Call initialize_agents() first")
    try:
        result = await mindat_geomaterial.ainvoke(state)  # ainvoke!
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
    result = await mindat_locality.ainvoke(state)  # ainvoke!
    return {
        "messages": result["messages"],
        "next": "supervisor"
    }

@traceable(run_type="chain", name="histogram_plotter_agent")
async def histogram_plotter_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    result = await histogram_plotter.ainvoke(state)  # ainvoke!
    return {
        "messages": result["messages"],
        "next": "supervisor"
    }

@traceable(run_type="chain", name="network_plotter_agent")
async def network_plotter_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    result = await network_plotter.ainvoke(state)  # ainvoke!
    return {
        "messages": result["messages"],
        "next": "supervisor"
    }

@traceable(run_type="chain", name="heatmap_plotter_agent")
async def heatmap_plotter_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    result = await heatmap_plotter.ainvoke(state)  # ainvoke!
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