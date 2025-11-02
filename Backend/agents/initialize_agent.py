from langchain.agents import create_agent
from .initialize_llm import initialize_llm
from langgraph.graph import StateGraph, MessagesState, START, END
from ..utils.custom_prompts import system_prompt, geomaterial_collector_prompt, histogram_plotter_prompt
from ..tools import mindat_geomaterial_collector_function, plotly_visualizing_function
from typing import List, Dict, Any, TypedDict


# get the llm initialized
llm = initialize_llm()

# create the agent with llm , tools, and 
mindat_geo_material_agent = create_agent(
    llm=llm, 
    tools=mindat_geomaterial_collector_function, 
    system_message = geomaterial_collector_prompt
)


historyogram_plotter_agent = create_agent(
    llm=llm,
    tools=plotly_visualizing_function,
    system_message=histogram_plotter_prompt
)   



# create the langgraph agent graph
class State(TypedDict):
    messages: list[str]
    result: str

graph  = StateGraph(State)

# add the nodes
graph.add_node()






