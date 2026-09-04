from flask import Blueprint, render_template
from app.models.committee import Committee
from app.utils.periods import current_period_label

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    committees = Committee.query.order_by(Committee.created_at.desc()).all()
    return render_template("main/index.html", committees=committees)