# Core package - contains app configuration and shared components
from .app import create_app
from .config import get_templates

__all__ = ["create_app", "get_templates"]