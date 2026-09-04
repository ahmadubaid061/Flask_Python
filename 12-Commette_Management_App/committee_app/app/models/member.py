from datetime import datetime, timezone

from flask_login import UserMixin
from app.extensions import db


class Member(db.Model):
    """Member of a committee."""

    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    committee_id = db.Column(db.Integer, db.ForeignKey("committees.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20), nullable=True)
    has_received_package = db.Column(db.Boolean, default=False)
    received_period = db.Column(db.String(50), nullable=True)
    payout_cycle = db.Column(db.Integer, default=1)  # Track which payout cycle they've received
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    committee = db.relationship("Committee", backref="members")