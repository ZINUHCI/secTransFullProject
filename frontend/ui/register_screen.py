import tkinter as tk



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
