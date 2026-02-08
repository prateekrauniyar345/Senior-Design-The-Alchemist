from fastapi import APIRouter, Query, HTTPException
from Backend.services import get_geomaterial_api
from Backend.utils.custom_message import MindatAPIException

# Models
from Backend.models import MindatGeomaterialInput

# Create router instance
router = APIRouter(prefix="/mindat", tags=["mindat"])

@router.get("/geomaterials")
async def search_geomaterials(
    ima: str = Query(..., description="Search query for minerals"), 
):
    """Search Mindat API for geomaterials"""
    try:
        geo_api = get_geomaterial_api()
        test_params = {"ima": ima}
        response = geo_api.search_geomaterials_minerals(test_params)
        
        return {
            "success": True,
            "query": ima,
            "total_results": response.get("count", 0),
            "results": response.get("results", [])
        }
    except MindatAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

