# Committee (Kameti/ROSCA) Management App — Documentation

## 1. Overview

A Flask web app for managing a rotating savings committee (kameti/bisi/ROSCA).
Each month every member pays a (possibly different) amount. The full pool
collected that month is handed to one member, chosen outside the app (by the
owner or by vote). Each member can only receive the payout once per cycle.
When everyone has received it, the cycle ends and a new one can start.

**Assumption locked in:** payout for a given month = sum of that month's
collected payments. If this is wrong, only the `Payout.amount` field and the
month-close logic in `routes/dashboard.py` need to change — nothing else in
the schema depends on it.

## 2. Tech Stack

| Layer         | Choice                                      |
| ------------- | ------------------------------------------- |
| Framework     | Flask (app factory pattern)                 |
| ORM           | Flask-SQLAlchemy (SQLAlchemy 2.x)           |
| Forms/CSRF    | Flask-WTF                                   |
| Templates     | Jinja2                                      |
| Auth sessions | Flask-Login                                 |
| Email         | Flask-Mail (SMTP)                           |
| DB            | Turso (libSQL) via `sqlalchemy-libsql`      |
| Migrations    | Flask-Migrate (Alembic)                     |
| Hosting       | Render (free web service) + Turso (free DB) |

## 3. Data Model

### Admin

Single admin account (extendable to more later).
| Field | Type | Notes |
|---|---|---|
| id | int, PK | |
| username | text, unique | |
| email | text, unique | verification codes sent here |
| password_hash | text | never store plaintext |
| created_at | datetime | |

### TrustedDevice

One row per browser the admin has verified. Checked on every login attempt.
| Field | Type | Notes |
|---|---|---|
| id | int, PK | |
| admin_id | FK → Admin | |
| device_token | text, unique | random token, stored in an HttpOnly cookie |
| user_agent | text | shown to admin for reference/audit only |
| created_at | datetime | |
| last_used_at | datetime | |

### LoginVerification

Short-lived email verification codes for new-browser logins.
| Field | Type | Notes |
|---|---|---|
| id | int, PK | |
| admin_id | FK → Admin | |
| code_hash | text | hash of the 6-digit code, not the raw code |
| expires_at | datetime | e.g. now + 10 minutes |
| consumed | bool | one-time use |
| created_at | datetime | |

### Cycle

One full round of the committee, start to finish.
| Field | Type | Notes |
|---|---|---|
| id | int, PK | |
| name | text | e.g. "Family Committee — 2026" |
| status | text | `active` \| `completed` |
| start_date | date | |
| end_date | date | null until completed |
| created_at | datetime | |

### Member

A person participating in a specific cycle. Members are cycle-scoped, so
"restarting" the committee means creating a new Cycle and new Member rows
(optionally copied forward from the previous cycle — see §6).
| Field | Type | Notes |
|---|---|---|
| id | int, PK | |
| cycle_id | FK → Cycle | |
| name | text | |
| gender | text | e.g. `male` / `female` / `other` |
| monthly_amount | numeric (stored as text or integer cents) | this member's fixed monthly contribution for this cycle |
| has_received_package | bool | default false |
| received_month | text, nullable | e.g. `"2026-11"`, set when payout happens |
| joined_at | datetime | |

> Per your requirement "database should only contain text data" — SQLite/Turso
> is dynamically typed, so numeric columns can be stored as TEXT and cast at
> query time if you want to be strict about it. Recommended pragmatic
> approach: store money as **integer cents** (still just digits, no files/
> blobs) to avoid floating point rounding bugs. This is discussed further in
> §7.

### Payment

One row per member per month.
| Field | Type | Notes |
|---|---|---|
| id | int, PK | |
| member_id | FK → Member | |
| cycle_id | FK → Cycle | denormalized for easy monthly queries |
| month | text | `"YYYY-MM"` |
| amount | integer (cents) | usually equals `member.monthly_amount`, but stored per-row so history is accurate even if amounts change later |
| paid | bool | default false |
| paid_date | date, nullable | |

### Payout

One row per month — who received the pool.
| Field | Type | Notes |
|---|---|---|
| id | int, PK | |
| cycle_id | FK → Cycle | |
| member_id | FK → Member | |
| month | text | `"YYYY-MM"` |
| amount | integer (cents) | sum of that month's Payments |
| payout_date | date | |

## 4. Admin Login + New-Browser Email Verification Flow

