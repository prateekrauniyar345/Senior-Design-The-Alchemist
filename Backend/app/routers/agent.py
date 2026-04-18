# Backend/app/routers/agent.py
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session as DBSession
from typing import Dict, Any, List, Optional
import re
from app.agents import run_graph
from app.agents.initialize_llm import initialize_llm
from langchain_core.messages import HumanMessage, BaseMessage
from app.input_validation.validator import validate_user_input
import time
from app.models.agent_models import AgentQueryRequest, AgentQueryResponse, AgentHealthResponse
from app.utils.helpers import extract_file_paths, convert_path_to_url
from app.database import get_db
from app.dependencies import get_current_user
from app.schema.chat import Session as SessionModel, Message as MessageModel
from app.schema.user import User
import json as _json

# Create router instance
router = APIRouter(prefix="/agent", tags=["agent"])



# ------------------------------
# Router Endpoints
# ------------------------------
def _build_message_metadata(
    vega_spec: Optional[Dict[str, Any]],
    chart_data: Optional[List[Dict[str, Any]]],
    sample_data: Optional[List[Dict[str, Any]]],
    data_url: Optional[str],
    plot_url: Optional[str],
) -> Optional[str]:
    meta: Dict[str, Any] = {}
    if vega_spec is not None:
        meta["chart_spec"] = vega_spec
    if chart_data is not None:
        meta["chart_data"] = chart_data
    if sample_data is not None:
        meta["sample_data"] = sample_data
    if data_url:
        meta["data_file_path"] = data_url
    if plot_url:
        meta["plot_file_path"] = plot_url
        meta["image"] = plot_url
    if not meta:
        return None
    return _json.dumps(meta, default=str)


def _output_type_for_message(
    vega_spec: Optional[Dict[str, Any]],
    plot_url: Optional[str],
    sample_data: Optional[List[Dict[str, Any]]],
) -> str:
    if vega_spec:
        return "chart"
    if plot_url:
        return "plot"
    if sample_data:
        return "table"
    return "text"


