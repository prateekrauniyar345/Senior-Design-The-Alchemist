#################################################
# define the Agents for the multio agent system
# And define the graph structure
#################################################

from langchain.agents import create_agent
from .initialize_llm import initialize_llm
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain.messages import AnyMessage
import operator
from ..utils.custom_prompts import (
    system_prompt,
    geomaterial_collector_prompt, 
    histogram_plotter_prompt,
    locality_collector_prompt 
)
from ..tools import (
    mindat_geomaterial_collector,
    mindat_locality_collector,
    pandas_hist_plot,
)
from ..models import (
    MindatGeoMaterialQuery, 
    MindatGeomaterialInput, 
    MindatLocalityQuery, 
    MindatLocalityInput, 
    PandasDFInput
)
from typing_extensions import TypedDict, Annotated
from typing import List, Dict, Any, TypedDict, Union, Optional, Literal
from IPython.display import Image, display       # for visualizing the graph


# get the llm initialized
llm = initialize_llm()

# create the agent with llm , tools, and 

# ----------------------------------------------
# Mindat Geomaterial Collector Agent
# ----------------------------------------------
mindat_geomaterial = create_agent(
    llm=llm, 
    tools=[mindat_geomaterial_collector], 
    system_prompt=geomaterial_collector_prompt
)

# ----------------------------------------------
# Mindat Locality Collector Agent
# ----------------------------------------------
mindat_locality = create_agent(
    llm=llm,
    tools=[mindat_locality_collector],
    system_prompt=locality_collector_prompt
)

# ----------------------------------------------
# Histogram Plotter Agent
# ----------------------------------------------
histogram_plotter = create_agent(
    llm=llm,
    tools=[pandas_hist_plot],
    system_prompt=histogram_plotter_prompt
)   

# ----------------------------------------------
# Define the Graph Structure
# ----------------------------------------------

# Define ControllerDecision schema
class ControllerDecision(BaseModel):
    """Decision made by the controller about which agent to invoke next."""
    action: Literal["mindat_geomaterial", "mindat_locality", "histogram_plotter", "FINISH"] = Field(
        ...,
        description="Either 'FINISH' to end or the name of the agent to handle the query."
    )
    reasoning: Optional[str] = Field(
        None,
        description="Brief explanation of why this agent was selected."
    )


class State(TypedDict):
    #The Annotated type with operator.add ensures that new messages are appended to the existing list rather than replacing it.
    messages: Annotated[List[AnyMessage], operator.add]    
    next: Optional[str]


# ----------------------------------------------
# Supervisor Node (AI-Powered)
# ----------------------------------------------
def supervisor_node(state: State) -> dict:
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
    decision: ControllerDecision = chain.invoke({"messages": messages})
    
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

def collector_node(state: State) -> dict:
    """Wrapper for collector agent that returns to supervisor"""
    result = mindat_geomaterial.invoke(state)
    return {
        "messages": result["messages"],
        "next": "supervisor"  # Return control to supervisor
    }

def locality_node(state: State) -> dict:
    """Wrapper for locality collector agent"""
    result = mindat_locality.invoke(state)
    return {
        "messages": result["messages"],
        "next": "supervisor"
    }

def plotter_node(state: State) -> dict:
    """Wrapper for plotter agent"""
    result = histogram_plotter.invoke(state)
    return {
        "messages": result["messages"],
        "next": "supervisor"
    }

def finish_node(state: State) -> dict:
    """Terminal node that ends the workflow"""
    return {
        "messages": [AIMessage(content="✅ Workflow completed successfully!")],
        "next": "FINISH"
    }

# ----------------------------------------------
# Graph Construction
# ----------------------------------------------

# Create the graph with State
graph = StateGraph(State)

# Add all nodes
graph.add_node("supervisor", supervisor_node)  
graph.add_node("collector", collector_node)
graph.add_node("locality_collector", locality_node)
graph.add_node("plotter", plotter_node)
graph.add_node("FINISH", finish_node)

# Define the workflow edges
# START -> Supervisor
graph.add_edge(START, "supervisor")

# Supervisor routes to agents based on decision
graph.add_conditional_edges(
    "supervisor",
    lambda state: state.get("next", "FINISH"),  # Route based on 'next' field
    {
        "collector": "collector",
        "locality_collector": "locality_collector",
        "plotter": "plotter",
        "FINISH": "FINISH"
    }
)

# All agents return to supervisor (removed direct agent->agent edges)
graph.add_edge("collector", "supervisor")
graph.add_edge("locality_collector", "supervisor")
graph.add_edge("plotter", "supervisor")

# FINISH ends the workflow
graph.add_edge("FINISH", END)

# Compile the graph
app = graph.compile()


# ----------------------------------------------
# Visualization Helper
# ----------------------------------------------

def display_graph():
    """Display the compiled graph structure"""
    try:
        graph_image = app.get_graph().draw_mermaid_png()
        display(Image(graph_image))
        return True
    except Exception as e:
        print(f"Could not display graph: {e}")
        # Save to file as fallback
        try:
            with open("Backend/contents/agent_workflow_graph.png", "wb") as f:
                f.write(graph_image)
            print("Graph saved to Backend/contents/agent_workflow_graph.png")
        except:
            pass
        return False


# call the display_graph
display_graph()



