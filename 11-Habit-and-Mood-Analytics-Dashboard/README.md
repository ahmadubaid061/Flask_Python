# Habit & Mood Dashboard

A simple Flask web app for tracking daily mood, sleep, water intake, exercise, and study time — with lightweight, automatically generated insights into how they relate to each other.

**Live app:** https://mood-and-habits.vercel.app/

## Features

- **Account system** — sign up, email verification (via a time-limited token), log in / log out
- **Daily logging** — log mood (1–10), sleep hours, water intake, exercise minutes, and study hours once per day (resubmitting edits the existing entry instead of creating a duplicate)
- **Habits** — add custom habits, mark them done for the day, delete them
- **Dashboard** — a mood vs. sleep line chart (Chart.js), plus plain-English insights (e.g. "Your mood tends to be higher on days you sleep more") once you have at least 7 days of data, generated with Pandas correlations
- **History** — a full table of every day you've logged

## Tech Stack

| Layer           | Technology                                              |
| --------------- | ------------------------------------------------------- |
| Backend         | Flask, Flask-Login, Flask-Mail, Flask-WTF               |
| Database        | PostgreSQL (Neon), via Flask-SQLAlchemy + Flask-Migrate |
| Data / Insights | Pandas                                                  |
| Frontend        | Jinja2 templates, Bootstrap, Chart.js                   |
| Deployment      | Vercel (serverless, via `wsgi.py`)                      |

## Project Structure

```
app/
├── routes/
│   ├── auth.py         # register, login, logout, email verification
│   ├── dashboard.py     # chart data + correlation insights
│   ├── habits.py        # create/toggle/delete habits
│   ├── logs.py           # daily log form + history
│   └── main.py           # landing page
├── templates/            # Jinja2 templates
├── utils/
│   └── email.py         # verification email + token handling
├── extensions.py        # db, login_manager, mail, migrate
├── forms.py              # WTForms definitions
├── models.py              # User, DailyLog, Habit, HabitLog
└── __init__.py           # app factory
config.py
run.py                     # local dev entry point
wsgi.py                     # Vercel entry point
```

## Running Locally

```bash
python -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create a `.env` file with:

```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
MAIL_SERVER=...
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=...
MAIL_PASSWORD=...
```

Then set up the database and run the app:

```bash
flask db upgrade
python run.py
```

## Deployment

Deployed on Vercel using `wsgi.py` as the entry point, with a Neon Postgres database (pooled connection). Environment variables are set in the Vercel dashboard rather than via `.env`.

## Data Model

- **User** — email, hashed password, verification status
- **DailyLog** — one row per user per day (`UniqueConstraint` on `user_id` + `log_date`), storing mood/sleep/water/exercise/study
- **Habit** — a user-defined habit
- **HabitLog** — one row per habit per day, tracking whether it was completed
