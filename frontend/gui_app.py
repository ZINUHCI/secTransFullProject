import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from crypto.hybrid_encrypt import (
    encrypt_text_hybrid,
    decrypt_text_hybrid,
    encrypt_file_hybrid,
    decrypt_file_hybrid,
)

# =======================
# GUI Functions
# =======================

def encrypt_text():
    try:
        message = text_input.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Please enter some text to encrypt.")
            return

        public_key_file = filedialog.askopenfilename(title="Select Public Key File")
        if not public_key_file:
            return

        encrypted = encrypt_text_hybrid(message, public_key_file)

        save_file = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if save_file:
            with open(save_file, "w") as f:
                f.write(encrypted)
            messagebox.showinfo("Success", f"Text encrypted and saved to {save_file}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def decrypt_text():
    try:
        private_key_file = filedialog.askopenfilename(title="Select Private Key File")
        if not private_key_file:
            return

        input_file = filedialog.askopenfilename(
            title="Select Encrypted JSON File", filetypes=[("JSON files", "*.json")]
        )
        if not input_file:
            return

        decrypted = decrypt_text_hybrid(input_file, private_key_file)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, decrypted)
        messagebox.showinfo("Success", "Text decrypted successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def encrypt_file():
    try:
        input_file = filedialog.askopenfilename(title="Select File to Encrypt")
        if not input_file:
            return

        public_key_file = filedialog.askopenfilename(title="Select Public Key File")
        if not public_key_file:
            return

        save_file = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        if save_file:
            encrypt_file_hybrid(input_file, save_file, public_key_file)
            messagebox.showinfo("Success", f"File encrypted and saved to {save_file}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def decrypt_file():
    try:
        input_file = filedialog.askopenfilename(
            title="Select Encrypted JSON File", filetypes=[("JSON files", "*.json")]
        )
        if not input_file:
            return

        private_key_file = filedialog.askopenfilename(title="Select Private Key File")
        if not private_key_file:
            return

        save_file = filedialog.asksaveasfilename(
            title="Save Decrypted File As", defaultextension=".*"
        )
        if save_file:
            decrypt_file_hybrid(input_file, save_file, private_key_file)
            messagebox.showinfo("Success", f"File decrypted and saved to {save_file}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# =======================
# GUI Layout
# =======================

root = tk.Tk()
root.title("Secure Data Transmission System (AES + RSA)")
root.geometry("700x500")
root.configure(bg="#1e1e2f")

# Title
title_label = tk.Label(
    root,
    text="🔒 Secure Data Transmission System",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="#1e1e2f",
)
title_label.pack(pady=10)

# Input box
tk.Label(root, text="Enter Text:", fg="white", bg="#1e1e2f").pack()
text_input = scrolledtext.ScrolledText(root, height=5, width=70)
text_input.pack(pady=5)

# Buttons
frame_buttons = tk.Frame(root, bg="#1e1e2f")
frame_buttons.pack(pady=10)

btn_encrypt_text = tk.Button(frame_buttons, text="Encrypt Text", command=encrypt_text, bg="#0078d7", fg="white")
btn_encrypt_text.grid(row=0, column=0, padx=10)

btn_decrypt_text = tk.Button(frame_buttons, text="Decrypt Text", command=decrypt_text, bg="#0078d7", fg="white")
btn_decrypt_text.grid(row=0, column=1, padx=10)

btn_encrypt_file = tk.Button(frame_buttons, text="Encrypt File", command=encrypt_file, bg="#28a745", fg="white")
btn_encrypt_file.grid(row=1, column=0, padx=10, pady=5)

btn_decrypt_file = tk.Button(frame_buttons, text="Decrypt File", command=decrypt_file, bg="#dc3545", fg="white")
btn_decrypt_file.grid(row=1, column=1, padx=10, pady=5)

# Output box
tk.Label(root, text="Output:", fg="white", bg="#1e1e2f").pack()
text_output = scrolledtext.ScrolledText(root, height=10, width=70)
text_output.pack(pady=5)

root.mainloop()