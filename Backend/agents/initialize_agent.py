#################################################
# define the Agents for the multio agent system
# And define the graph structure
#################################################

from langchain.agents import create_agent
from .initialize_llm import initialize_llm
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, MessagesState, START, END
from ..utils.custom_prompts import (
    system_prompt,
    geomaterial_collector_prompt, 
    histogram_plotter_prompt,
    locality_collector_prompt 
)
from ..tools import (
    mindat_geomaterial_data_collector_function,
    mindat_locality_data_collector_function,
    pandas_hist_plot_function,
)
from ..models import (
    MindatGeoMaterialQuery, 
    MindatGeomaterialInput, 
    MindatLocalityQuery, 
    MindatLocalityInput, 
    PandasDFInput
)
from typing import List, Dict, Any, TypedDict, Union, Optional
from 


# get the llm initialized
llm = initialize_llm()

# create the agent with llm , tools, and 

# ----------------------------------------------
# Mindat Geomaterial Collector Agent
# ----------------------------------------------
mindat_geo_material_collector_agent = create_agent(
    llm=llm, 
    tools=[mindat_geomaterial_data_collector_function], 
    system_prompt=geomaterial_collector_prompt
)

# ----------------------------------------------
# Mindat Locality Collector Agent
# ----------------------------------------------
mindat_locality_collector_agent = create_agent(
    llm=llm,
    tools=[mindat_locality_data_collector_function],
    system_prompt=locality_collector_prompt
)

# ----------------------------------------------
# Histogram Plotter Agent
# ----------------------------------------------
histogram_plotter_agent = create_agent(
    llm=llm,
    tools=[pandas_hist_plot_function],
    system_prompt=histogram_plotter_prompt
)   

##############################
# Define the Graph Structure
##############################

# crete the state
class State(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]
    next: str

# get the graph
graph = StateGraph(State)

# Add nodes (name, runnable/callable)
graph.add_node("collector", mindat_geo_material_collector_agent)
graph.add_node("locality_collector", mindat_locality_collector_agent)
graph.add_node("plotter", histogram_plotter_agent)

# Wire the flow: START -> collector -> plotter -> END
graph.add_edge(START, "supervisor")
graph.add_edge("collector", "plotter")
graph.add_edge("plotter", END)

# Compile
app = graph.compile()




