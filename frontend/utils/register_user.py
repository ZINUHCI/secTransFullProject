from tkinter import messagebox
import requests, os
from dotenv import load_dotenv
from Crypto.PublicKey import RSA


# Load variables from .env
load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")

   # -----------------------------
    # REGISTER FUNCTION
    # -----------------------------
def register_user(self):
    username = self.reg_username.get().strip()
    password = self.reg_password.get().strip()
    if not username or not password:
        messagebox.showwarning("Input Error", "All fields are required.")
        return
    try:
        res = requests.post(f"{SERVER_URL}/auth/register", json={"username": username, "password": password})
        if res.status_code == 200:
            messagebox.showinfo("Success", "Registration successful! You can now log in.")

            # 🔑 Generate RSA key pair on successful register
            key = RSA.generate(2048)
            print(key)
            self.private_key = key.export_key()
            self.public_key = key.publickey().export_key()
            print(f"Public key at register: {self.public_key}")


            self.show_login_screen()
        else:
            messagebox.showerror("Error", res.json().get("message", "Registration failed"))
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server.\n{e}")
