from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField
from wtforms.validators import DataRequired, Email,Length

class RegistrationForm(FlaskForm):
    name=StringField('Full Name',validators=[DataRequired(message="name cannot be empty!")])
    email=StringField("email ",validators=[DataRequired('Email cannot be empty'),Email("Email should match standard email pattern")])
    password=PasswordField("password",validators=[DataRequired(),Length(min=6)])
    submit=SubmitField("Register")