# 🌐 API Reference - 2ª Vara Cível de Cariacica

<div align="center">

![API Status](https://img.shields.io/badge/API-Online-success?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-2.0-blue?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Enterprise%20Grade-red?style=for-the-badge)

**Documentação Completa da API REST**

</div>

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Autenticação](#autenticação)
- [Endpoints Públicos](#endpoints-públicos)
- [Endpoints Administrativos](#endpoints-administrativos)
- [Chatbot API](#chatbot-api)
- [Sistema de Arquivos](#sistema-de-arquivos)
- [Códigos de Resposta](#códigos-de-resposta)
- [Rate Limiting](#rate-limiting)
- [Exemplos de Integração](#exemplos-de-integração)

---

## 🎯 Visão Geral

A API da 2ª Vara Cível de Cariacica fornece acesso programático a todos os serviços digitais do sistema, incluindo consultas processuais, agendamentos, chatbot inteligente e serviços administrativos.

### 🔧 Características Técnicas

- **Protocolo**: HTTPS obrigatório
- **Formato**: JSON (application/json)
- **Autenticação**: Session-based + CSRF tokens
- **Rate Limiting**: 100 requests/hora por IP
- **Versionamento**: URL path (/api/v2/)
- **Encoding**: UTF-8

### 🌐 Base URL

```
Produção: https://2vara-cariacica.replit.app
Desenvolvimento: http://localhost:5000
```

---

## 🔐 Autenticação

### 🎫 Tokens CSRF

Todos os endpoints POST/PUT/DELETE requerem token CSRF:

```http
POST /contato HTTP/1.1
Content-Type: application/x-www-form-urlencoded
X-CSRFToken: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

csrf_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...&name=João
```

### 🍪 Sessões

```javascript
// Obter token CSRF
fetch('/csrf-token')
  .then(response => response.json())
  .then(data => {
    const csrfToken = data.csrf_token;
    // Usar em requests subsequentes
  });
```

---

## 🌍 Endpoints Públicos

### 🏠 **Página Inicial**

#### `GET /`
Retorna a página inicial do sistema.

**Response:**
```html
<!DOCTYPE html>
<html>
  <head>
    <title>2ª Vara Cível de Cariacica</title>
    <!-- HTML da página -->
  </head>
</html>
```

### 📄 **Páginas de Conteúdo**

#### `GET /sobre`
Informações sobre a vara judicial.

#### `GET /servicos`
Lista todos os serviços disponíveis.

#### `GET /faq`
Perguntas frequentes categorizadas.

**Response Example:**
```json
{
  "categories": [
    {
      "name": "Processos",
      "questions": [
        {
          "question": "Como consultar meu processo?",
          "answer": "Acesse a seção de consulta processual..."
        }
      ]
    }
  ]
}
```

### 📞 **Contato**

#### `GET /contato`
Formulário de contato.

#### `POST /contato`
Envio de mensagem de contato.

**Request Body:**
```json
{
  "csrf_token": "token_csrf_aqui",
  "name": "João Silva",
  "email": "joao@email.com",
  "phone": "(27) 99999-9999",
  "subject": "consulta_processo",
  "message": "Gostaria de consultar o andamento do processo...",
  "process_number": "1234567-89.2024.8.08.0000",
  "preferred_contact": "email",
  "privacy": true
}
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Mensagem enviada com sucesso!",
  "protocol": "MSG-2024-001234",
  "estimated_response": "2 dias úteis"
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "Dados inválidos",
  "errors": [
    {
      "field": "email",
      "message": "Email inválido"
    }
  ]
}
```

---

## 🤖 Chatbot API

### 💬 **Enviar Mensagem**

#### `POST /chatbot/message`
Envia mensagem para o chatbot inteligente.

**Request Body:**
```json
{
  "message": "Como consultar um processo?",
  "session_id": "optional_session_id",
  "context": {
    "page": "consulta_processual",
    "user_type": "cidadao"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "response": {
    "message": "Para consultar um processo, você pode usar nossa ferramenta online...",
    "suggestions": [
      "Consultar processo",
      "Agendar atendimento",
      "Mais informações"
    ],
    "actions": [
      {
        "type": "link",
        "label": "Consultar Agora",
        "url": "/consulta-processual"
      }
    ]
  },
  "session_id": "sess_abc123def456",
  "timestamp": "2024-06-12T10:30:00Z"
}
```

### 📜 **Histórico de Conversas**

#### `GET /chatbot/history/{session_id}`
Recupera histórico de conversas.

**Response:**
```json
{
  "session_id": "sess_abc123def456",
  "messages": [
    {
      "id": "msg_001",
      "type": "user",
      "message": "Como consultar um processo?",
      "timestamp": "2024-06-12T10:29:45Z"
    },
    {
      "id": "msg_002",
      "type": "bot",
      "message": "Para consultar um processo...",
      "timestamp": "2024-06-12T10:30:00Z"
    }
  ],
  "total_messages": 2
}
```

### 🔄 **Limpar Sessão**

#### `DELETE /chatbot/session/{session_id}`
Remove histórico de uma sessão específica.

---

## ⚙️ Endpoints Administrativos

### 🔐 **Acesso Restrito**

Endpoints administrativos requerem autenticação administrativa:

```http
GET /admin/status HTTP/1.1
Authorization: Session admin_session_id
```

### 📊 **Status do Sistema**

#### `GET /admin/status`
Informações detalhadas do sistema.

**Response:**
```json
{
  "status": "healthy",
  "uptime": "15 days, 3 hours",
  "system_info": {
    "memory_usage": "45%",
    "cpu_usage": "12%",
    "disk_usage": "68%",
    "active_connections": 23,
    "response_time_avg": "245ms"
  },
  "services": {
    "database": "connected",
    "chatbot": "operational",
    "cache": "memory_fallback"
  },
  "security": {
    "blocked_ips": 3,
    "failed_logins": 0,
    "rate_limits_hit": 12
  }
}
```

### 🔍 **Health Check**

#### `GET /admin/health-check`
Verificação rápida de saúde do sistema.

**Response:**
```json
{
  "status": "success",
  "checks": {
    "database": "✅ Connected",
    "chatbot_api": "✅ Operational", 
    "file_system": "✅ Accessible",
    "memory": "✅ Normal (45%)",
    "cpu": "✅ Normal (12%)"
  },
  "timestamp": "2024-06-12T10:30:00Z",
  "response_time": "23ms"
}
```

### 📈 **Métricas**

#### `GET /admin/metrics`
Métricas detalhadas de performance.

**Response:**
```json
{
  "requests": {
    "total": 15420,
    "success": 14980,
    "errors": 440,
    "success_rate": "97.1%"
  },
  "chatbot": {
    "total_messages": 2340,
    "avg_response_time": "1.2s",
    "satisfaction_rate": "4.8/5.0"
  },
  "security": {
    "blocked_requests": 156,
    "csrf_failures": 12,
    "rate_limit_hits": 89
  },
  "performance": {
    "avg_response_time": "245ms",
    "slowest_endpoint": "/consulta-processual",
    "fastest_endpoint": "/health-check"
  }
}
```

### 📝 **Logs**

#### `GET /admin/logs`
Acesso aos logs do sistema.

**Query Parameters:**
- `level`: debug, info, warning, error
- `limit`: número de linhas (default: 100)
- `since`: timestamp ISO 8601

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-06-12T10:29:45Z",
      "level": "INFO",
      "component": "chatbot",
      "message": "Message processed successfully",
      "details": {
        "session_id": "sess_abc123",
        "response_time": "1.2s"
      }
    }
  ],
  "total": 1250,
  "filtered": 100
}
```

---

## 📁 Sistema de Arquivos

### 📤 **Upload de Arquivos**

#### `POST /upload`
Upload de documentos e anexos.

**Request (multipart/form-data):**
```http
POST /upload HTTP/1.1
Content-Type: multipart/form-data; boundary=----boundary

------boundary
Content-Disposition: form-data; name="csrf_token"

eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
------boundary
Content-Disposition: form-data; name="file"; filename="documento.pdf"
Content-Type: application/pdf

[binary file data]
------boundary--
```

**Response:**
```json
{
  "status": "success",
  "file": {
    "id": "file_abc123def456",
    "filename": "documento.pdf",
    "size": 2048576,
    "mime_type": "application/pdf",
    "upload_date": "2024-06-12T10:30:00Z",
    "url": "/files/file_abc123def456",
    "checksum": "sha256:abc123..."
  }
}
```

### 📥 **Download de Arquivos**

#### `GET /files/{file_id}`
Download de arquivo específico.

**Response Headers:**
```http
Content-Type: application/pdf
Content-Disposition: attachment; filename="documento.pdf"
Content-Length: 2048576
```

---

## 🚨 Códigos de Resposta

### ✅ **Códigos de Sucesso**

| Código | Nome | Descrição |
|:---:|:---|:---|
| `200` | OK | Requisição processada com sucesso |
| `201` | Created | Recurso criado com sucesso |
| `204` | No Content | Operação bem-sucedida sem retorno |

### ⚠️ **Códigos de Erro do Cliente**

| Código | Nome | Descrição |
|:---:|:---|:---|
| `400` | Bad Request | Dados inválidos na requisição |
| `401` | Unauthorized | Autenticação necessária |
| `403` | Forbidden | Acesso negado |
| `404` | Not Found | Recurso não encontrado |
| `409` | Conflict | Conflito com estado atual |
| `422` | Unprocessable Entity | Dados válidos mas processamento impossível |
| `429` | Too Many Requests | Rate limit excedido |

### 🔥 **Códigos de Erro do Servidor**

| Código | Nome | Descrição |
|:---:|:---|:---|
| `500` | Internal Server Error | Erro interno do servidor |
| `502` | Bad Gateway | Erro de gateway |
| `503` | Service Unavailable | Serviço temporariamente indisponível |
| `504` | Gateway Timeout | Timeout de gateway |

### 📋 **Formato de Erro Padrão**

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Dados de entrada inválidos",
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "Formato de email inválido"
      }
    ]
  },
  "timestamp": "2024-06-12T10:30:00Z",
  "request_id": "req_abc123def456"
}
```

---

## 🚦 Rate Limiting

### 📊 **Limites por Endpoint**

| Endpoint | Limite | Janela | Escopo |
|:---|:---:|:---:|:---:|
| `/contato` | 5 req | 15 min | IP |
| `/chatbot/message` | 30 req | 5 min | Session |
| `/upload` | 10 req | 1 hora | IP |
| `Geral` | 100 req | 1 hora | IP |

### 📈 **Headers de Rate Limit**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
X-RateLimit-Scope: ip
```

### ⚠️ **Resposta de Rate Limit Excedido**

```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Muitas requisições. Tente novamente em 15 minutos.",
    "retry_after": 900
  },
  "timestamp": "2024-06-12T10:30:00Z"
}
```

---

## 💻 Exemplos de Integração

### 🐍 **Python**

```python
import requests
import json

class CariacicaAPI:
    def __init__(self, base_url="https://2vara-cariacica.replit.app"):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        
    def get_csrf_token(self):
        """Obtém token CSRF"""
        response = self.session.get(f"{self.base_url}/csrf-token")
        self.csrf_token = response.json()["csrf_token"]
        return self.csrf_token
    
    def send_contact_message(self, name, email, message, subject="geral"):
        """Envia mensagem de contato"""
        if not self.csrf_token:
            self.get_csrf_token()
            
        data = {
            "csrf_token": self.csrf_token,
            "name": name,
            "email": email,
            "message": message,
            "subject": subject,
            "privacy": True
        }
        
        response = self.session.post(
            f"{self.base_url}/contato",
            data=data
        )
        return response.json()
    
    def chat_with_bot(self, message, session_id=None):
        """Conversa com o chatbot"""
        data = {
            "message": message,
            "session_id": session_id
        }
        
        response = self.session.post(
            f"{self.base_url}/chatbot/message",
            json=data
        )
        return response.json()

# Exemplo de uso
api = CariacicaAPI()

# Enviar mensagem de contato
result = api.send_contact_message(
    name="João Silva",
    email="joao@email.com",
    message="Gostaria de consultar meu processo",
    subject="consulta_processo"
)

print(f"Protocolo: {result['protocol']}")

# Conversar com chatbot
chat_response = api.chat_with_bot("Como consultar um processo?")
print(f"Bot: {chat_response['response']['message']}")
```

### 🟨 **JavaScript/Node.js**

```javascript
const axios = require('axios');

class CariacicaAPI {
  constructor(baseURL = 'https://2vara-cariacica.replit.app') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    this.csrfToken = null;
  }

  async getCsrfToken() {
    const response = await this.client.get('/csrf-token');
    this.csrfToken = response.data.csrf_token;
    return this.csrfToken;
  }

  async sendContactMessage(data) {
    if (!this.csrfToken) {
      await this.getCsrfToken();
    }

    const formData = new URLSearchParams({
      csrf_token: this.csrfToken,
      ...data
    });

    const response = await this.client.post('/contato', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    return response.data;
  }

  async chatWithBot(message, sessionId = null) {
    const response = await this.client.post('/chatbot/message', {
      message,
      session_id: sessionId
    });

    return response.data;
  }
}

// Exemplo de uso
(async () => {
  const api = new CariacicaAPI();

  try {
    // Enviar mensagem
    const result = await api.sendContactMessage({
      name: 'Maria Santos',
      email: 'maria@email.com',
      message: 'Preciso de informações sobre agendamento',
      subject: 'agendamento',
      privacy: true
    });

    console.log(`Protocolo: ${result.protocol}`);

    // Chat com bot
    const chatResponse = await api.chatWithBot('Como agendar atendimento?');
    console.log(`Bot: ${chatResponse.response.message}`);

  } catch (error) {
    console.error('Erro:', error.response?.data || error.message);
  }
})();
```

### 🌐 **Frontend JavaScript**

```javascript
class CariacicaWebAPI {
  constructor() {
    this.baseURL = window.location.origin;
    this.csrfToken = null;
  }

  async getCsrfToken() {
    const response = await fetch(`${this.baseURL}/csrf-token`);
    const data = await response.json();
    this.csrfToken = data.csrf_token;
    return this.csrfToken;
  }

  async sendContactForm(formData) {
    if (!this.csrfToken) {
      await this.getCsrfToken();
    }

    formData.append('csrf_token', this.csrfToken);

    const response = await fetch(`${this.baseURL}/contato`, {
      method: 'POST',
      body: formData
    });

    return await response.json();
  }

  async chatMessage(message, sessionId = null) {
    const response = await fetch(`${this.baseURL}/chatbot/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message,
        session_id: sessionId
      })
    });

    return await response.json();
  }
}

// Uso em formulário
document.getElementById('contactForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const api = new CariacicaWebAPI();
  const formData = new FormData(e.target);
  
  try {
    const result = await api.sendContactForm(formData);
    
    if (result.status === 'success') {
      alert(`Mensagem enviada! Protocolo: ${result.protocol}`);
    } else {
      alert(`Erro: ${result.message}`);
    }
  } catch (error) {
    console.error('Erro ao enviar:', error);
  }
});
```

---

## 🔧 Configuração de Desenvolvimento

### 🛠️ **Setup Local**

```bash
# Clone o repositório
git clone <repository-url>
cd 2vara-civil-cariacica

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dependências
pip install -r requirements.txt

# Variáveis de ambiente
cp .env.example .env
# Configure: DATABASE_URL, SESSION_SECRET, OPENAI_API_KEY

# Executar
python main.py
```

### 🧪 **Teste da API**

```bash
# Teste básico
curl -X GET http://localhost:5000/health-check

# Teste com token CSRF
curl -X GET http://localhost:5000/csrf-token
curl -X POST http://localhost:5000/contato \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "csrf_token=TOKEN&name=Test&email=test@email.com&message=Test"
```

---

## 📞 Suporte Técnico

### 🆘 **Contato para Desenvolvedores**

- **Email**: dev@2vara.cariacica.es.gov.br
- **Documentação**: [/api/docs](/api/docs)
- **Status Page**: [/admin/status](/admin/status)

### 📚 **Recursos Adicionais**

- [Postman Collection](./postman_collection.json)
- [OpenAPI Spec](./openapi.yaml)
- [SDK Python](./sdk/python/)
- [SDK JavaScript](./sdk/javascript/)

---

<div align="center">

**API versão 2.0 - Última atualização: 12/06/2025**

*Desenvolvido por Lex Intelligentia*

</div>