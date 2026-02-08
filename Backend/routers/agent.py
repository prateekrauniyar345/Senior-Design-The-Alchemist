from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import re
from pydantic import BaseModel
from ..agents import agent_graph, initialize_llm
from langchain_core.messages import HumanMessage, BaseMessage
import time

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
    data_file_path: Optional[str] = None
    plot_file_path: Optional[str] = None
    error: Optional[str] = None

class AgentHealthResponse(BaseModel):
    """Response model for agent health check"""
    ok: bool
    lat_ms: float

# ------------------------------
# Helper Functions
# ------------------------------
def extract_file_paths(messages: List[BaseMessage]) -> Dict[str, Optional[str]]:
    """
    Extract data and plot file paths from agent messages.
    Looks for paths in success messages.
    """
    data_path = None
    plot_path = None
    
    for msg in messages:
        content = getattr(msg, "content", "")
        
        # Look for JSON data files
        if "mindat_geomaterial_response.json" in content or "mindat_locality_response.json" in content or "mindat_locality.json" in content:
            json_match = re.search(r'([/\w\-. ]+\.json)', content)
            if json_match:
                data_path = json_match.group(1)
        
        # Look for plot files (PNG, HTML)
        if ".png" in content or ".html" in content:
            # Try PNG first
            png_match = re.search(r'([/\w\-. ]+\.png)', content)
            if png_match:
                plot_path = png_match.group(1)
            else:
                # Try HTML (for heatmaps)
                html_match = re.search(r'([/\w\-. ]+\.html)', content)
                if html_match:
                    plot_path = html_match.group(1)
    
    return {
        "data_file_path": data_path,
        "plot_file_path": plot_path
    }

def convert_path_to_url(file_path: Optional[str]) -> Optional[str]:
    """
    Convert absolute file system path to relative HTTP URL.
    Example: /Users/.../Backend/contents/plots/file.png -> /contents/plots/file.png
    """
    if not file_path:
        return None
    
    # Find the /contents/ part and extract everything after it
    if "/contents/" in file_path:
        parts = file_path.split("/contents/")
        return f"/contents/{parts[-1]}"
    
    return file_path

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
        # Prepare initial state with user message
        initial_state = {
            "messages": [HumanMessage(content=request.query)],
            "next": None
        }
        # Invoke the compiled graph asynchronously
        result: Dict[str, Any] = await agent_graph.ainvoke(initial_state)
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