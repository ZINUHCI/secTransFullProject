import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# ✅ Make file paths relative to the current script’s directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, "user_data", "files")


def save_file_message(self, file_bytes, filename, direction):
    """
    Saves the received or sent file locally in FILES_DIR and records metadata in SQLite.
    """
    os.makedirs(self.file_dir, exist_ok=True)  # Ensure folder exists

    safe_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
    filepath = os.path.join(self.file_dir, safe_filename)

    # ✅ Save the file
    with open(filepath, "wb") as f:
        f.write(file_bytes)

    # ✅ Save metadata in SQLite
    conn = sqlite3.connect(self.db_path)
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
