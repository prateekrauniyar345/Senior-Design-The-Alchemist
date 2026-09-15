# Backend/app/tools/locality.py
import json
from typing import Optional, List

from app.models import MindatLocalityQuery
from app.services.mindat_endpoints_services import get_locality_api
from app.utils import to_params, CONTENTS_DIR
from app.models import LocalityToolResponse


def collect_localities(
    country: Optional[str] = None,
    description: Optional[str] = None,
    elements_inc: Optional[List[str]] = None,
    elements_exc: Optional[List[str]] = None,
    page: int = 1,
    page_size: int = 100,
) -> LocalityToolResponse:
    """
    Query Mindat /v1/localities using individual filter parameters.
    Use this when the user asks to find mineral localities by country or elements.

    A country name is required for useful results.

    Parameters
    ----------
    country       : full English country name, e.g. "Brazil", "Japan", "USA"
    description   : locality description contains this string
    elements_inc  : elements that MUST be present at the locality, e.g. ["Au","Ag"]
    elements_exc  : elements that must NOT be present, e.g. ["Pb","Zn"]
    page          : page number for pagination (default 1)
    page_size     : results per page (default 100)
    """
    try:
        if not country:
            return LocalityToolResponse(
                status="ERROR",
                error="A country name is required to fetch locality data.",
                file_path="",
            )

        query = MindatLocalityQuery(
            country=country,
            description=description,
            elements_inc=elements_inc,
            elements_exc=elements_exc,
            page=page,
            page_size=page_size,
        )

        print(f"Locality Tool called with: {query}")
        query_dict = to_params(query)
        locality_api = get_locality_api()
        response = locality_api.search_localities(query_dict)

        if not isinstance(response, dict) or not response.get("results"):
            return LocalityToolResponse(
                status="ERROR",
                error=f"No results found for the given query. Response: {response}",
                file_path="",
            )

        sample_dir = CONTENTS_DIR / "sample_data"
        sample_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = sample_dir / "mindat_locality_response.json"

        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4, ensure_ascii=False)

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
