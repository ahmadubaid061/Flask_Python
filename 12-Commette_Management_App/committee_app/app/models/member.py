from datetime import datetime, timezone

from app.extensions import db


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    committee_id = db.Column(db.Integer, db.ForeignKey("committees.id"), nullable=False)

    name = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(20), nullable=True)

    has_received_package = db.Column(db.Boolean, nullable=False, default=False)
    # Period label this member received the payout in, e.g. "2026-11" or
    # "2026-W36". Null until they've received it.
    received_period = db.Column(db.String(20), nullable=True)

    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    payments = db.relationship(
        "Payment", backref="member", cascade="all, delete-orphan"
    )

    @property
    def total_contributed(self) -> int:
        """Sum of all paid Payment amounts for this member, in cents."""
        return sum(p.amount for p in self.payments if p.paid)
