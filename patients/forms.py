from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Email

class PatientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=1, max=120)])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=7, max=15)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Submit')

class VisitForm(FlaskForm):
    symptoms = StringField('Symptoms', validators=[DataRequired()])
    diagnosis = StringField('Diagnosis', validators=[DataRequired()])
    treatment = StringField('Treatment', validators=[DataRequired()])
    notes = StringField('Notes')
    submit = SubmitField('Submit')