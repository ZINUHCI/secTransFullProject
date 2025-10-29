import os
import shutil
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DB_FILE = os.getenv("DB_FILE")

FILES_DIR = "user_data/files"

def save_file_message(self, file_bytes, filename, direction):
    """
    Saves the received or sent file locally in FILES_DIR and records metadata in SQLite.
    """
    os.makedirs(FILES_DIR, exist_ok=True)  # Ensure folder exists

    # Generate unique filename to avoid collisions
    safe_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
    filepath = os.path.join(FILES_DIR, safe_filename)

    # ✅ Save actual file
    with open(filepath, "wb") as f:
        f.write(file_bytes)

    # ✅ Save metadata in SQLite
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

    cursor.execute("""
        INSERT INTO messages (owner, sender, receiver, filename, filepath, direction, type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        self.username,
        self.username if direction == "sent" else self.selected_user,
        self.selected_user if direction == "sent" else self.username,
        filename,
        filepath,
        direction,
        "file"
    ))
    conn.commit()
    conn.close()

    print(f"✅ File saved locally: {filepath}")
    return filepath
