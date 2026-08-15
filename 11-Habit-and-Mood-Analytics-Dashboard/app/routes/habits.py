from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Habit, HabitLog
from app.forms import HabitForm

habits_bp = Blueprint('habits', __name__)


def _compute_streak(completed_dates_desc):
    # completed_dates_desc: dates already sorted newest-first.
    # Counts consecutive days backward from the most recent completion.
    if not completed_dates_desc:
        return 0
    streak = 1
    for i in range(len(completed_dates_desc) - 1):
        if (completed_dates_desc[i] - completed_dates_desc[i + 1]).days == 1:
            streak += 1
        else:
            break
    return streak


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

    # Per-habit current streak, computed the same way as the dashboard's
    # overall streak: consecutive completed days ending at the most
    # recent completion for that specific habit.
    habit_streaks = {}
    for habit in habits:
        completed_dates = [
            hl.log_date for hl in HabitLog.query.filter_by(
                habit_id=habit.id, completed=True
            ).order_by(HabitLog.log_date.desc()).all()
        ]
        habit_streaks[habit.id] = _compute_streak(completed_dates)

    return render_template(
        'habits.html',
        form=form,
        habits=habits,
        today_logs=today_logs,
        habit_streaks=habit_streaks,
    )


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
