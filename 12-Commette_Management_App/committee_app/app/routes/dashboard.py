from datetime import date

from flask import Blueprint, request, abort, render_template, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models.committee import Committee
from app.models.member import Member
from app.models.payment import Payment
from app.models.payout import Payout
from app.forms.member_forms import CommitteeForm, MemberForm, RenameCommitteeForm
from app.utils.periods import current_period_label, get_available_periods, get_period_summary, generate_elapsed_periods

# ✅ BLUEPRINT DEFINITION
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


# ------------------------------------------------------------- rename committee

@dashboard_bp.route("/committee/<int:committee_id>/rename", methods=["POST"])
@login_required
def rename_committee(committee_id):
    """Only the name is editable after creation — start_date, frequency,
    and contribution_amount are left alone deliberately, since changing
    them after payments/payouts have been recorded would invalidate all
    the period math already tied to the original values."""
    committee = _committee_or_404(committee_id)

    form = RenameCommitteeForm()
    if form.validate_on_submit():
        committee.name = form.name.data
        db.session.commit()
        flash("Committee name updated.", "success")
    else:
        flash("Please enter a valid name.", "danger")

    return redirect(url_for("dashboard.explore", committee_id=committee.id))


# ------------------------------------------------------------- new committee

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
    period = current_period_label(committee.frequency, committee.start_date)

    members_data = []
    for m in committee.members:
        payment = Payment.query.filter_by(member_id=m.id, period_label=period).first()
        members_data.append({
            "member": m,
            "current_period_paid": bool(payment and payment.paid),
        })

    # Has a payout already been recorded for the current live period? Used to
    # hide/disable the "Record payout" form once one member has been paid for
    # this period, instead of just relying on the record_payout route to
    # reject it after the fact.
    current_period_payout = Payout.query.filter_by(
        committee_id=committee.id, period_label=period
    ).first()

    return render_template(
        "committees/explore.html",
        committee=committee,
        period=period,
        members_data=members_data,
        member_form=MemberForm(),
        rename_form=RenameCommitteeForm(obj=committee),
        current_period_payout=current_period_payout,
    )


# ------------------------------------------------------------ period history

