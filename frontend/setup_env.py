import os, sys
from dotenv import load_dotenv
from tkinter import messagebox

def set_up_environment(self):
    # Handle PyInstaller environment path

    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # db_path = os.path.join(base_path, "db", "database.db")
    self.base_dir = base_path

    # Path to config.env
    self.env_path = os.path.join(base_path, "config.env")
    print("🔧 Setting up environment from:", self.env_path)

    # Load .env if it exists
    if os.path.exists(self.env_path):
        load_dotenv(self.env_path)

        # Load variables
        # self.server_url = os.getenv("SERVER_URL", "http://localhost:5000")
        self.server_url = os.getenv("SERVER_URL")
        print("✅ Loaded SERVER_URL:", self.server_url)
        db_filename = os.getenv("DB_FILE", "local_messages.db")

        # ✅ Store DB in user's AppData folder (persistent)
        app_data_dir = os.path.join(os.getenv("LOCALAPPDATA"), "SecureTransmissionApp")
        os.makedirs(app_data_dir, exist_ok=True)

        self.db_path = os.path.join(app_data_dir, db_filename)

        # Create DB if missing
        if not os.path.exists(self.db_path):
            open(self.db_path, 'a').close()

    else:
        messagebox.showwarning(
            "Missing Config File",
            f"⚠️ The configuration file was not found at:\n{self.env_path}\n\n"
            "Default settings will be used until it's created."
        )
