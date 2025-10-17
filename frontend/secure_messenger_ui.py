import tkinter as tk
from tkinter import messagebox, scrolledtext, Listbox, END, filedialog
import requests, os, base64, socketio
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
import tempfile


SERVER_URL = "http://localhost:5000"  # Adjust if backend runs elsewhere

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


    # -----------------------------
    # LOGIN SCREEN
    # -----------------------------
    def show_login_screen(self):
        self.clear_window()
        tk.Label(self.root, text="🔐 Login", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self.root, text="Username").pack()
        self.login_username = tk.Entry(self.root, width=30)
        self.login_username.pack(pady=5)
        tk.Label(self.root, text="Password").pack()
        self.login_password = tk.Entry(self.root, show="*", width=30)
        self.login_password.pack(pady=5)
        tk.Button(self.root, text="Login", width=20, command=self.login_user).pack(pady=10)
        tk.Button(self.root, text="Create New Account", width=20, command=self.show_register_screen).pack()

    # -----------------------------
    # REGISTER SCREEN
    # -----------------------------
    def show_register_screen(self):
        self.clear_window()
        tk.Label(self.root, text="📝 Register", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self.root, text="Username").pack()
        self.reg_username = tk.Entry(self.root, width=30)
        self.reg_username.pack(pady=5)
        tk.Label(self.root, text="Password").pack()
        self.reg_password = tk.Entry(self.root, show="*", width=30)
        self.reg_password.pack(pady=5)
        tk.Button(self.root, text="Register", width=20, command=self.register_user).pack(pady=10)
        tk.Button(self.root, text="Back to Login", width=20, command=self.show_login_screen).pack()


    # -----------------------------
    # CHAT SCREEN
    # -----------------------------
    def show_chat_screen(self):
        self.clear_window()
        header = tk.Frame(self.root)
        header.pack(pady=5, fill="x")
        tk.Label(header, text=f"💬 Welcome, {self.username}", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        tk.Button(header, text="Logout", bg="red", fg="white", command=self.logout_user).pack(side="right")

        chat_frame = tk.Frame(self.root)
        chat_frame.pack(fill="both", expand=True)

        # Left: chat box
        left = tk.Frame(chat_frame)
        left.pack(side="left", fill="both", expand=True, padx=(10,5), pady=10)

        self.chat_box = scrolledtext.ScrolledText(left, width=60, height=25, state="disabled", wrap="word")
        self.chat_box.pack(fill="both", expand=True)

        # Right: users list
        right = tk.Frame(chat_frame, width=180)
        right.pack(side="right", fill="y", padx=(5,10), pady=10)
        tk.Label(right, text="👥 Users").pack(pady=(0,5))
        self.user_list = Listbox(right, height=20, width=25)
        self.user_list.pack(fill="y", expand=True)
        self.user_list.bind("<<ListboxSelect>>", self.on_user_select)

        # Bottom: input + file button
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=5, fill="x", padx=10)
        self.msg_entry = tk.Entry(input_frame, width=60)
        self.msg_entry.pack(side="left", padx=(0,5), expand=True, fill="x")
        tk.Button(input_frame, text="Send", width=10, command=self.send_message).pack(side="right", padx=5)
        tk.Button(input_frame, text="📁 File", width=10, command=self.send_file).pack(side="right")

        # fetch users
        self.fetch_users()
        self.clear_window()
        header = tk.Frame(self.root)
        header.pack(pady=5)
        tk.Label(header, text=f"💬 Welcome, {self.username}", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        tk.Button(header, text="Logout", bg="red", fg="white", command=self.logout_user).pack(side="right")

        chat_frame = tk.Frame(self.root)
        chat_frame.pack(fill="both", expand=True)

        self.chat_box = scrolledtext.ScrolledText(chat_frame, width=45, height=15, state="disabled")
        self.chat_box.pack(side="left", padx=10, pady=10)

        user_frame = tk.Frame(chat_frame)
        user_frame.pack(side="right", fill="y", padx=5, pady=10)
        tk.Label(user_frame, text="👥 Users").pack()
        self.user_list = Listbox(user_frame, height=15, width=20)
        self.user_list.pack()
        self.user_list.bind("<<ListboxSelect>>", self.on_user_select)

        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=5)
        self.msg_entry = tk.Entry(input_frame, width=40)
        self.msg_entry.pack(side="left", padx=5)
        tk.Button(input_frame, text="Send", width=10, command=self.send_message).pack(side="right", padx=5)
        tk.Button(input_frame, text="📁 File", width=10, command=self.send_file).pack(side="right", padx=5)

        self.fetch_users()

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
                self.show_login_screen()
            else:
                messagebox.showerror("Error", res.json().get("message", "Registration failed"))
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to server.\n{e}")

    def connect_socket(self):
        """Connect to the backend Socket.IO server."""
        try:
            self.sio.connect(SERVER_URL, transports=["websocket"], auth={"token": self.token})
            print("✅ Socket connected")

            # Emit event after connecting
            self.sio.emit("user_connected", {
                "username": self.username,
                "token": self.token
            })
            print(f"🔗 Emitted connection event for {self.username}")

            # Optionally listen for events from backend
            @self.sio.on("message_received")
            def on_message(data):
                self.display_incoming_message(data)

        except Exception as e:
            print(f"❌ Socket connection failed: {e}")

    def disconnect_socket(self):
        try:
            if self.sio.connected:
                self.sio.emit("user_disconnected", {"username": self.username})
                self.sio.disconnect()
                print("🔌 Socket disconnected")
        except Exception as e:
            print(f"❌ Error disconnecting socket: {e}")

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

                # 🔑 Generate RSA key pair on login
                key = RSA.generate(2048)
                self.private_key = key.export_key()
                self.public_key = key.publickey().export_key()

                # Send public key to backend
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
  # -----------------------------
    # USERS + HISTORY
    # -----------------------------
    def fetch_users(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            res = requests.get(f"{SERVER_URL}/view/users", headers=headers)
            if res.status_code == 200:
                self.users = res.json().get("users", [])
                self.user_list.delete(0, END)
                for user in self.users:
                    if user["username"] != self.username:
                        self.user_list.insert(END, user["username"])
            else:
                messagebox.showerror("Error", res.json().get("message", "Failed to fetch users"))
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch users.\n{e}")


    def on_user_select(self, event):
        selection = self.user_list.curselection()
        if not selection:
            return
        self.selected_user = self.user_list.get(selection[0])
        # clear chat box and fetch previous chat
        self.chat_box.config(state="normal")
        self.chat_box.delete("1.0", END)
        self.chat_box.insert(END, f"📩 Chatting with {self.selected_user}\n\n")
        self.chat_box.config(state="disabled")
        # fetch history and display
        self.fetch_and_display_history(self.selected_user)


    def fetch_and_display_history(self, other_username):
        """
        Assumes backend endpoint:
            GET /messages/history/:otherUsername
        returns list of messages relevant to current user and that user in ascending order.
        Each message must include:
          { sender, recipient, encryptedAesKeyB64, nonceB64, ciphertextB64, tagB64, type, filename?, createdAt }
        """
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            res = requests.get(f"{SERVER_URL}/messages/history/{other_username}", headers=headers)
            if res.status_code != 200:
                messagebox.showerror("Error", res.json().get("message", "Could not load history"))
                return

            msgs = res.json().get("messages", [])
            for m in msgs:
                try:
                    plaintext = self.decrypt_message_payload(m)
                    # display depending on type
                    self.chat_box.config(state="normal")
                    ts = m.get("createdAt", "")
                    if m.get("type") == "file":
                        # save file to temp and provide path
                        filename = m.get("filename") or "file"
                        tmp = tempfile.NamedTemporaryFile(delete=False, prefix="recv_", suffix="_"+filename)
                        tmp.write(plaintext)
                        tmp.close()
                        self.chat_box.insert(END, f"{m['sender']} → You: [file] {filename} saved to {tmp.name}\n")
                    else:
                        # treat as text
                        text = plaintext.decode("utf-8", errors="replace")
                        self.chat_box.insert(END, f"{m['sender']} ({ts}): {text}\n")
                    self.chat_box.config(state="disabled")
                except Exception as de:
                    # decryption failed for this message
                    print("Decryption error for message:", de)
                    self.chat_box.config(state="normal")
                    self.chat_box.insert(END, f"{m['sender']}: [unable to decrypt]\n")
                    self.chat_box.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch history.\n{e}")

    # -----------------------------
    # ENCRYPT AND DECRYPT MESSAGE (AES + RSA) HELPERS
    # -----------------------------
    def encrypt_for_recipient(self, plaintext, recipient_username):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = requests.get(f"{SERVER_URL}/pubKey/public-key/{recipient_username}", headers=headers)
        if res.status_code != 200:
            raise Exception("Recipient public key not found")

        recipient_public_key = RSA.import_key(res.json()["publicKey"])
        print(recipient_public_key)
        aes_key = get_random_bytes(32)
        cipher_aes = AES.new(aes_key, AES.MODE_GCM)
        ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext.encode() if isinstance(plaintext, str) else plaintext)

        cipher_rsa = PKCS1_OAEP.new(recipient_public_key)
        encrypted_aes_key = cipher_rsa.encrypt(aes_key)

        print(base64.b64encode(tag).decode())

        return {
            "encryptedAesKeyB64": base64.b64encode(encrypted_aes_key).decode(),
            "nonceB64": base64.b64encode(cipher_aes.nonce).decode(),
            "ciphertextB64": base64.b64encode(ciphertext).decode(),
             "tagB64": base64.b64encode(tag).decode(),
        }
    

    def decrypt_message_payload(self, msg_obj):
        """
        Decrypts a single message object from the server.
        Returns plaintext bytes (for text messages, decode to string).
        """
        if not self.private_key:
            raise Exception("No private key available to decrypt")

        enc_key_b64 = msg_obj.get("encryptedAesKeyB64")
        nonce_b64 = msg_obj.get("nonceB64")
        ct_b64 = msg_obj.get("ciphertextB64")
        tag_b64 = msg_obj.get("tagB64")

        if not (enc_key_b64 and nonce_b64 and ct_b64 and tag_b64):
            raise Exception("Missing fields for decryption")

        encrypted_aes_key = base64.b64decode(enc_key_b64)
        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(ct_b64)
        tag = base64.b64decode(tag_b64)

        # RSA decrypt AES key using private key
        priv = RSA.import_key(self.private_key)
        rsa_cipher = PKCS1_OAEP.new(priv)
        aes_key = rsa_cipher.decrypt(encrypted_aes_key)

        # AES-GCM decrypt
        aes_cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext = aes_cipher.decrypt_and_verify(ciphertext, tag)  # raises ValueError if tag mismatch
        return plaintext


    # -----------------------------
    # SEND TEXT MESSAGE
    # -----------------------------
    def send_message(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            messagebox.showwarning("Empty Message", "Type something to send.")
            return
        if not self.selected_user:
            messagebox.showwarning("No Recipient", "Select a user to chat with first.")
            return
        try:
            enc = self.encrypt_for_recipient(msg, self.selected_user)
            payload = {
                "recipient": self.selected_user,
                **enc
            }
            print(payload)
            headers = {"Authorization": f"Bearer {self.token}"}
            res = requests.post(f"{SERVER_URL}/messages/send-text", json=payload, headers=headers)
            if res.status_code == 200:
                self.chat_box.config(state="normal")
                self.chat_box.insert(tk.END, f"You → {self.selected_user}: {msg}\n")
                self.chat_box.config(state="disabled")
                self.msg_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", res.json().get("message", "Failed to send message"))
        except Exception as e:
            messagebox.showerror("Error", f"Encryption or send failed.\n{e}")

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
                self.chat_box.insert(tk.END, f"📤 You sent {os.path.basename(file_path)} to {self.selected_user}\n")
                self.chat_box.config(state="disabled")
            else:
                messagebox.showerror("Error", res.json().get("message", "Failed to send file"))
        except Exception as e:
            messagebox.showerror("Error", f"Could not send file.\n{e}")


    # -----------------------------
    # SOCKET RECEIVE HANDLER
    # -----------------------------
    def _on_socket_receive_message(self, data):
        """
        Expected data shape from backend when a message arrives in real time:
        {
          id, from, recipient, encryptedAesKeyB64, nonceB64, ciphertextB64, tagB64, type, filename?, filesize?
        }
        """
        try:
            sender = data.get("from") or data.get("sender")
            # try to decrypt
            plaintext = None
            try:
                plaintext = self.decrypt_message_payload(data)
            except Exception as e:
                print("Realtime decryption failed:", e)

            # if currently chatting with sender, display directly. Otherwise show notification.
            if self.selected_user == sender:
                self.chat_box.config(state="normal")
                if data.get("type") == "file":
                    # save file
                    filename = data.get("filename") or "file"
                    tmp = tempfile.NamedTemporaryFile(delete=False, prefix="recv_", suffix="_"+filename)
                    tmp.write(plaintext if plaintext else b"")
                    tmp.close()
                    self.chat_box.insert(END, f"{sender} → You: [file] {filename} saved to {tmp.name}\n")
                else:
                    text = plaintext.decode("utf-8", errors="replace") if plaintext else "[unable to decrypt]"
                    self.chat_box.insert(END, f"{sender}: {text}\n")
                self.chat_box.config(state="disabled")
            else:
                # Not currently chatting with sender: append top-level notification and optionally update UI
                self.chat_box.config(state="normal")
                short = "[file]" if data.get("type") == "file" else (plaintext.decode("utf-8", errors="replace")[:40] if plaintext else "[unable to decrypt]")
                self.chat_box.insert(END, f"\n🔔 New message from {sender}: {short}\n")
                self.chat_box.config(state="disabled")
        except Exception as e:
            print("Error handling incoming socket message:", e)



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

    # -----------------------------
    # UTIL
    # -----------------------------
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MessengerApp(root)
    root.mainloop()
