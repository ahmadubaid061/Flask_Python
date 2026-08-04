# User Profile Management System

A simple Flask mini project where users can sign up, sign in, and view their profile. Built to practice Flask routing, forms, and sessions.

## Features

- Sign up with username, email, password, phone, age, and hobbies
- Sign in with username and password
- View a personalized profile page after logging in
- Log out to end the session
- User data stored in memory (no database)

## Project structure

```
05-flask_mini_Project/
└── User Profile Management System/
    ├── app.py
    ├── templates/
    │   ├── base.html
    │   ├── home.html
    │   ├── sign_in.html
    │   ├── sign_up.html
    │   └── user_profile.html
    └── README.md
```

## How it works

1. **Home page** (`/`) — links to Sign Up and Sign In.
2. **Sign Up** (`/register`) — fills out a form (username, email, password, phone, age, hobbies) and is added to the `users` dictionary, then redirected to Sign In.
3. **Sign In** (`/login`) — checks the entered username/password against `users`. On success, `session['username']` is set to mark this browser as logged in, and the user is redirected to their profile.
4. **Profile** (`/user`) — reads the logged-in username from `session` and looks up that user's full details in `users` to display.
5. **Logout** (`/logout`) — removes `username` from `session`, ending the login, and redirects back to Sign In.

> **Note on sessions:** `session` only stores _who is currently logged in on this browser_ (just the username) — it is not a database. The full user records always live in the `users` dictionary; `session` is just a small pointer into it per visitor.

## Routes

| Route       | Method    | Description                           |
| ----------- | --------- | ------------------------------------- |
| `/`         | GET       | Home page                             |
| `/register` | GET, POST | Show sign-up form / create a new user |
| `/login`    | GET, POST | Show sign-in form / authenticate user |
| `/user`     | GET       | Show the logged-in user's profile     |
| `/logout`   | GET       | Clear session and log out             |

## Tech used

- **Flask** — routing, templating
- **Flask session** — remembers which user is currently logged in across requests, using a signed cookie (`app.secret_key`)
- **Jinja2** — HTML templating with template inheritance (`base.html`)
- **Python dictionary** — in-memory storage standing in for a database

## Running the project

```bash
pip install flask
python app.py
```

Then open `http://127.0.0.1:5000/` in your browser.

## Notes / limitations

- User data is stored in memory only — it resets every time the app restarts.
- Passwords are stored as plain text, which is fine for learning but not safe for a real app.
- Next steps for a production version: use a real database, hash passwords, and add form validation.
