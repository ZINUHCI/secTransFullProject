import tkinter as tk
from tkinter import scrolledtext, END, Listbox

def show_chat_screen(self):
    self.clear_window()

    # Header
    header = tk.Frame(self.root)
    header.pack(pady=5, fill="x")
    tk.Label(header, text=f"💬 Welcome, {self.username}", font=("Arial", 14, "bold")).pack(side="left", padx=10)
    tk.Button(header, text="Logout", bg="red", fg="white", command=self.logout_user).pack(side="right")

    # Main chat frame
    chat_frame = tk.Frame(self.root)
    chat_frame.pack(fill="both", expand=True)

    # Left: Chat box
    left = tk.Frame(chat_frame)
    left.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)

    self.chat_box = scrolledtext.ScrolledText(left, width=60, height=25, state="disabled", wrap="word")
    self.chat_box.pack(fill="both", expand=True)
    self.chat_box.config(state="normal")
    self.chat_box.insert(END, "💬 Select a user from the list to start chatting.\n")
    self.chat_box.config(state="disabled")

    # Right: User list
    right = tk.Frame(chat_frame, width=180)
    right.pack(side="right", fill="y", padx=(5, 10), pady=10)
    tk.Label(right, text="👥 Users").pack(pady=(0, 5))

    self.user_list = Listbox(right, height=20, width=25, exportselection=False)
    self.user_list.pack(fill="y", expand=True)
    self.user_list.bind("<<ListboxSelect>>", self.on_user_select)

    # Bottom: Message input + buttons
    input_frame = tk.Frame(self.root)
    input_frame.pack(pady=5, fill="x", padx=10)

    self.msg_entry = tk.Entry(input_frame, width=60)
    self.msg_entry.pack(side="left", padx=(0, 5), expand=True, fill="x")
    self.msg_entry.focus()

    tk.Button(input_frame, text="Send", width=10, command=self.send_message).pack(side="right", padx=5)
    tk.Button(input_frame, text="📁 File", width=10, command=self.send_file).pack(side="right")

    # Fetch users (in background)
    import threading
    threading.Thread(target=self.fetch_users, daemon=True).start()
