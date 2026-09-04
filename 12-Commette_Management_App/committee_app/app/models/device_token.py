from datetime import datetime, timezone

from app.extensions import db


class TrustedDevice(db.Model):
    """One row per browser the admin has completed email verification on.
    A matching, valid cookie lets the admin skip re-verification next login.
    """

    __tablename__ = "trusted_devices"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False)
    device_token = db.Column(db.String(128), unique=True, nullable=False)
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_used_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class LoginVerification(db.Model):
    """Short-lived 6-digit email codes issued when logging in from an
    unrecognized browser."""

    __tablename__ = "login_verifications"

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False)
    code_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    consumed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def is_valid(self) -> bool:
        """Check if verification code is still valid (not expired and not consumed)."""
        # Make expires_at timezone-aware if it's naive (for old database records)
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            # If naive, assume UTC
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        return not self.consumed and datetime.now(timezone.utc) < expires_at