# dev_runner.py
import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

APP_FILE = "secure_messenger_ui.py"  # your main Tkinter app file

class ReloadOnChange(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_app()

    def start_app(self):
        if self.process:
            self.process.terminate()
        print("🔁 Reloading app...")
        self.process = subprocess.Popen(["python", APP_FILE])

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            self.start_app()

if __name__ == "__main__":
    event_handler = ReloadOnChange()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()
    print("👀 Watching for changes... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
