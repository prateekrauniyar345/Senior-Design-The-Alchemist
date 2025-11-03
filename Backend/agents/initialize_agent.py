#################################################
# define the Agents for the multio agent system
# And define the graph structure
#################################################

from langchain.agents import create_agent
from .initialize_llm import initialize_llm
from langgraph.graph import StateGraph, MessagesState, START, END
from ..utils.custom_prompts import (
    system_prompt, geomaterial_collector_prompt, 
    histogram_plotter_prompt,
    locality_collector_prompt 
)
from ..tools import mindat_geomaterial_collector_function, plotly_visualizing_function
from typing import List, Dict, Any, TypedDict


# get the llm initialized
llm = initialize_llm()

# create the agent with llm , tools, and 

# ------------------------------
# Mindat Geomaterial Collector Agent
# ------------------------------
mindat_geo_material_agent = create_agent(
    llm=llm, 
    tools=[mindat_geomaterial_collector_function], 
    system_message = geomaterial_collector_prompt
)

# ------------------------------
# Mindat Locality Collector Agent
# ------------------------------
mindat_locality_collector_agent = create_agent(
    llm=llm,
    tools=[mindat_geomaterial_collector_function],
    system_message=locality_collector_prompt
)

# ------------------------------
# Histogram Plotter Agent
# ------------------------------
histogram_plotter_agent = create_agent(
    llm=llm,
    tools=[plotly_visualizing_function],
    system_message=histogram_plotter_prompt
)   

##############################
# Define the Graph Structure
##############################

#  use built in MessagesState to manage the state of the agent
graph = StateGraph(MessagesState)

# Add nodes (name, runnable/callable)
graph.add_node("collector", mindat_geo_material_agent)
graph.add_node("plotter", histogram_plotter_agent)

# Wire the flow: START -> collector -> plotter -> END
graph.add_edge(START, "collector")
graph.add_edge("collector", "plotter")
graph.add_edge("plotter", END)

# Compile
app = graph.compile()




