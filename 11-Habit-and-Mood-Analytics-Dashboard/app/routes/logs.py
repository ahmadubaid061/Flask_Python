from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import DailyLog
from app.forms import DailyLogForm

logs_bp = Blueprint('logs', __name__)


@logs_bp.route('/log', methods=['GET', 'POST'])
@login_required
def log_today():
    today = date.today()

    # Check if today's log already exists -- if so, we're editing it,
    # not creating a new one (this is what the UniqueConstraint protects)
    existing_log = DailyLog.query.filter_by(user_id=current_user.id, log_date=today).first()

    if existing_log:
        # Pre-fill the form with today's existing values, if any
        form = DailyLogForm(obj=existing_log)
    else:
        form = DailyLogForm()

    if form.validate_on_submit():
        if existing_log:
            form.populate_obj(existing_log)
        else:
            new_log = DailyLog(user_id=current_user.id, log_date=today)
            form.populate_obj(new_log)
            db.session.add(new_log)

        db.session.commit()
        flash('Today\'s log saved.')
        return redirect(url_for('dashboard.home'))

    return render_template('log_form.html', form=form, existing_log=existing_log)


@logs_bp.route('/history')
@login_required
def history():
    logs = (DailyLog.query
            .filter_by(user_id=current_user.id)
            .order_by(DailyLog.log_date.desc())
            .all())
    return render_template('history.html', logs=logs)