1. Admin submits username + password on `/auth/login`.
2. If credentials are correct, check for a `committee_trusted_device` cookie.
   - **Cookie present and matches a non-expired `TrustedDevice` row** →
     log the admin in immediately (`Flask-Login`'s `login_user`).
   - **Cookie missing, or doesn't match any `TrustedDevice` row** → this is
     treated as a new browser:
     a. Generate a random 6-digit code, hash it, store a `LoginVerification`
     row with a short expiry (10 min).
     b. Email the plain code to `Admin.email` via Flask-Mail.
     c. Redirect to `/auth/verify` and stash the pending admin id in the
     _server-side session_ (not a cookie the user controls) until verified.
3. On `/auth/verify`, admin enters the 6-digit code.
   - Compare hash, check expiry and `consumed` flag.
   - On success: create a new `TrustedDevice` row, set a long-lived
     (30-day), HttpOnly, Secure, SameSite=Lax cookie holding the device
     token, log the admin in, redirect to dashboard.
   - On failure: show error, allow retry until expiry, offer "resend code".
4. Logging out does **not** delete the `TrustedDevice` row — that's what
   makes it "verify once per browser," not "verify every login." If you
   want stricter behavior (verify every login regardless of device), that's
   a one-line change: skip the cookie check entirely.

This needs no third-party auth provider — just Flask-Mail + a code stored
server-side. Keep `MAIL_USERNAME`/`MAIL_PASSWORD` as an app password if using
Gmail SMTP.

## 5. Pages & Routes

| Route                                            | Access                 | Purpose                                                                                                    |
| ------------------------------------------------ | ---------------------- | ---------------------------------------------------------------------------------------------------------- |
| `/`                                              | Public                 | Home — highlights current month's pool total, who's received so far this cycle                             |
| `/members`                                       | Public                 | List of all members in the active cycle, color-coded: paid this month / not yet / already received package |
| `/members/<member_id>`                           | Public                 | Single member's full history: total contributed, months paid, whether/when they received the package       |
| `/history`                                       | Public                 | Chronological log of payouts and monthly totals, with datetime                                             |
| `/auth/login`                                    | Public                 | Admin login (username+password)                                                                            |
| `/auth/verify`                                   | Public (session-gated) | 6-digit email code entry for new browsers                                                                  |
| `/admin/dashboard`                               | Admin only             | CRUD hub: manage members, enter monthly payments, close a month, start/complete a cycle                    |
| `/admin/members/new`, `/admin/members/<id>/edit` | Admin only             | Add/edit member (add/remove locked after cycle start, per your rule — edit of name/gender always allowed)  |
| `/admin/payments/<month>`                        | Admin only             | Grid: mark which members paid this month + amounts                                                         |
| `/admin/payout/<month>`                          | Admin only             | Record who received the package this month                                                                 |
| `/admin/cycles/new`                              | Admin only             | Start a new cycle (only allowed once current cycle is `completed`)                                         |

## 6. Business Rules Encoded in the Schema

- **Members can only be added/removed while `Cycle.status == 'active'` AND
  no `Payment` rows exist yet for that cycle** (i.e. "only at the start").
  Enforce this in the route, not just the UI.
- **A member can't be selected for payout twice in one cycle** — enforce by
  checking `Member.has_received_package == False` in the payout form's
  member choices.
- **Cycle auto-completes** when every member in it has
  `has_received_package == True` — check this after every payout is recorded,
  and flip `Cycle.status = 'completed'`, `Cycle.end_date = today`.
- **Starting a new cycle**: admin picks "carry forward members" (copies
  names/genders into new Member rows with `has_received_package=False`) or
  "start fresh" (manually re-add). Either way, new `Member` rows are created
  — history from the old cycle stays intact and queryable via `/history`.

## 7. Open Items / Decisions Still Needed From You

1. **Money as integers (cents) vs. plain text strings** — I recommend
   integer cents for correctness (sorting, summing). Confirm this is fine,
   or tell me if you specifically need `TEXT` columns for some other reason.
2. **Carry-forward members on cycle restart** — auto-copy, or always manual
   re-entry?
3. **Gender field values** — free text, or a fixed set (male/female/other)?
4. **Timezone** for `history` timestamps — do you want local time
   (Pakistan, PKT) or UTC stored and localized on display?

## 8. Deployment Notes (Render + Turso)

- Create a Turso database (`turso db create committee-app`), grab
  `TURSO_DATABASE_URL` and `turso db tokens create committee-app`.
- Connection string used by SQLAlchemy (see `config.py`):
  `sqlite+libsql://<hostname>?secure=true` with `auth_token` passed via
  `connect_args`.
- On Render: free web service, add `TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`,
  `SECRET_KEY`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `ADMIN_EMAIL` as
  environment variables (never commit `.env`).
- Free web service sleeps after 15 min idle — fine, since this app is only
  used a few days a month. Turso's free DB does not expire or pause, so data
  survives the dormant weeks with no action needed.
