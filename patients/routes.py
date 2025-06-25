from datetime import datetime
from flask import jsonify, render_template, request, redirect, url_for, flash
from sqlalchemy import and_, distinct, func, or_, select
from . import patients_bp
from models import db, PatientInfo, Visit
from patients.forms import PatientForm, VisitForm


@patients_bp.route("/", methods=["GET"])
@patients_bp.route("/patients", methods=["GET"])
def display_patients():
    search_term = request.args.get("search")

    page = request.args.get("page", 1, type=int)
    per_page = 10

    statement = select(PatientInfo)

    if search_term:
        terms = [term.strip() for term in search_term.split(",") if term.strip()]

        filters = []
        for term in terms:
            filters.append(
                or_(
                    PatientInfo.phone.ilike(f"%{term}%"),
                    PatientInfo.name.ilike(f"%{term}%")
                )
            )
        statement = statement.where(or_(*filters))

    statement = statement.order_by(PatientInfo.created_at.desc())

    pagination = db.paginate(statement, page=page, per_page=per_page)

    patients = pagination.items
    return render_template(
        "patients.html",
        patients=patients,
        pagination=pagination,
        search_term=search_term,
    )


@patients_bp.route("/patients/autocomplete", methods=["GET"])
def autocomplete_patients():
    term = request.args.get("term", "").strip()

    if not term:
        return jsonify([])

    query = (
        select(PatientInfo.name, PatientInfo.phone)
        .where(
            or_(
                PatientInfo.name.ilike(f"%{term}%"),
                PatientInfo.phone.ilike(f"%{term}%"),
            )
        )
        .limit(10)
    )

    results = db.session.execute(query).all()
    results = [item for result in results for item in result]
    return jsonify(results)


@patients_bp.route("/patients/<int:pid>", methods=["GET"])
def display_patient(pid):
    statement = select(PatientInfo).where(PatientInfo.id == pid)
    patients = db.session.execute(statement).scalars().all()
    return render_template("patients.html", patients=patients)


