# 2ª Vara Cível de Cariacica - Project Documentation

## Overview
This project is a complete digital judicial platform for the 2nd Civil Court of Cariacica. It is a Flask-based web application featuring an AI-powered chatbot, process consultation, contact forms, and administrative functionalities. The system is designed for high performance, scalability, and security, aiming to streamline judicial processes and enhance user interaction. It is fully operational with a 100% test success rate, emphasizing production readiness and a robust architecture.

## User Preferences
- Focus on technical accuracy and comprehensive solutions
- Prefer detailed documentation with current status verification
- Emphasize production readiness and operational confirmation
- Value thorough testing and error resolution

## System Architecture

### Core Design Principles
The application follows a monorepo structure with a clear separation of frontend and backend components. It utilizes a Flask application factory pattern for modularity and scalability. Performance is optimized through comprehensive caching strategies (route, response, database), connection pooling, and strategic database indexing. Security is paramount, with extensive measures including CSRF protection, XSS prevention, robust input validation, and comprehensive security headers.

### Recent Integration Improvements (August 2, 2025)
- **Backend-Frontend Integration**: Implemented standardized API responses, automatic retry logic with exponential backoff, comprehensive input validation, and proper CORS configuration
- **Database Integration**: Optimized connection pooling for PostgreSQL, added transaction scoping with automatic rollback, implemented query optimization with indexes, and retry logic for transient errors
- **API Integration**: Added rate limiting (30 requests/minute for chat, 60 for others), intelligent caching strategy, comprehensive health monitoring endpoints, and robust error handling
- **Error Handling**: Global error handler with logging, user-friendly error messages, automatic recovery mechanisms, and comprehensive error monitoring
- **Performance**: Enabled response compression, implemented lazy loading, added strategic database indexes, and intelligent client-side caching

### Technical Implementation
- **Backend**: Flask web framework with robust API layer (routes_api.py) providing stable endpoints for all frontend interactions
- **Database**: PostgreSQL with SQLAlchemy ORM, optimized connection pooling (10 connections, 20 overflow), automatic table creation, and transaction management. All models use `extend_existing` to prevent redefinition errors
- **Models**: Contact, ProcessConsultation, ChatMessage, AssessorMeeting, and others, with defined relationships and serialization methods. Fixed field naming consistency issues
- **Services**: Modular service layer including:
  - Refined AI Chatbot (OpenAI GPT-4o integration) with fallback mechanisms
  - Content management with caching
  - API integration with retry logic
  - Scheduling with availability checking
  - Enhanced database integration service with connection pooling and retry logic
  - Frontend integration service for standardized responses
- **Security**: Implemented with Flask-WTF for CSRF, XSS protection via input sanitization, email validation, Content Security Policy (CSP), HSTS, Permissions Policy, and secure session cookies. Rate limiting is applied to API endpoints (30-60 requests/minute)
- **Frontend**: Responsive design with accessibility features adhering to WCAG 2.1 AA standards. Includes:
  - Court-themed animated loading indicators with smart context detection
  - Refined modular accessibility system with 16 features and keyboard shortcuts
  - Robust API client with automatic retry and error recovery (api-integration.js)
- **Code Quality**: Employs structured logging, type hints, comprehensive docstrings, robust error handling, and integration testing
- **Monitoring**: Integrated performance monitoring, query monitoring, health check endpoints (/health, /api/health) provide real-time diagnostics

### Key Features
- **AI Chatbot**: Advanced modular architecture with multiple response strategies (MeetingScheduling, Predefined, OpenAI, Fallback), comprehensive conversation management (10-message context), analytics, and a professional debug panel.
- **Process Consultation**: Allows users to consult judicial processes, with updated links to the TJES portal.
- **Scheduling Service**: Supports four distinct service types (Presencial, Videoconferência, Atendimento no Gabinete, Serviços do Cartório) with dynamic UI and comprehensive validation.
- **Virtual Counter**: Direct integration with the official TJES Virtual Counter.
- **User Interface**: Consistent design with a focus on user experience, professional judicial-themed visuals, and high accessibility.

## External Dependencies
- **Database**: PostgreSQL (specifically Supabase for cloud deployment).
- **AI/LLM**: OpenAI GPT-4o for chatbot functionalities, with fallback mechanisms.
- **Frontend Libraries**: Standard JavaScript ES6+ modules for interactivity, pure CSS animations.