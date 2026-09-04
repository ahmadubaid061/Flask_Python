from flask import current_app
from flask_mail import Message

from app.extensions import mail


def send_login_code_email(to_email: str, code: str) -> None:
    """Sends the 6-digit verification code. Requires MAIL_SERVER,
    MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD to be set in the environment —
    if they're missing, Flask-Mail will raise when this is called, which is
    the correct behavior (fail loudly rather than silently not send)."""
    msg = Message(
        subject="Your committee app login code",
        recipients=[to_email],
        body=(
            f"Your verification code is: {code}\n\n"
            f"This code expires in {current_app.config['LOGIN_CODE_EXPIRY_MINUTES']} minutes. "
            "If you didn't request this, you can ignore this email."
        ),
    )
    mail.send(msg)
