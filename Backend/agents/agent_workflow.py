from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence, Literal
import operator
import functools

# Local imports
from .initialize_llm import initialize_llm
from .initialize_agent import create_agent
from ..tools.mindat_tools import mindat_geomaterial_collector_tool
from ..tools.visualizing_tools import pandas_plot
from ..utils.custom_prompts import (
    system_prompt, 
    geomaterial_collector_prompt,
    histogram_plotter_prompt
)

# Fix typo: AegntState -> AgentState
class AgentState(TypedDict):
    """State shared between agents"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    data_file_path: str = None  # Track collected data
    plot_file_path: str = None  # Track generated plots

def agent_node(state: AgentState, agent, name: str) -> dict:
    """Execute an agent and return updated state"""
    try:
        result = agent.invoke(state)
        return {
            "messages": [HumanMessage(content=result["output"], name=name)]
        }
    except Exception as e:
        return {
            "messages": [HumanMessage(content=f"Error in {name}: {str(e)}", name=name)]
        }

# Define available agents and options
members = ["collector", "histogram_plotter"]
options = ["FINISH"] + members

# Supervisor function definition for routing
function_def = {
    "name": "route",
    "description": "Select the next role based on the conversation context.",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "next": {
                "title": "Next",
                "type": "string",
                "enum": options,
                "description": f"Choose from: {', '.join(options)}"
            }
        },
        "required": ["next"],
    },
}

# Supervisor prompt template
supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    (
        "system",
        "Given the conversation above, who should act next? "
        "Rules:\n"
        "- If user asks for data collection, choose 'collector'\n"
        "- If data exists and user wants visualization, choose 'histogram_plotter'\n"
        "- If task is complete or user says goodbye, choose 'FINISH'\n"
        "Select one of: {options}"
    ),
]).partial(options=str(options), members=", ".join(members))

# Initialize LLM
llm = initialize_llm()

# Create supervisor chain
supervisor_chain = (
    supervisor_prompt
    | llm.bind_functions(functions=[function_def], function_call="route")
    | JsonOutputFunctionsParser()
)

# Create specialized agents
collector_agent = create_agent(
    llm, 
    [mindat_geomaterial_collector_tool], 
    geomaterial_collector_prompt
)

histogram_plotter_agent = create_agent(
    llm,
    [pandas_plot],
    histogram_plotter_prompt
)

# Create agent nodes
collector_node = functools.partial(agent_node, agent=collector_agent, name="Collector")
histogram_plotter_node = functools.partial(agent_node, agent=histogram_plotter_agent, name="HistogramPlotter")

def supervisor_node(state: AgentState) -> dict:
    """Supervisor node that decides the next agent"""
    try:
        result = supervisor_chain.invoke(state)
        return {"next": result["next"]}
    except Exception as e:
        # Fallback to finish if routing fails
        return {"next": "FINISH"}

# Build the workflow graph
def create_workflow() -> StateGraph:
    """Create the multi-agent workflow graph"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("collector", collector_node)
    workflow.add_node("histogram_plotter", histogram_plotter_node)
    
    # Add edges
    # All agents report back to supervisor
    workflow.add_edge("collector", "supervisor")
    workflow.add_edge("histogram_plotter", "supervisor")
    
    # Supervisor routes to agents or END
    workflow.add_conditional_edges(
        "supervisor",
        lambda x: x["next"],
        {
            "collector": "collector",
            "histogram_plotter": "histogram_plotter",
            "FINISH": END,
        }
    )
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    return workflow

# Create and compile the workflow
def get_workflow():
    """Get compiled workflow ready for execution"""
    workflow = create_workflow()
    return workflow.compile()

# Convenience function to run the workflow
async def run_agent_workflow(user_input: str) -> str:
    """
    Run the complete agent workflow
    
    Args:
        user_input (str): User's request
        
    Returns:
        str: Final response from the workflow
    """
    try:
        # Get compiled workflow
        app = get_workflow()
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "next": "",
        }
        
        # Run workflow
        final_state = await app.ainvoke(initial_state)
        
        # Extract final message
        if final_state.get("messages"):
            return final_state["messages"][-1].content
        else:
            return "Workflow completed successfully"
            
    except Exception as e:
        return f"Workflow error: {str(e)}"

