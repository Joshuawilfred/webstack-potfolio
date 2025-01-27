from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Importing models for SQLAlchemy discovery
    from app.models import User, Artwork

    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

    # Register blueprints (routes)
    from app.routes import main_routes, auth_routes
    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)

    return app