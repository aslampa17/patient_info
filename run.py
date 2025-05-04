import webview
from threading import Thread, Event
from app import app, initialize_database

stop_event = Event()

app_title = "Patient Info"
host = "http://127.0.0.1"
port = 5000

def run():
    while not stop_event.is_set():
        app.run(port=port, use_reloader=False)
    
if __name__ == '__main__':

    initialize_database()

    t = Thread(target=run)
    t.daemon = True
    t.start()

    webview.create_window(
        app_title,
        f"{host}:{port}"
    )

    webview.start()

    stop_event.set()