# Committee Management Web Application

A web-based committee/ROSCA (Rotating Savings and Credit Association) management system. This application allows administrators to manage committee members, track recurring contributions, manage committee cycles, record payments, and monitor payouts.

## Technology Stack

| Layer             | Technology                         | Purpose                                    |
| ----------------- | ---------------------------------- | ------------------------------------------ |
| Backend           | Python + Flask                     | Application logic, routing, authentication |
| ORM / Database    | SQLAlchemy + Turso                 | Models and persistent relational data      |
| Forms             | WTForms / Flask-WTF                | Validation and secure form handling        |
| Frontend          | Jinja2 + HTML/CSS/Bootstrap        | Server-rendered user interface             |
| Authentication    | Flask session + email verification | Login and new-browser verification         |
| Production server | Gunicorn                           | WSGI server on Render                      |
| Hosting           | Render Web Service                 | Deploy and run Flask application           |
| Database hosting  | Turso                              | Persistent remote SQLite/libSQL database   |

## Application Architecture

The project follows a Flask application-factory structure. Extensions are initialized separately, models are grouped by responsibility, routes are separated into blueprints, and utility code handles email and browser/session verification.

**Request Flow:** Browser → Flask route/blueprint → form validation → business logic → SQLAlchemy model → Turso database → Jinja template → Browser.

## Folder Structure

```
your_project/
├── app/
│   ├── __init__.py              # Flask application factory
│   ├── config.py                # Environment-based configuration
│   ├── extensions.py            # SQLAlchemy / Flask-WTF extensions
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # Admin/user account
│   │   ├── committee.py         # Committee configuration
│   │   ├── member.py            # Committee members
│   │   ├── payment.py           # Member payment records
│   │   ├── payout.py            # Payout/turn records
│   │   └── session.py           # Browser verification/session records
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Login, verification, logout
│   │   ├── main.py              # Dashboard/home
│   │   ├── members.py           # Member management
│   │   ├── payments.py          # Payment recording/status
│   │   └── payouts.py           # Payout management
│   ├── forms/
│   │   ├── __init__.py
│   │   ├── login.py
│   │   ├── verify.py
│   │   ├── member.py
│   │   └── payment.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── verify.html
│   │   ├── dashboard.html
│   │   ├── members.html
│   │   ├── payments.html
│   │   └── payouts.html
│   └── utils/
│       ├── __init__.py
│       ├── email.py
│       └── browser.py
├── migrations/                  # Database migration files
├── requirements.txt
├── .env                         # Local secrets; NEVER commit
├── .gitignore
├── run.py                       # Local development entry point
└── README.md
```

## Core Data Models

### Committee

Stores committee-level configuration including name, total members, cycle frequency, start date, current cycle, and status.

### Member

Stores member-specific information such as name, contact details, joining date, position/order, and active status.

### Payment

Stores actual payment events including member_id, committee_id, cycle/period, amount_paid, payment_date, status, and notes.

### Payout

Stores which member receives the committee payout for a particular cycle/turn, the payout date, amount, and status.

### Session / Browser Verification

Stores information required to recognize a previously verified browser/session and support the new-browser email verification workflow.

## Authentication Flow

1. **Login:** Admin enters email and password.
2. **Recognized browser:** If the browser/session is already verified, continue to the dashboard.
3. **New browser:** Generate a short-lived verification code and send it to the registered email.
4. **Verification:** Admin enters the code on the verification page.
5. **Session approval:** Mark the browser/session as verified and allow access.
6. **Logout:** Clear the authentication session.

## Main Application Pages

| Page         | Purpose                                                                    |
| ------------ | -------------------------------------------------------------------------- |
| Login        | Admin authentication                                                       |
| Verification | Enter email verification code for an unrecognized browser                  |
| Dashboard    | Overview of committee status, members, payments, current cycle, and payout |
| Members      | Add, edit, deactivate, and view committee members                          |
| Payments     | View cycles and record/check each member's payment status                  |
| Payouts      | Manage the member receiving the payout for each cycle and payout records   |

## Environment Variables

```env
FLASK_SECRET_KEY=your-secret-key
TURSO_DATABASE_URL=your-turso-database-url
TURSO_AUTH_TOKEN=your-turso-auth-token
MAIL_SERVER=your-smtp-server
MAIL_PORT=587
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=your-email
```

The exact database URI format depends on the selected Turso/SQLAlchemy integration. Keep all credentials in Render Environment Variables in production and in a local `.env` file during development.

## Render Deployment

1. Push the project to GitHub.
2. Create a Render Web Service connected to the repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app` (if the Flask application object is exposed as `app`)
5. Add Turso database URL and authentication token as Render environment variables.
6. Add email/SMTP environment variables if email verification is enabled.
7. Deploy and test login, browser verification, member management, payments, and payouts.

## requirements.txt — Suggested Dependencies

```
Flask
Flask-SQLAlchemy
Flask-WTF
WTForms
python-dotenv
gunicorn
# Add the appropriate Turso/libSQL SQLAlchemy integration
# Add email-related package if required by the chosen mail implementation
```

## Security & Deployment Checklist

- [ ] Never commit `.env` or database authentication tokens.
- [ ] Use a strong Flask `SECRET_KEY` in production.
- [ ] Enable CSRF protection through Flask-WTF.
- [ ] Hash passwords; never store plaintext passwords.
- [ ] Make verification codes short-lived and invalidate them after successful use.
- [ ] Rate-limit or otherwise protect repeated verification-code requests.
- [ ] Use HTTPS in production.
- [ ] Validate authorization on every admin-only route.
- [ ] Use database migrations for schema changes.

## Recommended Development Order

1. Set up Flask application factory and extensions.
2. Configure Turso/SQLAlchemy connection.
3. Create User, Committee, Member, Payment, Payout, and Session models.
4. Implement migrations and initialize the database.
5. Build authentication and new-browser email verification.
6. Build committee and member management.
7. Implement equal-payment cycle logic.
8. Implement payment recording and status tracking.
9. Implement payout management.
10. Build dashboard summaries.
11. Apply UI styling and responsive design.
12. Test locally, deploy to Render, and test production environment variables.

## Design Principle

The committee defines one contribution amount, and every member has the same required contribution for each cycle. The database models the contribution amount at the committee level and uses payment records to track each member's individual payment status.

```

```
