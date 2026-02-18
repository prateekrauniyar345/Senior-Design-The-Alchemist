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
    heatmap_plotter_prompt, 
    vega_plot_planner_prompt
)
from typing_extensions import  Annotated
from typing import List, Dict, Any, TypedDict, Union, Optional, Literal
from IPython.display import Image, display  
import traceback
from Backend.models.agent_models import (
    CollectorAgentOutput,
    PlotterAgentOutput,
    VegaAgentOutput
)
from pathlib import Path


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
        ("vega_plot_planner", vega_plot_planner_prompt),
    ]
    agent_response_format = {
        "geomaterial_collector": CollectorAgentOutput,
        "locality_collector": CollectorAgentOutput,
        "histogram_plotter": PlotterAgentOutput,
        "network_plotter": PlotterAgentOutput,
        "heatmap_plotter": PlotterAgentOutput,
        "vega_plot_planner": VegaAgentOutput,
    }

    try:
        for name, prompt in agent_configs:
            registry.register(
                name=name,
                tools=mcp_tools,
                system_prompt=prompt, 
                response_format  = agent_response_format.get(name)  # Pass the specific response format for this agent
            )
    except Exception as e:
        print(f"Error initializing agents: {e}")
        traceback.print_exc()
    
    # print all the agents in the registry to verify
    print(f"Registered agents: {registry.list_agents()}")

# ----------------------------------------------
# Define the Graph Structure
# ----------------------------------------------

