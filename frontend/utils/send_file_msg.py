import requests, os
from tkinter import messagebox, filedialog, END
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")


    # -----------------------------
    # SEND FILE MESSAGE
    # -----------------------------
def send_file(self):
    if not self.selected_user:
        messagebox.showwarning("No Recipient", "Select a user to chat with first.")
        return
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        enc = self.encrypt_for_recipient(file_data, self.selected_user)
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "recipient": self.selected_user,
            "filename": os.path.basename(file_path),
            **enc
        }
        res = requests.post(f"{SERVER_URL}/messages/send-file", json=payload, headers=headers)
        if res.status_code == 200:
            self.chat_box.config(state="normal")
            self.chat_box.insert(END, f"📤 You sent {os.path.basename(file_path)} to {self.selected_user}\n")
            self.chat_box.config(state="disabled")
        else:
            messagebox.showerror("Error", res.json().get("message", "Failed to send file"))
    except Exception as e:
        messagebox.showerror("Error", f"Could not send file.\n{e}")