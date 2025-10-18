from typing import Dict, Optional
from ..config.mindat_config import MindatAPIClient, get_mindat_client
from ..utils.custom_message import MindatAPIException, ErrorSeverity

class GeomaterialAPI:
    """Geomaterial API Client for interacting with Mindat's geomaterial endpoint"""
    
    def __init__(self, client: Optional[MindatAPIClient] = None):
        self.client = client or get_mindat_client()
        self.endpoint_key = "geomaterials"  # Use endpoint key instead of full URL
    
    def search_geomaterials_minerals(self, query_params: Dict) -> Dict:
        """Search geomaterials/minerals with given query parameters"""
        
        # Use dict directly instead of Pydantic model for now
        params = query_params if query_params else {}
        
        if not params:
            raise MindatAPIException(
                message="Query parameters cannot be empty",
                status_code=400,
                severity=ErrorSeverity.ERROR,
                details={"provided_params": params}
            )
        
        try:
            return self.client.get_data_from_api(self.endpoint_key, params)
        except Exception as e:
            raise MindatAPIException(
                message=f"Failed to search geomaterials: {str(e)}",
                status_code=500,
                severity=ErrorSeverity.ERROR,
                details={"query_params": params}
            )

# Factory function
def get_geomaterial_api() -> GeomaterialAPI:
    """Get GeomaterialAPI instance"""
    return GeomaterialAPI()