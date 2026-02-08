from pathlib import Path
from Backend.database import SessionLocal
from Backend.schema import Message, Session, AgentTask
from pydantic import BaseModel
from typing import Any, Dict, Optional, Union


# check path for storing the samples files in directory folder
# Json files for the samples data will be saved in contents/sample_data
def check_sample_data_path() -> bool:
    current_dir = Path.cwd() # Get the current working directory
    parent_dir = current_dir.parent # Navigate to the parent directory
    sample_data_path = parent_dir / "contents" / "sample_data" # Construct the path to contents/sample_data
    if sample_data_path.exists():
        return True
    return False

def check_plots_path() -> bool:
    current_dir = Path.cwd() # Get the current working directory
    parent_dir = current_dir.parent # Navigate to the parent directory
    plots_path = parent_dir / "contents" / "plots" # Construct the path to contents/plots
    if plots_path.exists():
        return True
    return False

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
            print(f"🆕 New session created: {session_id}")

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
