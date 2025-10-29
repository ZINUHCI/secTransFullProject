import requests, os
from tkinter import messagebox
from dotenv import load_dotenv
from Crypto.PublicKey import RSA


# Load variables from .env
load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")


# -----------------------------
# LOGIN FUNCTION
# -----------------------------
def login_user(self):
    print(f"Login public key: {self.public_key}")
    username = self.login_username.get().strip()
    password = self.login_password.get().strip()
    if not username or not password:
        messagebox.showwarning("Input Error", "All fields are required.")
        return
    try:
        res = requests.post(f"{SERVER_URL}/auth/login", json={"username": username, "password": password})
        if res.status_code == 200:
            print("Login successful")
            data = res.json()
            print(data)
            self.username = username
            self.token = data["token"]
            self.save_logged_in_user()

            # 🔑 Generate RSA key pair on successful register
            key = RSA.generate(2048)
            self.private_key = key.export_key()
            self.public_key = key.publickey().export_key()
            print(f"Public key at register: {self.public_key}")

             # Send public key to backend for storage
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {"publicKeyPem": self.public_key.decode()}
            res2 = requests.post(f"{SERVER_URL}/pubKey/publish-public-key", json=payload, headers=headers)
            if res2.status_code != 200:
                messagebox.showerror("Unable to publish public key", res2.json().get("message", "Invalid credentials"))
                return


            # 🧠 Connect to Socket.IO after successful login
            self.connect_socket()

            self.show_chat_screen()
        else:
            messagebox.showerror("Login Failed", res.json().get("message", "Invalid credentials"))
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server.\n{e}")