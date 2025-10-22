import requests, os
from tkinter import messagebox
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")


# -----------------------------
# LOGIN FUNCTION
# -----------------------------
def login_user(self):
    username = self.login_username.get().strip()
    password = self.login_password.get().strip()
    if not username or not password:
        messagebox.showwarning("Input Error", "All fields are required.")
        return
    try:
        res = requests.post(f"{SERVER_URL}/auth/login", json={"username": username, "password": password})
        if res.status_code == 200:
            data = res.json()
            self.username = username
            self.token = data["token"]



            # 🧠 Connect to Socket.IO after successful login
            self.connect_socket()

            self.show_chat_screen()
        else:
            messagebox.showerror("Login Failed", res.json().get("message", "Invalid credentials"))
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server.\n{e}")