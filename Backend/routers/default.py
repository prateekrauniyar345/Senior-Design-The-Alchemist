from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
from Backend.core.config import get_templates

# Get templates instance
templates = get_templates()

# Create router instance
router = APIRouter(tags=["pages"])

@router.get("/", response_class=JSONResponse)
async def default(request: Request):
    return {
        "status": "success",
        "message": "Welcome to the LLM-Driven Smart Agents for User-Friendly Access to an Open Data Portal Backend!",
        "timestamp": datetime.utcnow()
    }


# health endpoint
@router.get("/health", response_class=JSONResponse)
async def health():
    return {
        "status": "ok",
        "service": "backend",
        "timestamp": datetime.utcnow()
    }

