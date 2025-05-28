import os
import signal
import sys
import threading
import time
import webbrowser
from flask import Flask, abort, jsonify, render_template, request
from patients import patients_bp
from models import db
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "defaultsecretkey")

if getattr(sys, "frozen", False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.abspath(os.path.dirname(__file__))


db_path = os.path.join(base_path, "info.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True

db.init_app(app)
app.register_blueprint(patients_bp)


@app.cli.command("init-db")
def create_tables():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully.")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/shutdown", methods=["POST"])
def shutdown():
    if request.method != "POST":
        abort(405)

    def delayed_shutdown():
        time.sleep(0.1)
        os.kill(os.getpid(), signal.SIGTERM)

    threading.Thread(target=delayed_shutdown).start()
    return "Shutting down.....", 200


def initialize_database():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Creating tables...")
        with app.app_context():
            db.create_all()
        print("Tables created successfully.")

    os.chmod(db_path, 0o666)


def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    initialize_database()
    threading.Thread(target=open_browser).start()
    app.run(use_reloader=False)
