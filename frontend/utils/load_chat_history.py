import sqlite3
import os
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()

DB_FILE = os.getenv("DB_FILE")

# -------------------------------
# Load chat history
# -------------------------------
def load_chat_history(self):
    """Load messages between self.username and self.selected_user."""
    if not self.username or not self.selected_user:
        print("⚠️ Cannot load chat: username or selected_user missing.")
        return []

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, message, direction, timestamp
        FROM messages
        WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
        ORDER BY timestamp ASC
    """, (self.username, self.selected_user, self.selected_user, self.username))
    rows = cursor.fetchall()
    conn.close()
    return rows