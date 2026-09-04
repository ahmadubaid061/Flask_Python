import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # --- Turso (libSQL) connection ---
    TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL")
    TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

    if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
        # `turso db show <name> --url` prints something like
        # "libsql://your-db-name.turso.io". The SQLAlchemy dialect just
        # wants the hostname, so strip the scheme if it was pasted in as-is.
        _hostname = TURSO_DATABASE_URL.replace("libsql://", "").replace("https://", "")
        SQLALCHEMY_DATABASE_URI = f"sqlite+libsql://{_hostname}?secure=true"
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {"auth_token": TURSO_AUTH_TOKEN},
        }
    else:
        # Local fallback so you can develop without a Turso account.
        SQLALCHEMY_DATABASE_URI = "sqlite:///local_dev.db"
        SQLALCHEMY_ENGINE_OPTIONS = {}

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Mail (for new-browser login verification) ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME")

    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

    # --- Trusted-device / login-code behavior ---
    TRUSTED_DEVICE_COOKIE_NAME = "committee_trusted_device"
    TRUSTED_DEVICE_MAX_AGE_DAYS = 30
    LOGIN_CODE_EXPIRY_MINUTES = 10

    # --- Admin credentials from .env (for auto-initialization) ---
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
    ADMIN_EMAIL_FOR_LOGIN = os.environ.get("ADMIN_EMAIL_FOR_LOGIN")