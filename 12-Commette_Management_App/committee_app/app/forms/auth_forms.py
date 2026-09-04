from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class VerifyCodeForm(FlaskForm):
    code = StringField(
        "6-digit code",
        validators=[DataRequired(), Length(min=6, max=6, message="Enter all 6 digits")],
    )
    submit = SubmitField("Verify")
