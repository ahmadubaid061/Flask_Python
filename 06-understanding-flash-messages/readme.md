# Flask Flash Messages - Mini Project

A simple feedback form built with Flask to demonstrate how **flash messages** work.

## What are Flash Messages?

Flash messages are short, one-time messages you can send to the user after an action (like submitting a form). They're commonly used for things like:

- "Login successful!"
- "Name cannot be empty"
- "Your feedback has been saved!"

The message is stored temporarily, shown once on the next page load, and then automatically removed.

## How They Work

1. **Flask stores the message** — using `flash("your message")` in a route.
2. **A secret key is required** — flash messages use sessions to store data, so `app.secret_key` must be set.
3. **The template displays it** — using `get_flashed_messages()` in Jinja2.
4. **It disappears after showing once** — the message is removed from the session as soon as it's displayed.

## In This Project

- **`App.py`** — handles the form submission. If the name or email field is empty, a flash message is triggered and the user is redirected back to the form.
- **`base.html`** — the shared layout. It contains the sidebar block that loops through and displays any flashed messages using `get_flashed_messages()`.
- **`form.html`** — the feedback form (name, email, message).
- **`welcome.html`** — the page shown after successful submission.

## How to Run

```bash
pip install flask
python App.py
```

Then open `http://127.0.0.1:5000/` in your browser.

## Try It Out

- Submit the form with an empty **name** or **email** → see a flash message appear.
- Submit the form correctly → see success flash messages, then land on the welcome page.