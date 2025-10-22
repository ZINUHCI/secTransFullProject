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

    threading.Thread(target=self._send_message_task, args=(msg,), daemon=True).start()

def _send_message_task(self, msg):
    try:
        print(self.selected_user)
        enc = self.encrypt_for_recipient(msg, self.selected_user)
        payload = {"recipient": self.selected_user, **enc}
        headers = {"Authorization": f"Bearer {self.token}"}

        print(f"Sending payload: {payload}")
        res = requests.post(f"{SERVER_URL}/messages/send-text", json=payload, headers=headers, timeout=5)

        if res.status_code == 200:
            self.root.after(0, lambda: self._append_sent_message(msg))
        else:
            messagebox.showerror("Error", res.json().get("message", "Failed to send message"))
    except requests.exceptions.ConnectionError:
        messagebox.showwarning("Network Error", "Could not connect to server.")
    except Exception as e:
        messagebox.showerror("Error", f"Message send failed.\n{e}")

def _append_sent_message(self, msg):
    self.chat_box.config(state="normal")
    self.chat_box.insert(END, f"You → {self.selected_user}: {msg}\n")
    self.chat_box.yview_moveto(1.0)
    self.chat_box.config(state="disabled")
    self.msg_entry.delete(0, END)
