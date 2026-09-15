# Backend/app/agents/initialize_agent.py
#################################################
# define the Agents for the multi-agent system
# And define the graph structure
#################################################
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
# from langchain.agents import create_agent
from app.agents.base_agent import AgentFactory, AgentRegistry
from app.agents.initialize_llm import initialize_llm
from langsmith import traceable
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages
from langchain.messages import AnyMessage
import operator
from app.utils.custom_prompts import (
    system_prompt,
    general_agent_prompt,
    geomaterial_collector_prompt, 
    locality_collector_prompt,
    vega_plot_generator_prompt
)
from typing_extensions import  Annotated
from typing import List, Dict, Any, TypedDict, Union, Optional, Literal
from IPython.display import Image, display  
import traceback
from app.models.agent_models import (
    CollectorAgentOutput,
    VegaAgentOutput,
    GeneralAgentOutput
)
from pathlib import Path


# ----------------------------------------------
# MCP Server Configuration
# ----------------------------------------------
# Get MCP server URL from environment variable (for Render deployment)
# Fallback to localhost for local development
MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "http://localhost:8010/mcp"
)
print(f"[Initialize Agent] MCP Server URL configured as: {MCP_SERVER_URL}")


# ----------------------------------------------
# Tool Schema Normalization for OpenAI
# ----------------------------------------------
def _normalize_schema_for_openai(schema: Dict[str, Any]) -> None:
    """
    Recursively rewrite a JSON schema in place so it satisfies OpenAI's strict
    function-calling requirements:
      1. Every object schema must set 'additionalProperties': false.
      2. Every object schema's 'required' array must list ALL of its properties
         (fields that were optional/had defaults are just included as-is; the
         model is still free to omit meaningful values via nullable typing,
         but MCP-generated schemas here don't mark them nullable, so we simply
         mark everything required, matching how the underlying Python function
         already provides sensible defaults for those args).

    Pydantic/FastMCP-generated schemas commonly factor nested models out into a
    top-level '$defs' section and reference them via '$ref' (e.g. a property
    schema of just {"$ref": "#/$defs/SomeModel"}). We don't resolve $refs, but
    since '$defs' entries are themselves full schemas, we normalize every
    definition in '$defs' directly wherever we encounter one.
    """
    if not isinstance(schema, dict):
        return

    # Normalize any nested definitions (Pydantic nests these under '$defs',
    # older JSON Schema drafts use 'definitions'). These are the actual object
    # schemas that '$ref' pointers resolve to.
    for defs_key in ("$defs", "definitions"):
        defs = schema.get(defs_key)
        if isinstance(defs, dict):
            for def_schema in defs.values():
                _normalize_schema_for_openai(def_schema)

    if schema.get("type") == "object" or ("properties" in schema and "type" not in schema):
        schema.setdefault("type", "object")
        schema.setdefault("additionalProperties", False)
        properties = schema.get("properties", {})
        if isinstance(properties, dict) and properties:
            schema["required"] = list(properties.keys())

    # Recurse into nested property schemas
    for prop_schema in schema.get("properties", {}).values():
        _normalize_schema_for_openai(prop_schema)

    # Recurse into array item schemas
    items_schema = schema.get("items")
    if isinstance(items_schema, dict):
        _normalize_schema_for_openai(items_schema)

    # Recurse into combinators (anyOf/oneOf/allOf) which is how Optional[...] fields are represented
    for combinator in ("anyOf", "oneOf", "allOf"):
        for sub_schema in schema.get(combinator, []):
            _normalize_schema_for_openai(sub_schema)


def normalize_tool_schemas(tools: List[Any]) -> List[Any]:
    """
    Normalize MCP tool schemas for OpenAI's strict function-calling requirements.

    langchain_mcp_adapters exposes the raw MCP inputSchema dict as `tool.args_schema`
    on the resulting StructuredTool, so we mutate it in place.
    """
    for tool in tools:
        schema = getattr(tool, "args_schema", None)
        if isinstance(schema, dict):
            _normalize_schema_for_openai(schema)
            print(f"[Tool Normalization] Normalized schema for '{tool.name}'")
        else:
            print(f"[Tool Normalization] Skipped '{getattr(tool, 'name', '?')}': args_schema is not a dict ({type(schema)})")
    return tools


# ----------------------------------------------
# Load the tools from the MCP servers
# ----------------------------------------------
async def load_mcp_tools():
    """Asynchronously load tools from the MCP servers"""
    try:
        print(f"[MCP Client] Attempting to connect to {MCP_SERVER_URL}")
        client = MultiServerMCPClient({
            "mindat": {
                "url": MCP_SERVER_URL,
                "transport": "http"  
            }
        })
        tools = await client.get_tools()
        print(f"[MCP Client] Successfully loaded {len(tools)} MCP tools from {MCP_SERVER_URL}")

        # Normalize tool schemas so OpenAI's strict function-calling validation accepts them
        tools = normalize_tool_schemas(tools)

        return tools
    except Exception as e:
        print(f"[MCP Client] Failed to load MCP tools from {MCP_SERVER_URL}: {e}")
        print(f"[MCP Client] Error type: {type(e).__name__}")
        raise RuntimeError(f"Could not connect to MCP server at {MCP_SERVER_URL}. Make sure the MCP service is running.") from e




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
_agents_initialized = False

