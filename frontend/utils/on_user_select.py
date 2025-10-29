import threading
from tkinter import END, messagebox
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")

def on_user_select(self, event):
    """Handles user selection in chat list and loads conversation (local + online sync)."""
    selection = self.user_list.curselection()
    if not selection:
        return

    self.selected_user = self.user_list.get(selection[0])

    # Reset chat box
    self.chat_box.config(state="normal")
    self.chat_box.delete("1.0", END)
    self.chat_box.insert(END, f"📩 Chatting with {self.selected_user}\n\n")
    self.chat_box.config(state="disabled")

    # Step 1: Load local messages first (for fast response)
    threading.Thread(target=self.fetch_and_display_history, args=(self.selected_user,), daemon=True).start()

    # Step 2: Then check for new messages from server (offline sync)
    threading.Thread(target=self._fetch_missed_messages_from_server, daemon=True).start()


def _fetch_missed_messages_from_server(self):
    """Fetch new/unseen messages from the backend for the selected user and update UI + DB."""
    try:
        headers = {"Authorization": f"Bearer {self.token}"}

        res = requests.get(f"{SERVER_URL}/messages/missed/{self.selected_user}", headers=headers, timeout=10)
        if res.status_code != 200:
            print("No new messages or failed to sync.")
            return

        new_msgs = res.json().get("messages", [])
        if not new_msgs:
            print("No new messages from server.")
            return

        print(f"Fetched {len(new_msgs)} new messages from backend.")

        for msg in new_msgs:
            # Save to local DB (so next time they appear from history)
            direction = "received" if msg.get("from") != self.username else "sent"
            msg_type = msg.get("type", "text")

            # Decrypt and display in UI
            try:
                decrypted = self.decrypt_message_payload(msg)

                if msg_type == "file":
                    # Save file to received_files
                    os.makedirs("received_files", exist_ok=True)
                    filename = msg.get("filename") or "file"
                    safe_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    file_path = os.path.join("received_files", safe_name)
                    with open(file_path, "wb") as f:
                        f.write(decrypted)

                    # Save to DB
                    self.save_file_message(decrypted, filename, "received")



                    # Show in chat
        
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
                    self.chat_box.tag_bind(tag_name, "<Button-1>", lambda e, p=file_path: self.open_file(p))

                    # Make text hoverable
                    self.chat_box.tag_bind(tag_name, "<Enter>", lambda e: self.chat_box.config(cursor="hand2"))
                    self.chat_box.tag_bind(tag_name, "<Leave>", lambda e: self.chat_box.config(cursor=""))

                    # Continue text
                    self.chat_box.insert(END, f" to {self.selected_user}\n")
                    self.chat_box.config(state="disabled")
                    self.chat_box.update_idletasks()



                else:
                    text = decrypted if isinstance(decrypted, str) else decrypted.decode("utf-8", errors="replace")
                    self.save_message(text, "text", direction)

                    self.chat_box.config(state="normal")
                    self.chat_box.insert(END, f"{msg.get('from')}: {text}\n")
                    self.chat_box.config(state="disabled")

            except Exception as de:
                print("Failed to decrypt a message from sync:", de)

        # Auto scroll
        self.chat_box.see(END)

    except requests.exceptions.RequestException:
        print("Unable to connect to server for sync (offline).")
    except Exception as e:
        messagebox.showerror("Sync Error", f"Could not fetch missed messages:\n{e}")
