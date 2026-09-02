from datetime import datetime, timezone

from app.extensions import db


class Committee(db.Model):
    __tablename__ = "committees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    # "weekly" or "monthly" — decides how period labels are generated
    frequency = db.Column(db.String(10), nullable=False, default="monthly")

    # Fixed amount every member pays each period, in cents (avoids float
    # rounding bugs). Divide by 100 when displaying.
    contribution_amount = db.Column(db.Integer, nullable=False)

    start_date = db.Column(db.Date, nullable=False)

    # "active" or "completed" — flips to completed once every member has
    # received the payout once
    status = db.Column(db.String(10), nullable=False, default="active")

    # Target member count, set at creation. Total periods = number of
    # members, since each period pays out to exactly one member.
    # Nullable: if left blank at creation, it locks in automatically to
    # however many members exist once the start date passes.
    target_member_count = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    members = db.relationship(
        "Member", backref="committee", cascade="all, delete-orphan"
    )
    payments = db.relationship(
        "Payment", backref="committee", cascade="all, delete-orphan"
    )
    payouts = db.relationship(
        "Payout", backref="committee", cascade="all, delete-orphan"
    )

    @property
    def total_periods(self) -> int:
        """Total periods = total members. Falls back to target count before
        the member list is locked in."""
        return len(self.members) or (self.target_member_count or 0)

    @property
    def is_locked(self) -> bool:
        """Members can only be added/removed before this returns True."""
        return self.start_date <= datetime.now(timezone.utc).date()
