import os
from datetime import timedelta


class Config:
    """Base configuration class."""

    # Basic Flask configuration
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database configuration - use absolute path for SQLite
    @staticmethod
    def init_app(app):
        # Ensure instance folder exists
        os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.abspath(os.path.join(os.getcwd(), "instance", "mediamaster.db"))}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # File upload configuration
    UPLOAD_FOLDER = os.path.join("media", "uploads")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp',
                          'gif', 'mp4', 'avi', 'mov', 'mkv', 'webm'}

    # Media serving configuration
    MEDIA_FOLDER = os.path.join(os.getcwd(), "media")

    # Base URL for file serving
    BASE_URL = os.environ.get('BASE_URL') or 'http://127.0.0.1:8000'

    # API Key configuration
    API_KEY = os.environ.get('API_KEY') or 'mediamaster-dev-key-12345'

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # Security headers
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=1)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    # Override database URI for development to use SQLite with absolute path
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.abspath(os.path.join(os.getcwd(), "instance", "mediamaster.db"))}'
    # SQLite doesn't need these engine options
    SQLALCHEMY_ENGINE_OPTIONS = {}

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        # Ensure instance and media directories exist
        os.makedirs(os.path.join(app.instance_path), exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        if not app.config['SECRET_KEY']:
            raise ValueError("No SECRET_KEY set for production environment")


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
