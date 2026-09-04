from datetime import date, timedelta


def _period_sort_key(label: str) -> int:
    """Sorts 'W1', 'W2', ... 'W10' numerically instead of alphabetically
    (plain string sort would put 'W10' before 'W2')."""
    digits = label[1:]
    return int(digits) if digits.isdigit() else 0


def generate_elapsed_periods(frequency: str, start_date: date, on_date: date = None) -> list[str]:
    """All period labels from period 1 up to and including the current one,
    based purely on start_date/frequency — regardless of whether any data
    has been recorded for them. This is what makes a backdated committee
    (e.g. start_date 4 weeks ago) show W1..W5 as selectable from day one,
    even though W1-W4 have no records yet."""
    current_label = current_period_label(frequency, start_date, on_date)
    prefix = current_label[0]
    current_number = int(current_label[1:]) if current_label[1:].isdigit() else 1
    return [f"{prefix}{n}" for n in range(1, current_number + 1)]


def get_available_periods(committee) -> list[str]:
    """Every period the committee has reached so far (from start_date up to
    the current period), most recent first. This is a superset of periods
    that actually have payment/payout data — a freshly backdated committee
    will show all its past periods as selectable, empty, ready to be filled
    in by the admin."""
    from app.models.payment import Payment
    from app.models.payout import Payout

    elapsed = set(generate_elapsed_periods(committee.frequency, committee.start_date))

    # Safety net: include any recorded labels that fall outside the normal
    # elapsed range too (shouldn't normally happen, but never hide real data).
    payment_labels = {
        row[0] for row in Payment.query.with_entities(Payment.period_label)
        .filter_by(committee_id=committee.id).distinct()
    }
    payout_labels = {
        row[0] for row in Payout.query.with_entities(Payout.period_label)
        .filter_by(committee_id=committee.id).distinct()
    }
    labels = elapsed | payment_labels | payout_labels
    return sorted(labels, key=_period_sort_key, reverse=True)


def get_period_summary(committee, period_label: str) -> dict:
    """Builds the full picture for one past period: who paid what, total
    collected, and any payout(s) recorded for that period."""
    from app.models.payment import Payment
    from app.models.payout import Payout

    payments_by_member = {
        p.member_id: p
        for p in Payment.query.filter_by(
            committee_id=committee.id, period_label=period_label
        ).all()
    }
    payouts = (
        Payout.query.filter_by(committee_id=committee.id, period_label=period_label)
        .order_by(Payout.payout_date.asc())
        .all()
    )

    members_data = []
    total_received = 0.0
    for member in committee.members:
        payment = payments_by_member.get(member.id)
        paid = bool(payment and payment.paid)
        amount = payment.amount if paid else 0.0
        total_received += amount
        members_data.append({
            "member": member,
            "paid": paid,
            "amount": amount,
            "paid_date": payment.paid_date if payment else None,
        })

    return {
        "period_label": period_label,
        "members_data": members_data,
        "total_received": total_received,
        "expected_total": committee.contribution_amount * len(committee.members),
        "payouts": payouts,
        "total_payout": sum(p.amount for p in payouts),
    }


def current_period_label(frequency: str, committee_start_date: date = None, on_date: date = None) -> str:
    """Returns the label for 'today's' period counted from committee start date.
    
    frequency: "weekly" or "monthly"
    committee_start_date: when the committee started (e.g., 2026-09-04)
    on_date: the date to calculate for (defaults to today)
    
    Returns:
    - Weekly:  "W1", "W2", "W3" etc (counted from start_date)
    - Monthly: "M1", "M2", "M3" etc (counted from start_date)
    """
    on_date = on_date or date.today()
    
    if committee_start_date is None:
        committee_start_date = on_date
    
    if frequency == "weekly":
        # Calculate number of weeks since committee start
        days_since_start = (on_date - committee_start_date).days
        weeks_since_start = days_since_start // 7
        return f"W{weeks_since_start + 1}"
    
    elif frequency == "monthly":
        # Calculate number of months since committee start
        months_since_start = (on_date.year - committee_start_date.year) * 12
        months_since_start += (on_date.month - committee_start_date.month)
        return f"M{months_since_start + 1}"
    
    # Fallback
    return "P1"