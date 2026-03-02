from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import re
from pydantic import BaseModel
from Backend.agents import run_graph
from Backend.agents.initialize_llm import initialize_llm
from langchain_core.messages import HumanMessage, BaseMessage
from Backend.input_validation.validator import validate_user_input
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
        print("RAW QUERY RECEIVED:", repr(request.query))
        # -------- INPUT VALIDATION LAYER (DISABLED FOR NEW IMPLEMENTATION) --------
        # validation = validate_user_input(request.query)

        # if validation["status"] != "safe":
        #     return AgentQueryResponse(
        #         success=False,
        #         message="Input validation failed",
        #         data_file_path=None,
        #         plot_file_path=None,
        #         error=validation["message"]
        #     )

        # clean_query = validation["clean_query"]
        clean_query = request.query.strip()
        
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
