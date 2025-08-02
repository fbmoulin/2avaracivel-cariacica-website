import os
import logging
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_compress import Compress
from werkzeug.middleware.proxy_fix import ProxyFix
from database import configure_database, create_all_tables, optimize_database_performance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

csrf = CSRFProtect()
compress = Compress()

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
    
    # Initialize extensions
    csrf.init_app(app)
    compress.init_app(app)
    
    # Register blueprints
    try:
        from routes import main_bp, services_bp, chatbot_bp
        from routes_api import api_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(services_bp)
        app.register_blueprint(chatbot_bp)
        app.register_blueprint(api_bp)
        
        # Exempt chatbot endpoints from CSRF protection
        csrf.exempt(app.view_functions['main.chat'])
        csrf.exempt(app.view_functions['chatbot.chatbot_message'])
        
        logging.info("Blueprints registered successfully")
    except ImportError as e:
        logging.error(f"Failed to register blueprints: {e}")
    except KeyError as e:
        logging.warning(f"Could not exempt CSRF for some endpoints: {e}")
    
    # Create database tables
    create_all_tables(app)
    
    # Apply database performance optimizations
    with app.app_context():
        optimize_database_performance()
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com fonts.googleapis.com; font-src 'self' fonts.gstatic.com; img-src 'self' data:; connect-src 'self'"
        return response
    
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
