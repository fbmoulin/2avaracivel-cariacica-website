"""
Production deployment configuration for 2ª Vara Cível de Cariacica
Optimized settings for Replit deployment
"""
import os

class ProductionConfig:
    """Production-optimized configuration"""
    
    # Core Flask settings
    SECRET_KEY = os.environ.get('SESSION_SECRET', os.urandom(32).hex())
    DEBUG = False
    TESTING = False
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 20,
        'pool_size': 10,
        'pool_reset_on_return': 'commit',
        'echo': False,
        'isolation_level': 'READ_COMMITTED'
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Performance settings
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    JSONIFY_PRETTYPRINT_REGULAR = False
    TEMPLATES_AUTO_RELOAD = False
    
    # Cache configuration
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate limiting
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # OpenAI configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = "gpt-4o"
    OPENAI_MAX_TOKENS = 500
    OPENAI_TEMPERATURE = 0.7
    
    # Application settings
    PERMANENT_SESSION_LIFETIME = 7200  # 2 hours
    
    @staticmethod
    def validate_config():
        """Validate production configuration"""
        required_vars = {
            'DATABASE_URL': os.environ.get('DATABASE_URL'),
            'SESSION_SECRET': os.environ.get('SESSION_SECRET')
        }
        
        missing = [key for key, value in required_vars.items() if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
        
        optional_vars = {
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY')
        }
        
        available_services = [key for key, value in optional_vars.items() if value]
        return {
            'required_complete': len(missing) == 0,
            'available_services': available_services,
            'missing_required': missing
        }