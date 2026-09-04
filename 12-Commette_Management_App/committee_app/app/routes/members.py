from flask import Blueprint, abort, render_template
from app.models.member import Member

members_bp = Blueprint("members", __name__)


@members_bp.route("/<int:member_id>")
def detail(member_id):
    member = Member.query.get(member_id)
    if member is None:
        abort(404)

    committee = member.committee
    period_history = sorted(member.payments, key=lambda p: p.period_label)

    total_contributed = member.total_contributed
    committee_total = sum(
        p.amount for c_member in committee.members for p in c_member.payments if p.paid
    )
    share_pct = round((total_contributed / committee_total) * 100, 1) if committee_total else 0.0

    return render_template(
        "members/detail.html",
        member=member,
        committee=committee,
        period_history=period_history,
        total_contributed=total_contributed,
        share_pct=share_pct
    )