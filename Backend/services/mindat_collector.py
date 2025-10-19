# this module will help us collect the data from different endpoints of mindat.org


from typing import Dict, Optional
from ..config.mindat_config import MindatAPIClient
from ..utils.custom_message import MindatAPIException, ErrorSeverity

class GeomaterialAPI:
    """Geomaterial API Client for interacting with Mindat's geomaterial endpoint"""
    
    def __init__(self, client: Optional[MindatAPIClient] = None):
        self.client = client or MindatAPIClient()
        self.endpoint = "geomaterials"
    
    def search_geomaterials_minerals(self, query_params: Dict) -> Dict:
        """Search geomaterials/minerals with given query parameters"""
        params = query_params if query_params else {}
        
        if not params:
            raise MindatAPIException(
                message="Query parameters cannot be empty",
                status_code=400,
                severity=ErrorSeverity.ERROR,
                details={"provided_params": params}
            )
        
        try:
            return self.client.get_data_from_api(self.endpoint, params)
        except Exception as e:
            raise MindatAPIException(
                message=f"Failed to search geomaterials: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.ERROR,
                details={"query_params": params}
            )
    
    def get_mineral_by_id(self, mineral_id: int) -> Dict:
        """Get specific mineral by ID"""
        if not isinstance(mineral_id, int) or mineral_id <= 0:
            raise ValueError("mineral_id must be a positive integer")
        
        try:
            params = {"id": mineral_id}
            return self.client.get_data_from_api(self.endpoint, params)
        except Exception as e:
            raise MindatAPIException(
                message=f"Failed to get mineral {mineral_id}: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.ERROR,
                details={"mineral_id": mineral_id}
            )


# Factory function
def get_geomaterial_api() -> GeomaterialAPI:
    """Get a configured GeomaterialAPI instance"""
    return GeomaterialAPI()
