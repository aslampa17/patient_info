import os
import sys
from flask import Flask, render_template
from patients import patients_bp
from models import db
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'defaultsecretkey')

if getattr(sys, 'frozen', False):  # Running as a PyInstaller executable
    base_path = os.path.dirname(sys.executable)  # Use the folder where the executable is located
else:
    base_path = os.path.abspath(os.path.dirname(__file__)) 

# Set the database path
db_path = os.path.join(base_path, "info.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

db.init_app(app)
app.register_blueprint(patients_bp)

@app.cli.command('init-db')
def create_tables():
    with app.app_context():
        print('Creating database tables...')
        db.create_all()
        print('Tables created successfully.')

@app.route('/')
def home():
    return render_template('index.html')

def initialize_database():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Creating tables...")
        with app.app_context():
            db.create_all()
        print("Tables created successfully.")
    
    os.chmod(db_path, 0o666)

if __name__ == '__main__':
    initialize_database()
    app.run()