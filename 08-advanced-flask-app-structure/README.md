# Flask App Structure

A simple, standard layout for a Flask application using the app factory pattern and blueprints.

```
flask_app/
├── run.py                   # Entry point - starts the app
├── requirements.txt         # Python dependencies
├── .env.example              # Sample environment variables
├── .gitignore
└── app/
    ├── __init__.py            # App factory - creates the Flask app
    ├── config.py              # Config classes (dev/prod settings)
    ├── extensions.py          # Shared extension instances (db, login manager, etc.)
    ├── routes/
    │   ├── __init__.py         # Registers blueprints
    │   ├── main.py              # Home / about / contact routes
    │   └── auth.py              # Login / logout / register routes
    ├── models/
    │   └── __init__.py         # Database models (e.g. User)
    ├── templates/
    │   ├── base.html            # Shared layout other pages extend
    │   ├── home.html
    │   ├── about.html
    │   ├── contact.html
    │   ├── errors/
    │   │   ├── 404.html
    │   │   └── 500.html
    │   └── auth/
    │       └── login.html
    └── static/
        ├── css/style.css
        ├── js/script.js
        └── images/
```

## Folder purposes

- **run.py** – the file you run (`python run.py`) to start the server.
- **requirements.txt** – pinned Python packages, installed with `pip install -r requirements.txt`.
- **.env.example** – template for environment variables; copy to `.env` and fill in secrets locally.
- **app/__init__.py** – the app factory function that creates and configures the Flask app, registers blueprints and extensions.
- **app/config.py** – configuration classes for different environments (development, production).
- **app/extensions.py** – instances of Flask extensions (e.g. SQLAlchemy, LoginManager) created once and imported wherever needed, avoiding circular imports.
- **app/routes/** – view functions grouped as blueprints (`main` for general pages, `auth` for authentication).
- **app/models/** – database models, typically using an ORM like SQLAlchemy.
- **app/templates/** – Jinja2 HTML templates, with `base.html` as the shared layout and `errors/` for custom error pages.
- **app/static/** – CSS, JS, and images served directly to the browser.

## Getting started

1. Fill in `app/config.py` and `.env` with your settings.
2. Set up extensions in `app/extensions.py` and initialize them in `app/__init__.py`.
3. Add routes inside `app/routes/` and register them as blueprints.
4. Define your models in `app/models/`.
5. Build out templates and static assets.
6. Run with `python run.py`.
