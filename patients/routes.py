from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import select
from . import patients_bp
from models import db, PatientInfo

@patients_bp.route('/', methods=['GET'])
@patients_bp.route('/patients', methods=['GET'])
def display_patients():
    search_term = request.args.get('search')
    statement = select(PatientInfo)

    if search_term:
        statement = statement.where(PatientInfo.phone.like(f"%{search_term}%"))

    patients = db.session.execute(statement).scalars().all()
    return render_template('patients.html', patients=patients)

@patients_bp.route('/patients/<int:pid>', methods=['GET'])
def display_patient(pid):
    statement = select(PatientInfo).where(PatientInfo.id == pid)
    patients = db.session.execute(statement).scalars().all()
    return render_template('patients.html', patients=patients)

@patients_bp.route('/patients/new', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        try:
            new_patient = PatientInfo(
                    name = request.form['name'],
                    age = int(request.form['age']),
                    gender = request.form['gender'],
                    email = request.form['email'],
                    phone = request.form['phone'],
                    location = request.form['location']            
            )
            db.session.add(new_patient)
            db.session.commit()
            flash('Patient details added successfully!', 'success')
            return  redirect(url_for('patients.display_patients'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'error')
            return  redirect(url_for('patients.new_patient'))

    return render_template('create_patient.html')

@patients_bp.route('/patients/<int:pid>/update', methods=['GET', 'POST'])
def update_patient(pid):
    if request.method == 'POST':
        try:
            statement = select(PatientInfo).where(PatientInfo.id == pid)
            patient = db.session.execute(statement).scalars().first()
            patient.name = request.form['name']
            patient.age = int(request.form['age'])
            patient.gender = request.form['gender']
            patient.email = request.form['email']
            patient.phone = request.form['phone']
            patient.location = request.form['location']            
            db.session.commit()
            flash('Patient details updated successfully!', 'success')
            return  redirect(url_for('patients.display_patients'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'error')
            return  redirect(url_for('patients.new_patient'))
    try:
        statement = select(PatientInfo).where(PatientInfo.id == pid)
        patient = db.session.execute(statement).scalars().first()
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')
        return  redirect(url_for('patients.display_patients'))
    print(patient)
    return render_template('create_patient.html', patient=patient)

@patients_bp.route('/patients/<int:pid>/delete', methods=['GET', 'POST'])
def delete_patient(pid):
    try:
        statement = select(PatientInfo).where(PatientInfo.id == pid)
        patient = db.session.execute(statement).scalars().first()

        if not patient:
            flash('Patient not found.', 'warning')
            return redirect(url_for('patients.display_patients'))

        if request.method == 'POST':
            db.session.delete(patient)
            db.session.commit()
            flash(f'Patient "{patient.name}" successfully deleted.', 'success')
            return redirect(url_for('patients.display_patients'))
        
        return render_template('delete_patient_confirmation.html', patient=patient)

    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')
        return  redirect(url_for('patients.display_patients'))