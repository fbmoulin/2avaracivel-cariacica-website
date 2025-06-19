#!/usr/bin/env python3
"""
Simple application runner for 2ª Vara Cível de Cariacica
Bypasses reloader issues and provides clean startup
"""
import os
import sys
import logging
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main application entry point"""
    print("🏛️  2ª Vara Cível de Cariacica - Sistema Judicial Digital")
    print("=" * 60)
    
    try:
        # Create Flask application
        app = create_app()
        
        # Check if we're in development or production
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'
        debug = os.environ.get('FLASK_ENV') == 'development'
        
        print(f"🚀 Starting server on {host}:{port}")
        print(f"📊 Debug mode: {'ON' if debug else 'OFF'}")
        print(f"🔗 Application URL: http://localhost:{port}")
        print("=" * 60)
        
        # Run the application without reloader to avoid hanging
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False,  # Disable reloader to prevent hanging
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        logging.error(f"Application startup error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()