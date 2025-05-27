import os
import sys
from threading import Thread, Event
from app import app, initialize_database

# ==== SETUP CONFIG ====
app_title = "Patient Info"
host = "127.0.0.1"
port = 5000
stop_event = Event()

# ==== FIX DATABASE PATH & WORKING DIR ====
if getattr(sys, 'frozen', False):  # PyInstaller bundle
    base_path = os.path.dirname(sys.executable)
    os.chdir(base_path)  # Set working dir to executable location
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# ==== INITIALIZE DB ====
initialize_database()

print(f"Using DB at: {base_path}")


# ==== RUN FLASK SERVER IN BACKGROUND THREAD ====
def run():
    # Important: disable reloader and multi-threading for SQLite safety
    app.run(host=host, port=port, threaded=False, use_reloader=False)

# ==== START EVERYTHING ====
if __name__ == '__main__':
    t = Thread(target=run)
    t.daemon = True
    t.start()

    # Create the desktop window pointing to the local Flask server
    webview.create_window(app_title, f"http://{host}:{port}")
    webview.start(gui='qt')

    # After window closes, stop the server loop
    stop_event.set()
