import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
# Local database connection credentials
DB_PARAMS = {
    "dbname": os.environ.get("DB_NAME", "postgres"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}

def save_memory(username: str, memory_text: str):
    """Appends a new character or profile fact about the user to the database."""
    try:
        # Open connection and get a database cursor
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Insert statement safely parameterized to prevent SQL injection
        cur.execute(
            "INSERT INTO user_memories (username, memory_text) VALUES (%s, %s);",
            (username, memory_text)
        )
        
        # Commit transaction and close connections
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error saving memory: {e}")

def load_memories(username: str) -> str:
    """Queries the database for all logged facts associated with the current user."""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Grab all historical memory text entries for this specific user string
        cur.execute("SELECT memory_text FROM user_memories WHERE username = %s;", (username,))
        rows = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Join matching rows into a single string block for prompt injection
        if rows:
            return "\n".join([f"- {row[0]}" for row in rows])
            
    except Exception as e:
        print(f"Error loading memories: {e}")
        
    return "No prior context available for this user."