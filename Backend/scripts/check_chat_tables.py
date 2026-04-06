"""One-off: print session/message counts from DATABASE_URL (run from Backend/)."""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def main():
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")
    load_dotenv(Path(__file__).resolve().parents[1] / "config" / ".env")
    url = (os.getenv("DATABASE_URL") or "").strip().strip('"').strip("'")
    if not url:
        print("NO DATABASE_URL")
        return
    engine = create_engine(url)
    with engine.connect() as c:
        n_sess = c.execute(text("select count(*) from sessions")).scalar()
        n_msg = c.execute(text("select count(*) from messages")).scalar()
        print("sessions count:", n_sess)
        print("messages count:", n_msg)
        rows = c.execute(
            text(
                "select session_id::text, count(*) as n from messages "
                "group by session_id order by n desc limit 10"
            )
        ).fetchall()
        print("messages per session (top 10):", rows)


if __name__ == "__main__":
    main()
