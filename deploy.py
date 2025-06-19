#!/usr/bin/env python3
"""
Production deployment script for 2ª Vara Cível de Cariacica
Final optimized version for Replit deployment
"""
import os
import sys
import logging
from app import create_app

# Production logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def validate_deployment_requirements():
    """Validate all deployment requirements"""
    required_env = ['DATABASE_URL', 'SESSION_SECRET']
    optional_env = ['OPENAI_API_KEY']
    
    missing = [var for var in required_env if not os.environ.get(var)]
    if missing:
        logging.error(f"Missing required environment variables: {missing}")
        return False
    
    available = [var for var in optional_env if os.environ.get(var)]
    logging.info(f"Available services: {available}")
    
    return True

def create_production_app():
    """Create and configure production app"""
    if not validate_deployment_requirements():
        sys.exit(1)
    
    app = create_app()
    
    # Production-specific configurations
    app.config.update({
        'ENV': 'production',
        'DEBUG': False,
        'TESTING': False,
        'SESSION_COOKIE_SECURE': True,
        'SESSION_COOKIE_HTTPONLY': True,
        'SEND_FILE_MAX_AGE_DEFAULT': 31536000,
        'TEMPLATES_AUTO_RELOAD': False
    })
    
    return app

def main():
    """Main deployment entry point"""
    logging.info("2ª Vara Cível de Cariacica - Production Deployment")
    logging.info("=" * 50)
    
    try:
        app = create_production_app()
        
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        
        logging.info(f"Starting production server on {host}:{port}")
        logging.info("Application ready for production deployment")
        
        app.run(
            host=host,
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except Exception as e:
        logging.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()