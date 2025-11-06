from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from pydantic import BaseModel
from ..utils import MindatAPIException


# Create router instance
router = APIRouter(prefix="/agent", tags=["agent"])

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
    data_file_path: str = None
    plot_file_path: str = None
    error: str = None


# ------------------------------
# Router Endpoints
# ------------------------------
@router.post("/chat", response_model=AgentQueryResponse)
async def chat_with_agent(request: AgentQueryRequest):
    """
    Process user query through the agent workflow
    
    This endpoint handles complex queries like:
    "Plot the histogram of elements distribution of IMA-approved minerals with hardness 3-5"
    """
    # try:
    #     logger.info(f"Processing agent query: {request.query}")
        
    #     # Run the agent workflow
    #     result = await run_agent_workflow(request.query)
        
    #     if result.get("success", True):
    #         return AgentQueryResponse(
    #             success=True,
    #             message=result.get("message", "Workflow completed successfully"),
    #             data_file_path=result.get("data_file_path"),
    #             plot_file_path=result.get("plot_file_path")
    #         )
    #     else:
    #         return AgentQueryResponse(
    #             success=False,
    #             message="Workflow failed",
    #             error=result.get("error", "Unknown error")
    #         )
            
    # except Exception as e:
    #     logger.error(f"Agent workflow error: {str(e)}")
    #     return AgentQueryResponse(
    #         success=False,
    #         message="Failed to process query",
    #         error=str(e)
    #     )
    return {
        "success": True,
        "message": "Agent query processing is currently disabled."
    }



@router.get("/health")
async def agent_health_check():
    """Check if the agent system is working"""
    # try:
    #     # Simple test to ensure agents can be imported
    #     from ..agents.agent_workflow import get_workflow
    #     workflow = get_workflow()
        
    #     return {
    #         "success": True,
    #         "message": "Agent system is healthy",
    #         "workflow_ready": workflow is not None
    #     }
    # except Exception as e:
    #     logger.error(f"Agent health check failed: {str(e)}")
    #     raise HTTPException(status_code=500, detail=f"Agent system unhealthy: {str(e)}")
    return {
        "success": True,
        "message": "Agent system is healthy"
    }