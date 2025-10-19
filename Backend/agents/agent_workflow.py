from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence, Dict, Any
import operator
import functools
import logging
import re

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

# Setup logging
logger = logging.getLogger(__name__)

# State class for the workflow
class AgentState(TypedDict):
    """State shared between agents"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    data_file_path: str
    plot_file_path: str

def agent_node(state: AgentState, agent, name: str) -> Dict[str, Any]:
    """Execute an agent and return updated state"""
    try:
        result = agent.invoke(state)
        
        # Extract file paths from agent responses
        updated_state = {
            "messages": [HumanMessage(content=result["output"], name=name)]
        }
        
        # Parse file paths from the response
        if name == "collector" and "Success:" in result["output"]:
            # Extract data file path from collector response
            file_path_match = re.search(r'saved to ([^\s]+)', result["output"])
            if file_path_match:
                updated_state["data_file_path"] = file_path_match.group(1)
        
        elif name == "histogram_plotter" and "Success:" in result["output"]:
            # Extract plot file path from plotter response
            file_path_match = re.search(r'saved to ([^\s]+)', result["output"])
            if file_path_match:
                updated_state["plot_file_path"] = file_path_match.group(1)
        
        return updated_state
        
    except Exception as e:
        logger.error(f"Error in {name} agent: {str(e)}")
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
    ("system", system_prompt.format(members=", ".join(members))),
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
try:
    llm = initialize_llm()
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    llm = None

def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """Supervisor node that decides the next agent"""
    try:
        if not llm:
            logger.error("LLM not initialized")
            return {"next": "FINISH"}
            
        # Create supervisor chain
        supervisor_chain = (
            supervisor_prompt
            | llm.bind_functions(functions=[function_def], function_call="route")
            | JsonOutputFunctionsParser()
        )
        
        result = supervisor_chain.invoke(state)
        return {"next": result["next"]}
    except Exception as e:
        logger.error(f"Supervisor error: {str(e)}")
        # Fallback logic based on the conversation
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1].content.lower()
            if "collect" in last_message or "data" in last_message:
                if not state.get("data_file_path"):
                    return {"next": "collector"}
                elif "plot" in last_message or "histogram" in last_message:
                    return {"next": "histogram_plotter"}
            return {"next": "FINISH"}
        return {"next": "collector"}  # Default

# Create specialized agents
def get_agents():
    """Create and return agent instances"""
    try:
        if not llm:
            raise Exception("LLM not initialized")
            
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
        
        return collector_agent, histogram_plotter_agent
        
    except Exception as e:
        logger.error(f"Failed to create agents: {e}")
        raise

# Build the workflow graph
def create_workflow() -> StateGraph:
    """Create the multi-agent workflow graph"""
    
    try:
        # Get agents
        collector_agent, histogram_plotter_agent = get_agents()
        
        # Create agent nodes
        collector_node = functools.partial(agent_node, agent=collector_agent, name="collector")
        histogram_plotter_node = functools.partial(agent_node, agent=histogram_plotter_agent, name="histogram_plotter")
        
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
        
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise

# Global workflow instance
_workflow_app = None

def get_workflow():
    """Get compiled workflow ready for execution"""
    global _workflow_app
    if _workflow_app is None:
        try:
            workflow = create_workflow()
            _workflow_app = workflow.compile()
        except Exception as e:
            logger.error(f"Failed to compile workflow: {e}")
            raise
    return _workflow_app

# Convenience function to run the workflow
async def run_agent_workflow(user_input: str) -> Dict[str, Any]:
    """
    Run the complete agent workflow
    
    Args:
        user_input (str): User's request
        
    Returns:
        Dict: Result with success status, message, and file paths
    """
    try:
        # Get compiled workflow
        app = get_workflow()
        
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "next": "",
            "data_file_path": "",
            "plot_file_path": ""
        }
        
        # Run workflow
        final_state = await app.ainvoke(initial_state)
        
        # Extract results
        messages = final_state.get("messages", [])
        data_file_path = final_state.get("data_file_path", "")
        plot_file_path = final_state.get("plot_file_path", "")
        
        # Determine success and create response
        if messages:
            last_message = messages[-1].content
            success = "Success:" in last_message or plot_file_path
            
            return {
                "success": success,
                "message": last_message,
                "data_file_path": data_file_path,
                "plot_file_path": plot_file_path,
                "all_messages": [msg.content for msg in messages]
            }
        else:
            return {
                "success": True,
                "message": "Workflow completed successfully",
                "data_file_path": data_file_path,
                "plot_file_path": plot_file_path
            }
            
    except Exception as e:
        error_msg = f"Workflow error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "error": str(e)
        }

