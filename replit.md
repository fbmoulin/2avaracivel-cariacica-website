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

### Technical Implementation
- **Backend**: Flask web framework.
- **Database**: PostgreSQL with SQLAlchemy ORM, optimized connection pooling, and automatic table creation. All models use `extend_existing` to prevent redefinition errors.
- **Models**: Contact, ProcessConsultation, ChatMessage, AssessorMeeting, and others, with defined relationships and serialization methods.
- **Services**: Modular service layer including a refined AI Chatbot (OpenAI GPT-4o integration), Content management, API integration, Scheduling, and Caching.
- **Security**: Implemented with Flask-WTF for CSRF, XSS protection via input sanitization, email validation, Content Security Policy (CSP), HSTS, Permissions Policy, and secure session cookies. Rate limiting is applied to API endpoints.
- **Frontend**: Responsive design with accessibility features adhering to WCAG 2.1 AA standards. Includes court-themed animated loading indicators with smart context detection and a refined modular accessibility system with 16 features and keyboard shortcuts.
- **Code Quality**: Employs structured logging, type hints, comprehensive docstrings, and robust error handling.
- **Monitoring**: Integrated performance monitoring, query monitoring, and health check endpoints provide real-time diagnostics.

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