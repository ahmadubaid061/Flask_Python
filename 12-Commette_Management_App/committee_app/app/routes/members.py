from flask import Blueprint, abort

from app.models.member import Member

members_bp = Blueprint("members", __name__)


@members_bp.route("/<int:member_id>")
def detail(member_id):
    member = Member.query.get(member_id)
    if member is None:
        abort(404)
    # TODO: render members/detail.html with per-period history + pie chart
    return {
        "id": member.id,
        "name": member.name,
        "committee_id": member.committee_id,
        "has_received_package": member.has_received_package,
        "total_contributed_cents": member.total_contributed,
    }
