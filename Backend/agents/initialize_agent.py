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
from typing import List, Dict, Any, TypedDict, Union, Optional
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

##############################
# Define the Graph Structure
##############################

# crete the state
class State(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]
    next: str

# get the graph
graph = StateGraph(State)


# ----------------------------------------------
# Define the supervisor agent node
# ----------------------------------------------                 




# Add nodes (name, runnable/callable)
graph.add_node("collector", mindat_geomaterial)
graph.add_node("locality_collector", mindat_locality)
graph.add_node("plotter", histogram_plotter)

# Wire the flow: START -> collector -> plotter -> END
graph.add_edge(START, "supervisor")
graph.add_edge("collector", "plotter")
graph.add_edge("plotter", END)

# Compile
app = graph.compile()




