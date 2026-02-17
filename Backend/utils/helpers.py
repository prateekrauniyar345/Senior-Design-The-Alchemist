from pathlib import Path
from Backend.database import SessionLocal
from Backend.schema import Message, Session, AgentTask
from pydantic import BaseModel
from typing import Any, Dict, Optional, Union, List
from langchain_core.messages import HumanMessage, BaseMessage
import re


CONTENTS_DIR = Path(__file__).resolve().parents[1] / "contents"


# utility function to convert pydantic models to API params, handling aliases, 
# None values, and list serialization
def to_params(q: Union[BaseModel, Dict[str, Any]]) -> Dict[str, str]:
    """
    Convert a Pydantic model or dict into API-ready params:
    - dump with aliases (if model)
    - drop None
    - convert lists to CSV strings
    """
    if isinstance(q, BaseModel):
        params: Dict[str, Any] = q.model_dump(by_alias=True, exclude_none=True)
    else:
        # assume it's already a dict-like input; drop None values
        params = {k: v for k, v in q.items() if v is not None}

    for k, v in list(params.items()):
        if isinstance(v, (list, tuple)):
            params[k] = ",".join(map(str, v))
        else:
            params[k] = str(v) if not isinstance(v, (int, float, str)) else v  # ensure JSON-serializable scalars

    return params  # type: ignore[return-value]



def save_message(sender: str, content: str, output_type="text", session_id=None):
    """
    Saves a message (either from user or agent) to the database.
    If no session_id is provided, it automatically creates a new chat session.
    
    Args:
        sender (str): "user" or "agent" — identifies who sent the message.
        content (str): The actual text of the message.
        output_type (str): Type of output (default="text", can be "plot", "map", etc.).
        session_id (UUID, optional): Existing session ID to link messages in the same chat.

    Returns:
        tuple: (session_id, message_id) after saving successfully.
    """
    
    # Create a new SQLAlchemy session to interact with the database
    db = SessionLocal()
    
    try:
        # If no existing session is provided, create a new chat session
        if session_id is None:
            new_session = Session()      # Create a new Session object
            db.add(new_session)           # Add it to the database session
            db.commit()                   # Commit to save the new session to DB
            db.refresh(new_session)       # Refresh to get the generated UUID
            session_id = new_session.id   # Store the new session's ID
            print(f"New session created: {session_id}")

        # Create a new message record linked to the session
        msg = Message(
            sender=sender,
            content=content,
            output_type=output_type,
            session_id=session_id
        )

        # Add the message to the database and commit the transaction
        db.add(msg)
        db.commit()
        db.refresh(msg)   # Get auto-generated fields like UUID and timestamps
        print(f"Message saved: {msg.id} (Session: {session_id})")

        # Return both the session ID and message ID for reference
        return session_id, msg.id

    except Exception as e:
        # Roll back any changes if an error occurs during the process
        db.rollback()
        print("Error saving message:", e)

    finally:
        # Always close the database connection to prevent memory leaks
        db.close()


def save_agent_task(agent_name, session_id, input_message_id=None, output_message_id=None, status="pending"):
    db = SessionLocal()
    try:
        task = AgentTask(
            agent_name=agent_name,
            session_id=session_id,
            input_message_id=input_message_id,
            output_message_id=output_message_id,
            status=status
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        print(f"AgentTask saved: {agent_name} ({status}) in session {session_id}")
        return task.id
    except Exception as e:
        db.rollback()
        print("Error saving agent task:", e)
    finally:
        db.close()





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