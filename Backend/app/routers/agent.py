# Backend/app/routers/agent.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any, List, Optional
import re
import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import text
from langchain_core.messages import HumanMessage, BaseMessage
import time

from app.agents import run_graph
from app.agents.initialize_llm import initialize_llm
from app.input_validation.validator import validate_user_input
from app.models.agent_models import AgentQueryRequest, AgentQueryResponse, AgentHealthResponse
from app.utils.helpers import extract_file_paths, convert_path_to_url
from app.database import get_db
from app.dependencies import get_optional_user
from app.schema.user import User
from app.schema.chat import Session as SessionModel

# Create router instance
router = APIRouter(prefix="/agent", tags=["agent"])
logger = logging.getLogger(__name__)


def _save_chat_message(
    db: DBSession,
    *,
    session_id,
    user_id,
    role: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    result = db.execute(
        text(
            """
            INSERT INTO chat_messages (session_id, user_id, role, content, metadata)
            VALUES (:session_id, :user_id, :role, :content, CAST(:metadata AS jsonb))
            RETURNING id
            """
        ),
        {
            "session_id": str(session_id),
            "user_id": str(user_id) if user_id else None,
            "role": role,
            "content": content,
            "metadata": json.dumps(metadata or {}),
        },
    )
    return result.scalar_one()


def _save_artifact(
    db: DBSession,
    *,
    session_id,
    message_id,
    artifact_type: str,
    storage_key: str,
    metadata: Optional[Dict[str, Any]] = None,
):
    filename = Path(storage_key).name if storage_key else None
    db.execute(
        text(
            """
            INSERT INTO chat_artifacts (session_id, message_id, type, name, storage_key, mime_type, metadata)
            VALUES (:session_id, :message_id, :type, :name, :storage_key, :mime_type, CAST(:metadata AS jsonb))
            """
        ),
        {
            "session_id": str(session_id),
            "message_id": str(message_id),
            "type": artifact_type,
            "name": filename,
            "storage_key": storage_key,
            "mime_type": None,
            "metadata": json.dumps(metadata or {}),
        },
    )


def _persist_assistant_turn(
    db: DBSession,
    *,
    session_id,
    user_id,
    final_message: str,
    vega_spec: Optional[Dict[str, Any]],
    sample_data: Optional[List[Dict[str, Any]]],
    data_url: Optional[str],
    lc_messages: List[BaseMessage],
) -> None:
    """Save assistant message and file artifacts; does not commit the caller's transaction boundaries."""
    meta: Dict[str, Any] = {}
    if vega_spec is not None:
        meta["chart_spec"] = vega_spec
    if sample_data is not None:
        meta["sample_data"] = sample_data
    if data_url:
        meta["data_file_path"] = data_url

    meta["output_type"] = "chart" if vega_spec else "data" if data_url else "text"

    assistant_message_id = _save_chat_message(
        db,
        session_id=session_id,
        user_id=user_id,
        role="assistant",
        content=final_message,
        metadata=meta,
    )
    logger.info(
        "agent.chat.persist: assistant message saved session_id=%s message_id=%s",
        session_id,
        assistant_message_id,
    )

    if data_url:
        _save_artifact(
            db,
            session_id=session_id,
            message_id=assistant_message_id,
            artifact_type="data_file",
            storage_key=data_url,
        )

    paths = extract_file_paths(lc_messages)
    plot_path = paths.get("plot_file_path")
    plot_url = convert_path_to_url(plot_path) if plot_path else None
    if plot_url:
        _save_artifact(
            db,
            session_id=session_id,
            message_id=assistant_message_id,
            artifact_type="plot_image",
            storage_key=plot_url,
        )


# ------------------------------
# Router Endpoints
# ------------------------------
@router.post("/chat", response_model=AgentQueryResponse)
async def chat_with_agent(
    request: AgentQueryRequest,
    db: DBSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
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

    try:
        print("RAW QUERY RECEIVED:", repr(request.query))
        print(
            f"[agent.chat] session_id={request.session_id} has_current_user={bool(current_user)}"
        )
        chat_db_user = None
        if request.session_id is not None:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required when session_id is provided",
                )
            chat_db_user = current_user.supabase_user_id
            session = db.execute(
                text(
                    """
                    SELECT id
                    FROM chat_sessions
                    WHERE id = :session_id AND user_id = :user_id
                    LIMIT 1
                    """
                ),
                {
                    "session_id": str(request.session_id),
                    "user_id": str(chat_db_user),
                },
            ).first()
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found",
                )

        # -------- INPUT VALIDATION LAYER --------
        validation = validate_user_input(request.query)

        # -------- BLOCKED (malicious) --------
        if validation["status"] == "blocked":
            if request.session_id is not None and chat_db_user:
                user_message_id = _save_chat_message(
                    db,
                    session_id=request.session_id,
                    user_id=chat_db_user,
                    role="user",
                    content=request.query,
                    metadata={"output_type": "text"},
                )
                assistant_message_id = _save_chat_message(
                    db,
                    session_id=request.session_id,
                    user_id=chat_db_user,
                    role="assistant",
                    content=validation["message"],
                    metadata={"output_type": "text"},
                )
                db.commit()
                print(
                    f"[agent.chat] blocked persisted session_id={request.session_id} user_message_id={user_message_id} assistant_message_id={assistant_message_id}"
                )
                print(
                    f"[agent.chat] saved rows under session_id={request.session_id}"
                )
            return AgentQueryResponse(
                success=False,
                message=validation["message"],
                data_file_path=None,
                plot_file_path=None,
                error=validation["message"],
            )

        # -------- ERROR (off-topic / invalid) --------
        if validation["status"] == "error":
            if request.session_id is not None and chat_db_user:
                user_message_id = _save_chat_message(
                    db,
                    session_id=request.session_id,
                    user_id=chat_db_user,
                    role="user",
                    content=request.query,
                    metadata={"output_type": "text"},
                )
                assistant_message_id = _save_chat_message(
                    db,
                    session_id=request.session_id,
                    user_id=chat_db_user,
                    role="assistant",
                    content="I only support mineral and Mindat-related queries.",
                    metadata={"output_type": "text"},
                )
                db.commit()
                print(
                    f"[agent.chat] validation-error persisted session_id={request.session_id} user_message_id={user_message_id} assistant_message_id={assistant_message_id}"
                )
                print(
                    f"[agent.chat] saved rows under session_id={request.session_id}"
                )
            return AgentQueryResponse(
                success=False,
                message="I only support mineral and Mindat-related queries.",
                data_file_path=None,
                plot_file_path=None,
                error=validation["message"],
            )

        # -------- SAFE (mineral query) --------
        clean_query = validation["clean_query"]

        if request.session_id is not None and chat_db_user:
            user_message_id = _save_chat_message(
                db,
                session_id=request.session_id,
                user_id=chat_db_user,
                role="user",
                content=clean_query,
                metadata={"output_type": "text"},
            )
            logger.info(
                "agent.chat.persist: user message saved session_id=%s message_id=%s",
                request.session_id,
                user_message_id,
            )
            print(
                f"[agent.chat] user message saved session_id={request.session_id} message_id={user_message_id}"
            )
            db.commit()
            print(f"[agent.chat] user message commit ok session_id={request.session_id}")
        else:
            print("[agent.chat] no session_id provided, persistence skipped")

        # Prepare user message
        user_message = HumanMessage(content=clean_query)

        # Run the graph
        result: Dict[str, Any] = await run_graph([user_message])

        # Extract messages
        lc_messages: List[BaseMessage] = result.get("messages", [])
        if not lc_messages:
            raise HTTPException(
                status_code=500, detail="No messages returned from agent workflow"
            )

        sample_data_path: Optional[str] = result.get("sample_data_path")
        vega_spec: Optional[Dict[str, Any]] = result.get("vega_spec")

        # --- MESSAGE EXTRACTION ---
        # Determine a clean human-readable message based on what was produced
        if vega_spec:
            # Chart was generated — extract title from spec for a clean message
            chart_title = vega_spec.get("title", "visualization")
            final_message = f"Here is your {chart_title}."
        elif sample_data_path:
            # Data was collected but no chart requested
            final_message = "Here is the data you requested."
        else:
            # General agent or fallback — find last meaningful message
            final_message = "Task completed successfully!"
            for msg in reversed(lc_messages):
                content = getattr(msg, "content", "").strip()
                if (
                    not content
                    or "Supervisor routing to" in content
                    or "Workflow completed successfully!" in content
                ):
                    continue
                if "Returning structured response:" in content:
                    match = re.search(
                        r"message=['\"](.*?)['\"](?= status=|$| error=)", content
                    )
                    if match:
                        final_message = match.group(1)
                        break
                    continue  # skip raw structured dumps
                final_message = content
                break

        # Read first 100 rows from saved JSON file for frontend preview

        sample_data = None
        try:
            if sample_data_path:
                with open(sample_data_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                sample_data = raw.get("results", [])[:100]
        except Exception as e:
            print(f"Error reading sample data file at {sample_data_path}: {e}")
            sample_data = None

        # Convert filesystem path → HTTP URL for client
        data_url = convert_path_to_url(sample_data_path) if sample_data_path else None

        paths = extract_file_paths(lc_messages)
        plot_url = convert_path_to_url(paths.get("plot_file_path"))

        if request.session_id is not None and current_user and chat_db_user:
            try:
                _persist_assistant_turn(
                    db,
                    session_id=request.session_id,
                    user_id=chat_db_user,
                    final_message=final_message,
                    vega_spec=vega_spec,
                    sample_data=sample_data,
                    data_url=data_url,
                    lc_messages=lc_messages,
                )
                db.commit()
                logger.info(
                    "agent.chat.persist: assistant commit complete session_id=%s",
                    request.session_id,
                )
                print(
                    f"[agent.chat] assistant message saved+committed session_id={request.session_id}"
                )
                print(
                    f"[agent.chat] saved rows under session_id={request.session_id}"
                )
            except Exception as persist_err:
                db.rollback()
                print(f"Chat persistence error (non-fatal): {persist_err}")

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
    except HTTPException:
        raise
    except Exception as e:
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
        healthy = getattr(msg, "content", "").strip().lower() == "ok"

        return AgentHealthResponse(ok=healthy, lat_ms=round(lat_ms, 1))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Agent system is not healthy: {str(e)}"
        )
