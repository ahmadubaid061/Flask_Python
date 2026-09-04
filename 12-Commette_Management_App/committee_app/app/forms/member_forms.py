from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange


class CommitteeForm(FlaskForm):
    name = StringField("Committee Name", validators=[DataRequired()])
    start_date = DateField("Start Date", validators=[DataRequired()])
    frequency = SelectField(
        "Frequency",
        choices=[("monthly", "Monthly"), ("weekly", "Weekly")],
        validators=[DataRequired()],
    )
    # Entered and stored in whole PKR — no conversion needed.
    contribution_amount = IntegerField(
        "Contribution Amount (per member, per period)",
        validators=[DataRequired(), NumberRange(min=1)],
    )
    target_member_count = IntegerField(
        "Target Member Count (optional \u2014 leave blank to set automatically)",
        validators=[Optional(), NumberRange(min=2)],
    )
    submit = SubmitField("Create Committee")


class RenameCommitteeForm(FlaskForm):
    """Deliberately just the name — start_date, frequency, and
    contribution_amount are left uneditable after creation because changing
    them would silently invalidate every period label and total already
    calculated from them."""
    name = StringField("Committee Name", validators=[DataRequired()])
    submit = SubmitField("Save")


class MemberForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    gender = SelectField(
        "Gender",
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Save Member")