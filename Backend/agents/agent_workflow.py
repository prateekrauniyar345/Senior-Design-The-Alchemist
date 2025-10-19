from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
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
logging.basicConfig(level=logging.INFO)
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
    logger.info(f"Executing agent: {name}")
    try:
        # For histogram plotter, inject the data file path into the message
        if name == "histogram_plotter" and state.get("data_file_path"):
            messages = [HumanMessage(content=f"Create a histogram from the mineral data at {state['data_file_path']}")]
            result = agent.invoke({"messages": messages})
        else:
            # Pass only the messages to the agent (not the full state)
            result = agent.invoke({"messages": state["messages"]})
        
        output = result.get("output", "")
        
        # Initialize updated state with the new message
        # IMPORTANT: We must preserve existing state values
        updated_state = {
            "messages": [AIMessage(content=output, name=name)],
            "data_file_path": state.get("data_file_path", ""),  # Preserve existing value
            "plot_file_path": state.get("plot_file_path", "")   # Preserve existing value
        }
        
        # Check if this is the collector agent and it successfully collected data
        if name == "collector":
            # Look for the success message and file path in various formats
            file_path = None
            
            # Pattern 1: "Success: ... saved to <path>"
            if "saved to" in output:
                file_path_match = re.search(r'saved to\s+(.+?\.json)', output)
                if file_path_match:
                    file_path = file_path_match.group(1).strip()
            
            # Pattern 2: Output is just a file path ending in .json
            elif output.strip().endswith('.json'):
                # The output might just be the file path
                file_path = output.strip()
            
            # Pattern 3: Look for any .json file path in the output
            elif '.json' in output:
                # Match file paths including those with spaces
                json_match = re.search(r'(/[^\n]+\.json)', output)
                if json_match:
                    file_path = json_match.group(1).strip()
            
            if file_path:
                updated_state["data_file_path"] = file_path
                logger.info(f"✓ Data file saved: {updated_state['data_file_path']}")
            else:
                logger.warning(f"Collector output doesn't contain a valid file path: {output}")
        
        elif name == "histogram_plotter":
            # Check if plot was successfully created
            plot_path = None
            
            # Pattern 1: "Success: ... saved to <path>"
            if "saved to" in output:
                plot_path_match = re.search(r'saved to\s+(.+?\.png)', output)
                if plot_path_match:
                    plot_path = plot_path_match.group(1).strip()
            
            # Pattern 2: Output is just a file path ending in .png
            elif output.strip().endswith('.png'):
                plot_path = output.strip()
            
            # Pattern 3: Look for any .png file path in the output
            elif '.png' in output:
                # Match file paths including those with spaces
                png_match = re.search(r'(/[^\n]+\.png)', output)
                if png_match:
                    plot_path = png_match.group(1).strip()
            
            if plot_path:
                updated_state["plot_file_path"] = plot_path
                logger.info(f"✓ Plot saved: {updated_state['plot_file_path']}")
            else:
                logger.warning(f"Plotter output doesn't contain a valid plot path: {output}")
        
        logger.info(f"Agent {name} updated state - data_file_path: {updated_state.get('data_file_path')}, plot_file_path: {updated_state.get('plot_file_path')}")
        return updated_state
        
    except Exception as e:
        logger.error(f"Error in {name} agent: {str(e)}")
        # Preserve state even on error
        return {
            "messages": [AIMessage(content=f"Error in {name}: {str(e)}", name=name)],
            "data_file_path": state.get("data_file_path", ""),
            "plot_file_path": state.get("plot_file_path", "")
        }

# Define available agents and options
members = ["collector", "histogram_plotter"]
options = ["FINISH"] + members

# Supervisor prompt template
supervisor_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("system",
     "Given the conversation above, who should act next? Or should we FINISH? Select one of: {options}"),
]).partial(options=str(options), members=", ".join(members))

# Initialize LLM
try:
    llm = initialize_llm()
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    llm = None

