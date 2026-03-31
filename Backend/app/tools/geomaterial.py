# Backend/app/tools/geomaterial.py
import json
from pathlib import Path
from typing import Union, Dict, Any

from app.models import MindatGeoMaterialQuery
from app.services import get_geomaterial_api
from app.utils import to_params, CONTENTS_DIR
from app.models import GeomaterialToolResponse


def collect_geomaterials(query: MindatGeoMaterialQuery) -> GeomaterialToolResponse:
    """
    Query Mindat /v1/geomaterials using a structured filter.
    Use this when the user asks to find minerals/geomaterials by properties
    (e.g., crystal system, hardness range, transparency, composition).
    """
    try:
        # Ensure limit is set to 100 to get maximum results
        if query.limit is None or query.limit < 100:
            query.limit = 100
        # if query.page_size is None or query.page_size<100:
        #     query.page_size =100
        query_dict = to_params(query)
        print("the query dict for fetching the data is : ", query_dict)
        geomaterial_api = get_geomaterial_api()
        response = geomaterial_api.search_geomaterials_minerals(query_dict)


        # Handle Empty or Invalid API Response
        if not isinstance(response, dict) or not response.get("results"):
            return GeomaterialToolResponse(
                status="ERROR",
                error=f"No results found or invalid response. Details: {response}",
                file_path="",
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
        )

    except Exception as e:
        return GeomaterialToolResponse(
            status="ERROR",
            error=f"Critical Error: {str(e)}",
            file_path="",
        )