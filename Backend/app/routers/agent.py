# Backend/app/routers/agent.py
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import re
from pydantic import BaseModel
from app.agents import run_graph
from app.agents.initialize_llm import initialize_llm
from langchain_core.messages import HumanMessage, BaseMessage
from app.input_validation.validator import validate_user_input
import time
from app.models.agent_models import AgentQueryRequest, AgentQueryResponse, AgentHealthResponse
from app.utils.helpers import extract_file_paths, convert_path_to_url
import json as _json

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
        print("RAW QUERY RECEIVED:", repr(request.query))
        clean_query = request.query.strip()
        print("CLEANED QUERY:", repr(clean_query))
        
        # Prepare user message
        user_message = HumanMessage(content=clean_query)

        # Run the graph
        result: Dict[str, Any] = await run_graph([user_message])

        # Extract messages
        messages: List[BaseMessage] = result.get("messages", [])
        if not messages:
            raise HTTPException(status_code=500, detail="No messages returned from agent workflow")

        # --- IMPROVED MESSAGE EXTRACTION ---
        final_message = "Task completed successfully!"
        
        # Iterate backwards to find the last substantial message that isn't just supervisor routing
        found_substantial = False
        for msg in reversed(messages):
            content = getattr(msg, "content", "").strip()
            
            # Skip empty messages or generic supervisor/finish messages
            if not content or "Supervisor routing to" in content or "Workflow completed successfully!" in content:
                continue
            
            # Extract content from structured tool response string
            # Format: Returning structured response: agent='...' message='...' ...
            if "Returning structured response:" in content:
                # Attempt to extract the 'message' parameter value using regex
                # We use a non-greedy match to grab the content of the message field specifically
                match = re.search(r"message=['\"](.*?)['\"](?= status=|$| error=)", content)
                if match:
                    final_message = match.group(1)
                    found_substantial = True
                    break
            
            # Fallback for standard AI or Human messages that aren't supervisor routine
            if content:
                final_message = content
                found_substantial = True
                break

        if not found_substantial:
            # Check if there's any AIMessage content we missed
            for msg in reversed(messages):
                if hasattr(msg, "type") and msg.type == "ai" and msg.content.strip():
                     final_message = msg.content.strip()
                     break

        sample_data_path: Optional[str] = result.get("sample_data_path")

        # Vega outputs
        vega_spec: Optional[Dict[str, Any]] = result.get("vega_spec")

        # Read first 100 rows from saved JSON file for frontend preview

        sample_data = None
        try:
            if sample_data_path:
                with open(sample_data_path, "r", encoding="utf-8") as f:
                    raw = _json.load(f)
                sample_data = raw.get("results", [])[:100]
        except Exception as e:
            print(f"Error reading sample data file at {sample_data_path}: {e}")
            sample_data = None

        # Convert filesystem path → HTTP URL for client
        data_url = convert_path_to_url(sample_data_path) if sample_data_path else None

        return AgentQueryResponse(
            success=True,
            message=final_message,
            data_file_path=data_url,
            plot_file_path=None,
            chart_spec=vega_spec,
            chart_data=None,
            sample_data=sample_data,
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
            sample_data=None,
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
