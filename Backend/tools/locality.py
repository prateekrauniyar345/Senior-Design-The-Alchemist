# tools/localities.py
import json
from pathlib import Path
from typing import Union, Dict, Any

from models import MindatLocalityInput
from services.mindat_endpoints import get_locality_api
from utils import to_params

# Directories
PARENT_DIR = Path(__file__).parent.resolve()
BASE_DATA_DIR = PARENT_DIR.parent.parent / "contents"

def collect_localities(query: MindatLocalityInput) -> str:
    """
    Query Mindat /v1/localities using a structured filter.
    
    Use this when the user asks to find localities by properties 
    (e.g., country, region, associated minerals, geological setting).
    """
    try:
        print(f"Locality Tool called with: {query}")

        query_dict = to_params(query)
        
        locality_api = get_locality_api()
        response = locality_api.search_localities(query_dict)

        if not isinstance(response, dict) or not response.get("results"):
            return f"Error: No results found or invalid response. Details: {response}"

        sample_dir = BASE_DATA_DIR / "sample_data"
        sample_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = sample_dir / "mindat_locality_response.json"

        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4, ensure_ascii=False)

        result_count = len(response.get("results", []))
        return f"Success: Collected {result_count} locality records and saved to {output_file_path}"

    except Exception as e:
        return f"Critical Error in collect_localities: {str(e)}"