# Committee Management App

A web app for running one or more rotating savings committees (ROSCA / kameti
/ bisi). Each committee has a fixed contribution amount that every member
pays every period (weekly or monthly). At the end of each period, one member
receives the full pool collected — chosen outside the app — until everyone in
that committee has received it exactly once.

> **Status:** planning / early scaffold. See `DOCUMENTATION.md` for the full
> client-facing spec (pages, roles, data model, open questions). This README
> is the developer-facing quick start.

## Features

- Multiple committees can run at the same time, each independent
- Each committee is **Weekly** or **Monthly**
- One fixed contribution amount per committee (not per member)
- Public, no-login pages: home (all committees), a committee's detail page,
  and a member's detail page with a contribution pie chart
- Admin-only dashboard: committee cards, an "Explore" screen per committee to
  manage members and mark payment/payout status, and a "Create Committee" form
- Members can only be added/removed before a committee's start date
- Admin login protected by email verification on any new/unrecognized browser

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Flask (application factory pattern) |
| ORM | Flask-SQLAlchemy |
| Forms | Flask-WTF (WTForms + CSRF) |
| Templates | Jinja2 |
| Auth | Flask-Login + Flask-Mail (email verification codes) |
| Database | Turso (libSQL), via `sqlalchemy-libsql` |
| Migrations | Flask-Migrate (Alembic) |
| Hosting | Render (free web service) |

## Project Structure

```
committee_app/
├── app/
│   ├── __init__.py          # app factory
│   ├── extensions.py        # db, login_manager, mail, csrf, migrate
│   ├── models/
│   │   ├── admin.py
│   │   ├── committee.py     # committee-level fixed amount, frequency, status
│   │   ├── member.py
│   │   ├── payment.py
│   │   ├── payout.py
│   │   └── device_token.py  # TrustedDevice + LoginVerification
│   ├── forms/
│   ├── routes/
│   │   ├── main.py          # home
│   │   ├── auth.py          # login, verify, logout
│   │   ├── committees.py    # public committee detail page
│   │   ├── members.py       # public member detail page
│   │   └── dashboard.py     # admin dashboard, explore, create-committee
│   ├── templates/
│   ├── static/
│   └── utils/
│       ├── email.py         # sends verification codes
│       ├── tokens.py        # code generation/hashing
│       └── decorators.py    # admin_required, etc.
├── migrations/
├── config.py
├── run.py
├── requirements.txt
├── .env.example
└── DOCUMENTATION.md
```

## Setup

### 1. Clone and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create a Turso database

```bash
turso db create committee-app
turso db show committee-app --url          # → TURSO_DATABASE_URL
turso db tokens create committee-app       # → TURSO_AUTH_TOKEN
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask session signing key |
| `TURSO_DATABASE_URL` | Turso database hostname |
| `TURSO_AUTH_TOKEN` | Turso auth token |
| `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD` | SMTP for sending login verification codes |
| `ADMIN_EMAIL` | Where verification codes are sent |

Without `TURSO_DATABASE_URL`/`TURSO_AUTH_TOKEN` set, the app falls back to a
local SQLite file (`local_dev.db`) so you can develop offline.

### 4. Initialize the database

```bash
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

### 5. Create the admin account

```bash
flask shell
>>> from app.extensions import db
>>> from app.models.admin import Admin
>>> a = Admin(username="admin", email="you@example.com")
>>> a.set_password("choose-a-strong-password")
>>> db.session.add(a); db.session.commit()
```

### 6. Run the dev server

```bash
flask --app run.py run --debug
```

Visit `http://127.0.0.1:5000`.

## Deployment (Render + Turso)

1. Push this repo to GitHub.
2. Create a Render **Web Service** connected to the repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn run:app`
3. Add all variables from `.env` as Render environment variables (never
   commit `.env`).
4. Deploy. The free web service sleeps after 15 minutes idle — fine for this
   app, since it's only actively used a few days each period. Turso's free
   database does not expire or pause, so data survives the dormant weeks
   with no action needed.

## Key Business Rules (enforced in routes, not just the UI)

- Members can only be added/removed while a committee's `status == "active"`
  **and** its start date hasn't passed yet.
- A member can't be selected for payout twice in the same committee.
- A committee auto-completes once every member's `has_received_package` is
  `True`.
