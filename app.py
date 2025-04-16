import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from patients import patients_bp
from models import db, PatientInfo
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()

app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///info.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

db.init_app(app)
app.register_blueprint(patients_bp)

@app.cli.command('init-db')
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()