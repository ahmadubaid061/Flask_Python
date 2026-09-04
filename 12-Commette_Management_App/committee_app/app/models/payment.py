from datetime import datetime, timezone

from app.extensions import db


class Payment(db.Model):
    """Record of a member's payment for a specific period."""

    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    committee_id = db.Column(db.Integer, db.ForeignKey("committees.id"), nullable=False)
    period_label = db.Column(db.String(50), nullable=False)  # "W1", "W2", "M1", etc
    amount = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))