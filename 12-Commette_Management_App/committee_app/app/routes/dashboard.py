from datetime import date

from flask import Blueprint, request, abort, render_template, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models.committee import Committee
from app.models.member import Member
from app.models.payment import Payment
from app.models.payout import Payout
from app.forms.member_forms import CommitteeForm, MemberForm
from app.utils.periods import current_period_label

# ✅ ADD THIS LINE - MISSING BLUEPRINT DEFINITION
dashboard_bp = Blueprint("dashboard", __name__)


def _committee_or_404(committee_id):
    committee = db.session.get(Committee, committee_id)
    if committee is None:
        abort(404)
    return committee


def _member_or_404(committee, member_id):
    member = db.session.get(Member, member_id)
    if member is None or member.committee_id != committee.id:
        abort(404)
    return member


# ---------------------------------------------------------------- dashboard

@dashboard_bp.route("/")
@login_required
def index():
    committees = Committee.query.order_by(Committee.created_at.desc()).all()
    return render_template("main/index.html", committees=committees)


# ------------------------------------------------------------ new committee

@dashboard_bp.route("/committee/new", methods=["GET", "POST"])
@login_required
def new_committee():
    form = CommitteeForm()
    if form.validate_on_submit():
        committee = Committee(
            name=form.name.data,
            start_date=form.start_date.data,
            frequency=form.frequency.data,
            contribution_amount=form.contribution_amount.data,
            target_member_count=form.target_member_count.data,
        )
        db.session.add(committee)
        db.session.commit()
        flash("Committee created successfully!", "success")
        return redirect(url_for("dashboard.explore", committee_id=committee.id))

    return render_template("committees/new_committee.html", form=form)


# ----------------------------------------------------------------- explore

@dashboard_bp.route("/committee/<int:committee_id>/explore")
@login_required
def explore(committee_id):
    committee = _committee_or_404(committee_id)
    period = current_period_label(committee.frequency)

    members_data = []
    for m in committee.members:
        payment = Payment.query.filter_by(member_id=m.id, period_label=period).first()
        members_data.append({
            "member": m,
            "current_period_paid": bool(payment and payment.paid),
        })

    return render_template(
        "committees/explore.html",
        committee=committee,
        period=period,
        members_data=members_data,
        member_form=MemberForm()
    )


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
    # This is the user's contribution as a percentage of the total committee contributions
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


# ------------------------------------------------------------- add member

@dashboard_bp.route("/committee/<int:committee_id>/members/new", methods=["POST"])
@login_required
def add_member(committee_id):
    committee = _committee_or_404(committee_id)

    form = MemberForm()
    if form.validate_on_submit():
        member = Member(committee_id=committee.id, name=form.name.data, gender=form.gender.data)
        db.session.add(member)
        db.session.commit()
        flash("Member added successfully!", "success")
    else:
        flash("Error adding member. Please check the input.", "danger")

    return redirect(url_for("dashboard.explore", committee_id=committee.id))


# ------------------------------------------------------------- edit member

@dashboard_bp.route("/committee/<int:committee_id>/members/<int:member_id>/edit", methods=["POST"])
@login_required
def edit_member(committee_id, member_id):
    committee = _committee_or_404(committee_id)
    member = _member_or_404(committee, member_id)

    form = MemberForm()
    if form.validate_on_submit():
        member.name = form.name.data
        member.gender = form.gender.data
        db.session.commit()
        flash("Member updated successfully!", "success")
    else:
        flash("Error updating member.", "danger")

    return redirect(url_for("dashboard.explore", committee_id=committee.id))


# ----------------------------------------------------------- remove member

@dashboard_bp.route("/committee/<int:committee_id>/members/<int:member_id>/remove", methods=["POST"])
@login_required
def remove_member(committee_id, member_id):
    committee = _committee_or_404(committee_id)
    member = _member_or_404(committee, member_id)

    db.session.delete(member)
    db.session.commit()
    flash("Member removed.", "info")
    return redirect(url_for("dashboard.explore", committee_id=committee.id))


# ---------------------------------------------------------------- payment

@dashboard_bp.route("/committee/<int:committee_id>/members/<int:member_id>/pay", methods=["POST"])
@login_required
def mark_payment(committee_id, member_id):
    committee = _committee_or_404(committee_id)
    member = _member_or_404(committee, member_id)
    period = current_period_label(committee.frequency)

    paid = request.form.get("paid", "true").lower() != "false"

    payment = Payment.query.filter_by(member_id=member.id, period_label=period).first()
    if payment is None:
        payment = Payment(
            member_id=member.id,
            committee_id=committee.id,
            period_label=period,
            amount=committee.contribution_amount,
        )
        db.session.add(payment)

    payment.paid = paid
    payment.paid_date = date.today() if paid else None
    db.session.commit()

    flash(f"Payment status updated for {member.name}.", "success")
    return redirect(url_for("dashboard.explore", committee_id=committee.id))


# ----------------------------------------------------------------- payout

@dashboard_bp.route("/committee/<int:committee_id>/payout", methods=["POST"])
@login_required
def record_payout(committee_id):
    committee = _committee_or_404(committee_id)
    member_id = request.form.get("member_id", type=int)
    member = _member_or_404(committee, member_id) if member_id else None

    if member is None:
        flash("Member ID is required for payout.", "danger")
        return redirect(url_for("dashboard.explore", committee_id=committee.id))

    if member.has_received_package:
        flash("This member has already received the payout in this committee.", "warning")
        return redirect(url_for("dashboard.explore", committee_id=committee.id))

    period = current_period_label(committee.frequency)

    existing = Payout.query.filter_by(committee_id=committee.id, period_label=period).first()
    if existing:
        flash(f"A payout for {period} has already been recorded.", "warning")
        return redirect(url_for("dashboard.explore", committee_id=committee.id))

    period_total = (
        db.session.query(db.func.coalesce(db.func.sum(Payment.amount), 0))
        .filter_by(committee_id=committee.id, period_label=period, paid=True)
        .scalar()
    )

    payout = Payout(
        committee_id=committee.id,
        member_id=member.id,
        period_label=period,
        amount=period_total,
        payout_date=date.today(),
    )
    db.session.add(payout)

    member.has_received_package = True
    member.received_period = period

    if all(m.has_received_package for m in committee.members):
        committee.status = "completed"

    db.session.commit()
    flash(f"Payout successfully recorded for {member.name}!", "success")
    return redirect(url_for("dashboard.explore", committee_id=committee.id))


# ----------------------------------------------------------- delete committee

@dashboard_bp.route("/committee/<int:committee_id>/delete", methods=["POST"])
@login_required
def delete_committee(committee_id):
    """Delete a committee and all associated data."""
    committee = _committee_or_404(committee_id)
    
    # Delete the committee (cascade will delete members, payments, payouts)
    db.session.delete(committee)
    db.session.commit()
    
    flash(f"Committee '{committee.name}' has been deleted.", "info")
    return redirect(url_for("dashboard.index"))