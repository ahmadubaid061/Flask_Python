from app.extensions import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    committee_id = db.Column(db.Integer, db.ForeignKey("committees.id"), nullable=False)

    # e.g. "2026-11" for a monthly committee, "2026-W36" for a weekly one
    period_label = db.Column(db.String(20), nullable=False)

    # Stored per-row (not just referencing committee.contribution_amount) so
    # history stays accurate even if the committee's amount is ever edited.
    # In cents.
    amount = db.Column(db.Integer, nullable=False)

    paid = db.Column(db.Boolean, nullable=False, default=False)
    paid_date = db.Column(db.Date, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("member_id", "period_label", name="uq_member_period"),
    )
