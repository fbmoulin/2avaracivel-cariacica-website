# API Reference - 2ª Vara Cível de Cariacica

## Overview

This document provides comprehensive API documentation for the court website system, including internal APIs, external integrations, and webhook specifications.

## Base URL
- **Production**: `https://2varacivel-cariacica.tjes.jus.br`
- **Staging**: `https://staging-2varacivel-cariacica.tjes.jus.br`
- **Development**: `http://localhost:5000`

## Authentication

Most public APIs require no authentication. Administrative APIs use IP-based access control.

### Rate Limiting
- **Default**: 1000 requests per hour per IP
- **Chatbot**: 30 requests per minute per IP
- **Admin**: 10 requests per minute per IP
- **Contact Forms**: 10 submissions per minute per IP

## Public APIs

### Health Check
Check system availability and status.

```http
GET /health
```

**Response**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-10T11:30:45.123456Z"
}
```

**Status Codes**
- `200`: System is healthy
- `503`: System is experiencing issues

### Chatbot API
Interactive chatbot for court-related queries.

```http
POST /chatbot/api/message
Content-Type: application/json
```

**Request Body**
```json
{
  "message": "Como consultar um processo?"
}
```

**Response**
```json
{
  "response": "Para consultar um processo, você deve acessar a seção 'Serviços' e clicar em 'Consulta Processual'. Será necessário informar o número do processo no formato CNJ (NNNNNNN-DD.AAAA.J.TR.OOOO).",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Error Response**
```json
{
  "error": "Mensagem é obrigatória"
}
```

**Status Codes**
- `200`: Success
- `400`: Invalid request
- `429`: Rate limit exceeded
- `500`: Internal server error

## Administrative APIs

### System Status
Retrieve comprehensive system status and metrics.

```http
GET /admin/status
```

**Response** (HTML Dashboard)
Returns a complete HTML dashboard with real-time system metrics including:
- Database connectivity
- OpenAI integration status
- Server performance
- Cache statistics
- Error logs

### Health Check Report
Get detailed health check results.

```http
GET /admin/health-check
```

**Response**
```json
{
  "status": "success",
  "content": "Environment Variables: ✓ PASS\nStatic Files: ✓ PASS\nTemplates: ✓ PASS\nDatabase Connection: ✓ PASS\nDatabase Models: ✓ PASS\nOpenAI Connection: ✓ PASS\nRoutes: ✓ PASS\n\nOverall: 7/7 checks passed"
}
```

### Error Report
Retrieve error monitoring report.

```http
GET /admin/error-report
```

**Response**
```json
{
  "status": "success",
  "content": "ERROR MONITORING REPORT\nGenerated: 2025-06-10 11:30:45\n==================================================\n\nSUMMARY (Last 24 hours):\n- Total Errors: 0\n- Error Types: 0\n- Components Affected: 0"
}
```

### Cache Management
Clear application cache.

```http
POST /admin/cache-clear
```

**Response**
```json
{
  "status": "success",
  "message": "Cache cleared successfully"
}
```

### Database Cleanup
Clean up old database records.

```http
POST /admin/database-cleanup
```

**Response**
```json
{
  "status": "success",
  "message": "Cleaned 150 records"
}
```

## Form Submission APIs

### Contact Form
Submit contact form with validation.

```http
POST /contato
Content-Type: application/x-www-form-urlencoded
```

**Request Body**
```
name=João Silva
email=joao.silva@email.com
phone=(27) 99999-9999
subject=Informações sobre processo
message=Gostaria de obter informações sobre o andamento do meu processo.
```

**Response**
- `302`: Redirect with success/error flash message
- `400`: Validation error
- `429`: Rate limit exceeded

### Process Consultation
Submit process number for consultation.

```http
POST /servicos/consulta-processual
Content-Type: application/x-www-form-urlencoded
```

**Request Body**
```
process_number=1234567-89.2024.8.08.0001
```

**Response**
Returns HTML page with consultation results or error message.

## External Integrations

### OpenAI GPT-4o Integration
The system integrates with OpenAI for the chatbot functionality.

**Configuration**
- **Model**: gpt-4o
- **Max Tokens**: 500
- **Temperature**: 0.7
- **Timeout**: 30 seconds

**Rate Limits**
- **Requests**: 500 per hour
- **Tokens**: 30,000 per minute

**Error Handling**
- Network timeout: Fallback to predefined responses
- Rate limit exceeded: Temporary disable with user notification
- API key invalid: Log error and use basic responses

### Database Integration
PostgreSQL database with optimized connection pooling.

**Connection Pool**
- **Size**: 10 connections
- **Max Overflow**: 20 connections
- **Timeout**: 30 seconds
- **Recycle**: 3600 seconds

**Models**
- `Contact`: Contact form submissions
- `NewsItem`: News and announcements
- `ProcessConsultation`: Process consultation logs
- `ChatMessage`: Chatbot conversation history

## Webhook Specifications

### Contact Form Webhook
Triggered when a new contact form is submitted.

**URL**: Configurable via environment variable `CONTACT_WEBHOOK_URL`

**Method**: POST

**Headers**
```
Content-Type: application/json
X-Webhook-Signature: sha256=<signature>
```

**Payload**
```json
{
  "event": "contact_received",
  "timestamp": "2025-06-10T11:30:45Z",
  "data": {
    "id": 123,
    "name": "João Silva",
    "email": "joao.silva@email.com",
    "phone": "(27) 99999-9999",
    "subject": "Informações sobre processo",
    "message": "Gostaria de obter informações...",
    "created_at": "2025-06-10T11:30:45Z"
  }
}
```

### System Alert Webhook
Triggered when system alerts occur.

**URL**: Configurable via environment variable `ALERT_WEBHOOK_URL`

**Payload**
```json
{
  "event": "system_alert",
  "timestamp": "2025-06-10T11:30:45Z",
  "severity": "high|medium|low",
  "component": "database|api|cache|application",
  "message": "High memory usage: 85%",
  "details": {
    "metric": "memory_usage",
    "value": 85,
    "threshold": 80
  }
}
```

## Performance Metrics API

### Real-time Metrics
Get current performance metrics.

```http
GET /admin/metrics
```

**Response**
```json
{
  "response_times": {
    "average": 0.145,
    "maximum": 2.341,
    "minimum": 0.023,
    "count": 1234
  },
  "system": {
    "memory_usage": 45.2,
    "cpu_usage": 23.8
  },
  "requests": {
    "total": 15678,
    "errors": 12,
    "slow_requests": 5
  },
  "timestamp": "2025-06-10T11:30:45Z"
}
```

### Historical Data
Get historical performance data.

```http
GET /admin/metrics/history?period=24h&metric=response_time
```

**Parameters**
- `period`: `1h`, `24h`, `7d`, `30d`
- `metric`: `response_time`, `memory`, `cpu`, `requests`

## Error Codes and Troubleshooting

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `302`: Redirect
- `400`: Bad Request - Invalid input data
- `403`: Forbidden - Access denied
- `404`: Not Found - Resource not found
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - System error
- `503`: Service Unavailable - System maintenance

### Error Response Format
```json
{
  "error": "Description of the error",
  "code": "ERROR_CODE",
  "timestamp": "2025-06-10T11:30:45Z",
  "request_id": "req_123456789"
}
```

### Common Error Codes
- `INVALID_INPUT`: Invalid or missing required fields
- `RATE_LIMIT_EXCEEDED`: Too many requests from IP
- `SYSTEM_UNAVAILABLE`: Temporary system maintenance
- `DATABASE_ERROR`: Database connectivity issues
- `EXTERNAL_API_ERROR`: OpenAI or other external service error

## Rate Limiting Details

### Limits by Endpoint
```
GET /                    : 100 requests/minute
GET /admin/status        : 10 requests/minute
POST /chatbot/api/message: 30 requests/minute
POST /contato            : 10 requests/minute
POST /servicos/*         : 20 requests/minute
```

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1625097600
```

### Rate Limit Exceeded Response
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

## Security Considerations

### CSRF Protection
All forms include CSRF tokens. API requests must include valid tokens in headers:
```
X-CSRFToken: <token_value>
```

### Input Validation
All inputs are validated and sanitized:
- HTML entities escaped
- SQL injection prevention
- XSS protection
- Length limits enforced

### HTTPS Requirements
- Production requires HTTPS
- All cookies use Secure flag
- HSTS headers enforced

## SDK and Libraries

### JavaScript Client
```javascript
class CourtAPIClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async sendChatMessage(message) {
    const response = await fetch(`${this.baseUrl}/chatbot/api/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message })
    });
    return await response.json();
  }

  async checkHealth() {
    const response = await fetch(`${this.baseUrl}/health`);
    return await response.json();
  }
}
```

### Python Client
```python
import requests

class CourtAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def send_chat_message(self, message):
        response = self.session.post(
            f"{self.base_url}/chatbot/api/message",
            json={"message": message}
        )
        return response.json()

    def check_health(self):
        response = self.session.get(f"{self.base_url}/health")
        return response.json()
```

## Testing

### API Testing with curl
```bash
# Health check
curl -X GET https://2varacivel-cariacica.tjes.jus.br/health

# Chatbot message
curl -X POST https://2varacivel-cariacica.tjes.jus.br/chatbot/api/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Como consultar um processo?"}'

# Admin status (requires proper IP)
curl -X GET https://2varacivel-cariacica.tjes.jus.br/admin/status
```

### Load Testing
```bash
# Using Apache Bench
ab -n 1000 -c 10 https://2varacivel-cariacica.tjes.jus.br/

# Using wrk
wrk -t12 -c400 -d30s https://2varacivel-cariacica.tjes.jus.br/
```

## API Versioning

Current version: **v1** (implicit in all endpoints)

Future versions will include version in URL:
- `v2`: `/api/v2/chatbot/message`
- `v3`: `/api/v3/chatbot/message`

## Support and Contact

For API support and integration assistance:
- **Email**: api-suporte@tjes.jus.br
- **Documentation**: Updated automatically with each release
- **Status Page**: https://status.tjes.jus.br
- **SLA**: 99.9% uptime, 4-hour response for critical issues