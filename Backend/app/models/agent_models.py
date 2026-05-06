# Backend/app/models/agent_models.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List, Literal
from uuid import UUID

# ----------------------------------------------
# Query and Response Models for API Endpoints
# ----------------------------------------------

class AgentQueryRequest(BaseModel):
    """Request model for agent queries"""
    query: str = Field(
        ...,
        min_length=1,
        description="The natural language query or instruction for the agent to process.",
        examples=["Generate a histogram of mineral samples from the Mojave desert."]
    )
    session_id: UUID = Field(
        ...,
        description="Chat session ID. Messages are persisted to this session for the authenticated user."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "Tell me about the geological composition of the Moon.",
                "session_id": "00000000-0000-4000-8000-000000000001",
            }
        }
    )

class AgentQueryResponse(BaseModel):
    """Response model for agent queries"""
    success: bool = Field(
        default=True, 
        description="Indicates if the agent successfully processed the request."
    )
    message: str = Field(
        ..., 
        description="A human-readable summary of the agent's action or result."
    )
    data_file_path: Optional[str] = Field(
        default=None, 
        description="The file system path or URL to the generated CSV/Data file."
    )
    plot_file_path: Optional[str] = Field(
        default=None, 
        description="The file system path or URL to the generated visualization/plot image."
    )
    chart_spec: Optional[Dict[str, Any]] = Field(
        default=None,
        description="The Vega-Lite chart specification used to generate the plot, if applicable."
    )
    chart_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="The raw data used for the chart, useful for client-side rendering or debugging."
    )
    sample_data: Optional[List[Dict[str,Any]]] = Field(
        default=None,
        description="A small sample of the data (e.g., first 100 rows) for quick inspection without loading the full dataset."
    )
    error: Optional[str] = Field(   
        default=None, 
        description="Detailed error message if 'success' is false."
    )


class AgentHealthResponse(BaseModel):
    """Response model for agent health check"""
    ok: bool = Field(
        default=True, 
        description="Status of the agent service. True if healthy."
    )
    lat_ms: float = Field(
        ..., 
        description="Latency of the health check in milliseconds.",
        ge=0,
        examples=[12.5]
    )


# ----------------------------------------------
# Additional models for specific tools (e.g., locality, geomaterial) can be defined here
# ----------------------------------------------
class CollectorAgentOutput(BaseModel):
    agent: Literal["geomaterial_collector", "locality_collector"]
    status: Literal["OK", "ERROR"]
    file_path: Optional[str] = None
    error: Optional[str] = None

class VegaAgentOutput(BaseModel):
    agent: Literal["vega_plot_generator"]
    status: Literal["OK", "ERROR"]
    vega_spec: Optional[Dict[str, Any]] = None 
    profile: Optional[Dict[str, Any]] = None    
    error: Optional[str] = None


class GeneralAgentOutput(BaseModel):
    agent: Literal["general_agent"]
    status: Literal["OK", "ERROR"]
    message: str
    error: Optional[str] = None


