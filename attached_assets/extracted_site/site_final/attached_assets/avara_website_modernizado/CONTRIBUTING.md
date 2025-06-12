# Contributing to 2ª Vara Cível de Cariacica

Thank you for your interest in contributing to the court website system. This document provides guidelines for contributing to ensure code quality and consistency.

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Redis 6.0+ (optional but recommended)
- Git

### Local Development
```bash
# Clone repository
git clone https://github.com/court-system/cariacica.git
cd cariacica

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your local settings

# Initialize database
python -c "from app_factory import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"

# Run health check
python debug_log.py

# Start development server
python main_optimized.py
```

## Code Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Maximum line length: 88 characters (Black formatter)
- Use descriptive variable and function names
- Add docstrings for all classes and functions

### Example Code Style
```python
from typing import Optional, Dict, Any
from flask import request, jsonify

def create_contact(data: Dict[str, Any]) -> tuple[Optional[Contact], Optional[str]]:
    """
    Create a new contact record with validation.
    
    Args:
        data: Dictionary containing contact form data
        
    Returns:
        Tuple of (Contact object, error message)
    """
    try:
        contact = Contact(
            name=data.get('name'),
            email=data.get('email'),
            message=data.get('message')
        )
        return contact, None
    except Exception as e:
        return None, str(e)
```

### JavaScript Style
- Use ES6+ features
- Prefer const/let over var
- Use arrow functions for simple operations
- Add JSDoc comments for functions
- Use meaningful variable names

### CSS/SCSS
- Follow BEM methodology for class naming
- Use Bootstrap 5.3 utilities when possible
- Keep custom CSS minimal and focused
- Use CSS custom properties for theming

## File Organization

### Project Structure
```
├── app_factory.py          # Application factory
├── config.py              # Configuration management
├── routes_optimized.py    # Route definitions
├── models.py             # Database models
├── /services/            # Business logic layer
├── /templates/           # Jinja2 templates
├── /static/             # CSS, JS, images
├── /utils/              # Helper functions
├── /tests/              # Test suite
└── /docs/               # Documentation
```

### Naming Conventions
- **Files**: snake_case (e.g., `database_service.py`)
- **Classes**: PascalCase (e.g., `DatabaseService`)
- **Functions**: snake_case (e.g., `create_contact`)
- **Variables**: snake_case (e.g., `user_data`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`)

## Testing Guidelines

### Test Structure
```python
import pytest
from app_factory import create_app, db

class TestContactService:
    """Test contact form functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def test_create_contact_success(self):
        """Test successful contact creation."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Test message'
        }
        
        response = self.client.post('/contato', data=data)
        assert response.status_code == 302  # Redirect after success
```

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/test_contact.py

# Run with verbose output
python -m pytest -v
```

## Git Workflow

### Branch Naming
- **Feature**: `feature/contact-form-enhancement`
- **Bug Fix**: `bugfix/fix-cache-invalidation`
- **Hotfix**: `hotfix/security-patch`
- **Documentation**: `docs/update-api-reference`

### Commit Messages
Follow conventional commit format:
```
type(scope): description

feat(chatbot): add fallback responses for API failures
fix(cache): resolve redis connection timeout issues
docs(api): update endpoint documentation
perf(database): optimize query performance
test(forms): add validation test coverage
```

### Pull Request Process
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation if needed
4. Run full test suite
5. Submit pull request with description
6. Address review feedback
7. Merge after approval

## Security Considerations

### Input Validation
- Always sanitize user inputs
- Use parameterized queries for database operations
- Validate file uploads for type and size
- Implement CSRF protection on forms

### Authentication & Authorization
- Use secure session management
- Implement rate limiting on sensitive endpoints
- Log security-related events
- Follow principle of least privilege

### Data Protection
- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement proper error handling
- Avoid exposing internal system details

## Performance Guidelines

### Database Operations
- Use connection pooling
- Implement query optimization
- Add appropriate indexes
- Use pagination for large datasets
- Cache frequently accessed data

### Caching Strategy
- Cache static content for long periods
- Use appropriate cache keys
- Implement cache invalidation
- Monitor cache hit rates
- Use compression for large cached data

### Frontend Performance
- Minimize HTTP requests
- Compress images and assets
- Use CDN for static content
- Implement lazy loading
- Optimize JavaScript bundles

## Documentation Standards

### Code Documentation
- Add docstrings to all public functions
- Document complex algorithms
- Include usage examples
- Keep documentation updated with code changes

### API Documentation
- Document all endpoints
- Include request/response examples
- Specify rate limits and authentication
- Document error codes and responses

### User Documentation
- Write clear installation instructions
- Provide troubleshooting guides
- Include configuration examples
- Update screenshots and examples

## Accessibility Requirements

### WCAG 2.1 AA Compliance
- Provide alt text for images
- Ensure keyboard navigation
- Use semantic HTML elements
- Maintain color contrast ratios
- Test with screen readers

### Implementation Guidelines
```html
<!-- Good: Semantic HTML with proper labels -->
<form>
    <label for="email">Email Address (required)</label>
    <input type="email" id="email" name="email" required 
           aria-describedby="email-help">
    <div id="email-help">We'll never share your email</div>
</form>

<!-- Good: Proper heading hierarchy -->
<h1>Main Page Title</h1>
<h2>Section Heading</h2>
<h3>Subsection Heading</h3>
```

## Deployment Process

### Staging Environment
- Test all changes in staging first
- Verify database migrations
- Check performance metrics
- Validate security configurations

### Production Deployment
- Use blue-green deployment strategy
- Run database backups before deployment
- Monitor system metrics post-deployment
- Have rollback plan ready

### Environment Configuration
```bash
# Development
FLASK_ENV=development
DEBUG=True
CACHE_TYPE=null

# Production
FLASK_ENV=production
DEBUG=False
CACHE_TYPE=redis
SESSION_COOKIE_SECURE=True
```

## Monitoring and Logging

### Application Metrics
- Response times and throughput
- Error rates and types
- Cache hit rates
- Database query performance

### Business Metrics
- User engagement statistics
- Form submission rates
- Chatbot usage patterns
- Service utilization

### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about operations
- **WARNING**: Something unexpected but not critical
- **ERROR**: Error occurred but application continues
- **CRITICAL**: Serious error, application may not continue

## Release Process

### Version Numbering
- **Major** (X.0.0): Breaking changes or major features
- **Minor** (1.X.0): New features, backward compatible
- **Patch** (1.0.X): Bug fixes and small improvements

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number bumped
- [ ] Changelog updated
- [ ] Security review completed
- [ ] Performance benchmarks met
- [ ] Staging deployment successful
- [ ] Rollback plan prepared

## Getting Help

### Communication Channels
- **Issues**: GitHub issues for bug reports and feature requests
- **Email**: suporte-tecnico@tjes.jus.br for technical support
- **Documentation**: Check existing documentation first

### Code Review Process
- All code must be reviewed before merging
- Focus on correctness, security, and performance
- Provide constructive feedback
- Test reviewer suggestions locally

## License and Legal

This project is property of Tribunal de Justiça do Espírito Santo (TJ-ES). All contributions become part of the project under the same terms.

### Contributor Agreement
By contributing, you agree that:
- Your contributions are your original work
- You have the right to contribute the code
- Your contributions may be used under the project license
- You will not include proprietary or confidential information