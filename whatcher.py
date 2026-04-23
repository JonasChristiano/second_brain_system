from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time, os


class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".md"):
            os.system(f'python rag/search.py "analise: {event.src_path}"')


observer = Observer()
observer.schedule(Handler(), "./vault/notes", recursive=True)
observer.start()

print("Jarvis ativo...")

while True:
    time.sleep(1)
