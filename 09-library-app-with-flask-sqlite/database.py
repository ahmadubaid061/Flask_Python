import sqlite3

DATABASE = "library.db"


# ---------- Connection ----------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, e.g. row["title"]
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL
        )
    """)

    # Add a few sample books only if the table is empty, so the app isn't blank on first run
    count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    if count == 0:
        sample_books = [
            ("Pride and Prejudice", "Jane Austen", "Literature"),
            ("A Brief History of Time", "Stephen Hawking", "Science"),
            ("Sapiens", "Yuval Noah Harari", "History"),
            ("1984", "George Orwell", "Literature"),
        ]
        conn.executemany(
            "INSERT INTO books (title, author, category) VALUES (?, ?, ?)",
            sample_books,
        )
        conn.commit()

    conn.close()


# ---------- Reads ----------

def get_all_books(category=None):
    """Return all books, optionally filtered by category."""
    conn = get_db_connection()
    if category:
        books = conn.execute(
            "SELECT * FROM books WHERE category = ? ORDER BY title", (category,)
        ).fetchall()
    else:
        books = conn.execute("SELECT * FROM books ORDER BY title").fetchall()
    conn.close()
    return books


def get_categories():
    """Return the distinct categories currently in use, for filter dropdowns."""
    conn = get_db_connection()
    categories = conn.execute(
        "SELECT DISTINCT category FROM books ORDER BY category"
    ).fetchall()
    conn.close()
    return categories


# ---------- Writes ----------

def add_book(title, author, category):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO books (title, author, category) VALUES (?, ?, ?)",
        (title, author, category),
    )
    conn.commit()
    conn.close()


def delete_book(book_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
