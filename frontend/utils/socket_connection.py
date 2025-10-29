from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

SERVER_URL = os.getenv("SERVER_URL")

def connect_socket(self):
        """Connect to the backend Socket.IO server."""
        try:
            print(self.token)
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