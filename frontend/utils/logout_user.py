import requests, os
from tkinter import messagebox
from dotenv import load_dotenv
import sqlite3


    # -----------------------------
    # LOGOUT
    # -----------------------------
def logout_user(self):
    confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
    if confirm:
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            requests.post(f"{self.server_url}/logout", headers=headers)
        except:
            pass
        try:
            if self.sio.connected:
                self.sio.disconnect()

                # Erase JWT from Local SQLite file
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("UPDATE user_session SET logged_in=0, jwt_token=NULL WHERE username=?", (self.username,))

                conn.commit()
                conn.close()
        except:
            pass
        self.username = None
        self.token = None
        self.private_key = None
        self.public_key = None
        self.show_login_screen()