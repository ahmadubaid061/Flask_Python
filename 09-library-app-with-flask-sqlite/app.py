from flask import Flask, render_template, request, redirect, url_for

import database as db

app = Flask(__name__)


# ---------- Routes ----------

@app.route("/")
def index():
    """Read-only view: browse all books, optionally filtered by category."""
    category = request.args.get("category", "")  # "" means no filter, show all
    books = db.get_all_books(category if category else None)
    categories = db.get_categories()
    return render_template(
        "index.html", books=books, categories=categories, selected_category=category
    )


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """CRUD view: add new books, and delete existing ones from a single page."""
    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        category = request.form["category"]
        db.add_book(title, author, category)
        return redirect(url_for("dashboard"))

    books = db.get_all_books()
    return render_template("dashboard.html", books=books)


@app.route("/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    db.delete_book(book_id)
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True)
