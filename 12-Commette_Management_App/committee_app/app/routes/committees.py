from flask import Blueprint, render_template, abort, request

from app.extensions import db
from app.models.committee import Committee
from app.models.payment import Payment
from app.utils.periods import current_period_label, get_available_periods, get_period_summary

committees_bp = Blueprint("committees", __name__)


@committees_bp.route("/<int:committee_id>")
def detail(committee_id):
    """Public view of a committee with members and their current period payment status."""
    committee = db.session.get(Committee, committee_id)
    if committee is None:
        abort(404)
    
    # ✅ Pass committee.start_date to current_period_label
    period = current_period_label(committee.frequency, committee.start_date)
    
    # Get total number of members
    total_members = len(committee.members)
    
    # Get all payments to calculate total pool
    all_payments = Payment.query.filter_by(committee_id=committee.id).all()
    number_of_cycles = len(set(p.period_label for p in all_payments)) if all_payments else 0
    
    # Calculate total pool
    total_pool = committee.contribution_amount * total_members * number_of_cycles if number_of_cycles > 0 else 0
    
    # Get all members with their payment info for current period
    members_data = []
    for member in committee.members:
        # Get payment for current period
        current_payment = Payment.query.filter_by(
            member_id=member.id, 
            period_label=period
        ).first()
        
        # Get all payments to calculate total
        all_member_payments = Payment.query.filter_by(member_id=member.id).all()
        total_paid = sum(p.amount for p in all_member_payments if p.paid)
        
        # Calculate percentage
        share_pct = round(
            (total_paid / total_pool * 100) if total_pool > 0 else 0
        )
        
        members_data.append({
            "member": member,
            "current_period_paid": bool(current_payment and current_payment.paid),
            "total_paid": total_paid,
            "share_pct": share_pct
        })
    
    # --- period history lookup (dropdown of past weeks/months with data) ---
    available_periods = get_available_periods(committee.id)
    selected_period = request.args.get("period")
    period_summary = None
    if selected_period and selected_period in available_periods:
        period_summary = get_period_summary(committee, selected_period)
    
    return render_template(
        "committees/detail.html",
        committee=committee,
        period=period,
        members_data=members_data,
        available_periods=available_periods,
        selected_period=selected_period,
        period_summary=period_summary,
    )