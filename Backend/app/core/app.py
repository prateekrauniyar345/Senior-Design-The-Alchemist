import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import( 
    default_router,
    auth_router,
    mindat_router,
    agent_router,
    plots_router,
    sessions_router
    )
from app.utils import MindatAPIException

def create_app() -> FastAPI:
    """Create and configure FastAPI app"""
    
    app = FastAPI(
        title="LLM-Driven Smart Agents for User-Friendly Access to an Open Data Portal", 
        description="A FastAPI application with Agentic Capabilities to facilitate user-friendly access to an open data portal using Large Language Models(GPT-4o).",
        version="0.0.1"
    )
    
    # Get base directory - Backend folder (one level up from app directory)
    APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BACKEND_DIR = os.path.dirname(APP_DIR)
    CONTENTS_DIR = os.path.join(BACKEND_DIR, "contents")
    
    # Mount contents directory to serve plots and data files (if it exists)
    if os.path.exists(CONTENTS_DIR):
        app.mount("/contents", StaticFiles(directory=CONTENTS_DIR), name="contents")
    else:
        # Create the directory if it doesn't exist
        os.makedirs(CONTENTS_DIR, exist_ok=True)
        app.mount("/contents", StaticFiles(directory=CONTENTS_DIR), name="contents")
    
    # Include routers
    app.include_router(default_router)
    app.include_router(auth_router) 
    app.include_router(mindat_router, prefix="/api")
    app.include_router(agent_router, prefix="/api")
    app.include_router(plots_router, prefix="/api")
    app.include_router(sessions_router)  
    
    # Exception handlers
    @app.exception_handler(MindatAPIException)
    async def mindat_exception_handler(request, exc: MindatAPIException):
        return {
            "error": exc.message,
            "status_code": exc.status_code,
            "severity": exc.severity.value,
            "details": exc.details
        }
    
    return app