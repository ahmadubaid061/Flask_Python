from flask import Blueprint, abort, jsonify

from app.models.committee import Committee
from app.models.payment import Payment
from app.utils.periods import current_period_label

committees_bp = Blueprint("committees", __name__)


@committees_bp.route("/<int:committee_id>")
def detail(committee_id):
    committee = Committee.query.get(committee_id)
    if committee is None:
        abort(404)

    period = current_period_label(committee.frequency)

    members_data = []
    for m in committee.members:
        payment = Payment.query.filter_by(member_id=m.id, period_label=period).first()
        if m.has_received_package:
            status = "received_package"
        elif payment and payment.paid:
            status = "paid_this_period"
        else:
            status = "pending_this_period"

        members_data.append({
            "id": m.id,
            "name": m.name,
            "status": status,
        })

    return jsonify({
        "id": committee.id,
        "name": committee.name,
        "frequency": committee.frequency,
        "status": committee.status,
        "current_period": period,
        "total_periods": committee.total_periods,
        "contribution_amount_cents": committee.contribution_amount,
        "members": members_data,
    })
