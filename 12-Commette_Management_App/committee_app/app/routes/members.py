from flask import Blueprint, abort, jsonify

from app.models.member import Member

members_bp = Blueprint("members", __name__)


@members_bp.route("/<int:member_id>")
def detail(member_id):
    member = Member.query.get(member_id)
    if member is None:
        abort(404)

    committee = member.committee
    period_history = [
        {
            "period": p.period_label,
            "amount_cents": p.amount,
            "paid": p.paid,
            "paid_date": p.paid_date.isoformat() if p.paid_date else None,
        }
        for p in sorted(member.payments, key=lambda p: p.period_label)
    ]

    total_contributed = member.total_contributed
    # Contribution share vs the whole committee's total collected so far,
    # for the pie chart on the member page.
    committee_total = sum(
        p.amount for c_member in committee.members for p in c_member.payments if p.paid
    )
    share_pct = round((total_contributed / committee_total) * 100, 1) if committee_total else 0.0

    return jsonify({
        "id": member.id,
        "name": member.name,
        "gender": member.gender,
        "committee_id": committee.id,
        "committee_name": committee.name,
        "has_received_package": member.has_received_package,
        "received_period": member.received_period,
        "total_contributed_cents": total_contributed,
        "contribution_share_pct": share_pct,
        "period_history": period_history,
    })
