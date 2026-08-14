from datetime import date, timedelta
import pandas as pd
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models import DailyLog

dashboard_bp = Blueprint('dashboard', __name__)

MIN_DAYS_FOR_INSIGHTS = 14  # don't show correlations until there's enough data


@dashboard_bp.route('/dashboard')
@login_required
def home():
    logs = DailyLog.query.filter_by(user_id=current_user.id).order_by(DailyLog.log_date).all()

    # Nothing logged yet -- show an empty state, not a broken chart
    if not logs:
        return render_template('dashboard.html', has_data=False)

    # Convert the SQLAlchemy rows into a DataFrame, same shape as the
    # notebook example -- this is where that earlier exercise pays off
    df = pd.DataFrame([{
        'date': log.log_date.isoformat(),
        'mood': log.mood,
        'sleep_hours': log.sleep_hours,
        'water_liters': log.water_liters,
        'exercise_minutes': log.exercise_minutes,
        'study_hours': log.study_hours,
    } for log in logs])

    chart_data = {
        'dates': df['date'].tolist(),
        'mood': df['mood'].tolist(),
        'sleep_hours': df['sleep_hours'].tolist(),
    }

    insights = []
    if len(df) >= MIN_DAYS_FOR_INSIGHTS:
        corr = df[['mood', 'sleep_hours', 'exercise_minutes', 'water_liters', 'study_hours']].corr()

        sleep_mood_corr = corr.loc['mood', 'sleep_hours']
        if sleep_mood_corr > 0.4:
            insights.append('Your mood tends to be higher on days you sleep more.')
        elif sleep_mood_corr < -0.4:
            insights.append('Your mood tends to be lower on days you sleep more — worth a second look.')

        exercise_mood_corr = corr.loc['mood', 'exercise_minutes']
        if exercise_mood_corr > 0.4:
            insights.append('You tend to feel better on days you exercise.')

    return render_template(
        'dashboard.html',
        has_data=True,
        chart_data=chart_data,
        insights=insights,
        days_logged=len(df),
        min_days=MIN_DAYS_FOR_INSIGHTS,
    )