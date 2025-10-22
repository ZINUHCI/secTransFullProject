import requests, tempfile, os
from tkinter import messagebox, END
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")


def fetch_and_display_history(self, other_username):
    """
    Assumes backend endpoint:
        GET /messages/history/:otherUsername
    returns list of messages relevant to current user and that user in ascending order.
    Each message must include:
        { sender, recipient, encryptedAesKeyB64, nonceB64, ciphertextB64, tagB64, type, filename?, createdAt }
    """
    try:
        headers = {"Authorization": f"Bearer {self.token}"}
        res = requests.get(f"{SERVER_URL}/messages/history/{other_username}", headers=headers)
        if res.status_code != 200:
            messagebox.showerror("Error", res.json().get("message", "Could not load history"))
            return

        msgs = res.json().get("messages", [])
        for m in msgs:
            try:
                plaintext = self.decrypt_message_payload(m)
                # display depending on type
                self.chat_box.config(state="normal")
                ts = m.get("createdAt", "")
                if m.get("type") == "file":
                    # save file to temp and provide path
                    filename = m.get("filename") or "file"
                    tmp = tempfile.NamedTemporaryFile(delete=False, prefix="recv_", suffix="_"+filename)
                    tmp.write(plaintext)
                    tmp.close()
                    self.chat_box.insert(END, f"{m['sender']} → You: [file] {filename} saved to {tmp.name}\n")
                else:
                    # treat as text
                    text = plaintext.decode("utf-8", errors="replace")
                    self.chat_box.insert(END, f"{m['sender']} ({ts}): {text}\n")
                self.chat_box.config(state="disabled")
            except Exception as de:
                # decryption failed for this message
                print("Decryption error for message:", de)
                self.chat_box.config(state="normal")
                self.chat_box.insert(END, f"{m['sender']}: [unable to decrypt]\n")
                self.chat_box.config(state="disabled")
    except Exception as e:
        messagebox.showerror("Error", f"Could not fetch history.\n{e}")