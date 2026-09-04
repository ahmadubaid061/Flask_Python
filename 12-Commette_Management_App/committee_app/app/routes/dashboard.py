from datetime import date

from flask import Blueprint, request, abort, jsonify
from flask_login import login_required

from app.extensions import db, csrf
from app.models.committee import Committee
from app.models.member import Member
from app.models.payment import Payment
from app.models.payout import Payout
from app.forms.member_forms import CommitteeForm, MemberForm
from app.utils.periods import current_period_label

dashboard_bp = Blueprint("dashboard", __name__)

# TEMPORARY: exempted from CSRF because there are no templates yet to embed
# a real {{ form.hidden_tag() }} token. Once the admin templates (explore,
# create-committee, etc.) exist and post through real <form> tags, remove
# this line so CSRF protection applies here like it already does on
# app/routes/auth.py.
# csrf.exempt(dashboard_bp)


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
    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "frequency": c.frequency,
            "status": c.status,
            "member_count": len(c.members),
            "total_periods": c.total_periods,
        }
        for c in committees
    ])


# ------------------------------------------------------------ new committee

@dashboard_bp.route("/committee/new", methods=["GET", "POST"])
@login_required
def new_committee():
    form = CommitteeForm(meta={"csrf": False})  # CSRF re-enabled once templates post real forms
    if form.validate_on_submit():
        committee = Committee(
            name=form.name.data,
            start_date=form.start_date.data,
            frequency=form.frequency.data,
            contribution_amount=int(form.contribution_amount.data) * 100,  # store as cents
            target_member_count=form.target_member_count.data,
        )
        db.session.add(committee)
        db.session.commit()
        return jsonify({"status": "created", "committee_id": committee.id}), 201

    return jsonify({"status": "invalid", "errors": form.errors}), 400


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
            "id": m.id,
            "name": m.name,
            "gender": m.gender,
            "has_received_package": m.has_received_package,
            "current_period_paid": bool(payment and payment.paid),
        })

    return jsonify({
        "committee": {
            "id": committee.id,
            "name": committee.name,
            "status": committee.status,
            "is_locked": committee.is_locked,
            "current_period": period,
            "total_periods": committee.total_periods,
        },
        "members": members_data,
    })


# ------------------------------------------------------------- add member

@dashboard_bp.route("/committee/<int:committee_id>/members/new", methods=["POST"])
@login_required
def add_member(committee_id):
    committee = _committee_or_404(committee_id)

    if committee.is_locked:
        return jsonify({
            "status": "error",
            "message": "Cannot add a member until the current cycle is completed.",
        }), 400

    form = MemberForm(meta={"csrf": False})
    if form.validate_on_submit():
        member = Member(committee_id=committee.id, name=form.name.data, gender=form.gender.data)
        db.session.add(member)
        db.session.commit()
        return jsonify({"status": "created", "member_id": member.id}), 201

    return jsonify({"status": "invalid", "errors": form.errors}), 400


# ------------------------------------------------------------- edit member

@dashboard_bp.route("/committee/<int:committee_id>/members/<int:member_id>/edit", methods=["POST"])
@login_required
def edit_member(committee_id, member_id):
    # Editing (e.g. fixing a name) is always allowed, even after the
    # committee is locked -- only add/remove are blocked.
    committee = _committee_or_404(committee_id)
    member = _member_or_404(committee, member_id)

    form = MemberForm(meta={"csrf": False})
    if form.validate_on_submit():
        member.name = form.name.data
        member.gender = form.gender.data
        db.session.commit()
        return jsonify({"status": "updated", "member_id": member.id})

    return jsonify({"status": "invalid", "errors": form.errors}), 400


# ----------------------------------------------------------- remove member

@dashboard_bp.route("/committee/<int:committee_id>/members/<int:member_id>/remove", methods=["POST"])
@login_required
def remove_member(committee_id, member_id):
    committee = _committee_or_404(committee_id)
    member = _member_or_404(committee, member_id)

    if committee.is_locked:
        return jsonify({
            "status": "error",
            "message": "Cannot remove a member until the current cycle is completed.",
        }), 400

    db.session.delete(member)
    db.session.commit()
    return jsonify({"status": "removed"})


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

    return jsonify({"status": "updated", "member_id": member.id, "period": period, "paid": paid})


# ----------------------------------------------------------------- payout

@dashboard_bp.route("/committee/<int:committee_id>/payout", methods=["POST"])
@login_required
def record_payout(committee_id):
    committee = _committee_or_404(committee_id)
    member_id = request.form.get("member_id", type=int)
    member = _member_or_404(committee, member_id) if member_id else None

    if member is None:
        return jsonify({"status": "error", "message": "member_id is required"}), 400

    if member.has_received_package:
        return jsonify({
            "status": "error",
            "message": "This member has already received the payout in this committee.",
        }), 400

    period = current_period_label(committee.frequency)

    existing = Payout.query.filter_by(committee_id=committee.id, period_label=period).first()
    if existing:
        return jsonify({
            "status": "error",
            "message": f"A payout for {period} has already been recorded.",
        }), 400

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

    # Auto-complete the committee once everyone has received the payout once.
    if all(m.has_received_package for m in committee.members):
        committee.status = "completed"

    db.session.commit()

    return jsonify({
        "status": "recorded",
        "member_id": member.id,
        "period": period,
        "amount_cents": period_total,
        "committee_status": committee.status,
    })
