# test_connection.py
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL)

# Test connection
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT NOW();"))
        print("Connection successful!")
        print("Current time from database:", result.scalar())
except Exception as e:
    print("Connection faileddd:")
    print(e)


