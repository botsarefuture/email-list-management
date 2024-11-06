from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_login import LoginManager
from routes import bp as main_routes
from admin_routes import admin_bp as admin_routes
from email_service import EmailService
from config import config
from DatabaseManager import DatabaseManager
from usermodel import User
from bson.objectid import ObjectId

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration from the config dictionary
    app.config.update(config)

    # Initialize CORS for the app
    CORS(app)

    # Initialize EmailService and attach it to the app
    email_service = EmailService()
    email_service.init_app(app)
    app.email_service = email_service

    db = DatabaseManager().get_instance().get_db()


    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'  # Redirect to login page if not authenticated

    @login_manager.user_loader
    def load_user(user_id):
        user_data = db.service_users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(_id=user_data["_id"], username=user_data["username"], password=user_data["password"], hashed=True)
        return None


    # Register Blueprints for routing
    app.register_blueprint(main_routes)
    app.register_blueprint(admin_routes)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  # Enable debug mode for development; disable in production
