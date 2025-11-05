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

#  use built in MessagesState to manage the state of the agent
graph = StateGraph(MessagesState)

# we will define the supervisor/controller 
# supervisor agent that will manage the flow between the other agents
# will take the system prompt and all tools


# ----------------------------------------------
# Define the tools for the Supervisor Agnet
# ----------------------------------------------

#tool uisng the geomaterial agent
@tool(
    name="use_geomaterial_agent",
    description=(
        "Delegate to the Geomaterial specialist agent. "
        "Use for /v1/geomaterials queries (properties, composition, hardness, etc.). "
        "Input: { query: MindatGeoMaterialQuery }"
    ),
    args_schema=MindatGeomaterialInput,
    return_direct=False,
)
def use_geomaterial_agent(query: Union[MindatGeoMaterialQuery, Dict[str, Any]]) -> str:
    # not using the alis
    payload = query.model_dump(by_alias=False, exclude_none=True) if hasattr(query, "model_dump") else query
    # force sub agent to use its own tools only
    msg = HumanMessage(
        content=(
            "Handle this geomaterial request using YOUR tools only. "
            "Return the string in this format : Used the Geomaterial Agent Successfully. Resault saved to  : file_path.\n\n"
            f"QUERY_JSON:\n{payload}"
        )
    )
    out = mindat_geo_material_collector_agent.invoke({"messages": [msg]})
    return out["messages"][-1].content


# tool using the locality agent
@tool(
    name="use_locality_agent",
    description=(
        "Delegate to the Locality specialist agent. "
        "Use for /v1/localities queries (country, description, include/exclude elements). "
        "Input: { query: MindatLocalityQuery }"
    ),
    args_schema=MindatLocalityInput,
    return_direct=False,
)
def use_locality_agent(query: Union[MindatLocalityQuery, Dict[str, Any]]) -> str:
    payload = query.model_dump(by_alias=True, exclude_none=True) if hasattr(query, "model_dump") else query
    msg = HumanMessage(
        content=(
            "Handle this locality request using YOUR tools only. "
             "Return the string in this format : Used the Geomaterial Agent Successfully. Resault saved to  : file_path.\n\n"
            f"QUERY_JSON:\n{payload}"
        )
    )
    out = mindat_locality_collector_agent.invoke({"messages": [msg]})
    return out["messages"][-1].content


# tool using the histogram plotter agent
@tool(
    name="use_histogram_plotter_agent",
    description=(
        "Delegate to the Histogram Plotter agent. "
        "Use to create histogram(s) from a JSON results file path produced by collectors. "
        "Input: { file_path: str, plot_title?: str }"
    ),
    args_schema=PandasDFInput,   # expects file_path, which is str
    return_direct=False,
)
def use_histogram_plotter_agent(file_path: str, plot_title: Optional[str] = None) -> str:
    # Pass a compact directive to the plotting agent
    directive = (
        "Create a histogram using your plotting tool with the provided file path "
        "and optional title. Return the plot file path."
    )
    msg = HumanMessage(content=f"{directive}\n\nfile_path={file_path}\nplot_title={plot_title or ''}")
    out = histogram_plotter_agent.invoke({"messages": [msg]})
    return out["messages"][-1].content



# ----------------------------------------------
# Supervisor / Controller Agent
# ----------------------------------------------
members = ["use_geomaterial_agent", "use_locality_agent", "use_histogram_plotter_agent"]
options = members + ["FINISH"]


system_prompt_template = ChatPromptTemplate.from_template(system_prompt)
rendered_system_prompt = system_prompt_template.format(
    members=", ".join(members),
    options=", ".join(options)
)

supervisor = create_agent(
    llm=llm, 
    tools=[
        use_geomaterial_agent, 
        use_locality_agent, 
        use_histogram_plotter_agent
    ], 
    system_prompt=rendered_system_prompt
)



# Add nodes (name, runnable/callable)
graph.add_node("supervisor", supervisor)
graph.add_node("collector", mindat_geo_material_collector_agent)
graph.add_node("locality_collector", mindat_locality_collector_agent)
graph.add_node("plotter", histogram_plotter_agent)

# Wire the flow: START -> collector -> plotter -> END
graph.add_edge(START, "supervisor")
graph.add_edge("collector", "plotter")
graph.add_edge("plotter", END)

# Compile
app = graph.compile()




