import os
import logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from database import db, configure_database, create_all_tables, optimize_database_performance

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

csrf = CSRFProtect()

def create_app():
    # Create the Flask application
    app = Flask(__name__)
    
    # Set secret key from environment variable
    app.secret_key = os.environ.get("SESSION_SECRET")
    
    # Proxy fix for deployment behind reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configure database with optimized settings
    configure_database(app)
    
    # Additional configuration
    app.config.update({
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
        'CACHE_TIMEOUT': 300
    })
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Register blueprints
    try:
        from routes import main_bp, services_bp, chatbot_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(services_bp)
        app.register_blueprint(chatbot_bp)
        logging.info("Blueprints registered successfully")
    except ImportError as e:
        logging.error(f"Failed to register blueprints: {e}")
    
    # Create database tables
    create_all_tables(app)
    
    # Apply database performance optimizations
    with app.app_context():
        optimize_database_performance()
    
    # Add health check endpoint
    @app.route('/health')
    def health():
        import time
        from database import check_database_health
        db_healthy, db_msg = check_database_health()
        return {
            'status': 'healthy' if db_healthy else 'unhealthy',
            'database': db_msg,
            'timestamp': str(time.time())
        }
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
