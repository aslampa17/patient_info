import csv
from flask import render_template, request, redirect, send_file, url_for, flash
import io
from sqlalchemy import select
from . import patients_bp
from models import db, PatientInfo, Visit
from patients.forms import PatientForm, VisitForm

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
    patient = db.get_or_404(PatientInfo, pid)
    form = PatientForm(obj=patient)
    if form.validate_on_submit():
        try:
            form.populate_obj(patient)       
            db.session.commit()
            flash('Patient details updated successfully!', 'success')
            return  redirect(url_for('patients.display_patients'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'error')
    return render_template('create_patient.html', patient=patient, form=form)

@patients_bp.route('/patients/<int:pid>/delete', methods=['GET', 'POST'])
def delete_patient(pid):
    try:
        patient = db.get_or_404(PatientInfo, pid)

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
        # data = "\n".join([f"{p.id}\t{p.name}\t{p.age}\t{p.gender}\t{p.email}\t{p.phone}\t{p.location}" for p in patients])
        # text_file = io.BytesIO(data.encode('utf-8'))
        # text_file.seek(0)
        # flash("Patient data synced successfully!", "success")
        # return send_file(
        #     text_file,
        #     mimetype='text/plain',
        #     as_attachment=True,
        #     download_name='patients_data.txt'
        # )
        si = io.StringIO()
        mem = io.BytesIO()
        writer = csv.writer(si)
        writer.writerow(["id", "name", "age", "gender", "email", "phone", "location"])
        for p in patients:
            writer.writerow([p.id, p.name, p.age, p.gender, p.email, p.phone, p.location])
        mem.write(si.getvalue().encode('utf-8'))
        mem.seek(0)
        si.close()
        flash("Patient data synced successfully!", "success")
        return send_file(
            mem,
            mimetype='text/csv',
            as_attachment=True,
            download_name='patients_data.csv'
        )
        
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'error')
        return  redirect(url_for('patients.display_patients'))

@patients_bp.route('/patients/<int:pid>/visits', methods=['GET'])
def display_visits(pid):
    patient = db.get_or_404(PatientInfo, pid)
    return render_template('visits.html', patient=patient)

@patients_bp.route('/patients/<int:pid>/visits/add', methods=['GET', 'POST'])
def add_visit(pid):
    patient = db.get_or_404(PatientInfo, pid)
    form = VisitForm()
    if form.validate_on_submit():
        try:
            new_visit = Visit(
                symptoms = form.symptoms.data,
                diagnosis = form.diagnosis.data,
                treatment = form.treatment.data,
                notes = form.notes.data,
                patient = patient
            )
            db.session.add(new_visit)
            db.session.commit()
            flash('Visit added successfully!', 'success')
            return  redirect(url_for('patients.display_visits', pid=pid))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'error')
    return  render_template('add_visit.html', patient=patient, form=form)