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

    # --- auto-create tables on startup ---
    # Scans every imported db.Model subclass and creates any table that
    # doesn't already exist in Turso. Does NOT alter existing tables if you
    # change a column later — for that you'd need Flask-Migrate. Fine for
    # early development, same behavior as your previous app.
    with app.app_context():
        db.create_all()

    return app
