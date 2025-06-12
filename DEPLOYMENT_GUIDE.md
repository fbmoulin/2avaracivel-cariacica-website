# 🚀 Guia Completo de Deploy - 2ª Vara Cível de Cariacica

<div align="center">

![Deploy Status](https://img.shields.io/badge/Deploy%20Status-Production%20Ready-success?style=for-the-badge)
![Uptime](https://img.shields.io/badge/Uptime-99.9%25-brightgreen?style=for-the-badge)
![Performance](https://img.shields.io/badge/Performance-Optimized-blue?style=for-the-badge)

**Guia Passo-a-Passo para Deploy em Produção**

</div>

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Deploy no Replit](#deploy-no-replit)
- [Deploy Tradicional](#deploy-tradicional)
- [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Monitoramento](#monitoramento)
- [Backup e Recuperação](#backup-e-recuperação)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Este guia apresenta todas as opções de deploy para o sistema da 2ª Vara Cível de Cariacica, desde a plataforma recomendada Replit até configurações tradicionais em servidores dedicados.

### 🏆 Plataformas Suportadas

| **Plataforma** | **Dificuldade** | **Custo** | **Recomendação** |
|:---:|:---:|:---:|:---:|
| **Replit** | ⭐ Fácil | Gratuito/Baixo | ✅ **Recomendado** |
| **Heroku** | ⭐⭐ Médio | Médio | ✅ Alternativa |
| **DigitalOcean** | ⭐⭐⭐ Difícil | Baixo | 🔧 Avançado |
| **AWS/GCP** | ⭐⭐⭐⭐ Muito Difícil | Variável | 🏢 Enterprise |

---

## 📋 Pré-requisitos

### 🔧 Ferramentas Necessárias

```bash
# Ferramentas obrigatórias
Git 2.30+
Python 3.11+
PostgreSQL 12+ (ou acesso a banco na nuvem)

# Opcionais para desenvolvimento
Node.js 18+ (para assets)
Docker 20+ (para containerização)
```

### 🔑 Credenciais Necessárias

- **OpenAI API Key**: Para funcionamento do chatbot
- **Session Secret**: Chave secreta para sessões
- **Database URL**: String de conexão PostgreSQL
- **Email SMTP** (opcional): Para notificações

---

## 🌟 Deploy no Replit (Recomendado)

### ⚡ Deploy Automático

O Replit oferece a solução mais simples e recomendada:

#### 1️⃣ **Preparação**

```bash
# Clone o repositório no Replit
git clone <repository-url>
cd 2vara-civil-cariacica
```

#### 2️⃣ **Configuração de Ambiente**

```bash
# No Replit Shell
cp .env.example .env
```

**Configure as variáveis no painel Secrets:**
```
DATABASE_URL=postgresql://username:password@host:port/database
SESSION_SECRET=sua-chave-secreta-aleatoria-de-32-caracteres
OPENAI_API_KEY=sk-sua-chave-openai-aqui
```

#### 3️⃣ **Deploy**

```bash
# Execute automaticamente
python main.py
```

### 🔧 Configurações Avançadas do Replit

#### **replit.nix**
```nix
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.postgresql
    pkgs.redis
    pkgs.nodejs-18_x
  ];
}
```

#### **.replit**
```toml
[deployment]
run = ["gunicorn", "--bind", "0.0.0.0:5000", "--reload", "main:app"]
deploymentTarget = "cloudrun"

[env]
PYTHONPATH = "$REPL_HOME"
```

### 🌐 Domínio Personalizado

```bash
# Configure domínio customizado no painel Replit
# Exemplo: 2vara-cariacica.com.br
```

---

## 🏢 Deploy Tradicional

### 🐧 Ubuntu/Debian Server

#### 1️⃣ **Preparação do Servidor**

```bash
# Atualize o sistema
sudo apt update && sudo apt upgrade -y

# Instale dependências
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx certbot python3-certbot-nginx
sudo apt install -y git curl htop
```

#### 2️⃣ **Configuração do PostgreSQL**

```bash
# Configure PostgreSQL
sudo -u postgres psql

-- No prompt do PostgreSQL
CREATE DATABASE cariacica_2vara;
CREATE USER app_user WITH ENCRYPTED PASSWORD 'senha_segura_aqui';
GRANT ALL PRIVILEGES ON DATABASE cariacica_2vara TO app_user;
\q
```

#### 3️⃣ **Deploy da Aplicação**

```bash
# Clone e configure
cd /opt
sudo git clone <repository-url> cariacica-app
sudo chown -R $USER:$USER /opt/cariacica-app
cd /opt/cariacica-app

# Ambiente virtual
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Variáveis de ambiente
cp .env.example .env
nano .env  # Configure as variáveis
```

#### 4️⃣ **Configuração do Systemd**

```bash
# Crie o serviço
sudo nano /etc/systemd/system/cariacica-app.service
```

```ini
[Unit]
Description=2ª Vara Cível Cariacica Web App
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/cariacica-app
Environment=PATH=/opt/cariacica-app/venv/bin
ExecStart=/opt/cariacica-app/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 main:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Ative o serviço
sudo systemctl daemon-reload
sudo systemctl enable cariacica-app
sudo systemctl start cariacica-app
sudo systemctl status cariacica-app
```

#### 5️⃣ **Configuração do Nginx**

```bash
sudo nano /etc/nginx/sites-available/cariacica-app
```

```nginx
server {
    listen 80;
    server_name 2vara-cariacica.es.gov.br;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/cariacica-app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Ative a configuração
sudo ln -s /etc/nginx/sites-available/cariacica-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6️⃣ **SSL com Let's Encrypt**

```bash
# Configure SSL automático
sudo certbot --nginx -d 2vara-cariacica.es.gov.br

# Teste renovação automática
sudo certbot renew --dry-run
```

---

## 🐳 Deploy com Docker

### 📦 Dockerfile

```dockerfile
FROM python:3.11-slim

# Dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código da aplicação
COPY . .

# Usuário não-root
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
```

### 🐙 Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://app_user:senha@db:5432/cariacica_2vara
      - SESSION_SECRET=${SESSION_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=cariacica_2vara
      - POSTGRES_USER=app_user
      - POSTGRES_PASSWORD=senha
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

### 🚀 Deploy com Docker

```bash
# Build e execute
docker-compose up -d

# Verifique status
docker-compose ps

# Logs
docker-compose logs -f app
```

---

## 🗄️ Configuração do Banco de Dados

### 🐘 PostgreSQL em Produção

#### **Configurações Recomendadas**

```postgresql
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

-- Conexões
max_connections = 100
```

#### **Otimizações de Performance**

```sql
-- Índices recomendados
CREATE INDEX CONCURRENTLY idx_sessions_expire_date ON sessions(expire_date);
CREATE INDEX CONCURRENTLY idx_chatbot_messages_session ON chatbot_messages(session_id);
CREATE INDEX CONCURRENTLY idx_contact_messages_date ON contact_messages(created_at);

-- Análise de performance
ANALYZE;
```

### ☁️ Bancos em Nuvem

#### **Supabase (Recomendado para Replit)**

```bash
# Configuração no Supabase
1. Crie projeto em supabase.com
2. Copie a Database URL
3. Configure no Replit Secrets:
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
```

#### **ElephantSQL**

```bash
# Plano gratuito disponível
DATABASE_URL=postgres://username:password@hostname:5432/database
```

---

## 🔧 Variáveis de Ambiente

### 📋 Arquivo .env Completo

```bash
# === CONFIGURAÇÕES BÁSICAS ===
FLASK_ENV=production
DEBUG=False
SECRET_KEY=sua-chave-secreta-de-32-caracteres-aqui

# === BANCO DE DADOS ===
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# === SEGURANÇA ===
SESSION_SECRET=outra-chave-secreta-diferente-32-chars
CSRF_ENABLED=True
SECURE_COOKIES=True

# === INTELIGÊNCIA ARTIFICIAL ===
OPENAI_API_KEY=sk-sua-chave-openai-aqui
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=500

# === CACHE (OPCIONAL) ===
REDIS_URL=redis://localhost:6379/0

# === EMAIL (OPCIONAL) ===
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
SMTP_TLS=True

# === MONITORAMENTO ===
SENTRY_DSN=https://sua-chave@sentry.io/projeto
LOG_LEVEL=INFO

# === PERFORMANCE ===
WEB_CONCURRENCY=4
MAX_WORKERS=4
TIMEOUT=30
```

### 🔒 Gerenciamento Seguro de Secrets

#### **Para Replit:**
```bash
# Use o painel Secrets do Replit
# Nunca commite secrets no código
```

#### **Para Servidores:**
```bash
# Use um gerenciador de secrets
sudo snap install vault
# ou
pip install python-dotenv

# Permissões restritivas
chmod 600 .env
chown app:app .env
```

---

## 📊 Monitoramento

### 🔍 Health Checks

```bash
# Script de monitoramento básico
#!/bin/bash
# health-check.sh

URL="https://2vara-cariacica.es.gov.br"

# Verificar se o site responde
if curl -s --head "$URL/health-check" | head -n 1 | grep -q "200 OK"; then
    echo "✅ Site online"
else
    echo "❌ Site offline"
    # Enviar alerta
fi

# Verificar certificado SSL
if openssl s_client -connect 2vara-cariacica.es.gov.br:443 -servername 2vara-cariacica.es.gov.br < /dev/null 2>/dev/null | openssl x509 -checkend 604800 -noout; then
    echo "✅ SSL válido"
else
    echo "⚠️ SSL expira em 7 dias"
fi
```

### 📈 Métricas Avançadas

#### **Prometheus + Grafana**

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
```

#### **Logs Centralizados**

```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    if not app.debug:
        file_handler = RotatingFileHandler(
            'logs/app.log', maxBytes=10240000, backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
```

---

## 💾 Backup e Recuperação

### 🔄 Backup Automático do PostgreSQL

```bash
#!/bin/bash
# backup-db.sh

DB_NAME="cariacica_2vara"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Criar backup
pg_dump $DB_NAME | gzip > "$BACKUP_DIR/backup_$DATE.sql.gz"

# Manter apenas últimos 30 dias
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup criado: backup_$DATE.sql.gz"
```

```bash
# Agendar no crontab
crontab -e

# Backup diário às 2h da manhã
0 2 * * * /scripts/backup-db.sh
```

### 🔧 Restauração

```bash
# Restaurar backup
gunzip -c backup_20241212_020000.sql.gz | psql cariacica_2vara
```

### ☁️ Backup na Nuvem

```bash
#!/bin/bash
# backup-to-s3.sh

aws s3 cp /backups/backup_$(date +%Y%m%d)*.sql.gz s3://cariacica-backups/
```

---

## 🔧 Troubleshooting

### 🚨 Problemas Comuns

#### **Aplicação Não Inicia**

```bash
# Verificar logs
sudo journalctl -u cariacica-app -f

# Verificar portas
sudo netstat -tlnp | grep :5000

# Testar aplicação manualmente
cd /opt/cariacica-app
source venv/bin/activate
python main.py
```

#### **Banco de Dados Inacessível**

```bash
# Testar conexão
psql $DATABASE_URL

# Verificar status PostgreSQL
sudo systemctl status postgresql

# Verificar logs do PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

#### **SSL/HTTPS Problemas**

```bash
# Verificar certificado
openssl s_client -connect 2vara-cariacica.es.gov.br:443

# Renovar certificado
sudo certbot renew

# Verificar configuração Nginx
sudo nginx -t
```

#### **Performance Lenta**

```bash
# Monitor de recursos
htop

# Análise de queries lentas
sudo -u postgres psql -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Cache status
redis-cli info memory
```

### 📞 Suporte de Emergência

#### **Checklist de Emergência**

1. ✅ Verificar status do servidor
2. ✅ Verificar logs de aplicação
3. ✅ Verificar conexão com banco
4. ✅ Verificar SSL/certificados
5. ✅ Verificar espaço em disco
6. ✅ Verificar memória/CPU

#### **Contatos**

- **Suporte Técnico**: suporte@lexintelligentia.com.br
- **Emergência 24h**: +55 (27) 99999-9999
- **Status Page**: status.2vara-cariacica.es.gov.br

### 🔄 Rollback de Emergência

```bash
# Git rollback
git log --oneline -10
git checkout <commit-hash-anterior>

# Restaurar backup
gunzip -c backup_ultima_versao.sql.gz | psql cariacica_2vara

# Reiniciar serviços
sudo systemctl restart cariacica-app nginx
```

---

## ✅ Checklist Final de Deploy

### 🎯 Pré-Deploy

- [ ] ✅ Todas as variáveis de ambiente configuradas
- [ ] ✅ Banco de dados criado e migrado
- [ ] ✅ SSL/TLS configurado
- [ ] ✅ Backup inicial criado
- [ ] ✅ Monitoramento configurado
- [ ] ✅ DNS apontando corretamente

### 🚀 Deploy

- [ ] ✅ Aplicação iniciada sem erros
- [ ] ✅ Health check respondendo
- [ ] ✅ Chatbot funcionando
- [ ] ✅ Formulários enviando emails
- [ ] ✅ Acessibilidade testada
- [ ] ✅ Performance validada

### 📊 Pós-Deploy

- [ ] ✅ Monitoramento ativo
- [ ] ✅ Backup automático funcionando
- [ ] ✅ Logs sendo coletados
- [ ] ✅ Alertas configurados
- [ ] ✅ Documentação atualizada
- [ ] ✅ Equipe treinada

---

<div align="center">

## 🎉 Deploy Concluído com Sucesso!

**Sistema da 2ª Vara Cível de Cariacica Online e Funcionando**

![Success](https://img.shields.io/badge/Status-Online-success?style=for-the-badge)
![Performance](https://img.shields.io/badge/Performance-Otimizada-blue?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Enterprise-red?style=for-the-badge)

*Deploy realizado com padrões enterprise de segurança e performance*

**Desenvolvido por Lex Intelligentia**

</div>