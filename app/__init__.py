from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from flask_bcrypt import Bcrypt  # Add bcrypt import
from Sportblog.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()  # Initialize bcrypt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)

    # Register Blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    return app
