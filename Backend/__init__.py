# Backend package - The main application package
"""
The Alchemist Backend Package

This package contains all the backend functionality for The Alchemist application,
including API clients, configurations, utilities, and agents.
"""

from .services import GeomaterialAPI
from .config import settings, MindatAPIClient
from .utils import AlchemistException, MindatAPIException, LLMException, ErrorSeverity
from .models import MindatGeoMaterialQuery

__version__ = "0.1.0"
__all__ = [
    "GeomaterialAPI",
    "settings", 
    "MindatAPIClient",
    "AlchemistException", 
    "MindatAPIException", 
    "LLMException", 
    "ErrorSeverity", 
    "MindatGeoMaterialQuery"
]