from flask import Blueprint, abort

from app.models.committee import Committee

committees_bp = Blueprint("committees", __name__)


@committees_bp.route("/<int:committee_id>")
def detail(committee_id):
    committee = Committee.query.get(committee_id)
    if committee is None:
        abort(404)
    # TODO: render committees/detail.html with member list + statuses
    return {
        "id": committee.id,
        "name": committee.name,
        "frequency": committee.frequency,
        "status": committee.status,
        "total_periods": committee.total_periods,
        "member_count": len(committee.members),
    }
