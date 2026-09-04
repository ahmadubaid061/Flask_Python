from datetime import datetime, timezone

from app.extensions import db


class Committee(db.Model):
    """A committee for collecting and distributing funds."""

    __tablename__ = "committees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # "weekly" or "monthly"
    contribution_amount = db.Column(db.Float, nullable=False)
    target_member_count = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), default="active")  # "active" or "completed"
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # ✅ Simple relationship without conflicting backref
    members = db.relationship("Member", cascade="all, delete-orphan")