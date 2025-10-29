# local_db.py
import sqlite3
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

DB_FILE = os.getenv("DB_FILE")


# after successful login response
def save_user_token(self):
    db_path = os.getenv("DB_FILE", "local_messages.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear old sessions and save the new one
    cursor.execute("DELETE FROM user_session")
    cursor.execute(
        "INSERT INTO user_session (username, jwt_token, logged_in) VALUES (?, ?, ?)",
        (self.username, self.token, 1)
    )
    conn.commit()
    conn.close()
