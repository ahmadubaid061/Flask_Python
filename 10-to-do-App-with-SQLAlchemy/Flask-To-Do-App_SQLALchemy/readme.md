# Flask To-Do App

A simple to-do list web app built with Flask and SQLAlchemy. Users can register, log in, and manage their own personal task list.

**Live demo:** [flask-todo-app-vert.vercel.app](https://flask-todo-app-vert.vercel.app/)

## Features

- User registration and login
- Add, view, and delete tasks
- Toggle task status between Pending → In Process → Completed
- Each user only sees their own tasks

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy
- **Database:** PostgreSQL (hosted on [Neon](https://neon.tech))
- **Deployment:** Vercel
- **Frontend:** HTML, CSS, Jinja2 templates

## Project Structure

```
Flask-To-Do-App_SQLAlchemy/
├── app/
│   ├── routes/
│   │   ├── auth.py          # Login, register, logout routes
│   │   └── tasks.py         # Task CRUD routes
│   ├── static/
│   │   ├── script.js
│   │   └── style.css
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── view_tasks.html
│   ├── __init__.py          # App factory
│   └── models.py            # User and Task models
├── requirements.txt
├── run.py                   # Local development entrypoint
├── wsgi.py                  # Production entrypoint (Vercel)
└── vercel.json
```

## Running Locally

1. Clone the repository and navigate to the project folder.

2. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root:
   ```
   DATABASE_URL=your_postgresql_connection_string
   SECRET_KEY=your_secret_key
   ```

4. Run the app:
   ```bash
   python run.py
   ```

5. Visit `http://localhost:5000` in your browser.

## Deployment

This app is deployed on Vercel using its Python runtime, with a Neon Postgres database (pooled connection) for storage. See `wsgi.py` and `vercel.json` for the production configuration.

## Notes

This is a learning project built to practice Flask, SQLAlchemy, authentication flows, and deployment. It is not intended for production use as-is — for example, passwords are currently stored in plain text rather than hashed.