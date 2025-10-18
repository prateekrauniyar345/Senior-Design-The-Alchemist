from typing import Dict
from ..config.mindat_config import MindatAPIClient
from ..models.mindat_query_models import MindatGeoMaterialQuery
from ..utils.custom_message import MindatAPIException, ErrorSeverity


class GeomaterialAPI():
    """
    Geomaterial API Client
    """
    def __init__(self, client : MindatAPIClient):
        self.client = client
        self.endpoint = self.client.endpoints["geomaterials"]

    def search_geomaterials_minerals(self, query_params: MindatGeoMaterialQuery) -> Dict:
        """
        Search geomaterials/minerals with given query parameters
        """
        params = Dict(query_params)
        if not params:
            raise MindatAPIException(
                
            )
        return self.client.get_data_from_api(self.endpoint, params)
