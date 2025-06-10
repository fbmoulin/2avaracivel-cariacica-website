import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    # Create the Flask application
    app = Flask(__name__)
    
    # Set secret key from environment variable or use default for development
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    
    # Proxy fix for deployment behind reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configure SQLite database
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///court_site.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from routes import main_bp, services_bp, chatbot_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(chatbot_bp)
    
    # Create database tables
    with app.app_context():
        import models
        db.create_all()
    
    # Setup error monitoring
    try:
        from error_monitor import setup_flask_error_handlers, start_monitoring
        setup_flask_error_handlers(app)
        start_monitoring()
    except ImportError:
        pass
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
