from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class AddAdminForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Login Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, message="Use at least 8 characters.")])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Add Admin")


class VerifyCodeForm(FlaskForm):
    code = StringField(
        "6-digit code",
        validators=[DataRequired(), Length(min=6, max=6, message="Enter all 6 digits")],
    )
    submit = SubmitField("Verify")
