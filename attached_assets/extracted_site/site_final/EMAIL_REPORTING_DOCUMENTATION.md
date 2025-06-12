# Sistema de Relatórios Automáticos por Email
## 2ª Vara Cível de Cariacica

### Visão Geral

O sistema de relatórios automáticos foi implementado para enviar diariamente às 17:00 um relatório completo das atividades do website para o email `fbmoulin@tjes.jus.br`. O sistema coleta e analisa automaticamente todas as interações dos usuários com o site.

### Funcionalidades Implementadas

#### 1. Relatórios Diários Automáticos
- **Horário**: Todos os dias às 17:00
- **Destinatário**: fbmoulin@tjes.jus.br
- **Conteúdo**: Relatório completo das atividades do dia anterior

#### 2. Dados Coletados e Reportados

**Formulários de Contato:**
- Total de submissões
- Detalhes de cada contato (nome, email, assunto, horário)

**Interações do Chatbot:**
- Total de interações
- Número de sessões únicas
- Análise dos tópicos mais consultados
- Categorização automática das consultas

**Consultas de Processo:**
- Total de consultas realizadas
- Lista dos números de processo consultados

**Agendamentos de Audiência:**
- Total de audiências agendadas
- Distribuição por tipo (conciliação, instrução, julgamento)
- Distribuição por modalidade (virtual, presencial, híbrida)

**Estatísticas Gerais:**
- Total de interações no site
- Métricas de engajamento
- Análise de tendências

#### 3. Relatórios Adicionais

**Relatórios Semanais:**
- Enviados às sextas-feiras às 18:00
- Resumo das atividades da semana
- Comparativo com semanas anteriores

**Relatórios Mensais:**
- Enviados no primeiro dia do mês às 09:00
- Análise completa do mês anterior
- Métricas de crescimento e tendências

#### 4. Funcionalidades de Manutenção

**Limpeza Automática de Dados:**
- Executada aos domingos às 02:00
- Remove mensagens do chatbot após 90 dias
- Remove consultas de processo após 180 dias
- Mantém dados importantes indefinidamente

### Configuração Técnica

#### Variáveis de Ambiente Necessárias

```bash
# Configuração SMTP para envio de emails
EMAIL_USER=seu_usuario_smtp@domain.com
EMAIL_PASSWORD=sua_senha_smtp
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
FROM_EMAIL=noreply@varacivel.cariacica.tjes.jus.br

# Email do administrador para receber relatórios
ADMIN_EMAIL=fbmoulin@tjes.jus.br
```

#### Serviços Implementados

**EmailService (`services/email_service.py`):**
- Gerencia envio de emails via SMTP
- Gera relatórios em formato HTML
- Coleta e analisa dados do banco
- Cria estatísticas e métricas

**SchedulerService (`services/scheduler_service.py`):**
- Controla agendamento de tarefas
- Executa relatórios automáticos
- Gerencia limpeza de dados
- Monitora execução de jobs

### Interface de Administração

**URL de Acesso:**
```
https://seu-dominio.com/admin/relatorios?token=admin2024vara
```

**Funcionalidades Disponíveis:**
- Visualização de estatísticas em tempo real
- Envio de relatórios de teste
- Configuração de parâmetros
- Monitoramento do status do sistema
- Visualização de relatórios de exemplo

### Exemplo de Relatório Diário

O relatório enviado por email contém:

```html
📊 Relatório Diário - 2ª Vara Cível de Cariacica
Data: 11/06/2024

📈 Resumo de Atividades:
- Total de Interações: 25
- Formulários de Contato: 3
- Consultas de Processo: 8
- Audiências Agendadas: 2
- Interações Chatbot: 12
- Sessões Únicas: 8

📝 Formulários de Contato:
• João Silva (14:30) - joao@email.com - Dúvida sobre processo
• Maria Santos (16:45) - maria@email.com - Solicitação de certidão

🤖 Tópicos Mais Consultados no Chatbot:
• Consultas de Processo: 5 consultas
• Agendamento de Audiências: 4 consultas
• Informações de Contato: 2 consultas
• Documentos e Certidões: 1 consulta

🔍 Consultas de Processo:
• 1234567-89.2024.8.08.0000
• 2345678-90.2024.8.08.0000
• 3456789-01.2024.8.08.0000

📅 Audiências Agendadas:
Por tipo:
• Conciliação: 1
• Instrução: 1

Por modalidade:
• Virtual: 2
```

### Segurança e Privacidade

**Proteção de Dados:**
- Apenas dados estatísticos são enviados nos relatórios
- Informações pessoais sensíveis são omitidas
- Acesso administrativo protegido por token

**Configurações de Segurança:**
- Comunicação SMTP criptografada (TLS)
- Autenticação obrigatória para envio
- Interface administrativa com controle de acesso

### Monitoramento e Logs

**Logging Automático:**
- Registra sucesso/falha de envios
- Monitora erros de conectividade
- Acompanha performance do sistema

**Alertas Automáticos:**
- Notificação em caso de falha no envio
- Monitoramento de integridade do serviço
- Backup automático de configurações

### Troubleshooting

**Problemas Comuns:**

1. **Relatório não enviado:**
   - Verificar configurações SMTP
   - Confirmar credenciais de email
   - Checar logs do sistema

2. **Dados faltando no relatório:**
   - Verificar conexão com banco de dados
   - Confirmar modelos de dados
   - Revisar queries de coleta

3. **Erro de autenticação SMTP:**
   - Verificar EMAIL_USER e EMAIL_PASSWORD
   - Confirmar configurações do servidor
   - Testar conectividade

### Comandos Úteis

**Enviar Relatório de Teste:**
```bash
curl "https://seu-dominio.com/admin/test-report?token=admin2024vara"
```

**Verificar Status do Sistema:**
```bash
curl "https://seu-dominio.com/admin/relatorios?token=admin2024vara"
```

### Manutenção e Atualizações

**Backup Regular:**
- Configurações salvas em variáveis de ambiente
- Códigos versionados no Git
- Logs arquivados automaticamente

**Atualizações Futuras:**
- Novos tipos de relatório podem ser facilmente adicionados
- Métricas adicionais podem ser incluídas
- Formato de email pode ser personalizado

### Contato e Suporte

Para questões técnicas ou modificações no sistema:
- Revisar logs do sistema em `/admin/relatorios`
- Verificar configurações de ambiente
- Testar conectividade SMTP

### Cronograma de Execução

| Tarefa | Frequência | Horário | Descrição |
|--------|------------|---------|-----------|
| Relatório Diário | Diário | 17:00 | Atividades do dia anterior |
| Resumo Semanal | Sextas | 18:00 | Consolidado da semana |
| Relatório Mensal | Dia 1 | 09:00 | Análise do mês anterior |
| Limpeza de Dados | Domingos | 02:00 | Remoção de dados antigos |

### Status Atual

✅ Sistema implementado e ativo
✅ Relatórios diários configurados para 17:00
✅ Email de destino: fbmoulin@tjes.jus.br
✅ Interface administrativa disponível
✅ Coleta automática de dados funcionando
✅ Formato HTML otimizado para visualização
✅ Sistema de backup e logs implementado

O sistema está totalmente operacional e enviará automaticamente os relatórios diários conforme configurado.