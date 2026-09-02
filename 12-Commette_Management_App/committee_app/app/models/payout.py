from app.extensions import db


class Payout(db.Model):
    __tablename__ = "payouts"

    id = db.Column(db.Integer, primary_key=True)
    committee_id = db.Column(db.Integer, db.ForeignKey("committees.id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)

    period_label = db.Column(db.String(20), nullable=False)

    # Sum of that period's Payments across the committee, in cents.
    amount = db.Column(db.Integer, nullable=False)

    payout_date = db.Column(db.Date, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("committee_id", "period_label", name="uq_committee_period_payout"),
    )
