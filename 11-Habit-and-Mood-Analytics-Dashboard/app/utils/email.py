from threading import Thread
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from flask_mail import Message

from app.extensions import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    # 'salt' namespaces this token so it can't be reused for some other
    # purpose (like password resets) even if someone got hold of it
    return serializer.dumps(email, salt='email-verify')


def confirm_verification_token(token, expiration=3600):
    # expiration is in seconds -- 3600 = 1 hour. After that, the link dies.
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-verify', max_age=expiration)
    except Exception:
        # Covers both a tampered token and an expired one
        return None
    return email


def send_verification_email(user_email):
    token = generate_verification_token(user_email)
    verify_url = url_for('auth.verify_email', token=token, _external=True)

    msg = Message(
        subject='Verify your email — Habit & Mood Dashboard',
        recipients=[user_email],
        body=f'Click the link to verify your account: {verify_url}\n\n'
             f'This link expires in 1 hour.'
    )
    # Send in background thread to prevent Vercel timeout
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
    
    