from flask import Flask

from config import Config
from app.extensions import db, login_manager, mail, csrf, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    # --- models must be imported before create_all / migrations pick them up
    from app.models import admin, committee, member, payment, payout, device_token  # noqa: F401

    # --- blueprints ---
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.committees import committees_bp
    from app.routes.members import members_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(committees_bp, url_prefix="/committee")
    app.register_blueprint(members_bp, url_prefix="/member")
    app.register_blueprint(dashboard_bp, url_prefix="/admin")

    from app.models.admin import Admin

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Admin, int(user_id))

    from app.cli import register_commands
    register_commands(app)

    # --- auto-create tables on startup ---
    # Scans every imported db.Model subclass and creates any table that
    # doesn't already exist in Turso. Does NOT alter existing tables if you
    # change a column later — for that you'd need Flask-Migrate. Fine for
    # early development, same behavior as your previous app.
    with app.app_context():
        db.create_all()
        
        # --- Auto-initialize admin from .env if it doesn't exist ---
        _initialize_admin_from_env(app)

    return app


def _initialize_admin_from_env(app):
    """Auto-create admin user from .env if credentials are provided and admin doesn't exist."""
    from app.models.admin import Admin
    
    username = app.config.get("ADMIN_USERNAME")
    password = app.config.get("ADMIN_PASSWORD")
    email = app.config.get("ADMIN_EMAIL_FOR_LOGIN")
    
    # Check if all required credentials are in .env
    if not all([username, password, email]):
        print("[INFO] ⏭️  Skipping auto-admin creation: missing ADMIN_USERNAME, ADMIN_PASSWORD, or ADMIN_EMAIL_FOR_LOGIN in .env")
        return
    
    # Check if admin already exists
    existing_admin = Admin.query.filter_by(username=username).first()
    if existing_admin:
        print(f"[INFO] ✅ Admin '{username}' already exists in database")
        return
    
    try:
        # Create new admin from .env
        admin = Admin(username=username, email=email)
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"[INFO] ✅ Auto-created admin from .env:")
        print(f"       Username: {username}")
        print(f"       Email: {email}")
    except Exception as e:
        print(f"[ERROR] ❌ Failed to auto-create admin: {str(e)}")
        db.session.rollback()