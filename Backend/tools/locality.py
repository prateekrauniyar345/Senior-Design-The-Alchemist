# tools/localities.py
import json
from pathlib import Path
from typing import Union, Dict, Any

from Backend.models import MindatLocalityQuery
from Backend.services.mindat_endpoints_services import get_locality_api
from Backend.utils import to_params, CONTENTS_DIR
from Backend.models import LocalityToolResponse


def collect_localities(query: MindatLocalityQuery) -> LocalityToolResponse:
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

        # 1. Handle API Failure or Empty Results
        if not isinstance(response, dict) or not response.get("results"):
            return LocalityToolResponse(
                status="ERROR",
                error=f"No results found for the given query. Response: {response}",
                file_path="",
            )

        # 2. Save logic
        sample_dir = CONTENTS_DIR / "sample_data"
        sample_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = sample_dir / "mindat_locality_response.json"

        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4, ensure_ascii=False)

        # 3. Successful Return
        return LocalityToolResponse(
            status="OK",
            error=None,
            file_path=str(output_file_path),
        )

    except Exception as e:
        return LocalityToolResponse(
            status="ERROR",
            error=f"Critical Error in collect_localities: {str(e)}",
            file_path="",
        )