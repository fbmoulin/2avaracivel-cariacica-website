#!/usr/bin/env python3
"""
Debug log script for 2ª Vara Cível de Cariacica website
Monitors application health, errors, and performance
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from flask import Flask
from werkzeug.exceptions import HTTPException

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_database_connection():
    """Check database connection status"""
    try:
        from app import app, db
        with app.app_context():
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT 1"))
                logger.info("Database connection: OK")
                return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def check_openai_connection():
    """Check OpenAI API connection"""
    try:
        from services.chatbot import ChatbotService
        chatbot = ChatbotService()
        if chatbot.openai_client:
            logger.info("OpenAI connection: OK")
            return True
        else:
            logger.warning("OpenAI connection: Not configured")
            return False
    except Exception as e:
        logger.error(f"OpenAI connection failed: {str(e)}")
        return False

def check_static_files():
    """Check if static files are accessible"""
    static_files = [
        'static/css/style.css',
        'static/js/main.js',
        'static/js/chatbot.js',
        'static/js/forms.js'
    ]
    
    all_exist = True
    for file_path in static_files:
        if os.path.exists(file_path):
            logger.info(f"Static file OK: {file_path}")
        else:
            logger.error(f"Static file missing: {file_path}")
            all_exist = False
    
    return all_exist

def check_templates():
    """Check if template files exist"""
    template_files = [
        'templates/base.html',
        'templates/index.html',
        'templates/about.html',
        'templates/contact.html',
        'templates/faq.html',
        'templates/news.html',
        'templates/judge.html'
    ]
    
    all_exist = True
    for template in template_files:
        if os.path.exists(template):
            logger.info(f"Template OK: {template}")
        else:
            logger.error(f"Template missing: {template}")
            all_exist = False
    
    return all_exist

def check_environment_variables():
    """Check required environment variables"""
    required_vars = [
        'DATABASE_URL',
        'SESSION_SECRET',
        'OPENAI_API_KEY'
    ]
    
    all_present = True
    for var in required_vars:
        if os.environ.get(var):
            logger.info(f"Environment variable OK: {var}")
        else:
            logger.warning(f"Environment variable missing: {var}")
            all_present = False
    
    return all_present

def check_models():
    """Check database models"""
    try:
        from models import Contact, NewsItem, ProcessConsultation, ChatMessage
        from app import app, db
        logger.info("Database models loaded successfully")
        
        # Check table creation
        with app.app_context():
            with db.engine.connect() as conn:
                tables = ['contact', 'news_item', 'process_consultation', 'chat_message']
                for table in tables:
                    try:
                        result = conn.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        logger.info(f"Table {table}: {count} records")
                    except Exception as e:
                        logger.error(f"Table {table} error: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Models check failed: {str(e)}")
        return False

def check_routes():
    """Check if all routes are registered"""
    try:
        from app import app
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.rule} [{', '.join(rule.methods)}]")
        
        logger.info(f"Registered routes ({len(routes)}):")
        for route in sorted(routes):
            logger.info(f"  {route}")
        
        return True
    except Exception as e:
        logger.error(f"Routes check failed: {str(e)}")
        return False

def run_health_check():
    """Run comprehensive health check"""
    logger.info("="*50)
    logger.info("STARTING HEALTH CHECK")
    logger.info("="*50)
    
    checks = [
        ("Environment Variables", check_environment_variables),
        ("Static Files", check_static_files),
        ("Templates", check_templates),
        ("Database Connection", check_database_connection),
        ("Database Models", check_models),
        ("OpenAI Connection", check_openai_connection),
        ("Routes", check_routes),
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            logger.info(f"\n--- {check_name} ---")
            result = check_func()
            results[check_name] = result
            logger.info(f"{check_name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            logger.error(f"{check_name}: ERROR - {str(e)}")
            logger.error(traceback.format_exc())
            results[check_name] = False
    
    logger.info("\n" + "="*50)
    logger.info("HEALTH CHECK SUMMARY")
    logger.info("="*50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{check_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("🟢 All systems operational")
    elif passed > total // 2:
        logger.warning("🟡 Some issues detected")
    else:
        logger.error("🔴 Critical issues detected")
    
    return results

if __name__ == "__main__":
    # Add the current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        results = run_health_check()
        
        # Write summary to file
        with open('health_check_summary.txt', 'w') as f:
            f.write(f"Health Check Summary - {datetime.now()}\n")
            f.write("="*50 + "\n\n")
            
            for check_name, result in results.items():
                status = "PASS" if result else "FAIL"
                f.write(f"{check_name}: {status}\n")
            
            passed = sum(1 for result in results.values() if result)
            total = len(results)
            f.write(f"\nOverall: {passed}/{total} checks passed\n")
        
        logger.info("\nHealth check complete. Results saved to health_check_summary.txt")
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)