import tkinter as tk


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
