from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()  # ✅ Ensure `db` is declared globally

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school_name = db.Column(db.String(150), nullable=True)
    birth_date = db.Column(db.String(10), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)

    # Relationship to sessions
    sessions = db.relationship('Session', backref='student', lazy=True, cascade="all, delete-orphan")


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)  # ✅ Corrected FK
    remark = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, default=datetime.date.today, nullable=False)
    selected = db.Column(db.Boolean, default=False, nullable=False)
