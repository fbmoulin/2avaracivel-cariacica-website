from flask import Blueprint, render_template, request, jsonify

main_bp = Blueprint('main', __name__)
services_bp = Blueprint('services', __name__, url_prefix='/servicos')
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# Rotas principais
@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/sobre')
def about():
    return render_template('about.html')

@main_bp.route('/juiz')
def judge():
    return render_template('judge.html')

@main_bp.route('/faq')
def faq():
    return render_template('faq.html')

@main_bp.route('/contato')
def contact():
    return render_template('contact.html')

@main_bp.route('/noticias')
def news():
    # Em uma implementação real, buscaríamos notícias do banco de dados
    noticias = [
        {
            'id': 1,
            'titulo': 'TJES institui Programa de Monitoramento do Cumprimento de Metas Nacionais do CNJ',
            'resumo': 'O programa visa melhorar a prestação jurisdicional e acompanhar o desempenho das unidades judiciárias.',
            'data': '02/06/2025'
        },
        {
            'id': 2,
            'titulo': 'Tribunais de Justiça implementam novos mecanismos de mediação online',
            'resumo': 'A 2ª Vara Cível de Cariacica já está adaptada para realizar sessões virtuais de conciliação.',
            'data': '20/05/2025'
        },
        {
            'id': 3,
            'titulo': 'Nova regulamentação do TJES sobre a digitalização de processos físicos',
            'resumo': 'Advogados devem ficar atentos aos prazos para manifestação após a conclusão da digitalização.',
            'data': '15/05/2025'
        }
    ]
    return render_template('news.html', noticias=noticias)

# Rotas de serviços
@services_bp.route('/')
def services_index():
    return render_template('services/index.html')

@services_bp.route('/audiencias')
def hearings():
    return render_template('services/hearings.html')

@services_bp.route('/agendamento')
def scheduling():
    return render_template('services/scheduling.html')

@services_bp.route('/balcao-virtual')
def virtual_desk():
    return render_template('services/virtual_desk.html')

@services_bp.route('/certidoes')
def certificates():
    return render_template('services/certificates.html')

# Rotas do chatbot
@chatbot_bp.route('/')
def chatbot_index():
    return render_template('chatbot/index.html')

@chatbot_bp.route('/api/message', methods=['POST'])
def chatbot_message():
    # Esta é uma implementação simulada
    # Em produção, integraria com a API da OpenAI
    data = request.json
    user_message = data.get('message', '')
    
    # Resposta simulada
    if 'processo' in user_message.lower():
        response = "Para consultar seu processo, você precisa do número no formato CNJ. Com esse número, você pode acessar a consulta processual no site do TJES."
    elif 'audiência' in user_message.lower():
        response = "As audiências podem ser realizadas de forma híbrida. Você pode participar presencialmente ou pelo aplicativo Zoom."
    elif 'horário' in user_message.lower():
        response = "A 2ª Vara Cível de Cariacica funciona das 12h às 18h em dias úteis."
    elif 'contato' in user_message.lower():
        response = "Você pode entrar em contato pelo telefone (27) 3246-XXXX ou pelo e-mail 2varacivel.cariacica@tjes.jus.br."
    else:
        response = "Olá! Sou o assistente virtual da 2ª Vara Cível de Cariacica. Como posso ajudar você hoje?"
    
    return jsonify({'response': response})
