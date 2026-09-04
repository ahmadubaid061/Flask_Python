from flask import Blueprint, render_template, abort

from app.extensions import db
from app.models.committee import Committee
from app.models.payment import Payment
from app.utils.periods import current_period_label

committees_bp = Blueprint("committees", __name__)


@committees_bp.route("/<int:committee_id>")
def detail(committee_id):
    """Public view of a committee with members and their current period payment status."""
    committee = db.session.get(Committee, committee_id)
    if committee is None:
        abort(404)
    
    # Get current period label
    period = current_period_label(committee.frequency)
    
    # Get all members with their payment info for current period
    members_data = []
    for member in committee.members:
        # Get payment for current period
        current_payment = Payment.query.filter_by(
            member_id=member.id, 
            period_label=period
        ).first()
        
        # Get all payments to calculate total
        all_payments = Payment.query.filter_by(member_id=member.id).all()
        total_paid = sum(p.amount for p in all_payments if p.paid)
        
        members_data.append({
            "member": member,
            "current_period_paid": bool(current_payment and current_payment.paid),
            "total_paid": total_paid
        })
    
    return render_template(
        "committees/detail.html",
        committee=committee,
        period=period,
        members_data=members_data
    )