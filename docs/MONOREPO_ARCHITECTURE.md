# Monorepo Architecture - 2ª Vara Cível de Cariacica

## Overview
Complete modularization of the court application into a scalable monorepo structure with separated frontend/backend architecture, enhanced maintainability, and improved developer experience.

## Architecture Structure

```
src/
├── backend/                 # Flask API Backend
│   ├── api/                # REST API endpoints
│   │   ├── __init__.py    # Blueprint registration
│   │   ├── contact.py     # Contact form API
│   │   ├── process.py     # Process consultation API
│   │   ├── chatbot.py     # Chatbot interaction API
│   │   ├── scheduling.py  # Meeting scheduling API
│   │   └── health.py      # Health monitoring API
│   ├── core/              # Core infrastructure
│   │   ├── config.py      # Environment configurations
│   │   ├── database.py    # Database management
│   │   ├── extensions.py  # Flask extensions
│   │   ├── middleware.py  # Request/response middleware
│   │   └── error_handlers.py # Centralized error handling
│   ├── models/            # Database models
│   │   └── __init__.py    # SQLAlchemy models
│   ├── services/          # Business logic services
│   │   └── chatbot_service.py # AI chatbot service
│   └── app.py            # Application factory
├── frontend/             # Modern JavaScript Frontend
│   ├── components/       # Reusable UI components
│   ├── services/         # Frontend services
│   │   └── ApiService.js # HTTP client for API
│   ├── pages/           # Page-specific logic
│   ├── styles/          # CSS modules
│   ├── assets/          # Static assets
│   └── app.js          # Frontend application entry
└── shared/              # Shared utilities
    ├── types/           # TypeScript definitions
    ├── utils/           # Common utilities
    └── constants/       # Shared constants
```

## Key Features

### Backend Architecture
- **Modular API Design**: RESTful endpoints organized by feature
- **Configuration Management**: Environment-specific configurations
- **Database Layer**: SQLAlchemy ORM with connection pooling
- **Security**: CORS, rate limiting, CSRF protection
- **Error Handling**: Centralized error management
- **Health Monitoring**: System metrics and diagnostics

### Frontend Architecture
- **Component-Based**: Modular JavaScript components
- **Service Layer**: Centralized API communication
- **Modern JavaScript**: ES6+ with module system
- **Accessibility**: WCAG 2.1 AA compliance maintained
- **Performance**: Optimized loading and caching

### API Endpoints

#### Contact Management
- `POST /api/v1/contact` - Submit contact form
- `GET /api/v1/contact` - Retrieve contacts (admin)
- `GET /api/v1/contact/{id}` - Get specific contact

#### Process Consultation
- `POST /api/v1/process/consultation` - Submit consultation request
- `GET /api/v1/process/consultation/{id}` - Get consultation details
- `GET /api/v1/process/search` - Search process information

#### Chatbot Interaction
- `POST /api/v1/chatbot/chat` - Send message to chatbot
- `GET /api/v1/chatbot/history/{session_id}` - Get chat history
- `GET /api/v1/chatbot/analytics` - Usage analytics

#### Meeting Scheduling
- `POST /api/v1/scheduling/meeting` - Schedule meeting
- `GET /api/v1/scheduling/meeting/{id}` - Get meeting details
- `GET /api/v1/scheduling/availability` - Check time availability

#### Health Monitoring
- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system metrics
- `GET /api/v1/health/metrics` - Prometheus-style metrics

## Benefits

### Scalability
- Independent scaling of frontend/backend
- Modular architecture for feature development
- Clear separation of concerns

### Maintainability
- Organized codebase with clear boundaries
- Centralized configuration management
- Consistent error handling patterns

### Developer Experience
- Clear project structure
- Modular development workflow
- Comprehensive documentation

### Performance
- Optimized API endpoints
- Efficient database queries
- Frontend component optimization

## Migration Strategy

### Phase 1: Backend Modularization
1. Create modular API structure
2. Implement core services
3. Setup database models
4. Configure middleware and security

### Phase 2: Frontend Separation
1. Extract frontend components
2. Implement API service layer
3. Modernize JavaScript architecture
4. Maintain accessibility features

### Phase 3: Integration & Testing
1. Connect frontend to modular backend
2. Comprehensive testing suite
3. Performance optimization
4. Documentation updates

## Development Workflow

### Backend Development
```bash
# Start backend server
python src/backend/app.py

# Run tests
python -m pytest tests/backend/

# Database migrations
python src/backend/migrate.py
```

### Frontend Development
```bash
# Serve frontend (development)
python -m http.server 3000

# Build for production
npm run build

# Run frontend tests
npm test
```

### Full Stack Development
```bash
# Start both services
python src/backend/app.py &
python -m http.server 3000
```

## Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for chatbot
- `REDIS_URL`: Redis connection for caching
- `FLASK_ENV`: Development/production environment

### Security Configuration
- CORS origins configuration
- Rate limiting settings
- CSRF protection enabled
- Security headers implementation

## Monitoring & Observability

### Health Checks
- Database connectivity
- Cache availability
- System resource usage
- API response times

### Metrics Collection
- Request/response metrics
- Error rates and types
- Performance benchmarks
- User interaction analytics

## Future Enhancements

### Microservices Evolution
- Extract services into separate deployments
- Implement service mesh architecture
- Add container orchestration

### Enhanced Frontend
- Progressive Web App features
- Advanced component library
- State management implementation
- Real-time updates via WebSocket

### DevOps Integration
- CI/CD pipeline setup
- Automated testing workflows
- Container deployment
- Infrastructure as Code

This modular architecture provides a solid foundation for scaling the court application while maintaining code quality, performance, and accessibility standards.