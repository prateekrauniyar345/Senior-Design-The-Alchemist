from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from dotenv import load_dotenv
import os
import requests
from urllib.parse import urljoin
from ..utils.custom_message import MindatAPIException, ErrorSeverity
from ..config.settings import settings



class MindatAuth():
    """Handle Mindat API authentication"""
    def __init__(self):
        self.api_key = settings.mindat_api_key
        self.base_url = settings.mindat_base_url
        if not self.base_url:
            raise ValueError("Mindat BASE URL is not configured.")
        if not self.api_key:
            raise ValueError("Mindat API KEY is not configured.")
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        if not self.api_key:
            raise ValueError("Mindat API KEY is not configured.")
        return {
            'Authorization': f'Token {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mindat-API-Tutorial/1.0'
        }



class MindatAPIClient:
    """Comprehensive client for the Mindat.org API"""
    def __init__(self, auth: MindatAuth = None):
        self.auth = auth or MindatAuth()
        self.base_url = auth.base_url
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
        if not endpoint:
            raise MindatAPIException(
                message="API endpoint is required",
                status_code=400,
                severity=ErrorSeverity.ERROR,
                details={"endpoint": endpoint}
            )
        else:
            url  = self.endpoints[endpoint]
        try:
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as http_err:
            raise MindatAPIException(
                message="HTTP error occurred while accessing Mindat API",
                status_code=response.status_code,
                severity=ErrorSeverity.CRITICAL,
                details={"error": str(http_err), "url": url, "params": params}
            )
        except requests.RequestException as req_err:
            raise MindatAPIException(
                message="Request error occurred while accessing Mindat API",
                status_code=500,
                severity=ErrorSeverity.CRITICAL,
                details={"error": str(req_err), "url": url, "params": params}
            )
    

# Initialize the API client
client = MindatAPIClient()