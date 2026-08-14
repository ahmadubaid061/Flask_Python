from flask import Flask
from config import Config
from app.extensions import db, login_manager, mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.habits import habits_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.main import main_bp
    from app.routes.logs import logs_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(dashboard_bp)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app