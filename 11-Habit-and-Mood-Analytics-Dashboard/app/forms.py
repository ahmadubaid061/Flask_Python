from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError

from app.models import User


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )
    submit = SubmitField('Sign Up')

    # Custom validator: WTForms auto-calls any method named validate_<fieldname>
    def validate_email(self, field):
        existing_user = User.query.filter_by(email=field.data).first()
        if existing_user:
            raise ValidationError('An account with this email already exists.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class DailyLogForm(FlaskForm):
    mood = IntegerField('Mood (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    sleep_hours = FloatField('Sleep (hours)', validators=[DataRequired(), NumberRange(min=0, max=24)])
    water_liters = FloatField('Water (liters)', validators=[DataRequired(), NumberRange(min=0)])
    exercise_minutes = IntegerField('Exercise (minutes)', validators=[DataRequired(), NumberRange(min=0)])
    study_hours = FloatField('Study (hours)', validators=[DataRequired(), NumberRange(min=0, max=24)])
    submit = SubmitField('Save Log')


class HabitForm(FlaskForm):
    name = StringField('Habit name', validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Add Habit')