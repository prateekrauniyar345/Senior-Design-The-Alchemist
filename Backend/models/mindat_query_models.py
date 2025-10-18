from pydantic import BaseModel, Field
from typing import Optional, Dict
from utils.helpers import check_sample_data_path, check_plots_path, get_endpoints, set_headers_for_mindat_api
from config.mindat_config import MindatAPIClient
from utils.custom_message import CustomErrorMessage

class MindatGeoMaterialQuery(BaseModel):
    """
    Mindat Query Parameters
    """
    ima: Optional[bool] = Field(description="Only IMA-approved names, should be True by default")
    hardness_min: Optional[float] = Field(description="Mohs hardness from")
    hardness_max: Optional[float] = Field(description="Mohs hardness to")
    crystal_system: Optional[list[str]] = Field(description=" Crystal system (csystem): multiple choice (OR), Items Enum: 'Amorphous','Hexagonal','Icosahedral','Isometric','Monoclinic','Orthorhombic','Tetragonal','Triclinic','Trigonal'")
    el_inc: Optional[str] = Field(description="Chemical elements must include, e.g., 'Fe,Cu'")
    el_exc: Optional[str] = Field(description="Chemical elements must exclude, e.g., 'Fe,Cu'")
    expand: Optional[str] = Field(description="Expand the search scope, 'description','type_localities','locality','relations','minstats', leave blank if necessary")



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
            CustomErrorMessage("At least one query parameter must be provided for searching geomaterials.")
        return self.client.get_data_from_api(self.endpoint, params)
