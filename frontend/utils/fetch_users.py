from tkinter import messagebox, END
import requests, os, threading
from dotenv import load_dotenv



def fetch_users(self):
    print(self.token)
    try:
        headers = {"Authorization": f"Bearer {self.token}"}
        res = requests.get(f"{self.server_url}/view/users", headers=headers, timeout=5)

        if res.status_code == 200:
            self.users = res.json().get("users", [])
            self.user_list.delete(0, END)
            for user in self.users:
                if user["username"] != self.username:
                    self.user_list.insert(END, user["username"])
        else:
            msg = res.json().get("message", "Failed to fetch users")
            messagebox.showerror("Error", msg)

    except requests.exceptions.ConnectionError:
        messagebox.showwarning("Connection Error", "Could not connect to the server.")
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")

def start_user_refresh(self):
    # Run fetch_users in a background thread to avoid freezing UI
    threading.Thread(target=self.fetch_users, daemon=True).start()
    # Refresh every 5 seconds
    self.root.after(5000, self.start_user_refresh)
