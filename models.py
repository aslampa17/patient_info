from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo

db = SQLAlchemy()

class PatientInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), onupdate=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))

    visits = db.relationship('Visit', back_populates='patient', lazy=True,cascade='all, delete-orphan')

    def __repr__(self):
        return f"<PatientInfo {self.id}: {self.name}>"

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_info.id'), nullable=False)
    visit_date = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")))
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    notes = db.Column(db.Text)

    patient = db.relationship('PatientInfo', back_populates='visits')

    def __repr__(self):
        return f'Visit {self.id} for Patient {self.patient_id} on {self.visit_date}'