from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name=None):
    """Create and configure the Flask application.

    Args:
        config_name: Configuration name to use

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')

    config_class = None
    if config_name == 'development':
        from config import DevelopmentConfig
        config_class = DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'production':
        from config import ProductionConfig
        config_class = ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        from config import TestingConfig
        config_class = TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from config import DevelopmentConfig
        config_class = DevelopmentConfig
        app.config.from_object(DevelopmentConfig)

    # Initialize configuration-specific setup
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)

    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            'logs/mediamaster.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('MediaMaster startup')

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # Import models after app creation to avoid circular imports
    from app import models

    # Media files route
    @app.route("/media/<path:filename>")
    def media_files(filename):
        """Serve media files from the media directory.

        Args:
            filename: Path to the file within media directory

        Returns:
            File response or 404 if not found
        """
        try:
            media_folder = app.config['MEDIA_FOLDER']
            return send_from_directory(media_folder, filename)
        except FileNotFoundError:
            return {"error": "File not found"}, 404

    return app
