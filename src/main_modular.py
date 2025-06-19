"""
Main Application Entry Point - Modular Architecture
Production-ready Flask application with separated frontend/backend architecture
"""
import os
import sys
import logging
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from backend.app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_modular.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point"""
    try:
        # Create Flask application using factory pattern
        app = create_app()
        
        # Get configuration from environment
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_ENV') == 'development'
        
        logger.info(f"Starting modular court application on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        logger.info(f"Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
        
        # Start the application
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False  # Disable reloader to prevent hanging
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()