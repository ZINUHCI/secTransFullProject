from tkinter import END


def on_user_select(self, event):
    selection = self.user_list.curselection()
    print(f"The selection is {selection}")
    print(self.user_list)
    if not selection:
        return
    self.selected_user = self.user_list.get(selection[0])
    print(self.selected_user)
    # clear chat box and fetch previous chat
    self.chat_box.config(state="normal")
    self.chat_box.delete("1.0", END)
    self.chat_box.insert(END, f"📩 Chatting with {self.selected_user}\n\n")
    self.chat_box.config(state="disabled")
    # fetch history and display
    self.fetch_and_display_history(self.selected_user)