# tools/geomaterials.py
import json
from pathlib import Path
from typing import Union, Dict, Any

from Backend.models import MindatGeoMaterialQuery
from Backend.services import get_geomaterial_api
from Backend.utils import to_params, CONTENTS_DIR
from Backend.models import GeomaterialToolResponse


def collect_geomaterials(query: MindatGeoMaterialQuery) -> GeomaterialToolResponse:
    """
    Query Mindat /v1/geomaterials using a structured filter.
    Use this when the user asks to find minerals/geomaterials by properties
    (e.g., crystal system, hardness range, transparency, composition).
    """
    try:
        query_dict = to_params(query)
        geomaterial_api = get_geomaterial_api()
        response = geomaterial_api.search_geomaterials_minerals(query_dict)

        # Handle Empty or Invalid API Response
        if not isinstance(response, dict) or not response.get("results"):
            return GeomaterialToolResponse(
                status="ERROR",
                error=f"No results found or invalid response. Details: {response}",
                file_path="",
                raw_data=response
            )

        # Save to file
        sample_dir = CONTENTS_DIR / "sample_data"
        sample_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = sample_dir / "mindat_geomaterial_response.json"
        
        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4, ensure_ascii=False)

        # Return the structured Pydantic model
        return GeomaterialToolResponse(
            status="OK",
            error=None,
            file_path=str(output_file_path),
            raw_data=response
        )

    except Exception as e:
        return GeomaterialToolResponse(
            status="ERROR",
            error=f"Critical Error: {str(e)}",
            file_path="",
            raw_data=None
        )