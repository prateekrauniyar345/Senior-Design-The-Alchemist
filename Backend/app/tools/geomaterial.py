# Backend/app/tools/geomaterial.py
import json
from typing import Optional, List, Dict, Any

from app.models import MindatGeoMaterialQuery
from app.services import get_geomaterial_api
from app.utils import to_params, CONTENTS_DIR
from app.models import GeomaterialToolResponse


def collect_geomaterials(
    # ── IMA status ──────────────────────────────────────────
    ima: Optional[bool] = None,
    ima_status: Optional[List[int]] = None,
    ima_notes: Optional[List[int]] = None,
    # ── Hardness (use alias names that match Mindat API) ────
    hmin: Optional[float] = None,   # Mohs hardness lower bound
    hmax: Optional[float] = None,   # Mohs hardness upper bound
    # ── Crystal system (alias name) ─────────────────────────
    csystem: Optional[List[str]] = None,
    # ── Elements ────────────────────────────────────────────
    el_inc: Optional[List[str]] = None,
    el_exc: Optional[List[str]] = None,
    el_essential: Optional[bool] = None,
    # ── Physical properties ─────────────────────────────────
    name: Optional[str] = None,
    colour: Optional[str] = None,
    diapheny: Optional[List[str]] = None,
    lustretype: Optional[List[str]] = None,
    cleavagetype: Optional[List[str]] = None,
    fracturetype: Optional[List[str]] = None,
    tenacity: Optional[List[str]] = None,
    streak: Optional[str] = None,
    # ── Density ─────────────────────────────────────────────
    density_min: Optional[float] = None,
    density_max: Optional[float] = None,
    # ── Optics ──────────────────────────────────────────────
    ri_min: Optional[float] = None,
    ri_max: Optional[float] = None,
    opticaltype: Optional[str] = None,
    opticalsign: Optional[str] = None,
    optical2v_min: Optional[str] = None,
    optical2v_max: Optional[str] = None,
    bi_min: Optional[str] = None,
    bi_max: Optional[str] = None,
    # ── Misc ────────────────────────────────────────────────
    entrytype: Optional[List[int]] = None,
    expand: Optional[List[str]] = None,
    page: int = 1,
    page_size: int = 100,
) -> GeomaterialToolResponse:
    """
    Query Mindat /v1/geomaterials using flat filter parameters.
    All parameters are optional — pass only the ones relevant to the request.

    Parameters
    ----------
    ima           : True = IMA-approved minerals only
    hmin          : Mohs hardness lower bound (e.g. 5.0)
    hmax          : Mohs hardness upper bound (e.g. 7.0)
    csystem       : crystal system list, e.g. ["Hexagonal", "Isometric"]
    el_inc        : elements that MUST be present, e.g. ["Fe", "O"]
    el_exc        : elements that must NOT be present, e.g. ["S"]
    diapheny      : transparency list, e.g. ["Transparent", "Translucent"]
    lustretype    : lustre list, e.g. ["Vitreous", "Metallic"]
    density_min   : minimum density g/cm³
    density_max   : maximum density g/cm³
    opticaltype   : "Biaxial", "Isotropic", or "Uniaxial"
    page          : page number for pagination (default 1)
    page_size     : results per page (default 100)
    """
    try:
        # Build the Pydantic query using Python field names (aliases map to API params)
        query = MindatGeoMaterialQuery(
            ima=ima,
            ima_status=ima_status,
            ima_notes=ima_notes,
            hardness_min=hmin,      # Python field, alias=hmin
            hardness_max=hmax,      # Python field, alias=hmax
            crystal_system=csystem, # Python field, alias=csystem
            el_inc=el_inc,
            el_exc=el_exc,
            el_essential=el_essential,
            name=name,
            colour=colour,
            diapheny=diapheny,
            lustretype=lustretype,
            cleavagetype=cleavagetype,
            fracturetype=fracturetype,
            tenacity=tenacity,
            streak=streak,
            density_min=density_min,
            density_max=density_max,
            ri_min=ri_min,
            ri_max=ri_max,
            opticaltype=opticaltype,
            opticalsign=opticalsign,
            optical2v_min=optical2v_min,
            optical2v_max=optical2v_max,
            bi_min=bi_min,
            bi_max=bi_max,
            entrytype=entrytype,
            expand=expand,
            page=page,
            page_size=page_size,
        )

        query_dict = to_params(query)
        print("query dict for API call:", query_dict)
        geomaterial_api = get_geomaterial_api()
        response = geomaterial_api.search_geomaterials_minerals(query_dict)

        if not isinstance(response, dict) or not response.get("results"):
            return GeomaterialToolResponse(
                status="ERROR",
                error=f"No results found or invalid response. Details: {response}",
                file_path="",
            )

        sample_dir = CONTENTS_DIR / "sample_data"
        sample_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = sample_dir / "mindat_geomaterial_response.json"

        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=4, ensure_ascii=False)

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
