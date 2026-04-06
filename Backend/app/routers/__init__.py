from .default import router as default_router
from .mindat import router as mindat_router
from .agent import router as agent_router
from .auth import router as auth_router
from .plots import router as plots_router
from .sessions import router as sessions_router
from .user import router as user_router
from .profile import router as profile_router

__all__ = ["default_router", "mindat_router", "agent_router", "auth_router", "plots_router", "sessions_router", "user_router", "profile_router"]