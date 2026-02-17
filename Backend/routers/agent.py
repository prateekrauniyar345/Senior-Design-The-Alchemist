from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import re
from pydantic import BaseModel
from Backend.agents import run_graph
from Backend.agents.initialize_llm import initialize_llm
from langchain_core.messages import HumanMessage, BaseMessage
import time
from Backend.models.agent_models import AgentQueryRequest, AgentQueryResponse, AgentHealthResponse
from Backend.utils.helpers import extract_file_paths, convert_path_to_url


# Create router instance
router = APIRouter(prefix="/agent", tags=["agent"])



# ------------------------------
# Router Endpoints
# ------------------------------
@router.post("/chat", response_model=AgentQueryResponse)
async def chat_with_agent(request: AgentQueryRequest):
    """
    Process user query through the agent workflow.
    
    This endpoint handles complex queries like:
    - "Plot the histogram of elements distribution of IMA-approved minerals with hardness 3-5"
    - "Get locality data for Korea"
    - "Get minerals with Neodymium but without sulfur"
    
    The agent_graph will:
    1. Route to supervisor
    2. Supervisor decides which agent to use
    3. Agent executes and returns to supervisor
    4. Loop continues until FINISH
    """
    
    try:
        # Prepare user message
        user_message = HumanMessage(content=request.query)
        
        # Run the graph - this handles initialization automatically
        result: Dict[str, Any] = await run_graph([user_message])
        
        # Extract messages from result
        messages: List[BaseMessage] = result.get("messages", [])
        
        if not messages:
            raise HTTPException(
                status_code=500,
                detail="No messages returned from agent workflow"
            )
        
        # Get the last message as the final response
        last_message = messages[-1]
        final_message = getattr(last_message, "content", "Task completed")
 
        # Extract file paths from all messages
        file_paths = extract_file_paths(messages)
        
        # Convert file system paths to HTTP URLs
        data_url = convert_path_to_url(file_paths["data_file_path"])
        plot_url = convert_path_to_url(file_paths["plot_file_path"])
         
        # Return success response
        return AgentQueryResponse(
            success=True,
            message=final_message,
            data_file_path=data_url,
            plot_file_path=plot_url,
            error=None
        )
    except Exception as e:
        # Return error response
        return AgentQueryResponse(
            success=False,
            message="Agent workflow failed",
            data_file_path=None,
            plot_file_path=None,
            error=str(e)
        )


@router.get("/health", response_model=AgentHealthResponse)
async def agent_health_check():
    """
    Check if the agent system is working.
    Tests LLM connectivity and response time.
    """
    try:
        llm = initialize_llm()
        start = time.perf_counter()
        
        # Use ainvoke for async
        msg = await llm.ainvoke([HumanMessage(content="Reply with: ok")])
        
        lat_ms = (time.perf_counter() - start) * 1000
        healthy = (getattr(msg, "content", "").strip().lower() == "ok")

        return AgentHealthResponse(
            ok=healthy, 
            lat_ms=round(lat_ms, 1)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Agent system is not healthy: {str(e)}"
        )