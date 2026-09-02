from flask import Blueprint

from app.models.committee import Committee

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    # Minimal placeholder so you can confirm the DB connection works end to
    # end. This queries Turso through the Committee model — if this runs
    # without error, your connection string and tables are set up correctly.
    committees = Committee.query.all()
    return {
        "status": "ok",
        "committees_found": len(committees),
        "note": "Home page template not built yet — this is a raw JSON check.",
    }
