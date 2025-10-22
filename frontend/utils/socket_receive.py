import tempfile
from tkinter import END



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

