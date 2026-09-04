# --------------------------------------------------------- member details view (PUBLIC - NO LOGIN REQUIRED)

@dashboard_bp.route("/committee/<int:committee_id>/members/<int:member_id>")
def member_details(committee_id, member_id):
    """View detailed information about a specific member (PUBLIC VIEW)."""
    committee = _committee_or_404(committee_id)
    member = _member_or_404(committee, member_id)
    
    # Get all payments for this member
    period_history = Payment.query.filter_by(member_id=member.id).order_by(Payment.period_label.desc()).all()
    
    # Calculate member's total contribution (only paid ones)
    member_total_paid = sum(p.amount for p in period_history if p.paid)
    
    # Get total number of members in committee (at the time of contribution)
    total_members = len(committee.members)
    
    # Calculate expected total for this member
    # Expected = contribution_amount × number_of_cycles
    number_of_cycles = len(period_history)
    expected_total = committee.contribution_amount * number_of_cycles
    
    # Calculate total pool for all members across all cycles
    # Total Pool = contribution_amount × total_members × number_of_cycles
    total_pool = committee.contribution_amount * total_members * number_of_cycles
    
    # Calculate percentage: (member's paid / total pool) × 100
    contribution_percentage = round(
        (member_total_paid / total_pool * 100) if total_pool > 0 else 0
    )
    
    return render_template(
        "members/detail.html",
        committee=committee,
        member=member,
        period_history=period_history,
        total_contributed=member_total_paid,
        share_pct=contribution_percentage,
        expected_total=expected_total,
        total_pool=total_pool,
        number_of_cycles=number_of_cycles,
        total_members=total_members
    )