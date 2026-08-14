from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    # UserMixin gives this class the properties Flask-Login expects
    # (is_authenticated, is_active, get_id, etc.) for free.

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One user -> many daily logs, many habits.
    # cascade='all, delete-orphan' means: if a User is deleted,
    # delete their logs/habits too, instead of leaving orphaned rows.
    daily_logs = db.relationship('DailyLog', backref='user', cascade='all, delete-orphan')
    habits = db.relationship('Habit', backref='user', cascade='all, delete-orphan')

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f'<User {self.email}>'


class DailyLog(db.Model):
    # One row per user per day.
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    log_date = db.Column(db.Date, default=date.today, nullable=False)

    mood = db.Column(db.Integer)              # 1-10
    sleep_hours = db.Column(db.Float)
    water_liters = db.Column(db.Float)
    exercise_minutes = db.Column(db.Integer)
    study_hours = db.Column(db.Float)

    # Enforces: a user can only have ONE log row per date.
    # Prevents accidental duplicate entries for the same day.
    __table_args__ = (
        db.UniqueConstraint('user_id', 'log_date', name='uq_user_date'),
    )

    def __repr__(self):
        return f'<DailyLog {self.user_id} {self.log_date}>'


class Habit(db.Model):
    # A habit the user defines for themselves, e.g. "Meditate", "Read".
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    logs = db.relationship('HabitLog', backref='habit', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Habit {self.name}>'


class HabitLog(db.Model):
    # Whether a specific habit was completed on a specific date.
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    log_date = db.Column(db.Date, default=date.today, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('habit_id', 'log_date', name='uq_habit_date'),
    )

    def __repr__(self):
        return f'<HabitLog {self.habit_id} {self.log_date} {self.completed}>'