async def initialize_agents():
    """Initialize all agents using the Registry."""
    global mcp_tools, _agents_initialized

    if _agents_initialized:
        return
    
    mcp_tools = await get_mcp_tools()
    print(f"MCP tools loaded: {[tool.name for tool in mcp_tools]}")
    
    # Register all agents in one place
    agent_configs = [
        ("general_agent", general_agent_prompt),
        ("geomaterial_collector", geomaterial_collector_prompt),
        ("locality_collector", locality_collector_prompt),
        ("vega_plot_generator", vega_plot_generator_prompt),
    ]
    agent_response_format = {
        "general_agent": GeneralAgentOutput,
        "geomaterial_collector": CollectorAgentOutput,
        "locality_collector": CollectorAgentOutput,
        "vega_plot_generator": VegaAgentOutput,
    }

    try:
        for name, prompt in agent_configs:
            registry.register(
                name=name,
                tools=mcp_tools,
                system_prompt=prompt,
                response_format  = agent_response_format.get(name)
            )
        print(f"Registered agents: {registry.list_agents()}")
        _agents_initialized = True
    except Exception as e:
        print(f"Error initializing agents: {e}")
        traceback.print_exc()
    
    

# ----------------------------------------------
# Define the Graph Structure
# ----------------------------------------------

# Define ControllerDecision schema
class ControllerDecision(BaseModel):
    """Decision made by the controller about which agent to invoke next."""
    next_agent: Literal[
                "general_agent",
                "geomaterial_collector", 
                "locality_collector", 
                "vega_plot_generator", 
                "FINISH"] = Field(
                            ...,
                            description="Either 'FINISH' to end or the name of the agent to handle the query."
                )
    reasoning: Optional[str] = Field(
        None,
        description="Brief explanation of why this agent was selected."
    )


class State(TypedDict):
    # create_agent's internal AgentState uses the add_messages reducer, which merges by
    # message id and returns the FULL accumulated message list on every ainvoke() call
    # (not just the newly generated ones). Using plain operator.add here would re-concatenate
    # that already-complete list on top of our existing state, duplicating history every
    # cycle and destabilizing the supervisor's routing decisions. add_messages merges by id
    # instead, so re-adding the same messages is a no-op and only genuinely new ones are appended.
    messages: Annotated[List[AnyMessage], add_messages]
    next: Optional[str]

    # sample_data path
    sample_data_path: Optional[str] = None

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
    print(f"all the registered agents are : ", registered_agents)
    options = registered_agents + ["FINISH"]
    print("all the Supervisor options: ", options)
    
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
        if structured and structured.status == "OK" and structured.file_path:
            updates["sample_data_path"] = structured.file_path

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
        if structured and structured.status == "OK" and structured.file_path:
            updates["sample_data_path"] = structured.file_path

        print(f"[DEBUG] locality_collector result: {result}")
        return updates

    except Exception as e:
        print(f"[ERROR] locality_collector_node failed: {e}")
        traceback.print_exc()
        raise



@traceable(run_type="chain", name="vega_plot_generator_agent")
async def vega_plot_generator_node(state: State) -> dict:
    agent = registry.get("vega_plot_generator")
    if agent is None:
        raise Exception("Vega Plot Generator agent not found in registry")

    try:
        # make the path visible to the LLM
        if state.get("sample_data_path"):
            state["messages"].append(
                SystemMessage(
                    content=f"SAMPLE_DATA_PATH={state['sample_data_path']}"
                )
            )
        result = await agent.ainvoke(state)
        updates: dict = {
            "messages": result["messages"],
            "next": "supervisor",
        }
        structured: VegaAgentOutput | None = result.get("structured_response")

        if structured and structured.status == "OK":
            updates["vega_spec"] = structured.vega_spec
            updates["profile"] = structured.profile
        return updates
    except Exception as e:
        print(f"[ERROR] vega_plot_generator_node failed: {e}")
        traceback.print_exc()
        raise


@traceable(run_type="chain", name="general_agent_node")
async def general_agent_node(state: State) -> dict:
    agent = registry.get("general_agent")
    if agent is None:
        raise Exception("General Agent not found in registry")
    try:
        result = await agent.ainvoke(state)
        updates: dict = {
            "messages": result["messages"],
            "next": "supervisor",
        }
        return updates
    except Exception as e:
        print(f"[ERROR] general_agent_node failed: {e}")
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
workflow.add_node("general_agent", general_agent_node)
workflow.add_node("geomaterial_collector", geomaterial_collector_node)
workflow.add_node("locality_collector", locality_collector_node) 
workflow.add_node("vega_plot_generator", vega_plot_generator_node)
workflow.add_node("FINISH", finish_node)

# Define the workflow edges
# START -> Supervisor
workflow.add_edge(START, "supervisor")

# Supervisor routes to agents based on decision
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state.get("next", "FINISH"),
    {
        "general_agent": "general_agent",
        "geomaterial_collector": "geomaterial_collector",
        "locality_collector": "locality_collector",
        "vega_plot_generator": "vega_plot_generator",
        "FINISH": "FINISH"
    }
)

# All agents return to supervisor
workflow.add_edge("general_agent", "supervisor")
workflow.add_edge("geomaterial_collector", "supervisor")
workflow.add_edge("locality_collector", "supervisor")
workflow.add_edge("vega_plot_generator", "supervisor")

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

    print("\n[DEBUG] Final message trace:")
    for i, msg in enumerate(result.get("messages", [])):
        print(f"   [{i}] {type(msg).__name__}: {msg.content}")

    print(f"[DEBUG] Graph execution complete. Result keys: {result.keys()}")
    print(f"[DEBUG] Result messages count: {len(result.get('messages', []))}")


    print("[DEBUG] Workflow finished.\n")

    return result
