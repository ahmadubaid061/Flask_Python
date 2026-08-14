from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate

# Initialized here, with no app yet attached.
# Each extension gets wired to the real app later inside create_app()
# via db.init_app(app), login_manager.init_app(app), mail.init_app(app).
# This split is what avoids circular imports: models.py can import `db`
# from here without needing the app factory, and the app factory can
# import models.py without needing extensions defined inside itself.

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


# Where Flask-Login redirects a user if they hit a @login_required
# route without being logged in. 'auth.login' means: blueprint 'auth',
# route function 'login'.
login_manager.login_view = 'auth.login'