from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
from ..core.config import get_templates

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

@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """About page"""
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    """Privacy policy page"""
    return templates.TemplateResponse("privacy_policy.html", {"request": request})

@router.get("/terms-of-service", response_class=HTMLResponse)
async def terms_of_service(request: Request):
    """Terms of service page"""
    return templates.TemplateResponse("terms_of_service.html", {"request": request})