from langchain.tools import tool
from ..models import (
    MindatGeoMaterialQuery, 
    MindatGeomaterialInput, 
    MindatLocalityQuery, 
    MindatLocalityInput
)
import pathlib
from typing import Union, Dict
import json
import logging
from ..services.mindat_endpoints import get_geomaterial_api, get_locality_api
from ..utils.custom_message import MindatAPIException


# get cwd
PARENT_DIR = pathlib.Path(__file__).parent.resolve()
# base directory for the data storage
BASE_DATA_DIR=F"{PARENT_DIR.parent.parent}/contents"

@tool(
    name="mindat_geomaterial_data_collector_function",
    description=(
        "Query Mindat /v1/geomaterials using a structured filter.\n"
        "Use this when the user asks to find minerals/geomaterials by properties "
        "(e.g., crystal system, hardness range, transparency, composition).\n\n"
        "Input: { query: MindatGeoMaterialQuery }\n"
        "Output: JSON results from Mindat.\n\n"
        "Examples:\n"
        " - Find hexagonal, transparent minerals with Mohs 6-7 and include Ag, exclude Fe.\n"
        " - IMA-approved vitreous minerals named 'Quartz'."
    ), 
    args_schema=MindatGeomaterialInput, 
    return_direct=False, 
)
def mindat_geomaterial_data_collector_function(query: Union[MindatGeoMaterialQuery, Dict]) -> str:
    """
    Collect geomaterial data from Mindat API and save to JSON file
    
    Args:
        query: Either a MindatGeoMaterialQuery object or a dictionary with query parameters
        
    Returns:
        str: Success/failure message with file path
    """
    try:
        # Convert query to dict if it's a Pydantic model
        if hasattr(query, 'model_dump'):
            query_dict = query.model_dump(exclude_none=True)
        else:
            query_dict = query
        print("the query dict is", query_dict)
        # Get API instance
        geomaterial_api = get_geomaterial_api()
        # Make API call
        response = geomaterial_api.search_geomaterials_minerals(query_dict)
        # Check if we have a valid response
        if not response or not response.get('results'):
            raise MindatAPIException(
                message="Empty or invalid response from Mindat API for the Geomaterial endpoint",
                status_code=500,
                severity="ERROR",
                details={"response": response}
            )
        # Ensure directory exists
        SAMPLE_DATA_DIR= pathlib.Path(f"{BASE_DATA_DIR}/sample_data")
        SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        # Create output file path
        output_file_path = SAMPLE_DATA_DIR / "mindat_geomaterial_response.json"
        # Write response to file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=4, ensure_ascii=False)
        result_count = len(response.get('results', []))
        return f"Success: Collected {result_count} mineral records and saved to {output_file_path}"
        
    except Exception as e:
        error_msg = f"Failed to collect data: {str(e)}"
        return error_msg