from app import create_app
from utils.security_middleware import SecurityMiddleware

app = create_app()

# Initialize security middleware
security_middleware = SecurityMiddleware(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
