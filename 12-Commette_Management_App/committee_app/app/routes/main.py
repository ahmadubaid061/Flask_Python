from flask import Blueprint, jsonify

from app.models.committee import Committee
from app.utils.periods import current_period_label

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    committees = Committee.query.order_by(Committee.created_at.desc()).all()

    data = []
    for c in committees:
        period = current_period_label(c.frequency)
        received_so_far = [
            {"member_id": m.id, "name": m.name, "received_period": m.received_period}
            for m in c.members
            if m.has_received_package
        ]
        data.append({
            "id": c.id,
            "name": c.name,
            "frequency": c.frequency,
            "status": c.status,
            "current_period": period,
            "member_count": len(c.members),
            "total_periods": c.total_periods,
            "members_received": received_so_far,
        })

    return jsonify({"committees": data})
