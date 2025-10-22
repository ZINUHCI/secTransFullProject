
def clear_window(self):
    for widget in self.root.winfo_children():
        widget.destroy()