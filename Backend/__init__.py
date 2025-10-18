# Backend package - The main application package
"""
The Alchemist Backend Package

This package contains all the backend functionality for The Alchemist application,
including API clients, configurations, utilities, and agents.
"""

from .api import get_geomaterial_api, GeomaterialAPI
from .config import settings, get_mindat_client, MindatAPIClient
from .utils import AlchemistException, MindatAPIException, LLMException, ErrorSeverity

__version__ = "0.1.0"
__all__ = [
    "get_geomaterial_api", 
    "GeomaterialAPI",
    "settings", 
    "get_mindat_client", 
    "MindatAPIClient",
    "AlchemistException", 
    "MindatAPIException", 
    "LLMException", 
    "ErrorSeverity"
]