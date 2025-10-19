from ..services.mindat_collector import GeomaterialAPI
import json
from ..utils.helpers import check_sample_data_path
from pathlib import Path

current_dir = Path.cwd() # Get the current working directory
parent_dir = current_dir.parent # Navigate to the parent directory
sample_data_path = parent_dir / "contents" / "sample_data" # Construct the path to contents/sample_data


def mindat_geomaterial_collector_function(query : dict) -> bool:
    geomaterial_api = GeomaterialAPI()
    response = geomaterial_api.search_geomaterials_minerals(query)
    output_file_name = "mindat_geomaterial_response.json"
    # Check if we have a valid response
    if not response:
        return False
    # Prepare output file
    output_file_name = "mindat_geomaterial_response.json"
    
    # Check if sample data directory exists
    if check_sample_data_path():
        output_file_path = sample_data_path / output_file_name
        # Ensure directory exists
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        # Write response to file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=4, ensure_ascii=False)
        return True
    return False
  
