import requests, os
from tkinter import messagebox
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")

    # -----------------------------
    # LOGOUT
    # -----------------------------
def logout_user(self):
    confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
    if confirm:
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            requests.post(f"{SERVER_URL}/logout", headers=headers)
        except:
            pass
        try:
            if self.sio.connected:
                self.sio.disconnect()
        except:
            pass
        self.username = None
        self.token = None
        self.private_key = None
        self.public_key = None
        self.show_login_screen()