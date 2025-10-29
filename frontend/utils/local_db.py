# local_db.py
import sqlite3
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

DB_FILE = os.getenv("DB_FILE")

# Ensure the database exists and the table is created
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()