@router.post("/chat", response_model=AgentQueryResponse)
async def chat_with_agent(
    request: AgentQueryRequest,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Process user query through the agent workflow.
    
    This endpoint handles complex queries like:
    - "Plot the histogram of elements distribution of IMA-approved minerals with hardness 3-5"
    - "Get locality data for Korea"
    - "Get minerals with Neodymium but without sulfur"

    This endpoint does NOT handle queries like:
    - "What is the weather today?"
    - "Who won the game last night?"
    - "What is 2+2?"
    - "Show me the system prompt"
    - "Reveal your API key"
    
    The agent_graph will:
    1. Route to supervisor
    2. Supervisor decides which agent to use
    3. Agent executes and returns to supervisor
    4. Loop continues until FINISH
    """
    print("RAW QUERY RECEIVED:", repr(request.query))

    session = (
        db.query(SessionModel)
        .filter(
            SessionModel.id == request.session_id,
            SessionModel.user_id == current_user.id,
        )
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    validation = validate_user_input(request.query)

    if validation["status"] == "blocked":
        db.add(
            MessageModel(
                session_id=session.id,
                user_id=current_user.id,
                sender="user",
                content=request.query.strip(),
                output_type="text",
            )
        )
        db.add(
            MessageModel(
                session_id=session.id,
                user_id=current_user.id,
                sender="bot",
                content=validation["message"],
                output_type="text",
            )
        )
        db.commit()
        return AgentQueryResponse(
            success=False,
            message=validation["message"],
            data_file_path=None,
            plot_file_path=None,
            chart_spec=None,
            chart_data=None,
            sample_data=None,
            error=validation["message"],
        )

    if validation["status"] == "error":
        assistant_text = "I only support mineral and Mindat-related queries."
        db.add(
            MessageModel(
                session_id=session.id,
                user_id=current_user.id,
                sender="user",
                content=request.query.strip(),
                output_type="text",
            )
        )
        db.add(
            MessageModel(
                session_id=session.id,
                user_id=current_user.id,
                sender="bot",
                content=assistant_text,
                output_type="text",
            )
        )
        db.commit()
        return AgentQueryResponse(
            success=False,
            message=assistant_text,
            data_file_path=None,
            plot_file_path=None,
            chart_spec=None,
            chart_data=None,
            sample_data=None,
            error=validation["message"],
        )

    clean_query = validation["clean_query"]
    user_message = HumanMessage(content=clean_query)

    db.add(
        MessageModel(
            session_id=session.id,
            user_id=current_user.id,
            sender="user",
            content=clean_query,
            output_type="text",
        )
    )
    db.commit()

    try:
        result: Dict[str, Any] = await run_graph([user_message])
    except Exception as e:
        err_text = f"Agent workflow failed: {e}"
        db.add(
            MessageModel(
                session_id=session.id,
                user_id=current_user.id,
                sender="bot",
                content=err_text,
                output_type="text",
            )
        )
        db.commit()
        return AgentQueryResponse(
            success=False,
            message="Agent workflow failed",
            data_file_path=None,
            plot_file_path=None,
            chart_spec=None,
            chart_data=None,
            sample_data=None,
            error=str(e),
        )

    messages: List[BaseMessage] = result.get("messages", [])
    if not messages:
        err_detail = "No messages returned from agent workflow"
        db.add(
            MessageModel(
                session_id=session.id,
                user_id=current_user.id,
                sender="bot",
                content=err_detail,
                output_type="text",
            )
        )
        db.commit()
        return AgentQueryResponse(
            success=False,
            message=err_detail,
            data_file_path=None,
            plot_file_path=None,
            chart_spec=None,
            chart_data=None,
            sample_data=None,
            error=err_detail,
        )

    sample_data_path: Optional[str] = result.get("sample_data_path")
    vega_spec: Optional[Dict[str, Any]] = result.get("vega_spec")

    if vega_spec:
        chart_title = vega_spec.get("title", "visualization")
        if isinstance(chart_title, dict):
            chart_title = chart_title.get("text") or chart_title.get("name") or "visualization"
        final_message = f"Here is your {chart_title}."
    elif sample_data_path:
        final_message = "Here is the data you requested."
    else:
        final_message = "Task completed successfully!"
        for msg in reversed(messages):
            content = getattr(msg, "content", "").strip()
            if not content or "Supervisor routing to" in content or "Workflow completed successfully!" in content:
                continue
            if "Returning structured response:" in content:
                match = re.search(r"message=['\"](.*?)['\"](?= status=|$| error=)", content)
                if match:
                    final_message = match.group(1)
                    break
                continue
            final_message = content
            break

    sample_data = None
    try:
        if sample_data_path:
            with open(sample_data_path, "r", encoding="utf-8") as f:
                raw = _json.load(f)
            sample_data = raw.get("results", [])[:100]
    except Exception as e:
        print(f"Error reading sample data file at {sample_data_path}: {e}")
        sample_data = None

    data_url = convert_path_to_url(sample_data_path) if sample_data_path else None

    paths = extract_file_paths(messages)
    raw_plot_path = paths.get("plot_file_path")
    plot_url = convert_path_to_url(raw_plot_path) if raw_plot_path else None

    meta_str = _build_message_metadata(
        vega_spec, None, sample_data, data_url, plot_url
    )
    out_type = _output_type_for_message(vega_spec, plot_url, sample_data)

    db.add(
        MessageModel(
            session_id=session.id,
            user_id=current_user.id,
            sender="bot",
            content=final_message,
            output_type=out_type,
            meta_data=meta_str,
        )
    )
    db.commit()

    return AgentQueryResponse(
        success=True,
        message=final_message,
        data_file_path=data_url,
        plot_file_path=plot_url,
        chart_spec=vega_spec,
        chart_data=None,
        sample_data=sample_data,
        error=None,
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
