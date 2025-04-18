import io
from flask import render_template, request, redirect, send_file, url_for, flash
from sqlalchemy import select
from . import patients_bp
from models import db, PatientInfo
from patients.forms import PatientForm

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
    form = PatientForm()
    if form.validate_on_submit():
        try:
            new_patient = PatientInfo(
                    name = form.name.data,
                    age = form.age.data,
                    gender = form.gender.data,
                    email = form.email.data,
                    phone = form.phone.data,
                    location = form.location.data                    
            )
            db.session.add(new_patient)
            db.session.commit()
            flash('Patient details added successfully!', 'success')
            return  redirect(url_for('patients.display_patients'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'error')
            return  redirect(url_for('patients.new_patient'))

    return render_template('create_patient.html', form=form)

@patients_bp.route('/patients/<int:pid>/update', methods=['GET', 'POST'])
def update_patient(pid):
    form = PatientForm()
    if form.validate_on_submit():
        try:
            statement = select(PatientInfo).where(PatientInfo.id == pid)
            patient = db.session.execute(statement).scalars().first()
            patient.name = form.name.data
            patient.age = form.age.data
            patient.gender = form.gender.data
            patient.email = form.email.data
            patient.phone = form.phone.data
            patient.location = form.location.data            
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
    return render_template('create_patient.html', patient=patient, form=form)

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
    
@patients_bp.route('/sync-data')
def sync_data():
    try:
        patients = db.session.execute(select(PatientInfo)).scalars().all()
        data = "\n".join([f"{p.id}\t{p.name}\t{p.age}\t{p.gender}\t{p.email}\t{p.phone}\t{p.location}" for p in patients])
        text_file = io.BytesIO(data.encode('utf-8'))
        text_file.seek(0)
        flash("Patient data synced successfully!", "success")
        return send_file(
            text_file,
            mimetype='text/plain',
            as_attachment=True,
            download_name='patients_data.txt'
        )
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')
        return  redirect(url_for('patients.display_patients'))