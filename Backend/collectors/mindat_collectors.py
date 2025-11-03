# from ..services import get_geomaterial_api
# from pathlib import Path
# import json 
# import logging
# from typing import Union, Dict
# from ..models import MindatGeoMaterialQuery

# # Setup logging
# logger = logging.getLogger(__name__)

# # Get paths properly
# HERE = Path(__file__).resolve()
# ROOT = HERE.parents[1]  # Backend directory
# SAMPLE_DATA_DIR = ROOT / "contents" / "sample_data"

# def mindat_geomaterial_collector_function(query: Union[MindatGeoMaterialQuery, Dict]) -> str:
#     """
#     Collect geomaterial data from Mindat API and save to JSON file
    
#     Args:
#         query: Either a MindatGeoMaterialQuery object or a dictionary with query parameters
        
#     Returns:
#         str: Success/failure message with file path
#     """
#     try:
#         # Convert query to dict if it's a Pydantic model
#         if hasattr(query, 'model_dump'):
#             query_dict = query.model_dump(exclude_none=True)
#         else:
#             query_dict = query
        
#         # Get API instance
#         geomaterial_api = get_geomaterial_api()
        
#         # Make API call
#         response = geomaterial_api.search_geomaterials_minerals(query_dict)
        
#         # Check if we have a valid response
#         if not response or not response.get('results'):
#             logger.error("Empty or invalid response from Mindat API")
#             return "Failed: No data received from Mindat API"
        
#         # Ensure directory exists
#         SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
#         # Create output file path
#         output_file_path = SAMPLE_DATA_DIR / "mindat_geomaterial_response.json"
        
#         # Write response to file
#         with open(output_file_path, 'w', encoding='utf-8') as f:
#             json.dump(response, f, indent=4, ensure_ascii=False)
        
#         result_count = len(response.get('results', []))
#         logger.info(f"Successfully saved {result_count} records to {output_file_path}")
        
#         return f"Success: Collected {result_count} mineral records and saved to {output_file_path}"
        
#     except Exception as e:
#         error_msg = f"Failed to collect data: {str(e)}"
#         logger.error(error_msg)
#         return error_msg
  
