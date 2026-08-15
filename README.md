# Flask_Python

A Flask learning repo — basics to advanced, with mini projects built along the way as new concepts are learned. Updated continuously.

## What's In Here

The repo is organized as a series of numbered folders, each covering a concept or building on the last:

| Folder                                  | Topic                                                                  |
| --------------------------------------- | ---------------------------------------------------------------------- |
| `00-flask-basic-structure`              | Flask basics — app setup, routes                                       |
| `01-jinja2-templates_in_flask`          | Jinja2 templating                                                      |
| `03-form-handling`                      | Handling HTML forms                                                    |
| `04-implementing_Login`                 | Login implementation                                                   |
| `05-flask_mini_Project`                 | Early mini project                                                     |
| `06-understanding-flash-messages`       | Flash messages                                                         |
| `07-Flask-WTF-Forms`                    | Flask-WTF forms                                                        |
| `08-advanced-flask-app-structure`       | App factory pattern, blueprints, larger app structure                  |
| `09-library-app-with-flask-sqlite`      | Library app — Flask + raw `sqlite3`, no ORM                            |
| `10-to-do-App-with-SQLAlchemy`          | To-Do app — Flask + SQLAlchemy + auth                                  |
| `11-Habit-and-Mood-Analytics-Dashboard` | Habit & Mood Dashboard — full app with auth, Postgres, Pandas insights |

Each project folder has its own README with setup instructions and details specific to that project.

## Featured Projects

### 📚 Library App

A small library catalog app used to learn how `sqlite3` works with Flask using raw SQL — no ORM, so every database call is visible. Add and delete books, filter by category.

- Not deployed — run locally
- [Project README](./09-library-app-with-flask-sqlite/README.md)

### ✅ To-Do App

A personal task manager with per-user accounts. Add, view, and delete tasks, and move them through Pending → In Process → Completed.

- **Live:** [flask-todo-app-vert.vercel.app](https://flask-todo-app-vert.vercel.app/)
- [Project README](./10-to-do-App-with-SQLAlchemy/Flask-To-Do-App_SQLALchemy/README.md)

### 📊 Habit & Mood Dashboard

The most advanced project in the repo — a wellness tracker with email-verified accounts, daily mood/sleep/water/exercise/study logging, custom habit tracking, and a dashboard that surfaces Pandas-generated correlation insights (e.g. "your mood tends to be higher on days you sleep more") once there's enough data.

- **Live:** [mood-and-habits.vercel.app](https://mood-and-habits.vercel.app/)
- [Project README](./11-Habit-and-Mood-Analytics-Dashboard/README.md)

## Progression

Roughly, the repo moves from:

**Flask fundamentals** (routing, templating, forms, flash messages) → **structuring a real app** (blueprints, app factory) → **persistence** (raw SQL, then an ORM) → **full applications** (auth, deployment, external services like email and hosted Postgres, and lightweight data analysis with Pandas).

## Tech Touched Across the Repo

Flask, Jinja2, Flask-WTF / WTForms, Flask-Login, Flask-SQLAlchemy, Flask-Migrate, Flask-Mail, SQLite, PostgreSQL (Neon), Pandas, Chart.js, and deployment on Vercel.
