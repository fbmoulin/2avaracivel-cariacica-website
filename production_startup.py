#!/usr/bin/env python3
"""
Production-ready startup script for 2ª Vara Cível de Cariacica
Optimized for deployment with proper error handling and monitoring
"""
import os
import sys
import logging
import signal
from app import create_app

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ProductionServer:
    def __init__(self):
        self.app = None
        self.running = True
        
    def signal_handler(self, signum, frame):
        """Handle graceful shutdown"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        sys.exit(0)
    
    def validate_environment(self):
        """Validate required environment variables"""
        required_vars = ['DATABASE_URL', 'SESSION_SECRET']
        optional_vars = ['OPENAI_API_KEY']
        
        missing_required = [var for var in required_vars if not os.environ.get(var)]
        if missing_required:
            logger.error(f"Missing required environment variables: {missing_required}")
            return False
            
        available_optional = [var for var in optional_vars if os.environ.get(var)]
        logger.info(f"Optional services available: {available_optional}")
        
        return True
    
    def start_server(self):
        """Start the production server"""
        if not self.validate_environment():
            sys.exit(1)
            
        # Register signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Create Flask application
            self.app = create_app()
            
            # Server configuration
            port = int(os.environ.get('PORT', 5000))
            host = os.environ.get('HOST', '0.0.0.0')
            debug = os.environ.get('FLASK_ENV', 'production') == 'development'
            
            logger.info("=== 2ª Vara Cível de Cariacica - Sistema Judicial Digital ===")
            logger.info(f"Starting production server on {host}:{port}")
            logger.info(f"Debug mode: {'ON' if debug else 'OFF'}")
            logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
            logger.info("=" * 60)
            
            # Run the application
            self.app.run(
                host=host,
                port=port,
                debug=debug,
                use_reloader=False,
                threaded=True
            )
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}", exc_info=True)
            sys.exit(1)

def main():
    """Main entry point"""
    server = ProductionServer()
    server.start_server()

if __name__ == '__main__':
    main()