def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """Supervisor node that decides the next agent"""
    logger.info("=== SUPERVISOR ROUTING ===")
    
    if not llm:
        logger.error("LLM not initialized")
        return {
            "next": "FINISH",
            "data_file_path": state.get("data_file_path", ""),
            "plot_file_path": state.get("plot_file_path", "")
        }

    # Get current state
    messages = state.get("messages", [])
    data_file_path = state.get("data_file_path", "")
    plot_file_path = state.get("plot_file_path", "")
    
    logger.info(f"State: data={bool(data_file_path)}, plot={bool(plot_file_path)}, msgs={len(messages)}")
    if data_file_path:
        logger.info(f"Data file path: {data_file_path}")
    if plot_file_path:
        logger.info(f"Plot file path: {plot_file_path}")
    
    # Get original user query
    user_query = ""
    if messages:
        for msg in messages:
            if isinstance(msg, HumanMessage):
                user_query = msg.content.lower()
                break
    
    # Deterministic routing
    next_action = "FINISH"
    
    # Check if we're stuck in a loop - if we have too many messages without progress
    if len(messages) > 15 and not data_file_path:
        logger.warning(f"⚠️  Possible infinite loop detected - {len(messages)} messages but no data collected")
        next_action = "FINISH"
        logger.info(f"→ FINISH (breaking potential loop)")
        return {
            "next": next_action,
            "data_file_path": data_file_path,
            "plot_file_path": plot_file_path
        }
    
    # Stage 1: Need to collect data
    if not data_file_path:
        next_action = "collector"
        logger.info(f"→ COLLECTOR (no data)")
    
    # Stage 2: Have data, need to plot
    elif data_file_path and not plot_file_path:
        # Check if user wants visualization
        wants_plot = any(kw in user_query for kw in ["plot", "histogram", "chart", "graph", "visual"])
        if wants_plot:
            next_action = "histogram_plotter"
            logger.info(f"→ HISTOGRAM_PLOTTER (data ready, plot requested)")
        else:
            next_action = "FINISH"
            logger.info(f"→ FINISH (data collected, no plot requested)")
    
    # Stage 3: Everything complete
    else:
        next_action = "FINISH"
        logger.info(f"→ FINISH (workflow complete)")
    
    # Always preserve the state
    return {
        "next": next_action,
        "data_file_path": data_file_path,
        "plot_file_path": plot_file_path
    }

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
        collector_agent, histogram_plotter_agent = get_agents()
        
        collector_node = functools.partial(agent_node, agent=collector_agent, name="collector")
        histogram_plotter_node = functools.partial(agent_node, agent=histogram_plotter_agent, name="histogram_plotter")
        
        workflow = StateGraph(AgentState)
        
        workflow.add_node("supervisor", supervisor_node)
        workflow.add_node("collector", collector_node)
        workflow.add_node("histogram_plotter", histogram_plotter_node)
        
        workflow.add_edge("collector", "supervisor")
        workflow.add_edge("histogram_plotter", "supervisor")
        
        workflow.add_conditional_edges(
            "supervisor",
            lambda x: x["next"],
            {
                "collector": "collector",
                "histogram_plotter": "histogram_plotter",
                "FINISH": END,
            }
        )
        
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

def convert_file_path_to_url(file_path: str) -> str:
    """
    Convert absolute file system path to HTTP URL for serving static files
    
    Args:
        file_path: Absolute file system path
        
    Returns:
        HTTP URL path relative to the server
    """
    if not file_path:
        return ""
    
    # Convert to Path object for easier manipulation
    from pathlib import Path
    path = Path(file_path)
    
    # Find the 'contents' directory in the path
    try:
        parts = path.parts
        contents_index = parts.index('contents')
        # Build URL from 'contents' onwards
        url_parts = parts[contents_index:]
        url_path = '/' + '/'.join(url_parts)
        return url_path
    except (ValueError, IndexError):
        # If 'contents' not found, return the filename only
        logger.warning(f"Could not convert path to URL: {file_path}")
        return f"/contents/{path.name}"

async def run_agent_workflow(user_input: str) -> Dict[str, Any]:
    """Run the complete agent workflow"""
    try:
        app = get_workflow()
        
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "next": "",
            "data_file_path": "",
            "plot_file_path": ""
        }
        
        final_state = await app.ainvoke(initial_state, config={"recursion_limit": 25})
        
        messages = final_state.get("messages", [])
        data_file_path = final_state.get("data_file_path", "")
        plot_file_path = final_state.get("plot_file_path", "")
        
        # Convert file system paths to HTTP URLs
        data_url = convert_file_path_to_url(data_file_path)
        plot_url = convert_file_path_to_url(plot_file_path)
        
        if messages:
            last_message = messages[-1].content
            success = "Success:" in last_message or plot_file_path
            
            return {
                "success": success,
                "message": last_message,
                "data_file_path": data_url,
                "plot_file_path": plot_url,
                "all_messages": [msg.content for msg in messages]
            }
        else:
            return {
                "success": True,
                "message": "Workflow completed successfully",
                "data_file_path": data_url,
                "plot_file_path": plot_url
            }
            
    except Exception as e:
        error_msg = f"Workflow error: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "message": error_msg,
            "error": str(e)
        }