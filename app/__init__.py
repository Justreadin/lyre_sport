from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()  # Initialize Flask-Mail globally


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    print("Mail initialized:", mail is not None)

    # Set login_view for Flask-Login
    login_manager.login_view = 'auth.login'

    # Import User model here to avoid circular imports
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # Query User model by ID

    # Register Blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    from .routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    return app
