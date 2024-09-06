from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS
from routes import bp as main_routes
from admin_routes import admin_bp as admin_routes
from email_service import EmailService
from config import config


def create_app():
    app = Flask(__name__)

    # Load configuration from the config dictionary
    app.config.update(config)

    # Initialize CORS
    CORS(app)

    # Initialize and configure MongoDB
    mongo = PyMongo(app)

    app.mongo = mongo

    # Initialize and configure EmailService
    email_service = EmailService()
    email_service.init_app(app)

    # Add email_service to app context
    app.email_service = email_service

    # Register Blueprints
    app.register_blueprint(main_routes)
    app.register_blueprint(admin_routes)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  # It's a good idea to have debug=True during development
