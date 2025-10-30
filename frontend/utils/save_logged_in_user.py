# local_db.py
import sqlite3
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

DB_FILE = os.getenv("DB_FILE")


# after successful login response
def save_user_session(self):
    db_path = os.getenv("DB_FILE", "local_messages.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Clear old sessions and save the new one
    cursor.execute("DELETE FROM user_session")
    cursor.execute("""
        INSERT INTO user_session (username, jwt_token, private_key, logged_in)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(username) DO UPDATE SET 
            jwt_token = excluded.jwt_token,
            private_key = excluded.private_key,
            logged_in = 1,
            last_login = CURRENT_TIMESTAMP
    """, (self.username, self.token, self.private_key))

    conn.commit()
    conn.close()

