from ..services import get_geomaterial_api
from pathlib import Path
from ..utils.helpers import check_sample_data_path
import json 
from ..models import MindatGeoMaterialQuery

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]  # adjust if your package depth differs
SAMPLE_DATA_DIR = ROOT / "contents" / "sample_data"
OUTPUT_FILE_NAME = "mindat_geomaterial_response.json"

def mindat_geomaterial_collector_function(query : MindatGeoMaterialQuery) -> str:
    query  = query.model_dump(exclude_none=True)
    geomaterial_api = get_geomaterial_api()
    response = geomaterial_api.search_geomaterials_minerals(query)
    output_file_name = "mindat_geomaterial_response.json"
    # Check if we have a valid response
    if not response:
        return "Failed: Empty response from Mindat API"
    # Prepare output file
    output_file_name = "mindat_geomaterial_response.json"
    
    # Check if sample data directory exists
    if check_sample_data_path():
        output_file_path = f"{SAMPLE_DATA_DIR}/{output_file_name}"
        # Ensure directory exists
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        # Write response to file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=4, ensure_ascii=False)
        return f"Success: Response saved to {output_file_path}"
    return "Failed: Sample data path check failed"
  
