"""Apply migrations/001_add_messages_user_id.sql using DATABASE_URL (run from repo/Backend)."""
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
        raise SystemExit("DATABASE_URL is not set")

    sql_path = Path(__file__).resolve().parents[1] / "migrations" / "001_add_messages_user_id.sql"
    raw = sql_path.read_text(encoding="utf-8")
    chunks = []
    for part in raw.split(";"):
        lines = [ln for ln in part.splitlines() if ln.strip() and not ln.strip().startswith("--")]
        stmt = "\n".join(lines).strip()
        if stmt:
            chunks.append(stmt)
    engine = create_engine(url)
    with engine.begin() as conn:
        for stmt in chunks:
            conn.execute(text(stmt))
    print("Applied:", sql_path, f"({len(chunks)} statements)")


if __name__ == "__main__":
    main()
