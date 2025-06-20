#!/usr/bin/env python3
"""
Script de Migração para Hostinger
Migra dados da base atual para o Hostinger de forma segura
"""
import os
import sys
import json
import psycopg2
from datetime import datetime
from urllib.parse import urlparse

def parse_database_url(url):
    """Extrai componentes da URL da base de dados"""
    parsed = urlparse(url)
    return {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path[1:],  # Remove leading /
        'username': parsed.username,
        'password': parsed.password
    }

def test_connection(db_url, name="Database"):
    """Testa conexão com a base de dados"""
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        conn.close()
        print(f"✓ {name} conectada: {version[:50]}...")
        return True
    except Exception as e:
        print(f"✗ Erro ao conectar {name}: {e}")
        return False

def export_data_to_json(source_url, backup_file="backup_data.json"):
    """Exporta dados da base atual para JSON"""
    print(f"Exportando dados para {backup_file}...")
    
    try:
        conn = psycopg2.connect(source_url)
        cursor = conn.cursor()
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'source_url': source_url.split('@')[1] if '@' in source_url else 'local',
            'tables': {}
        }
        
        # Lista de tabelas para backup
        tables = [
            'contact',
            'news_item', 
            'process_consultation',
            'assessor_meeting',
            'chat_message'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                backup_data['tables'][table] = {
                    'columns': columns,
                    'rows': []
                }
                
                for row in rows:
                    # Converter datetime para string
                    converted_row = []
                    for item in row:
                        if isinstance(item, datetime):
                            converted_row.append(item.isoformat())
                        else:
                            converted_row.append(item)
                    backup_data['tables'][table]['rows'].append(converted_row)
                
                print(f"✓ {table}: {len(rows)} registos exportados")
                
            except Exception as e:
                print(f"⚠ Erro ao exportar {table}: {e}")
        
        conn.close()
        
        # Salvar JSON
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Backup criado: {backup_file}")
        return backup_file
        
    except Exception as e:
        print(f"✗ Erro durante exportação: {e}")
        return None

def create_tables_hostinger(hostinger_url):
    """Cria estrutura de tabelas no Hostinger"""
    print("Criando estrutura de tabelas no Hostinger...")
    
    # SQL para criar tabelas (baseado nos modelos optimizados)
    create_tables_sql = """
    -- Tabela de contactos
    CREATE TABLE IF NOT EXISTS contact (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(120) NOT NULL,
        phone VARCHAR(20),
        subject VARCHAR(200) NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address VARCHAR(45),
        user_agent VARCHAR(500),
        status VARCHAR(20) DEFAULT 'pending',
        priority VARCHAR(10) DEFAULT 'normal'
    );
    
    CREATE INDEX IF NOT EXISTS idx_contact_created_at ON contact(created_at);
    CREATE INDEX IF NOT EXISTS idx_contact_email ON contact(email);
    
    -- Tabela de notícias
    CREATE TABLE IF NOT EXISTS news_item (
        id SERIAL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        content TEXT NOT NULL,
        summary VARCHAR(500),
        published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        is_featured BOOLEAN DEFAULT FALSE,
        author VARCHAR(100),
        category VARCHAR(50) DEFAULT 'geral',
        view_count INTEGER DEFAULT 0
    );
    
    CREATE INDEX IF NOT EXISTS idx_news_published_active ON news_item(published_at, is_active);
    CREATE INDEX IF NOT EXISTS idx_news_featured ON news_item(is_featured);
    
    -- Tabela de consulta processual
    CREATE TABLE IF NOT EXISTS process_consultation (
        id SERIAL PRIMARY KEY,
        process_number VARCHAR(50) NOT NULL,
        requester_name VARCHAR(100) NOT NULL,
        requester_cpf VARCHAR(14) NOT NULL,
        consulted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address VARCHAR(45),
        user_agent VARCHAR(500),
        consultation_type VARCHAR(20) DEFAULT 'public'
    );
    
    CREATE INDEX IF NOT EXISTS idx_process_number ON process_consultation(process_number);
    CREATE INDEX IF NOT EXISTS idx_consultation_date ON process_consultation(consulted_at);
    
    -- Tabela de agendamentos
    CREATE TABLE IF NOT EXISTS assessor_meeting (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(100) NOT NULL,
        document VARCHAR(20) NOT NULL,
        email VARCHAR(120) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        process_number VARCHAR(50),
        meeting_type VARCHAR(30) NOT NULL,
        meeting_subject TEXT NOT NULL,
        preferred_date DATE NOT NULL,
        preferred_time VARCHAR(10) NOT NULL,
        alternative_times TEXT,
        scheduled_date TIMESTAMP,
        assessor_name VARCHAR(100),
        meeting_room VARCHAR(50),
        meeting_link VARCHAR(500),
        status VARCHAR(20) DEFAULT 'pending',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        confirmation_token VARCHAR(100) UNIQUE,
        reminder_sent BOOLEAN DEFAULT FALSE,
        priority VARCHAR(10) DEFAULT 'normal'
    );
    
    CREATE INDEX IF NOT EXISTS idx_meeting_date_status ON assessor_meeting(preferred_date, status);
    CREATE INDEX IF NOT EXISTS idx_meeting_email ON assessor_meeting(email);
    
    -- Tabela de mensagens do chatbot
    CREATE TABLE IF NOT EXISTS chat_message (
        id SERIAL PRIMARY KEY,
        user_message TEXT NOT NULL,
        bot_response TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        session_id VARCHAR(100),
        response_time FLOAT,
        confidence_score FLOAT,
        response_type VARCHAR(20) DEFAULT 'openai'
    );
    
    CREATE INDEX IF NOT EXISTS idx_chat_session_time ON chat_message(session_id, created_at);
    CREATE INDEX IF NOT EXISTS idx_chat_created_at ON chat_message(created_at);
    """
    
    try:
        conn = psycopg2.connect(hostinger_url)
        cursor = conn.cursor()
        
        # Executar cada comando SQL
        for statement in create_tables_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        conn.close()
        print("✓ Estrutura de tabelas criada no Hostinger")
        return True
        
    except Exception as e:
        print(f"✗ Erro ao criar tabelas: {e}")
        return False

def import_data_from_json(hostinger_url, backup_file="backup_data.json"):
    """Importa dados do JSON para o Hostinger"""
    print(f"Importando dados de {backup_file}...")
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        conn = psycopg2.connect(hostinger_url)
        cursor = conn.cursor()
        
        for table_name, table_data in backup_data['tables'].items():
            if not table_data['rows']:
                print(f"⚠ {table_name}: sem dados para importar")
                continue
            
            columns = table_data['columns']
            
            # Preparar placeholders para SQL
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            
            insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            try:
                cursor.executemany(insert_sql, table_data['rows'])
                conn.commit()
                print(f"✓ {table_name}: {len(table_data['rows'])} registos importados")
                
            except Exception as e:
                print(f"✗ Erro ao importar {table_name}: {e}")
                conn.rollback()
        
        conn.close()
        print("✓ Importação concluída")
        return True
        
    except Exception as e:
        print(f"✗ Erro durante importação: {e}")
        return False

def verify_migration(source_url, hostinger_url):
    """Verifica se a migração foi bem-sucedida"""
    print("Verificando migração...")
    
    tables = ['contact', 'news_item', 'process_consultation', 'assessor_meeting', 'chat_message']
    
    try:
        # Conectar às duas bases
        source_conn = psycopg2.connect(source_url)
        hostinger_conn = psycopg2.connect(hostinger_url)
        
        source_cursor = source_conn.cursor()
        hostinger_cursor = hostinger_conn.cursor()
        
        all_match = True
        
        for table in tables:
            try:
                # Contar registos na origem
                source_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                source_count = source_cursor.fetchone()[0]
                
                # Contar registos no destino
                hostinger_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                hostinger_count = hostinger_cursor.fetchone()[0]
                
                if source_count == hostinger_count:
                    print(f"✓ {table}: {source_count} = {hostinger_count}")
                else:
                    print(f"✗ {table}: {source_count} ≠ {hostinger_count}")
                    all_match = False
                    
            except Exception as e:
                print(f"⚠ Erro ao verificar {table}: {e}")
                all_match = False
        
        source_conn.close()
        hostinger_conn.close()
        
        if all_match:
            print("✓ Migração verificada com sucesso!")
        else:
            print("⚠ Algumas discrepâncias encontradas")
        
        return all_match
        
    except Exception as e:
        print(f"✗ Erro durante verificação: {e}")
        return False

def main():
    """Função principal da migração"""
    print("=== MIGRAÇÃO PARA HOSTINGER ===")
    print()
    
    # Verificar variáveis de ambiente
    source_url = os.environ.get('DATABASE_URL')
    hostinger_url = os.environ.get('HOSTINGER_DATABASE_URL')
    
    if not source_url:
        print("✗ DATABASE_URL não definida (base atual)")
        sys.exit(1)
    
    if not hostinger_url:
        print("✗ HOSTINGER_DATABASE_URL não definida")
        print("Defina: export HOSTINGER_DATABASE_URL='postgresql://user:pass@host:5432/db'")
        sys.exit(1)
    
    # Testar conexões
    print("1. Testando conexões...")
    if not test_connection(source_url, "Base atual"):
        sys.exit(1)
    
    if not test_connection(hostinger_url, "Hostinger"):
        sys.exit(1)
    
    # Confirmar migração
    print("\n2. Confirmar migração")
    source_info = parse_database_url(source_url)
    hostinger_info = parse_database_url(hostinger_url)
    
    print(f"Origem: {source_info['host']}/{source_info['database']}")
    print(f"Destino: {hostinger_info['host']}/{hostinger_info['database']}")
    
    confirm = input("\nProsseguir com a migração? (s/N): ")
    if confirm.lower() != 's':
        print("Migração cancelada")
        sys.exit(0)
    
    # Executar migração
    print("\n3. Exportando dados...")
    backup_file = export_data_to_json(source_url)
    if not backup_file:
        sys.exit(1)
    
    print("\n4. Criando estrutura no Hostinger...")
    if not create_tables_hostinger(hostinger_url):
        sys.exit(1)
    
    print("\n5. Importando dados...")
    if not import_data_from_json(hostinger_url, backup_file):
        sys.exit(1)
    
    print("\n6. Verificando migração...")
    if verify_migration(source_url, hostinger_url):
        print("\n✓ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"\nPróximo passo: Atualizar DATABASE_URL para:")
        print(f"export DATABASE_URL='{hostinger_url}'")
    else:
        print("\n⚠ Migração completada com avisos. Verifique os dados.")

if __name__ == "__main__":
    main()