import requests, os, threading
from tkinter import messagebox, END
from dotenv import load_dotenv

load_dotenv()
SERVER_URL = os.getenv("SERVER_URL")

def send_message(self):
    msg = self.msg_entry.get().strip()
    if not msg:
        messagebox.showwarning("Empty Message", "Type something to send.")
        return
    if not self.selected_user:
        messagebox.showwarning("No Recipient", "Select a user to chat with first.")
        return

    # ✅ Save the message locally right away
    self.save_message(msg, "text", "sent")

    # ✅ Display locally
    self.root.after(0, lambda: self._append_sent_message(msg))

    # ✅ Then try sending online (so offline works too)
    threading.Thread(target=self._send_message_task, args=(msg,), daemon=True).start()

def _send_message_task(self, msg):
    try:
        enc = self.encrypt_for_recipient(msg, self.selected_user)
        payload = {"recipient": self.selected_user, **enc}
        headers = {"Authorization": f"Bearer {self.token}"}

        res = requests.post(f"{SERVER_URL}/messages/send-text", json=payload, headers=headers, timeout=5)

        if res.status_code != 200:
            messagebox.showerror("Error", res.json().get("message", "Failed to send message"))
    except requests.exceptions.ConnectionError:
        messagebox.showwarning("Network Error", "Could not connect to server. Message stored locally.")
    except Exception as e:
        messagebox.showerror("Error", f"Message send failed.\n{e}")

def _append_sent_message(self, msg):
    self.chat_box.config(state="normal")
    self.chat_box.insert(END, f"You: {msg}\n")
    self.chat_box.see(END)
    self.chat_box.config(state="disabled")
