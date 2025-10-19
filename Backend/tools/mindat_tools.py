from langchain.tools import StructuredTool
from ..collectors import mindat_geomaterial_collector_function
from ..models import MindatGeomaterialInput

mindat_geomaterial_collector_tool = StructuredTool.from_function(
    func=mindat_geomaterial_collector_function,
    name="mindat_collect",
    description="Collect mindat geomaterial data based on query filters and save to JSON. Returns the saved file path.",
    return_direct=False,
    args_schema=MindatGeomaterialInput
)   
