import os
import requests
from tkinter import messagebox, filedialog, END
from dotenv import load_dotenv
import platform
import subprocess


# -----------------------------
# SEND FILE MESSAGE
# -----------------------------
def send_file(self):
    if not self.selected_user:
        messagebox.showwarning("No Recipient", "Select a user to chat with first.")
        return

    file_path = filedialog.askopenfilename()
    if not file_path:
        return  # user canceled file picker

    filename = os.path.basename(file_path)

    try:
        # Read the file content
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        # Encrypt the file for the recipient
        enc = self.encrypt_for_recipient(file_bytes, self.selected_user)
        headers = {"Authorization": f"Bearer {self.token}"}
        files = {"file": (filename, open(file_path, "rb"))}
        data = {
            "recipient": self.selected_user,
            "encryptedAesKeyB64": enc["encryptedAesKeyB64"],
            "nonceB64": enc["nonceB64"],
            "ciphertextB64": enc["ciphertextB64"],
            "tagB64": enc["tagB64"]
        }

        self.save_file_message(file_bytes, os.path.basename(file_path), "sent")

        
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

        # Create multipart form data
        files = {"file": (filename, open(file_path, "rb"))}
        data = {
            "recipient": self.selected_user,
            "encryptedAesKeyB64": enc["encryptedAesKeyB64"],
            "nonceB64": enc["nonceB64"],
            "ciphertextB64": enc["ciphertextB64"],
            "tagB64": enc["tagB64"]
        }

        # Try to send online
        try:
            res = requests.post(f"{self.server_url}/messages/send-file", files=files, data=data, headers=headers, timeout=10)
            print("place 1")
            if res.status_code != 200:
                messagebox.showerror("Send Error", res.json().get("message", "Failed to send file"))
            print("place 2")
        except requests.exceptions.RequestException:
            # If no connection, keep local copy and continue silently
            messagebox.showwarning("Offline Mode", "File saved locally but not sent (no internet).")
            print("place 3")

    except Exception as e:
        messagebox.showerror("Error", f"Could not send file.\n{e}")
        print("FIle sent successfully")


def open_file(path):
    try:
        print("Opening file:", path)
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Open File Error", f"Could not open file:\n{e}")
