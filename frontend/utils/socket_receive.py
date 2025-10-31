import os
import sqlite3
from tkinter import END, messagebox
from datetime import datetime
import platform, subprocess

def _on_socket_receive_message(self, data):
    """
    Expected data shape from backend when a message arrives in real time:
    {
        id, from, recipient, encryptedAesKeyB64, nonceB64, ciphertextB64, tagB64, type, filename?, filesize?
    }
    """

    try:
        sender = data.get("from") or data.get("sender")
        msg_type = data.get("type", "text")

        # Try to decrypt the message
        try:
            plaintext_bytes = self.decrypt_message_payload(data)
        except Exception as e:
            print("Realtime decryption failed:", e)
            plaintext_bytes = b"[unable to decrypt]"

        # Prepare storage paths and DB
        db_path = os.getenv("DB_FILE", "local_messages.db")
        os.makedirs("received_files", exist_ok=True)

        conn = sqlite3.connect(db_path)
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

        # If it's a file
        if msg_type == "file":
            filename = data.get("filename") or "file"
            safe_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file_path = os.path.join("received_files", safe_name)

            # Save file bytes to disk
            try:
                with open(file_path, "wb") as f:
                    f.write(plaintext_bytes if plaintext_bytes else b"")
            except Exception as fe:
                print("File write failed:", fe)
                file_path = "[error saving file]"

            # Save file metadata in DB
            cursor.execute(
                "INSERT INTO messages (owner, sender, receiver, type, filepath, direction) VALUES (?, ?, ?, ?, ?, ?)",
                (sender, sender, self.username, "file", file_path, "received")
            )
            conn.commit()

            # Display clickable filename in UI
            self.chat_box.config(state="normal")
            if self.selected_user == sender:
                self.chat_box.insert(END, f"📥 {sender} sent ")

                start_index = self.chat_box.index("end-1c")
                self.chat_box.insert(END, filename)
                end_index = self.chat_box.index("end-1c")

                tag_name = f"recv_file_{safe_name}"
                self.chat_box.tag_add(tag_name, start_index, end_index)
                self.chat_box.tag_config(tag_name, foreground="blue", underline=True)
                self.chat_box.tag_bind(tag_name, "<Button-1>", lambda e, p=file_path: self.open_file(p))
                self.chat_box.tag_bind(tag_name, "<Enter>", lambda e: self.chat_box.config(cursor="hand2"))
                self.chat_box.tag_bind(tag_name, "<Leave>", lambda e: self.chat_box.config(cursor=""))

                self.chat_box.insert(END, "\n")
            else:
                self.chat_box.insert(END, f"\n🔔 New file from {sender}: {filename}\n")

            self.chat_box.config(state="disabled")
            self.chat_box.see(END)

        else:
            # It's a text message
            # text = plaintext_bytes.decode("utf-8", errors="replace")
            text = plaintext_bytes

            cursor.execute(
                "INSERT INTO messages (owner, sender, receiver, type, message, direction) VALUES (?, ?, ?, ?, ?, ?)",
                (sender, sender, self.username, "text", text, "received")
            )
            conn.commit()

            self.chat_box.config(state="normal")
            if self.selected_user == sender:
                self.chat_box.insert(END, f"{sender}: {text}\n")
            else:
                short_preview = text[:40] + ("..." if len(text) > 40 else "")
                self.chat_box.insert(END, f"\n🔔 New message from {sender}: {short_preview}\n")

            self.chat_box.config(state="disabled")
            self.chat_box.see(END)

        conn.close()

    except Exception as e:
        print("Error handling incoming socket message:", e)

