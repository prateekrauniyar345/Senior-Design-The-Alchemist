"""
The Alchemist Backend Package

This package contains all the backend functionality for The Alchemist application,
including API clients, configurations, utilities, and agents.
"""

from .core import create_app, get_templates
from .services import GeomaterialAPI, get_geomaterial_api
from .config import settings, MindatAPIClient
from .utils import AlchemistException, MindatAPIException, LLMException, ErrorSeverity
from .models import MindatGeoMaterialQuery

__version__ = "0.1.0"
__all__ = [
    "create_app",
    "get_templates",
    "GeomaterialAPI",
    "get_geomaterial_api",
    "settings", 
    "MindatAPIClient",
    "AlchemistException", 
    "MindatAPIException", 
    "LLMException", 
    "ErrorSeverity",
    "MindatGeoMaterialQuery"
]