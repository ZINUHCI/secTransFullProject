import tkinter as tk
import socketio, os
from dotenv import load_dotenv
from ui.chat_screen import show_chat_screen
from ui.login_screen import show_login_screen
from ui.register_screen import show_register_screen
from utils import clear_window, decryption, encryption, fetch_and_display_history, fetch_users, send_file_msg, login_user, logout_user, on_user_select, register_user, send_text_msg, socket_connection, socket_receive

# Load variables from .env
load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")

class MessengerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔐 Secure Messenger")
        self.root.geometry("550x550")

        # user-related data
        self.username = None
        self.token = None
        self.private_key = None
        self.public_key = None
        self.selected_user = None
        self.users = []

        
        # SocketIO client
        self.sio = socketio.Client()
        self.sio.on("receive_message", self._on_socket_receive_message)

        self.show_login_screen()

    def show_login_screen(self):
        show_login_screen(self)

    def show_register_screen(self):
        show_register_screen(self)

    def clear_window(self):
        clear_window.clear_window(self)

    def decrypt_message_payload(self, msg_obj):
        return decryption.decrypt_message_payload(self, msg_obj)

    def encrypt_for_recipient(self, plaintext, recipient_username):
        return encryption.encrypt_for_recipient(self, plaintext, recipient_username)

    def fetch_and_display_history(self, other_username):
        fetch_and_display_history.fetch_and_display_history(self, other_username)

    def fetch_users(self):
        fetch_users.fetch_users(self)

    def login_user(self):
        login_user.login_user(self)

    def show_chat_screen(self):
        show_chat_screen(self)

    def logout_user(self):
        logout_user.logout_user(self)

    def on_user_select(self, event):
        on_user_select.on_user_select(self, event)

    def register_user(self):
        register_user.register_user(self)

    def send_file(self):
        send_file_msg.send_file(self)

    def send_message(self):
        send_text_msg.send_message(self)

    def _send_message_task(self, msg):
        send_text_msg._send_message_task(self, msg)

    def _append_sent_message(self, msg):
        send_text_msg._append_sent_message(self, msg)

    def connect_socket(self):
        socket_connection.connect_socket(self)
    
    def disconnect_socket(self):
        socket_connection.disconnect_socket(self)

    def _on_socket_receive_message(self, data):
        socket_receive._on_socket_receive_message(self, data)



if __name__ == "__main__":
    root = tk.Tk()
    app = MessengerApp(root)
    root.mainloop()
