from langchain.tools import tool
from ..models import (
    MindatGeoMaterialQuery,
    MindatGeomaterialInput,
    MindatLocalityQuery,
    MindatLocalityInput,
)
from pydantic import BaseModel
from typing import Union, Dict, Any, Optional, List
from pathlib import Path
import json
import logging
from ..services.mindat_endpoints import get_geomaterial_api, get_locality_api
from ..utils.custom_message import MindatAPIException



# Directories
PARENT_DIR = Path(__file__).parent.resolve()
BASE_DATA_DIR = PARENT_DIR.parent / "contents"

def _to_params(q: Union[BaseModel, Dict[str, Any]]) -> Dict[str, str]:
    """
    Convert a Pydantic model or dict into API-ready params:
    - dump with aliases (if model)
    - drop None
    - convert lists to CSV strings
    """
    if isinstance(q, BaseModel):
        params: Dict[str, Any] = q.model_dump(by_alias=True, exclude_none=True)
    else:
        # assume it's already a dict-like input; drop None values
        params = {k: v for k, v in q.items() if v is not None}

    for k, v in list(params.items()):
        if isinstance(v, (list, tuple)):
            params[k] = ",".join(map(str, v))
        else:
            params[k] = str(v) if not isinstance(v, (int, float, str)) else v  # ensure JSON-serializable scalars

    return params  # type: ignore[return-value]





#####################################
# Geomaterial data collector tool
#####################################
@tool(
    "mindat_geomaterial_collector",
    description=(
        "Query Mindat /v1/geomaterials using a structured filter.\n"
        "Use this when the user asks to find minerals/geomaterials by properties "
        "(e.g., crystal system, hardness range, transparency, composition).\n\n"
        "Input: { query: MindatGeomaterialInput }\n"
        "Output: JSON results from Mindat."
    ),
    args_schema=MindatGeomaterialInput,
    return_direct=False,
)
def mindat_geomaterial_collector(
    query: Union[MindatGeomaterialInput, Dict[str, Any]]
) -> str:
    try:
        print("\n")
        print("Mindat Geomaterial Collector called with query:", query)
        query_dict = _to_params(query)
        geomaterial_api = get_geomaterial_api()
        response = geomaterial_api.search_geomaterials_minerals(query_dict)
        print("\n")
        # print("Received response from Mindat Geomaterial API : ", response)

        if not isinstance(response, dict) or not response.get("results"):
            raise MindatAPIException(
                message="Empty or invalid response from Mindat API for the Geomaterial endpoint",
                status_code=500,
                severity="ERROR",
                details={"response": response},
            )

        sample_dir = BASE_DATA_DIR / "sample_data"
        sample_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = sample_dir / "mindat_geomaterial_response.json"
        print("\n")
        print("Saving response to file:", output_file_path)

        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4, ensure_ascii=False)

        result_count = len(response.get("results", []))
        return f"Success: Collected {result_count} mineral records and saved to {output_file_path}"

    except Exception as e:
        return f"Failed to collect data: {e}"








#####################################
# Locality data collector tool
#####################################
@tool(
    "mindat_locality_collector",
    description=(
        "Search Mindat /v1/localities by structured filters "
        "(country, description, include/exclude elements). "
        "Use when the user asks for localities with certain elements or in a country/region. "
        "Input: { query: MindatLocalityQuery }. Output: JSON."
    ),
    args_schema=MindatLocalityInput,  # <-- fixed
    return_direct=False,
)
def mindat_locality_collector(
    query: Union[MindatLocalityQuery, Dict[str, Any]]
) -> str:
    try:
        query_dict = _to_params(query)

        locality_api = get_locality_api()
        response = locality_api.search_localities(query_dict)

        if not isinstance(response, dict) or not response.get("results"):
            raise MindatAPIException(
                message="Empty or invalid response from Mindat API for the Locality endpoint",
                status_code=500,
                severity="ERROR",
                details={"response": response},
            )

        sample_dir = BASE_DATA_DIR / "sample_data"
        sample_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = sample_dir / "mindat_locality_response.json"

        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4, ensure_ascii=False)

        result_count = len(response.get("results", []))
        return f"Success: Collected {result_count} locality records and saved to {output_file_path}"

    except Exception as e:
        return f"Failed to collect data: {e}"
