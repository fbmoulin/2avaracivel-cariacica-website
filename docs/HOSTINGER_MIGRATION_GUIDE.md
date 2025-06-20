# Guia de Migração para Hostinger

## Pré-requisitos

### 1. Informações do Hostinger
Você precisará das seguintes informações do seu plano Hostinger:
- **Host**: Normalmente `sqlxxx.hostinger.com`
- **Porta**: Geralmente `3306` (MySQL) ou `5432` (PostgreSQL)
- **Nome da Base de Dados**: Criada no painel do Hostinger
- **Usuário**: Criado no painel do Hostinger
- **Senha**: Definida no painel do Hostinger

### 2. Acesso ao Painel Hostinger
1. Entre no painel de controle Hostinger
2. Vá para "Bases de Dados" ou "Databases"
3. Crie uma nova base de dados PostgreSQL ou MySQL
4. Anote as credenciais de acesso

## Opção 1: Migração Manual (Recomendado)

### Passo 1: Preparar os Dados Atuais

```bash
# 1. Fazer backup dos dados importantes
python -c "
from app import create_app
from models import Contact, NewsItem, AssessorMeeting, ProcessConsultation
app = create_app()
with app.app_context():
    # Exportar contactos
    contacts = Contact.query.all()
    print(f'Contactos: {len(contacts)}')
    
    # Exportar notícias
    news = NewsItem.query.all()
    print(f'Notícias: {len(news)}')
    
    # Exportar agendamentos
    meetings = AssessorMeeting.query.all()
    print(f'Agendamentos: {len(meetings)}')
"
```

### Passo 2: Configurar Variáveis de Ambiente

Crie um arquivo `.env` com as credenciais do Hostinger:

```env
# Hostinger Database Configuration
DATABASE_URL=postgresql://usuario:senha@sqlxxx.hostinger.com:5432/nome_da_base

# Ou para MySQL:
# DATABASE_URL=mysql://usuario:senha@sqlxxx.hostinger.com:3306/nome_da_base

# Outras variáveis necessárias
SESSION_SECRET=sua_chave_secreta_aqui
OPENAI_API_KEY=sua_chave_openai_aqui
```

### Passo 3: Testar Conexão

```python
# Script de teste de conexão
import os
import psycopg2  # ou pymysql para MySQL

def test_hostinger_connection():
    try:
        # Para PostgreSQL
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        print(f"Conexão bem-sucedida: {result[0]}")
        conn.close()
        return True
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    test_hostinger_connection()
```

### Passo 4: Migrar Estrutura da Base de Dados

```python
# Script para criar tabelas no Hostinger
from optimized_app import create_optimized_app
from optimized_database import create_optimized_tables

def migrate_schema():
    app = create_optimized_app()
    with app.app_context():
        # Criar todas as tabelas
        create_optimized_tables(app)
        print("Estrutura da base de dados criada com sucesso!")

if __name__ == "__main__":
    migrate_schema()
```

### Passo 5: Migrar Dados

```python
# Script de migração de dados
import json
from datetime import datetime
from optimized_app import create_optimized_app
from optimized_models import Contact, NewsItem, AssessorMeeting

def export_current_data():
    """Exportar dados atuais para JSON"""
    # Código para exportar dados da base atual
    pass

def import_to_hostinger():
    """Importar dados para Hostinger"""
    app = create_optimized_app()
    with app.app_context():
        # Importar dados do backup
        pass

if __name__ == "__main__":
    export_current_data()
    import_to_hostinger()
```

## Opção 2: Migração Automática com pg_dump/mysqldump

### Para PostgreSQL:

```bash
# 1. Fazer dump da base atual
pg_dump $DATABASE_URL_ATUAL > backup_database.sql

# 2. Restaurar no Hostinger
psql $DATABASE_URL_HOSTINGER < backup_database.sql
```

### Para MySQL:

```bash
# 1. Fazer dump da base atual
mysqldump -h host_atual -u usuario_atual -p nome_base > backup_database.sql

# 2. Restaurar no Hostinger
mysql -h sqlxxx.hostinger.com -u usuario_hostinger -p nome_base_hostinger < backup_database.sql
```

## Configuração da Aplicação

### 1. Atualizar config.py

```python
class ProductionConfig(Config):
    """Configuração para produção no Hostinger"""
    DEBUG = False
    TESTING = False
    
    # Configuração da base de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'pool_timeout': 45,
        'max_overflow': 20,
        'pool_size': 10,
        'pool_reset_on_return': 'commit',
        'echo': False,
        'connect_args': {
            'sslmode': 'require'  # Para PostgreSQL
        }
    }
```

### 2. Configurar SSL (se necessário)

Para conexões seguras com o Hostinger:

```python
# No config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'connect_args': {
        'sslmode': 'require',
        'sslcert': 'client-cert.pem',
        'sslkey': 'client-key.pem',
        'sslrootcert': 'server-ca.pem'
    }
}
```

## Scripts de Verificação

### Verificar Migração

```python
def verify_migration():
    """Verificar se a migração foi bem-sucedida"""
    app = create_optimized_app()
    with app.app_context():
        from optimized_models import Contact, NewsItem, AssessorMeeting
        
        # Verificar contagem de registos
        contacts = Contact.query.count()
        news = NewsItem.query.count()
        meetings = AssessorMeeting.query.count()
        
        print(f"Contactos migrados: {contacts}")
        print(f"Notícias migradas: {news}")
        print(f"Agendamentos migrados: {meetings}")
        
        # Testar funcionalidades
        health_check = requests.get("http://localhost:5000/health")
        print(f"Status da aplicação: {health_check.status_code}")
```

## Considerações Importantes

### 1. Limitações do Hostinger
- Verifique os limites de conexões simultâneas
- Confirme o espaço de armazenamento disponível
- Verifique se suporta PostgreSQL (alguns planos só MySQL)

### 2. Performance
- Configure índices apropriados após migração
- Otimize consultas para o ambiente Hostinger
- Configure cache adequadamente

### 3. Segurança
- Use sempre conexões SSL
- Configure firewall se disponível
- Mantenha credenciais seguras

### 4. Backup
- Configure backups automáticos no Hostinger
- Mantenha cópias locais importantes
- Teste restauração periodicamente

## Resolução de Problemas

### Erro de Conexão SSL
```python
# Adicionar ao DATABASE_URL
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

### Timeout de Conexão
```python
# Aumentar timeout no config
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_timeout': 60,
    'pool_recycle': 3600
}
```

### Charset/Encoding
```python
# Para MySQL
DATABASE_URL=mysql://user:pass@host:3306/db?charset=utf8mb4
```

## Pós-Migração

1. **Testar todas as funcionalidades**
2. **Configurar monitorização**
3. **Documentar nova configuração**
4. **Treinar equipa se necessário**
5. **Configurar alertas para problemas**

Este guia cobre os cenários mais comuns. Se encontrar problemas específicos, pode adaptar os scripts conforme necessário.