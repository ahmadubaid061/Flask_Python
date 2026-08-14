from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Habit, HabitLog
from app.forms import HabitForm

habits_bp = Blueprint('habits', __name__)


@habits_bp.route('/habits', methods=['GET', 'POST'])
@login_required
def list_habits():
    form = HabitForm()

    if form.validate_on_submit():
        new_habit = Habit(user_id=current_user.id, name=form.name.data)
        db.session.add(new_habit)
        db.session.commit()
        flash(f'Added habit: {new_habit.name}')
        return redirect(url_for('habits.list_habits'))

    habits = Habit.query.filter_by(user_id=current_user.id).all()

    # For each habit, check whether it's already logged as done today,
    # so the template can show a checked/unchecked state
    today = date.today()
    today_logs = {
        hl.habit_id: hl.completed
        for hl in HabitLog.query.join(Habit).filter(
            Habit.user_id == current_user.id, HabitLog.log_date == today
        ).all()
    }

    return render_template('habits.html', form=form, habits=habits, today_logs=today_logs)


@habits_bp.route('/habits/<int:habit_id>/toggle', methods=['POST'])
@login_required
def toggle_habit(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    today = date.today()

    habit_log = HabitLog.query.filter_by(habit_id=habit.id, log_date=today).first()

    if habit_log:
        habit_log.completed = not habit_log.completed
    else:
        habit_log = HabitLog(habit_id=habit.id, log_date=today, completed=True)
        db.session.add(habit_log)

    db.session.commit()
    return redirect(url_for('habits.list_habits'))


@habits_bp.route('/habits/<int:habit_id>/delete', methods=['POST'])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    db.session.delete(habit)
    db.session.commit()
    flash(f'Deleted habit: {habit.name}')
    return redirect(url_for('habits.list_habits'))