from flask import Blueprint, abort, render_template
from app.models.committee import Committee
from app.utils.periods import current_period_label

committees_bp = Blueprint("committees", __name__)


@committees_bp.route("/<int:committee_id>")
def detail(committee_id):
    committee = Committee.query.get(committee_id)
    if committee is None:
        abort(404)

    period = current_period_label(committee.frequency)
    return render_template("committees/detail.html", committee=committee, period=period)