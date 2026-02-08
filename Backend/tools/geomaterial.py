# tools/geomaterials.py
import json
from pathlib import Path
from typing import Union, Dict, Any

from Backend.models import MindatGeomaterialInput
from Backend.services import get_geomaterial_api
from Backend.utils import to_params



# Directories
PARENT_DIR = Path(__file__).parent.resolve()
BASE_DATA_DIR = PARENT_DIR.parent.parent / "contents" # Adjusted for tool/ subdir

def collect_geomaterials(query: MindatGeomaterialInput) -> str:
    """
    Query Mindat /v1/geomaterials using a structured filter.
    
    Use this when the user asks to find minerals/geomaterials by properties 
    (e.g., crystal system, hardness range, transparency, composition).
    """
    try:
        print(f"Geomaterial Tool called with: {query}")
        
        # Convert Pydantic model directly to API params
        query_dict = to_params(query)
        
        geomaterial_api = get_geomaterial_api()
        response = geomaterial_api.search_geomaterials_minerals(query_dict)

        if not isinstance(response, dict) or not response.get("results"):
             # Return a string error so the LLM sees it and can retry or apologize
            return f"Error: No results found or invalid response. Details: {response}"

        # Save to file
        sample_dir = BASE_DATA_DIR / "sample_data"
        sample_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = sample_dir / "mindat_geomaterial_response.json"

        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4, ensure_ascii=False)

        result_count = len(response.get("results", []))
        return f"Success: Collected {result_count} mineral records and saved to {output_file_path}"

    except Exception as e:
        return f"Critical Error in collect_geomaterials: {str(e)}"