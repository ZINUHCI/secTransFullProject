import sqlite3
from tkinter import END
import os
from dotenv import load_dotenv

# Load environment variables (for DB file path)
load_dotenv()
DB_FILE = os.getenv("DB_FILE")


def fetch_and_display_history(self, other_username):
    """
    Fetch chat history between self.username and other_username,
    and display it neatly in the chat box.
    """

    if not DB_FILE or not os.path.exists(DB_FILE):
        print("⚠️ No local chat database found.")
        return

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sender, message, direction, timestamp, type, filename, filepath
                FROM messages
                WHERE (sender = ? AND receiver = ?)
                   OR (sender = ? AND receiver = ?)
                ORDER BY timestamp ASC
            """, (self.username, other_username, other_username, self.username))
            rows = cursor.fetchall()

        # Prepare chat box for fresh messages
        self.chat_box.config(state="normal")
        self.chat_box.delete("1.0", END)
        self.chat_box.insert(END, f"📩 Chatting with {other_username}\n\n")

        # Hover effects for clickable file links
        def on_hover_enter(e):
            e.widget.config(cursor="hand2")

        def on_hover_leave(e):
            e.widget.config(cursor="")

        print("📜 Loaded chat rows:", len(rows))

        for row in rows:
            sender, message, direction, timestamp, msg_type, filename, filepath = row
            print("Row data:", row)

            # Determine message ownership properly
            is_sent_by_me = sender == self.username
            is_received = sender == other_username

            print(f"is_sent_by_me:{is_sent_by_me}")
            print(f"is_received:{is_received}")

            # Handle FILE messages
            if msg_type == "file":
                display_name = filename if filename else os.path.basename(filepath) if filepath else "[Unknown File]"
                self.chat_box.config(state="normal")

                if is_sent_by_me:
                    # Message sent by the logged-in user
                    self.chat_box.insert(END, "📤 You sent ")

                    start_index = self.chat_box.index("end-1c")
                    self.chat_box.insert(END, display_name)
                    end_index = self.chat_box.index("end-1c")

                    tag_name = f"file_{display_name}"
                    self.chat_box.tag_add(tag_name, start_index, end_index)
                    self.chat_box.tag_config(tag_name, foreground="blue", underline=True)
                    self.chat_box.tag_bind(tag_name, "<Button-1>", lambda e, p=filepath: self.open_file(p))
                    self.chat_box.tag_bind(tag_name, "<Enter>", on_hover_enter)
                    self.chat_box.tag_bind(tag_name, "<Leave>", on_hover_leave)

                    self.chat_box.insert(END, f" to {other_username}\n")

                elif is_received:
                    # Message received from the other user
                    self.chat_box.insert(END, "📥 You received ")

                    start_index = self.chat_box.index("end-1c")
                    self.chat_box.insert(END, display_name)
                    end_index = self.chat_box.index("end-1c")

                    tag_name = f"file_{display_name}"
                    self.chat_box.tag_add(tag_name, start_index, end_index)
                    self.chat_box.tag_config(tag_name, foreground="blue", underline=True)
                    self.chat_box.tag_bind(tag_name, "<Button-1>", lambda e, p=filepath: self.open_file(p))
                    self.chat_box.tag_bind(tag_name, "<Enter>", on_hover_enter)
                    self.chat_box.tag_bind(tag_name, "<Leave>", on_hover_leave)

                    self.chat_box.insert(END, f" from {sender}\n")

                else:
                    # Fallback for uncertain direction
                    self.chat_box.insert(END, f"📁 {sender}: {display_name}\n")

                self.chat_box.update_idletasks()

            # Handle TEXT messages
                print("Before Handle text messages")
            else:
                # self.chat_box.config(state="normal")
                if is_sent_by_me:
                    self.chat_box.insert(END, f"You: {message}\n")
                else:
                    self.chat_box.insert(END, f"{sender}: {message}\n")
                # self.chat_box.config(state="disabled")

        self.chat_box.config(state="disabled")

    except Exception as e:
        print(f"⚠️ Error loading chat history: {e}")
