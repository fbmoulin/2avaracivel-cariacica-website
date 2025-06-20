#!/bin/bash
# Script de configuração para migração Hostinger
# Execute: chmod +x setup_hostinger.sh && ./setup_hostinger.sh

echo "=== CONFIGURAÇÃO HOSTINGER ==="
echo

# Verificar dependências
echo "1. Verificando dependências..."

if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 não encontrado"
    exit 1
fi

if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo "⚠ psycopg2 não instalado, instalando..."
    pip install psycopg2-binary
fi

echo "✓ Dependências verificadas"

# Configurar variáveis de ambiente
echo
echo "2. Configurar credenciais do Hostinger"
echo

read -p "Host do Hostinger (ex: sql123.hostinger.com): " HOSTINGER_HOST
read -p "Porta (geralmente 5432): " HOSTINGER_PORT
read -p "Nome da base de dados: " HOSTINGER_DB
read -p "Usuário: " HOSTINGER_USER
read -s -p "Senha: " HOSTINGER_PASS
echo

# Construir URL da base de dados
HOSTINGER_URL="postgresql://${HOSTINGER_USER}:${HOSTINGER_PASS}@${HOSTINGER_HOST}:${HOSTINGER_PORT}/${HOSTINGER_DB}"

# Testar conexão
echo
echo "3. Testando conexão com Hostinger..."

python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('$HOSTINGER_URL')
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()[0]
    print(f'✓ Conexão bem-sucedida: {version[:50]}...')
    conn.close()
except Exception as e:
    print(f'✗ Erro de conexão: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "Erro na conexão. Verifique as credenciais."
    exit 1
fi

# Criar arquivo .env.hostinger
echo
echo "4. Criando arquivo de configuração..."

cat > .env.hostinger << EOF
# Configuração Hostinger
HOSTINGER_DATABASE_URL=$HOSTINGER_URL

# Para usar após migração:
# DATABASE_URL=$HOSTINGER_URL

# Outras variáveis necessárias
SESSION_SECRET=$(openssl rand -hex 32)
FLASK_ENV=production
EOF

echo "✓ Arquivo .env.hostinger criado"

# Instruções finais
echo
echo "=== PRÓXIMOS PASSOS ==="
echo
echo "1. Carregar configuração:"
echo "   source .env.hostinger"
echo
echo "2. Executar migração:"
echo "   python3 scripts/migrate_to_hostinger.py"
echo
echo "3. Após migração bem-sucedida:"
echo "   export DATABASE_URL=\$HOSTINGER_DATABASE_URL"
echo
echo "4. Testar aplicação:"
echo "   python3 main.py"
echo

# Perguntar se deve executar migração
read -p "Executar migração agora? (s/N): " RUN_MIGRATION

if [ "$RUN_MIGRATION" = "s" ] || [ "$RUN_MIGRATION" = "S" ]; then
    echo
    echo "Executando migração..."
    source .env.hostinger
    export HOSTINGER_DATABASE_URL=$HOSTINGER_URL
    python3 scripts/migrate_to_hostinger.py
fi

echo
echo "Configuração concluída!"