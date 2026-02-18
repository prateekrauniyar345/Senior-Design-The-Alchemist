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
        user_message = HumanMessage(content=request.query)

        # Run the graph
        result: Dict[str, Any] = await run_graph([user_message])

        # Extract messages
        messages: List[BaseMessage] = result.get("messages", [])
        if not messages:
            raise HTTPException(status_code=500, detail="No messages returned from agent workflow")

        final_message = getattr(messages[-1], "content", "Task completed")

        sample_data_path: Optional[str] = result.get("sample_data_path") or result.get("data_file_path")
        plot_file_path: Optional[str] = result.get("plot_file_path")

        # Vega outputs (from vega_plot_planner_node updates)
        vega_spec: Optional[Dict[str, Any]] = result.get("vega_spec")
        profile: Optional[Dict[str, Any]] = result.get("profile")

        # Optional: fallback to message parsing ONLY if state missing (legacy safety net)
        if not sample_data_path or not plot_file_path:
            file_paths = extract_file_paths(messages)
            sample_data_path = sample_data_path or file_paths.get("data_file_path")
            plot_file_path = plot_file_path or file_paths.get("plot_file_path")

        # Convert filesystem paths → HTTP URLs for client
        data_url = convert_path_to_url(sample_data_path) if sample_data_path else None
        plot_url = convert_path_to_url(plot_file_path) if plot_file_path else None

        # Map to your response model fields
        return AgentQueryResponse(
            success=True,
            message=final_message,
            data_file_path=data_url,       # this is URL now (fine per your docstring)
            plot_file_path=plot_url,       # URL
            chart_spec=vega_spec,          # Vega spec goes here
            chart_data=None,               # keep None (you decided not to ship raw data)
            error=None
        )
    except Exception as e:
        return AgentQueryResponse(
            success=False,
            message="Agent workflow failed",
            data_file_path=None,
            plot_file_path=None,
            chart_spec=None,
            chart_data=None,
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