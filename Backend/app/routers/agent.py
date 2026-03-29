from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import re
import json
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession
from app.agents import run_graph
from app.agents.initialize_llm import initialize_llm
from langchain_core.messages import HumanMessage, BaseMessage
from app.input_validation.validator import validate_user_input
import time
from app.models.agent_models import AgentQueryRequest, AgentQueryResponse, AgentHealthResponse
from app.utils.helpers import extract_file_paths, convert_path_to_url
from app.database import get_db
from app.schema.chat import Message as MessageModel
from app.schema.user import User
from app.dependencies import get_optional_user


# Create router instance
router = APIRouter(prefix="/agent", tags=["agent"])


# ------------------------------
# Router Endpoints
# ------------------------------
@router.post("/chat", response_model=AgentQueryResponse)
async def chat_with_agent(
    body: AgentQueryRequest,
    db: DBSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Process user query through the agent workflow.
    When session_id is provided and the user is authenticated, messages are saved to the database.
    """

    try:
        clean_query = body.query.strip()

        # --- Persist user message ---
        if current_user and body.session_id:
            try:
                user_msg = MessageModel(
                    session_id=body.session_id,
                    user_id=current_user.id,
                    sender="user",
                    content=clean_query,
                    output_type="text",
                )
                db.add(user_msg)
                db.commit()
            except Exception as save_err:
                print(f"Warning: Failed to save user message: {save_err}")
                db.rollback()

        # --- Run agent ---
        user_message = HumanMessage(content=clean_query)
        result: Dict[str, Any] = await run_graph([user_message])

        messages: List[BaseMessage] = result.get("messages", [])
        if not messages:
            raise HTTPException(status_code=500, detail="No messages returned from agent workflow")

        # --- Extract final message ---
        final_message = "Task completed successfully!"
        found_substantial = False

        for msg in reversed(messages):
            content = getattr(msg, "content", "").strip()
            if not content or "Supervisor routing to" in content or "Workflow completed successfully!" in content:
                continue
            if "Returning structured response:" in content:
                match = re.search(r"message=['\"](.*?)['\"](?= status=|$| error=)", content)
                if match:
                    final_message = match.group(1)
                    found_substantial = True
                    break
            if content:
                final_message = content
                found_substantial = True
                break

        if not found_substantial:
            for msg in reversed(messages):
                if hasattr(msg, "type") and msg.type == "ai" and msg.content.strip():
                    final_message = msg.content.strip()
                    break

        sample_data_path: Optional[str] = result.get("sample_data_path") or result.get("data_file_path")
        plot_file_path: Optional[str] = result.get("plot_file_path")
        vega_spec: Optional[Dict[str, Any]] = result.get("vega_spec")
        profile: Optional[Dict[str, Any]] = result.get("profile")

        if not sample_data_path or not plot_file_path:
            file_paths = extract_file_paths(messages)
            sample_data_path = sample_data_path or file_paths.get("data_file_path")
            plot_file_path = plot_file_path or file_paths.get("plot_file_path")

        data_url = convert_path_to_url(sample_data_path) if sample_data_path else None
        plot_url = convert_path_to_url(plot_file_path) if plot_file_path else None

        # --- Persist bot message ---
        if current_user and body.session_id:
            try:
                meta = {}
                if plot_url:
                    meta["plot"] = plot_url
                if data_url:
                    meta["data"] = data_url
                if vega_spec:
                    meta["chart_spec"] = vega_spec

                bot_msg = MessageModel(
                    session_id=body.session_id,
                    user_id=current_user.id,
                    sender="bot",
                    content=final_message,
                    output_type="rich" if (plot_url or vega_spec) else "text",
                    meta_data=json.dumps(meta) if meta else None,
                )
                db.add(bot_msg)
                db.commit()
            except Exception as save_err:
                print(f"Warning: Failed to save bot message: {save_err}")
                db.rollback()

        return AgentQueryResponse(
            success=True,
            message=final_message,
            data_file_path=data_url,
            plot_file_path=plot_url,
            chart_spec=vega_spec,
            chart_data=None,
            error=None,
        )

    except Exception as e:
        return AgentQueryResponse(
            success=False,
            message="Agent workflow failed",
            data_file_path=None,
            plot_file_path=None,
            chart_spec=None,
            chart_data=None,
            error=str(e),
        )


@router.get("/health", response_model=AgentHealthResponse)
async def agent_health_check():
    """Check if the agent system is working."""
    try:
        llm = initialize_llm()
        start = time.perf_counter()
        msg = await llm.ainvoke([HumanMessage(content="Reply with: ok")])
        lat_ms = (time.perf_counter() - start) * 1000
        healthy = (getattr(msg, "content", "").strip().lower() == "ok")
        return AgentHealthResponse(ok=healthy, lat_ms=round(lat_ms, 1))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent system is not healthy: {str(e)}")
