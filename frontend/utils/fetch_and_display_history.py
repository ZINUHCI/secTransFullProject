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
    and display it in the chat box.
    """

    if not DB_FILE or not os.path.exists(DB_FILE):
        print("⚠️ No local chat database found.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Get all messages where sender/receiver are self.username and other_username
        cursor.execute("""
            SELECT sender, message, direction, timestamp, type, filename, filepath
            FROM messages
            WHERE owner = ? AND ((sender=? AND receiver=?) OR (sender=? AND receiver=?))
            ORDER BY timestamp ASC
        """, (self.username, self.username, other_username, other_username, self.username))

        rows = cursor.fetchall()
        conn.close()

        # Now display them in the chat box
        self.chat_box.config(state="normal")
        self.chat_box.delete("1.0", END)
        self.chat_box.insert(END, f"📩 Chatting with {other_username}\n\n")

        for row in rows:
            print(row)
            sender, message, direction, timestamp, msg_type, filename, filepath = row

            if msg_type == "file":
                # File messages
                if sender == self.username:


                     # Display clickable filename in chat
                    self.chat_box.config(state="normal")

                    # Insert the initial text
                    self.chat_box.insert(END, "📤 You sent ")

                    # Capture the position before inserting filename
                    start_index = self.chat_box.index("end-1c")
                    self.chat_box.insert(END, filename)
                    end_index = self.chat_box.index("end-1c")

                    # Add clickable tag
                    tag_name = f"file_{filename}"
                    self.chat_box.tag_add(tag_name, start_index, end_index)
                    self.chat_box.tag_config(tag_name, foreground="blue", underline=True)
                    self.chat_box.tag_bind(tag_name, "<Button-1>", lambda e, p=filepath: self.open_file(p))

                    # Make text hoverable
                    self.chat_box.tag_bind(tag_name, "<Enter>", lambda e: self.chat_box.config(cursor="hand2"))
                    self.chat_box.tag_bind(tag_name, "<Leave>", lambda e: self.chat_box.config(cursor=""))

                    # Continue text
                    self.chat_box.insert(END, f" to {self.selected_user}\n")
                    self.chat_box.config(state="disabled")
                    self.chat_box.update_idletasks()


                else:



                     # Display clickable filename in chat
                    self.chat_box.config(state="normal")

                    # Insert the initial text
                    self.chat_box.insert(END, "📤 You received ")

                    # Capture the position before inserting filename
                    start_index = self.chat_box.index("end-1c")
                    self.chat_box.insert(END, filename)
                    end_index = self.chat_box.index("end-1c")

                    # Add clickable tag
                    tag_name = f"file_{filename}"
                    self.chat_box.tag_add(tag_name, start_index, end_index)
                    self.chat_box.tag_config(tag_name, foreground="blue", underline=True)
                    self.chat_box.tag_bind(tag_name, "<Button-1>", lambda e, p=filepath: self.open_file(p))

                    # Make text hoverable
                    self.chat_box.tag_bind(tag_name, "<Enter>", lambda e: self.chat_box.config(cursor="hand2"))
                    self.chat_box.tag_bind(tag_name, "<Leave>", lambda e: self.chat_box.config(cursor=""))

                    # Continue text
                    self.chat_box.insert(END, f" from {self.selected_user}\n")
                    self.chat_box.config(state="disabled")
                    self.chat_box.update_idletasks()



            else:
                # Text messages
                if sender == self.username:
                    self.chat_box.insert(END, f"You: {message}\n")
                else:
                    self.chat_box.insert(END, f"{sender}: {message}\n")

        self.chat_box.config(state="disabled")

    except Exception as e:
        print(f"⚠️ Error loading chat history: {e}")
