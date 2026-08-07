# Flask + SQLite3 Library

A tiny library app built to learn how `sqlite3` works with Flask, using
plain SQL (no ORM like SQLAlchemy) so every database call is visible.

## What it does

- **Home page (`/`)** — read-only: lists all books, with a dropdown to
  filter by category.
- **Dashboard (`/dashboard`)** — CRUD page: a form to add a new book
  (title, author, category), plus the full book list with a Delete
  button per row.
- **`/delete/<id>`** — deletes a book (triggered by a Delete button on
  the dashboard).

## Project structure

```
library_app/
├── app.py                  # Flask app: routes only, no SQL
├── database.py              # All sqlite3 logic lives here
├── requirements.txt
├── templates/
│   ├── index.html            # read-only book list + category filter
│   └── dashboard.html        # add-book form + delete-able book list
└── library.db                # created automatically on first run
```

## How it's organized

- **`database.py`** owns everything database-related:
  - `get_db_connection()` opens a connection and sets
    `conn.row_factory = sqlite3.Row` so columns can be read by name
    (`book["title"]`) instead of by index (`book[0]`).
  - `init_db()` creates the `books` table if it doesn't exist yet, and
    seeds 4 sample books the first time so the list isn't blank.
  - `get_all_books(category=None)` / `get_categories()` handle reads.
  - `add_book(...)` / `delete_book(...)` handle writes.
  - All queries use `?` placeholders with parameters passed as a tuple,
    which avoids building SQL strings by hand — the standard safe
    pattern in sqlite3, even for a learning project.
- **`app.py`** only defines routes and calls into `database.py` — it
  never touches SQL directly. This keeps the "how do I talk to the
  database" logic separate from the "what does each URL do" logic.
- Every database function opens a connection, does its query, and
  closes the connection. There's no connection pooling or app-level
  teardown logic — kept simple on purpose.

## Running it

```bash
cd library_app
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser, and
http://127.0.0.1:5000/dashboard to add or delete books.

The first run seeds 4 sample books (Literature, Science, History) so the
list isn't empty. Delete `library.db` any time to reset the database.

## Ideas to extend later

- Edit an existing book (currently you can only add/delete).
- Search by title/author with `LIKE '%term%'`.
- Move category into its own table with a foreign key, to see how
  joins work in sqlite3.
