# System Dependencies Guide
**2ª Vara Cível de Cariacica - Required System Packages**

## Current Environment Status

### Python Environment
- **Python Version**: 3.11.10 ✓
- **Package Manager**: pip ✓
- **Web Server**: gunicorn ✓

### Core Dependencies Installed
- **asyncio**: Built-in Python async support ✓
- **openai**: AI chatbot integration ✓
- **flask**: Web framework ✓
- **gunicorn**: Production WSGI server ✓
- **postgresql**: Database support ✓

### Async-Specific Dependencies
- **aiohttp**: HTTP async client (needed for async operations)
- **aiodns**: Async DNS resolution
- **asyncio**: Core async functionality (built-in)

## Recommended replit.nix Configuration

```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.gunicorn
    pkgs.postgresql_17
    pkgs.openssl
    pkgs.zlib
  ];
}
```

## Python Package Dependencies

### Core Application Packages
```
flask
flask-sqlalchemy
flask-wtf
flask-caching
flask-limiter
gunicorn
psycopg2-binary
```

### Async Enhancement Packages
```
aiohttp
aiodns
asyncio
```

### AI and Integration Packages
```
openai
requests
pillow
email-validator
```

### Security and Monitoring
```
werkzeug
psutil
redis
schedule
```

## System Package Benefits

### Python 3.11
- Enhanced async/await syntax
- Improved performance for async operations
- Better error handling and debugging

### PostgreSQL 17
- Advanced database features
- Better concurrent connection handling
- Improved performance for court data management

### OpenSSL
- Secure HTTPS connections
- Certificate management
- Encrypted communication with external services

### Zlib
- Data compression for better performance
- Reduced bandwidth usage
- Faster file operations

## Installation Commands

### System Dependencies (Manual Installation)
```bash
# These would be handled by replit.nix
nix-env -iA nixpkgs.python311
nix-env -iA nixpkgs.postgresql_17
nix-env -iA nixpkgs.openssl
nix-env -iA nixpkgs.zlib
```

### Python Packages (Already Configured)
```bash
pip install aiohttp aiodns
pip install flask flask-sqlalchemy
pip install openai requests
pip install gunicorn psycopg2-binary
```

## Environment Variables Required

### Database Configuration
```
DATABASE_URL=postgresql://user:pass@localhost/dbname
PGPORT=5432
PGUSER=postgres
PGPASSWORD=password
PGDATABASE=court_db
PGHOST=localhost
```

### Application Security
```
SESSION_SECRET=your-secret-key-here
FLASK_ENV=production
WTF_CSRF_ENABLED=true
```

### External Integrations
```
OPENAI_API_KEY=your-openai-api-key
```

## Performance Optimizations

### Database Connections
- Connection pooling configured for 10-25 connections
- Pre-ping enabled for connection health
- Automatic reconnection on failures

### Async Operations
- HTTP session pooling for external requests
- Intelligent caching with 5-minute expiration
- Concurrent request handling

### Security Features
- CSRF protection enabled
- Rate limiting configured
- Input sanitization active
- Security headers enforced

## Production Deployment

### Required System Components
1. **Python 3.11+**: Latest async features and performance
2. **PostgreSQL 17**: Advanced database functionality
3. **OpenSSL**: Secure communications
4. **Gunicorn**: Production WSGI server
5. **Redis** (optional): Enhanced caching and session storage

### Performance Monitoring
- Real-time async operation tracking
- Database connection monitoring
- Cache hit rate analysis
- Error logging and alerting

## Troubleshooting

### Common Issues
1. **aiohttp not available**: Install with `pip install aiohttp aiodns`
2. **Database connection errors**: Verify PostgreSQL is running
3. **OpenAI API errors**: Check API key configuration
4. **Async operation failures**: Verify asyncio support

### Verification Commands
```bash
python -c "import asyncio; print('Async support:', asyncio.iscoroutinefunction(lambda: None))"
python -c "import aiohttp; print('HTTP async available')"
python -c "import openai; print('OpenAI integration ready')"
```

## Current Implementation Status

### Fully Operational
- Core Flask application
- Database integration with PostgreSQL
- Basic async operations with built-in asyncio
- OpenAI chatbot integration
- Error logging and monitoring

### Enhanced with System Dependencies
- Advanced async HTTP operations (requires aiohttp)
- Improved security with OpenSSL
- Better compression with zlib
- Optimized database performance

The system is currently functional with the core dependencies. The suggested replit.nix configuration would provide additional performance and security enhancements for production deployment.