@patients_bp.route("/patients/new", methods=["GET", "POST"])
def new_patient():
    form = PatientForm()
    if form.validate_on_submit():
        try:
            new_patient = PatientInfo(
                name=form.name.data,
                age=form.age.data,
                gender=form.gender.data,
                email=form.email.data,
                phone=form.phone.data,
                location=form.location.data,
            )
            db.session.add(new_patient)
            db.session.commit()
            flash("Patient details added successfully!", "success")
            return redirect(url_for("patients.display_patients"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("patients.new_patient"))

    return render_template("create_patient.html", form=form)


@patients_bp.route("/patients/<int:pid>/update", methods=["GET", "POST"])
def update_patient(pid):
    patient = db.get_or_404(PatientInfo, pid)
    form = PatientForm(obj=patient)
    if form.validate_on_submit():
        try:
            form.populate_obj(patient)
            db.session.commit()
            flash("Patient details updated successfully!", "success")
            return redirect(url_for("patients.display_patients"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
    return render_template("create_patient.html", patient=patient, form=form)


@patients_bp.route("/patients/<int:pid>/delete", methods=["GET", "POST"])
def delete_patient(pid):
    try:
        patient = db.get_or_404(PatientInfo, pid)

        if request.method == "POST":
            db.session.delete(patient)
            db.session.commit()
            flash(f'Patient "{patient.name}" successfully deleted.', "success")
            return redirect(url_for("patients.display_patients"))

        return render_template("delete_patient_confirmation.html", patient=patient)

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("patients.display_patients"))


@patients_bp.route("/patients/<int:pid>/visits", methods=["GET"])
def display_visits(pid):
    patient = db.get_or_404(PatientInfo, pid)

    page = request.args.get("page", 1, type=int)
    per_page = 10

    statement = (
        select(Visit).where(Visit.patient_id == pid).order_by(Visit.visit_date.desc())
    )
    pagination = db.paginate(statement, page=page, per_page=per_page)
    visits = pagination.items

    return render_template(
        "visits.html", patient=patient, visits=visits, pagination=pagination
    )


@patients_bp.route("/patients/<int:pid>/visits/add", methods=["GET", "POST"])
def add_visit(pid):
    patient = db.get_or_404(PatientInfo, pid)
    form = VisitForm()
    if form.validate_on_submit():
        try:
            new_visit = Visit(
                visit_date = form.visit_date.data,
                symptoms=form.symptoms.data,
                diagnosis=form.diagnosis.data,
                treatment=form.treatment.data,
                notes=form.notes.data,
                patient=patient,
            )
            if isinstance(form.visit_date.data, str):
                new_visit.visit_date = datetime.strptime(form.visit_date.data, "%Y-%m-%dT%H:%M")
            db.session.add(new_visit)
            db.session.commit()
            flash("Visit added successfully!", "success")
            return redirect(url_for("patients.display_visits", pid=pid))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
    return render_template("add_visit.html", patient=patient, form=form)


@patients_bp.route(
    "/patients/<int:pid>/visits/<int:vid>/update", methods=["GET", "POST"]
)
def update_visit(pid, vid):
    patient = db.get_or_404(PatientInfo, pid)
    visit = db.get_or_404(Visit, vid)
    if visit.patient_id != patient.id:
        flash("This visit does not belong to this patient.", "error")
        return redirect(url_for("patients.display_visits", pid=pid))

    form = VisitForm(obj=visit)
    if form.validate_on_submit():
        try:
            form.populate_obj(visit)
            if isinstance(form.visit_date.data, str):
                visit.visit_date = datetime.strptime(form.visit_date.data, "%Y-%m-%dT%H:%M")
            db.session.commit()
            flash("Patient visit details updated successfully!", "success")
            return redirect(url_for("patients.display_visits", pid=pid))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
    return render_template("add_visit.html", patient=patient, visit=visit, form=form)


@patients_bp.route(
    "/patients/<int:pid>/visits/<int:vid>/delete", methods=["GET", "POST"]
)
def delete_visit(pid, vid):

    visit = db.get_or_404(Visit, vid)
    patient = db.get_or_404(PatientInfo, pid)
    if visit.patient_id != patient.id:
        flash("Visit not found for this patient.", "error")
        return redirect(url_for("patients.display_visits", pid=pid))
    if request.method == "POST":
        try:
            db.session.delete(visit)
            db.session.commit()
            flash(
                f'Visit on {visit.visit_date.strftime("%Y-%m-%d %H:%M") if visit.visit_date else "Unknown Date"} successfully deleted.',
                "success",
            )
            return redirect(url_for("patients.display_visits", pid=pid))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while deleting the visit: {str(e)}", "error")
            return redirect(url_for("patients.display_visits", pid=pid))
    else:
        return render_template(
            "delete_visit_confirmation.html", patient=patient, visit=visit
        )


@patients_bp.route("/diagnosis_search", methods=["GET", "POST"])
def diagnosis_search():
    search_term = request.args.get("search")

    page = request.args.get("page", 1, type=int)
    per_page = 10

    statement = select(Visit)

    if search_term:
        terms = [
            term.replace(" ", "").strip()
            for term in search_term.split(",")
            if term.strip()
        ]

        filters = []

        clean_diag = func.replace(Visit.diagnosis, " ", "")

        for term in terms:
            filters.append(
                or_(
                    clean_diag == term,
                    clean_diag.like(f"{term},%"),
                    clean_diag.like(f"%,{term}"),
                    clean_diag.like(f"%,{term},%"),
                )
            )

        statement = statement.where(or_(*filters))

    statement = statement.order_by(Visit.visit_date.desc())

    pagination = db.paginate(statement, page=page, per_page=per_page)

    visits = pagination.items
    return render_template(
        "diagnosis_search.html",
        visits=visits,
        pagination=pagination,
        search_term=search_term,
    )


@patients_bp.route("/diagnosis_search/autocomplete", methods=["GET"])
def autocomplete_diagnosis():
    term = request.args.get("term", "").strip()

    if not term:
        return jsonify([])

    query = (
        select(distinct(Visit.diagnosis))
        .where(Visit.diagnosis.isnot(None), Visit.diagnosis.ilike(f"%{term}%"))
        .limit(10)
    )

    results = db.session.execute(query).scalars().all()
    temp = []
    for result in results:
        if "," in result:
            result = result.split(",")
            for item in result:
                item = item.strip()
                if term.lower() in item.lower():
                    temp.append(item)
        else:
            temp.append(result)
    temp = list(set(temp))
    return jsonify(temp)


@patients_bp.route("/symptoms_search", methods=["GET", "POST"])
def symptoms_search():
    search_term = request.args.get("search")
    page = request.args.get("page", 1, type=int)
    per_page = 10

    statement = select(Visit)

    if search_term:
        terms = [
            term.replace(" ", "").strip().lower()
            for term in search_term.split(",")
            if term.strip()
        ]

        clean_diag = func.lower(func.replace(Visit.symptoms, " ", ""))
        conditions = []

        for term in terms:
            conditions.append(
                or_(
                    clean_diag == term,
                    clean_diag.like(f"{term},%"),
                    clean_diag.like(f"%,{term}"),
                    clean_diag.like(f"%,{term},%"),
                )
            )

        statement = statement.where(and_(*conditions))

    statement = statement.order_by(Visit.visit_date.desc())
    pagination = db.paginate(statement, page=page, per_page=per_page)
    visits = pagination.items

    return render_template(
        "symptoms_search.html",
        visits=visits,
        pagination=pagination,
        search_term=search_term,
    )


@patients_bp.route("/symptoms_search/autocomplete", methods=["GET"])
def autocomplete_symptoms():
    term = request.args.get("term", "").strip()

    if not term:
        return jsonify([])

    query = (
        select(distinct(Visit.symptoms))
        .where(Visit.symptoms.isnot(None), Visit.symptoms.ilike(f"%{term}%"))
        .limit(10)
    )

    results = db.session.execute(query).scalars().all()
    temp = []
    for result in results:
        if "," in result:
            result = result.split(",")
            for item in result:
                item = item.strip()
                if term.lower() in item.lower():
                    temp.append(item)
        else:
            temp.append(result)
    temp = list(set(temp))
    return jsonify(temp)
