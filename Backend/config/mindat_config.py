from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from dotenv import load_dotenv
import os
import requests
from urllib.parse import urljoin
from ..utils.custom_message import CustomErrorMessage
from dotenv import load_dotenv

# load the environment variables
load_dotenv()



Mindat_Base_Url  = os.getenv("MINDAT_HOST", "https://api.mindat.org/v1/")
Mindat_Api_Key  = os.getenv("MINDAT_API_KEY", "")


class MindatConfig(BaseModel):
    host:str = Field(..., description="Host URL of the Mindat API", example="https://www.mindat.org/api/v1")
    api_key: str = Field(..., description="API key for accessing the Mindat API", example="******************")


class MindatAuth:
    """Handle Mindat API authentication"""
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('MINDAT_API_KEY')
        if not self.api_key:
            print("⚠️  Warning: No API key found!")
            print("Get your API key from: https://www.mindat.org/a/how_to_get_an_api_key")
            print("Set it as MINDAT_API_KEY environment variable")
            raise CustomErrorMessage("Mindat API key for MinDat is missing. Please set the MINDAT_API_KEY environment variable.")
        else:
            print(f"✅ API key loaded: {self.api_key[:8]}{'*' * (len(self.api_key) - 8)}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        if not self.api_key:
            raise CustomErrorMessage("Mindat API key for MinDat is missing. Please set the MINDAT_API_KEY environment variable.")
        return {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mindat-API-Tutorial/1.0'
        }



class MindatAPIClient:
    """Comprehensive client for the Mindat.org API"""
    def __init__(self, api_key: str = None):
        self.auth = MindatAuth(api_key)
        self.base_url = Mindat_Base_Url
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
        
        print(f"Mindat API Client initialized")
        print(f"Base URL: {self.base_url}")
        print(f"Available endpoints: {len(self.endpoints)}")
    
    def get_data_from_api(self, endpoint: str, params: Dict = None, timeout: int = 30) -> Dict:
        """Make GET request to API endpoint"""
        if endpoint:
            url  = endpoint
        else : 
            CustomErrorMessage("Endpoint URL is required for GET request.")
        
        try:
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            raise
    
    def search(self, endpoint: str, query: str, limit: int = 10) -> Dict:
        """Search within an endpoint"""
        params = {
            'q': query,
            'limit': limit
        }
        return self.get_data_from_api(endpoint, params)
    

# Initialize the API client
client = MindatAPIClient()
client.list_endpoints()