@dashboard_bp.route("/committee/<int:committee_id>/history")
@login_required
def period_history(committee_id):
    """Standalone page for browsing a past period's payments/payout, kept
    separate from explore() so the live current-period panel never sits
    above a historical period the admin just searched for — that layout on
    the old combined page was the source of the 'which week am I even
    looking at' confusion."""
    committee = _committee_or_404(committee_id)

    available_periods = get_available_periods(committee)
    selected_period = request.args.get("period")
    if not selected_period and available_periods:
        selected_period = available_periods[0]

    period_summary = None
    if selected_period and selected_period in available_periods:
        period_summary = get_period_summary(committee, selected_period)

    return render_template(
        "committees/period_history.html",
        committee=committee,
        member_form=MemberForm(),
        available_periods=available_periods,
        selected_period=selected_period,
        period_summary=period_summary,
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
    
    # Get total number of members in committee
    total_members = len(committee.members)
    
    # Calculate expected total for this member
    number_of_cycles = len(period_history)
    expected_total = committee.contribution_amount * number_of_cycles
    
    # Calculate total pool for all members across all cycles
    total_pool = committee.contribution_amount * total_members * number_of_cycles
    
    # Calculate percentage
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

    # If a period_label is passed explicitly (e.g. from the Period History
    # panel, used to backfill a past week), act on that period instead of
    # today's live one. This is what lets an admin fill in W1-W4 for a
    # committee that was backdated when it was added to the app.
    period = request.form.get("period_label") or current_period_label(
        committee.frequency, committee.start_date
    )

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

    flash(f"Payment status updated for {member.name} ({period}).", "success")

    redirect_kwargs = {"committee_id": committee.id}
    if request.form.get("period_label"):
        redirect_kwargs["period"] = period
    return redirect(url_for("dashboard.explore", **redirect_kwargs))


# ----------------------------------------------------------------- payout

@dashboard_bp.route("/committee/<int:committee_id>/payout", methods=["POST"])
@login_required
def record_payout(committee_id):
    """Record payout to a member - flexible logic with deadline check."""
    committee = _committee_or_404(committee_id)
    member_id = request.form.get("member_id", type=int)
    member = _member_or_404(committee, member_id) if member_id else None

    if member is None:
        flash("Member ID is required for payout.", "danger")
        return redirect(url_for("dashboard.explore", committee_id=committee.id))

    # Same idea as mark_payment: an explicit period_label (from the Period
    # History panel) lets the admin backfill a payout for a past period,
    # e.g. one that happened offline before the committee was added here.
    # It's treated exactly like a live payout — same checks, same effect
    # on cycle tracking below — so the rotation stays accurate afterward.
    period = request.form.get("period_label") or current_period_label(
        committee.frequency, committee.start_date
    )

    # ✅ CHECK 1: Member hasn't received payout in this cycle
    if member.has_received_package:
        flash("This member has already received the payout in this cycle.", "warning")
        return redirect(url_for("dashboard.explore", committee_id=committee.id))

    # ✅ CHECK 1b: No one else has already received the payout for THIS period.
    # This is the rule that was missing — without it, every member whose own
    # has_received_package is still False (i.e. everyone except whoever just
    # got paid) remains selectable, so a second, third, etc. member could be
    # paid out for the same week/month. Only one payout is allowed per period.
    existing_payout_for_period = Payout.query.filter_by(
        committee_id=committee.id, period_label=period
    ).first()
    if existing_payout_for_period:
        existing_member = db.session.get(Member, existing_payout_for_period.member_id)
        existing_name = existing_member.name if existing_member else "another member"
        flash(
            f"A payout for {period} has already been recorded ({existing_name}). "
            f"Only one member can receive the payout per period.",
            "warning",
        )
        return redirect(url_for("dashboard.explore", committee_id=committee.id))

    # ✅ CHECK 2: Calculate how many members have paid
    total_members = len(committee.members)
    paid_members = 0
    
    for m in committee.members:
        payment = Payment.query.filter_by(
            member_id=m.id, 
            period_label=period
        ).first()
        if payment and payment.paid:
            paid_members += 1
    
    # ✅ CHECK 3: Decide if payout can proceed
    can_payout = False
    payout_reason = ""
    
    if paid_members == total_members:
        # All have paid - full amount available
        can_payout = True
        payout_reason = "✓ All members have paid"
    elif paid_members > 0:
        # Some have paid - partial payout allowed
        # Warning: Not all members paid
        flash(
            f"⚠️ Only {paid_members}/{total_members} members have paid. "
            f"Proceeding with partial payout of collected amount.",
            "warning"
        )
        can_payout = True
        payout_reason = f"Partial - {paid_members}/{total_members} paid"
    else:
        # Nobody paid - cannot proceed
        flash(
            f"❌ No members have paid for {period} yet. "
            f"Cannot proceed with payout.",
            "error"
        )
        return redirect(url_for("dashboard.explore", committee_id=committee.id))

    if not can_payout:
        return redirect(url_for("dashboard.explore", committee_id=committee.id))

    # ✅ Calculate total available for payout (all paid amounts for this period)
    period_total = (
        db.session.query(db.func.coalesce(db.func.sum(Payment.amount), 0))
        .filter_by(committee_id=committee.id, period_label=period, paid=True)
        .scalar()
    )

    # ✅ Create payout record
    payout = Payout(
        committee_id=committee.id,
        member_id=member.id,
        period_label=period,
        amount=period_total,
        payout_date=date.today(),
        payout_cycle=member.payout_cycle
    )
    db.session.add(payout)

    # ✅ Mark member as received
    member.has_received_package = True
    member.received_period = period

    db.session.commit()

    flash(f"✓ Payout of Rs. {period_total:,.0f} recorded for {member.name} ({period})! ({payout_reason})", "success")

    # ✅ CHECK 4: If all members have received payout, reset for next cycle
    #
    # BUGFIX: this used to check `all(m.has_received_package for m in
    # committee.members)` on its own. That only looks at whoever currently
    # exists in the committee — if the committee is meant to eventually hold
    # more members than have been added so far, every existing member could
    # receive a payout and trigger a "full cycle" reset early. Anyone already
    # paid in that short cycle then looks eligible again immediately, even
    # though members intended for the rotation haven't received anything
    # yet. Requiring the live member count to reach target_member_count
    # (falling back to the live count when no target was set) closes that.
    required_members = committee.target_member_count or total_members
    all_received = (
        total_members > 0
        and total_members >= required_members
        and all(m.has_received_package for m in committee.members)
    )
    
    if all_received:
        # Reset all members for next cycle
        for m in committee.members:
            m.has_received_package = False
            m.payout_cycle += 1
            m.received_period = None
        
        db.session.commit()
        flash(f"🔄 All members have received their payout! System reset for next cycle.", "info")

    redirect_kwargs = {"committee_id": committee.id}
    if request.form.get("period_label"):
        redirect_kwargs["period"] = period
    return redirect(url_for("dashboard.explore", **redirect_kwargs))
# ----------------------------------------------------------- reset payout (undo)

@dashboard_bp.route("/committee/<int:committee_id>/members/<int:member_id>/reset-payout", methods=["POST"])
@login_required
def reset_member_payout(committee_id, member_id):
    """Reset a member's payout status back to pending."""
    committee = _committee_or_404(committee_id)
    member = _member_or_404(committee, member_id)

    if not member.has_received_package:
        flash(f"{member.name} hasn't received a payout yet.", "warning")
        return redirect(url_for("dashboard.explore", committee_id=committee.id))

    # Delete the payout record
    period = member.received_period
    payout = Payout.query.filter_by(
        committee_id=committee.id,
        member_id=member.id,
        period_label=period
    ).first()

    if payout:
        db.session.delete(payout)

    # Reset member status
    member.has_received_package = False
    member.received_period = None

    db.session.commit()

    flash(f"Payout for {member.name} has been reset to pending. They can receive payout again.", "info")
    return redirect(url_for("dashboard.explore", committee_id=committee.id))


# ----------------------------------------------------------- delete committee

@dashboard_bp.route("/committee/<int:committee_id>/delete", methods=["POST"])
@login_required
def delete_committee(committee_id):
    """Delete a committee and all associated data."""
    committee = _committee_or_404(committee_id)
    
    db.session.delete(committee)
    db.session.commit()
    
    flash(f"Committee '{committee.name}' has been deleted.", "info")
    return redirect(url_for("dashboard.index"))

# ----------------------------------------------------------- catch up payments

@dashboard_bp.route("/committee/<int:committee_id>/members/<int:member_id>/catchup", methods=["GET", "POST"])
@login_required
def member_catchup(committee_id, member_id):
    """Allow member to pay for past weeks they missed."""
    committee = _committee_or_404(committee_id)
    member = _member_or_404(committee, member_id)

    # Every period the committee has reached so far (e.g. W1..W5), regardless
    # of whether a Payment row exists yet for any of them.
    elapsed_periods = generate_elapsed_periods(committee.frequency, committee.start_date)

    # Payment rows that DO exist for this member, keyed by period label.
    existing_payments = {
        p.period_label: p
        for p in Payment.query.filter_by(member_id=member.id).all()
    }

    if request.method == "POST":
        period_label = request.form.get("period_label")

        payment = existing_payments.get(period_label)
        if payment:
            payment.paid = True
            payment.paid_date = date.today()
        else:
            # No row ever existed for this period (member missed it entirely) —
            # create it now as paid.
            payment = Payment(
                member_id=member.id,
                committee_id=committee.id,
                period_label=period_label,
                amount=committee.contribution_amount,
                paid=True,
                paid_date=date.today(),
            )
            db.session.add(payment)

        db.session.commit()
        flash(f"Payment for {period_label} marked as paid.", "success")
        return redirect(url_for("dashboard.member_catchup", committee_id=committee.id, member_id=member.id))

    # An elapsed period counts as unpaid if there's no row for it at all,
    # or there's a row but it's marked paid=False.
    unpaid_payments = []
    for label in elapsed_periods:
        payment = existing_payments.get(label)
        if payment is None or not payment.paid:
            unpaid_payments.append({
                "period_label": label,
                "amount": payment.amount if payment else committee.contribution_amount,
            })

    return render_template(
        "members/catchup.html",
        committee=committee,
        member=member,
        unpaid_payments=unpaid_payments
    )