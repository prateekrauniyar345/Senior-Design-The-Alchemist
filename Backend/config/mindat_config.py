from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import requests
from urllib.parse import urljoin
from ..utils.custom_message import MindatAPIException, ErrorSeverity
from ..config.settings import settings




class MindatAuth:
    """Handle Mindat API authentication"""
    def __init__(self, config =settings):
        self.api_key = config.mindat_api_key
        self.base_url  = config.mindat_base_url
        if not self.api_key:
            raise MindatAPIException(
                message="Mindat API key is missing.",
                status_code=500,
                severity=ErrorSeverity.CRITICAL,
                details={
                    "hint": "Set MINDAT_API_KEY in your environment or .env file.",
                    "doc": "https://www.mindat.org/a/how_to_get_an_api_key",
                },
            )
       
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        if not self.api_key:
            raise MindatAPIException(
                message="Mindat API key is missing.",
                status_code=500,
                severity=ErrorSeverity.CRITICAL,
                details={
                    "hint": "Set MINDAT_API_KEY in your environment or .env file.",
                    "doc": "https://www.mindat.org/a/how_to_get_an_api_key",
                },
            )
        return {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mindat-API-Tutorial/1.0'
        }



class MindatAPIClient:
    """Comprehensive client for the Mindat.org API"""
    def __init__(self, auth : MindatAuth = None):
        self.auth = auth or MindatAuth()
        self.base_url = self.auth.base_url
        self.session = requests.Session()
        self.session.headers.update(self.auth.get_headers())
        
        # Available endpoints
        self.endpoints = {
                "minerals-ima": "https://api.mindat.org/v1/minerals-ima/",
                "geomaterials": "https://api.mindat.org/v1/geomaterials/",
                "geomaterials-search": "https://api.mindat.org/v1/geomaterials-search/",
                "relations": "https://api.mindat.org/v1/relations/",
                "nickel-strunz-10": "https://api.mindat.org/v1/nickel-strunz-10/",
                "dana-8": "https://api.mindat.org/v1/dana-8/",
                "crystalclasses": "https://api.mindat.org/v1/crystalclasses/",
                "spacegroups": "https://api.mindat.org/v1/spacegroups/",
                "spacegroupsets": "https://api.mindat.org/v1/spacegroupsets/",
                "localities": "https://api.mindat.org/v1/localities/",
                "locality-type": "https://api.mindat.org/v1/locality-type/",
                "locality-status": "https://api.mindat.org/v1/locality-status/",
                "locality-age": "https://api.mindat.org/v1/locality-age/",
                "loc-by-min": "https://api.mindat.org/v1/loc-by-min/",
                "occurrences": "https://api.mindat.org/v1/occurrences/",
                "occurrences-statistics": "https://api.mindat.org/v1/occurrences-statistics/",
                "references": "https://api.mindat.org/v1/references/",
                "reference-citations": "https://api.mindat.org/v1/reference-citations/",
                "reference-authors": "https://api.mindat.org/v1/reference-authors/",
                "reference-authors-unique": "https://api.mindat.org/v1/reference-authors-unique/",
                "reference-types": "https://api.mindat.org/v1/reference-types/",
                "reference-classify": "https://api.mindat.org/v1/reference-classify/",
                "reference-lcc": "https://api.mindat.org/v1/reference-lcc/",
                "reference-ddc": "https://api.mindat.org/v1/reference-ddc/",
                "reference-extra": "https://api.mindat.org/v1/reference-extra/",
                "reference-languages": "https://api.mindat.org/v1/reference-languages/",
                "reference-isbn": "https://api.mindat.org/v1/reference-isbn/"
        }
    
    def get_data_from_api(self, endpoint: str, params: Dict = None, timeout: int = 30) -> Dict:
        """Make GET request to API endpoint"""
        if endpoint:
            url  = endpoint
        else : 
            raise MindatAPIException(
                message="Mindat API key is missing.",
                status_code=500,
                severity=ErrorSeverity.CRITICAL,
                details={
                    "hint": "Set MINDAT_API_KEY in your environment or .env file.",
                    "doc": "https://www.mindat.org/a/how_to_get_an_api_key",
                },
            )
        try:
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            raise
    
    

# Initialize the API client
client = MindatAPIClient()
