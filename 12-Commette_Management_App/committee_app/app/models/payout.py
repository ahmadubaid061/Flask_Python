from datetime import datetime, timezone

from app.extensions import db


class Payout(db.Model):
    """Record of payout made to a member in a specific period."""

    __tablename__ = "payouts"

    id = db.Column(db.Integer, primary_key=True)
    committee_id = db.Column(db.Integer, db.ForeignKey("committees.id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    period_label = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payout_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    payout_cycle = db.Column(db.Integer, default=1)  # Track which cycle (1st, 2nd, 3rd payout)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))