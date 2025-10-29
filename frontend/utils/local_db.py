# local_db.py
import sqlite3
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

DB_FILE = os.getenv("DB_FILE")

# Ensure the database exists and the tables are created
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Table for storing messages (per user)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            message TEXT,
            direction TEXT CHECK(direction IN ('sent', 'received')) NOT NULL,
            type TEXT CHECK(type IN ('text', 'file')) DEFAULT 'text',
            filename TEXT,
            filepath TEXT,  
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for storing the logged-in user's data and JWT token
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_session (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            jwt_token TEXT,
            logged_in BOOLEAN DEFAULT 0,
            last_login DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# Save user session (store or update JWT)
def save_user_session(username, jwt_token):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO user_session (username, jwt_token, logged_in)
        VALUES (?, ?, 1)
        ON CONFLICT(username) DO UPDATE SET jwt_token=excluded.jwt_token, logged_in=1
    """, (username, jwt_token))

    conn.commit()
    conn.close()


# Fetch the currently logged-in user (if any)
def get_logged_in_user():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT username, jwt_token FROM user_session WHERE logged_in=1 LIMIT 1")
    user = cursor.fetchone()

    conn.close()
    print(user)
    return user  # returns (username, jwt_token) or None

