from datetime import datetime
import sqlite3
import os
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()

DB_FILE = os.getenv("DB_FILE")

# -------------------------------
# Save message to local database
# -------------------------------
def save_message(self, message, type, direction):
    """Store a message in the local SQLite DB using self.username and self.selected_user."""
    if not self.username or not self.selected_user:
        print("⚠️ Cannot save message: username or selected_user missing.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (owner, sender, receiver, message, direction, type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        self.username,
        self.username if direction == "sent" else self.selected_user,
        self.selected_user if direction == "sent" else self.username,
        message,
        direction,
        type,
    ))
    conn.commit()
    conn.close()