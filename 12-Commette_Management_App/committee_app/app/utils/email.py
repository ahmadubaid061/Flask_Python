import requests
from flask import current_app

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_login_code_email(to_email: str, code: str) -> None:
    """Sends the 6-digit verification code via Brevo's HTTP API instead of
    raw SMTP. Render's free tier blocks all outbound traffic on SMTP ports
    (25, 465, 587) as of Sept 2025 - smtplib/Flask-Mail simply can't connect
    from there. Brevo sends over plain HTTPS (port 443), which is never
    blocked, so this works on Render's free instance without any upgrade.

    Requires BREVO_API_KEY and BREVO_SENDER_EMAIL to be set in the
    environment - if they're missing, this raises, which is the correct
    behavior (fail loudly rather than silently not send).
    """
    api_key = current_app.config.get("BREVO_API_KEY")
    sender_email = current_app.config.get("BREVO_SENDER_EMAIL")
    if not api_key or not sender_email:
        raise RuntimeError(
            "BREVO_API_KEY and BREVO_SENDER_EMAIL must be set to send login-code emails."
        )

    body_text = (
        f"Your verification code is: {code}\n\n"
        f"This code expires in {current_app.config['LOGIN_CODE_EXPIRY_MINUTES']} minutes. "
        "If you didn't request this, you can ignore this email."
    )

    response = requests.post(
        BREVO_API_URL,
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "sender": {
                "name": current_app.config.get("BREVO_SENDER_NAME", "Committee Manager"),
                "email": sender_email,
            },
            "to": [{"email": to_email}],
            "subject": "Your committee app login code",
            "textContent": body_text,
        },
        timeout=15,
    )

    if response.status_code >= 400:
        # Surface Brevo's actual error message (e.g. unverified sender,
        # bad API key) instead of a generic failure.
        raise RuntimeError(
            f"Brevo API error {response.status_code}: {response.text}"
        )