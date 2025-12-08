import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print("Loaded URL:", DATABASE_URL)

if not DATABASE_URL:
    print("DATABASE_URL not found. Check your .env file or working directory.")
    exit()

try:
    # Connect directly using the DATABASE_URL
    connection = psycopg2.connect(DATABASE_URL)
    print("Connection successful!")

    cursor = connection.cursor()
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("Current Time from Supabase:", result)

    cursor.close()
    connection.close()
    print("Connection closed.")
except Exception as e:
    print(f"Failed to connect: {e}")
