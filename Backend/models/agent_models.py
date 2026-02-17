from pydantic import BaseModel, Field, EmailStr 
from typing import Optional, List, Dict, Literal


# ------------------------------
# Query and Response Models
# ------------------------------
class AgentQueryRequest(BaseModel):
    """Request model for agent queries"""
    query: str
    
class AgentQueryResponse(BaseModel):
    """Response model for agent queries"""
    success: bool
    message: str
    data_file_path: Optional[str] = None
    plot_file_path: Optional[str] = None
    error: Optional[str] = None

class AgentHealthResponse(BaseModel):
    """Response model for agent health check"""
    ok: bool
    lat_ms: float

