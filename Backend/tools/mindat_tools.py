from langchain.tools import StructuredTool
from ..collectors import mindat_geomaterial_collector_function
from ..models import MindatGeomaterialInput

mindat_geomaterial_collector_tool = StructuredTool.from_function(
    func=mindat_geomaterial_collector_function,
    name="mindat_geomaterial_collector_tool",
    description="useful for collecting mindat mineral information and saving as json, will return the file path.",
    return_direct=False,   #setting it to false enables us to send the output back to llm for further processing
    args_schema=MindatGeomaterialInput
)   
