from .database import  engine
from sqlalchemy import text

def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW();"))
            print("Database Connected! Current time:", list(result))
    except Exception as e:
        print("Database Connection Failed:", e)

if __name__ == "__main__":
    test_connection()
