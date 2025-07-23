import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create app with environment-specific configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=app.config.get('DEBUG', False))
