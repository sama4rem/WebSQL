# -*- coding: utf-8 -*-
import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import SQLAlchemyError
from .models import db, Student, Session

app_routes = Blueprint('app_routes', __name__)

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)


@app_routes.route('/')
def home():
    return redirect(url_for('app_routes.students'))


@app_routes.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        name = request.form.get('name', "").strip()
        if not name:
            flash("Le nom de l'élève est obligatoire.", "error")
            return redirect(url_for('app_routes.students'))

        new_student = Student(name=name)
        try:
            db.session.add(new_student)
            db.session.commit()
            flash("Élève ajouté avec succès.", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout de l'élève : {str(e)}", "error")

        return redirect(url_for('app_routes.students'))

    students = Student.query.all()
    return render_template('students.html', students=students)


@app_routes.route('/remarks/<int:student_id>', methods=['GET', 'POST'])
def remarks(student_id):
    student = Student.query.get(student_id)

    if not student:
        logging.error(f"Élève ID {student_id} introuvable.")
        flash("Élève introuvable.", "error")
        return redirect(url_for('app_routes.students'))

    if request.method == 'POST':
        remark = request.form.get('remark', "").strip()
        logging.debug(f"Tentative d'ajout de séance pour l'élève ID {student_id} avec la remarque : '{remark}'")

        if remark:
            new_session = Session(student_id=student.id, remark=remark, selected=False)
            try:
                db.session.add(new_session)
                db.session.commit()
                logging.info(f"Séance ajoutée avec succès pour l'élève ID {student_id}")
                flash("Séance ajoutée avec succès.", "success")
            except SQLAlchemyError as e:
                db.session.rollback()
                logging.error(f"Erreur lors de l'ajout de la séance : {e}")
                flash(f"Erreur lors de l'ajout de la séance : {e}", "error")
        else:
            logging.warning("Remarque vide soumise.")
            flash("La remarque ne peut pas être vide.", "error")

        return redirect(url_for('app_routes.remarks', student_id=student.id))

    student_sessions = Session.query.filter_by(student_id=student_id).order_by(Session.selected.asc(), Session.id.desc()).all()
    selected_sessions = {s.id for s in student_sessions if s.selected}
    unrecorded_count = sum(1 for s in student_sessions if not s.selected)

    return render_template(
        "remarks.html",
        student_id=student.id,
        student_name=student.name,
        student_school=student.school_name or "",
        student_birth_date=student.birth_date or "",
        student_phone_number=student.phone_number or "",
        sessions=student_sessions,
        selected_sessions=selected_sessions,
        unrecorded_count=unrecorded_count,
    )


@app_routes.route('/update_info/<int:student_id>', methods=['POST'])
def update_info(student_id):
    student = Student.query.get(student_id)
    if not student:
        flash("Élève introuvable.", "error")
        return redirect(url_for('app_routes.students'))

    try:
        student.school_name = request.form.get('school_name', "").strip()
        student.birth_date = request.form.get('birth_date', "").strip()
        student.phone_number = request.form.get('phone_number', "").strip()

        db.session.commit()
        flash("Les informations de l'élève ont été mises à jour avec succès.", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Erreur lors de la mise à jour des informations : {str(e)}", "error")

    return redirect(url_for('app_routes.remarks', student_id=student_id))


@app_routes.route('/save_selection/<int:student_id>', methods=['POST'])
def save_selection(student_id):
    try:
        selected_sessions = request.form.getlist('selected_sessions')
        selected_sessions = list(map(int, selected_sessions))

        # Fetch all sessions for this student in the correct order
        student_sessions = Session.query.filter_by(student_id=student_id).order_by(Session.id.asc()).all()

        # Update the selected status while maintaining order
        for session in student_sessions:
            session.selected = session.id in selected_sessions

        db.session.commit()
        flash("Les sélections ont été sauvegardées avec succès.", "success")
        return '', 200  # Return success response

    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Erreur lors de la sauvegarde des sélections : {str(e)}", "error")
        return "Une erreur s'est produite lors de la sauvegarde.", 500


@app_routes.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        try:
            # Delete all associated sessions first
            Session.query.filter_by(student_id=student_id).delete()
            db.session.delete(student)
            db.session.commit()
            flash("Élève et séances associées supprimés avec succès.", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Erreur lors de la suppression de l'élève : {str(e)}", "error")

    return redirect(url_for('app_routes.students'))
@app_routes.route('/edit_remark/<int:student_id>/<int:session_id>', methods=['POST'])
def edit_remark(student_id, session_id):
    session_to_edit = Session.query.get(session_id)

    if session_to_edit:
        new_remark = request.form.get('remark', "").strip()
        if new_remark:
            try:
                session_to_edit.remark = new_remark
                db.session.commit()
                flash("La remarque a été mise à jour avec succès.", "success")
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f"Erreur lors de la modification de la remarque : {str(e)}", "error")
        else:
            flash("La remarque ne peut pas être vide.", "error")

    return redirect(url_for('app_routes.remarks', student_id=student_id))
@app_routes.route('/delete_remark/<int:student_id>/<int:session_id>', methods=['POST'])
def delete_remark(student_id, session_id):
    session_to_delete = Session.query.get(session_id)
    if session_to_delete:
        try:
            db.session.delete(session_to_delete)
            db.session.commit()
            flash("Remarque supprimée avec succès.", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Erreur lors de la suppression de la remarque : {str(e)}", "error")

    return redirect(url_for('app_routes.remarks', student_id=student_id))
