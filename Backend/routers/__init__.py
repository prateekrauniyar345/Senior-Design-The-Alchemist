from .default import router as default_router
from .mindat import router as mindat_router
from .agent import router as agent_router
from .auth import router as auth_router

__all__ = ["default_router", "mindat_router", "agent_router", "auth_router"]