# Define ControllerDecision schema
class ControllerDecision(BaseModel):
    """Decision made by the controller about which agent to invoke next."""
    next_agent: Literal[
                "geomaterial_collector", 
                "locality_collector", 
                "histogram_plotter", 
                "network_plotter", 
                "heatmap_plotter", 
                "vega_plot_planner", 
                "FINISH"] = Field(
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

    # data payloads (not in chat messages)
    geomaterial_raw: Optional[Dict[str, Any]] = None
    locality_raw: Optional[Dict[str, Any]] = None
    rows: Optional[List[Dict[str, Any]]] = None

    # plot payloads
    plot_file_path: Optional[str] = None

    # chart payloads
    vega_spec: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None 


# ----------------------------------------------
# Supervisor Node (AI-Powered)
# ----------------------------------------------
@traceable(run_type="chain", name="supervisor_decision")
async def supervisor_node(state: State) -> dict:
    # Dynamically get the list of agents from your Registry
    # This will return ['geomaterial_collector', 'locality_collector', ...]
    registered_agents = registry.list_agents()
    options = registered_agents + ["FINISH"]
    
    # Set up the structured output model
    decision_model = factory.llm.with_structured_output(ControllerDecision)
    
    # Inject the dynamic list into the system prompt
    decision_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", f"You must route to one of the following: {', '.join(options)}.")
    ])
    
    chain = decision_prompt | decision_model
    
    # Invoke and handle result
    decision = await chain.ainvoke({"messages": state["messages"]})
    
    print(f"\n[SUPERVISOR] Decision: {decision.next_agent}")
    
    return {
        "next": decision.next_agent,
        "messages": [AIMessage(content=f"Supervisor routing to {decision.next_agent}.")]
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
        updates: dict = {
            "messages": result["messages"],
            "next": "supervisor",
        }

        # map to structured output if available
        structured: CollectorAgentOutput | None = result.get("structured_response")

        # update state with raw data if available
        if structured and structured.status == "OK":
            # store these in State so other agents don’t parse messages
            updates["geomaterial_raw"] = structured.raw_data
            updates["rows"] = (structured.raw_data or {}).get("results", [])
        else:
            # optional: store error info
            updates["geomaterial_raw"] = None
            updates["rows"] = None

        print(f"[DEBUG] geomaterial_collector result: {result}")
        return updates
    
    except Exception as e:
        print(f"[ERROR] geomaterial_collector_node failed: {e}")
        traceback.print_exc()
        raise



@traceable(run_type="chain", name="locality_collector_agent")
async def locality_collector_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    agent = registry.get("locality_collector")
    if agent is None:
        raise Exception("Locality Collector agent not found in registry")
    try:
        result = await agent.ainvoke(state)  # ainvoke!
        updates: dict = {
            "messages": result["messages"],
            "next": "supervisor",
        }
        # map to structured output if available
        structured: CollectorAgentOutput | None = result.get("structured_response") or None

        # update state with raw data if available
        if structured and structured.status == "OK":
            # store these in State so other agents don’t parse messages
            updates["locality_raw"] = structured.raw_data
            updates["rows"] = (structured.raw_data or {}).get("results", [])
        else:
            # optional: store error info
            updates["locality_raw"] = None
            updates["rows"] = None  

        print(f"[DEBUG] locality_collector result: {result}")
        return updates

    except Exception as e:
        print(f"[ERROR] locality_collector_node failed: {e}")
        traceback.print_exc()
        raise


@traceable(run_type="chain", name="histogram_plotter_agent")
async def histogram_plotter_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    agent = registry.get("histogram_plotter")
    if agent is None:
        raise Exception("Histogram Plotter agent not found in registry")
    try:
        result = await agent.ainvoke(state)  # ainvoke!

        updates: dict = {
            "messages": result["messages"],
            "next": "supervisor",
        }

        structured: PlotterAgentOutput | None = result.get("structured_response") or None
        if structured and structured.status == "OK":
            updates["plot_file_path"] = structured.file_path
        else:
            updates["plot_file_path"] = None  # or some error info

        return updates
    except Exception as e:
        print(f"[ERROR] histogram_plotter_node failed: {e}")
        traceback.print_exc()
        raise


@traceable(run_type="chain", name="network_plotter_agent")
async def network_plotter_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    agent = registry.get("network_plotter")
    if agent is None:
        raise Exception("Network Plotter agent not found in registry")
    try:
        result = await agent.ainvoke(state)  # ainvoke!
        updates: dict = {
            "messages": result["messages"],
            "next": "supervisor",
        }
        structured: PlotterAgentOutput | None = result.get("structured_response") or None
        if structured and structured.status == "OK":
            updates["plot_file_path"] = structured.file_path
        else:
            updates["plot_file_path"] = None  # or some error info
        
        return updates
    except Exception as e:
        print(f"[ERROR] network_plotter_node failed: {e}")
        traceback.print_exc()
        raise


@traceable(run_type="chain", name="heatmap_plotter_agent")
async def heatmap_plotter_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    agent = registry.get("heatmap_plotter")
    if agent is None:
        raise Exception("Heatmap Plotter agent not found in registry")
    try:
        result = await agent.ainvoke(state)  # ainvoke!
        updates: dict = {
            "messages": result["messages"],
            "next": "supervisor",
        }
        structured: PlotterAgentOutput | None = result.get("structured_response") or None
        if structured and structured.status == "OK":
            updates["plot_file_path"] = structured.file_path
        else:
            updates["plot_file_path"] = None  # or some error info
        return updates
    except Exception as e:
        print(f"[ERROR] network_plotter_node failed: {e}")
        traceback.print_exc()
        raise


@traceable(run_type="chain", name="vega_plot_planner_agent")
async def vega_plot_planner_node(state: State) -> dict:  # Now async!
    """Wrapper calls MCP-enabled agent."""
    agent = registry.get("vega_plot_planner")
    if agent is None:
        raise Exception("Vega Plot Planner agent not found in registry")
    try:
        result = await agent.ainvoke(state)  # ainvoke!
        updates: dict = {
            "messages": result["messages"],
            "next": "supervisor",
        }
        structured: VegaAgentOutput | None = result.get("structured_response") or None
        if structured and structured.status == "OK":
            updates["vega_spec"] = structured.vega_spec
            updates["profile"] = structured.profile
        else:
            updates["vega_spec"] = None
            updates["profile"] = None
        return updates
    except Exception as e:
        print(f"[ERROR] vega_plot_planner_node failed: {e}")
        traceback.print_exc()
        raise


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
workflow.add_node("vega_plot_planner", vega_plot_planner_node)
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
        "vega_plot_planner": "vega_plot_planner",
        "FINISH": "FINISH"
    }
)

# All agents return to supervisor
workflow.add_edge("geomaterial_collector", "supervisor")
workflow.add_edge("locality_collector", "supervisor")
workflow.add_edge("histogram_plotter", "supervisor")
workflow.add_edge("network_plotter", "supervisor")
workflow.add_edge("heatmap_plotter", "supervisor")
workflow.add_edge("vega_plot_planner", "supervisor")

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
            base_dir = Path(__file__).resolve().parents[1]
            graph_path = base_dir / "contents" / "agent_workflow_graph.png"
            with open(graph_path, "wb") as f:
                f.write(graph_image)
            print(f"Graph saved to {graph_path}")
        except Exception as save_error:
            print(f"Could not save graph: {save_error}")
        return False
    

async def run_graph(input_messages: List[AnyMessage]):
    """Run the agent graph. Initializes agents on first call."""
    print(f"[DEBUG] run_graph called with {len(input_messages)} messages, message is : {input_messages}")
    await initialize_agents()  # Ensure agents are initialized
    print(f"[DEBUG] Agents initialized, invoking graph...")
    result = await agent_graph.ainvoke({"messages": input_messages})
    print(f"[DEBUG] Graph execution complete. Result keys: {result.keys()}")
    print(f"[DEBUG] Result messages count: {len(result.get('messages', []))}")
    return result