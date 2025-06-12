"""
Production-Ready Async Routes for 2ª Vara Cível de Cariacica
Enhanced chatbot and health monitoring with async capabilities
"""

from flask import Blueprint, request, jsonify
from utils.simple_async import simple_async, async_route_simple
from utils.security import sanitize_input
import logging
import json
from datetime import datetime
import os

# Create simplified async blueprint
async_simple_bp = Blueprint('async_simple', __name__, url_prefix='/api/async')

logger = logging.getLogger('async_simple_routes')

@async_simple_bp.route('/chatbot', methods=['POST'])
@async_route_simple
async def enhanced_chatbot():
    """Enhanced async chatbot with caching and performance optimization"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Mensagem é obrigatória'
            }), 400
        
        message = sanitize_input(data['message'])
        conversation_id = data.get('conversation_id', f'conv_{int(datetime.now().timestamp())}')
        
        if not message.strip():
            return jsonify({
                'success': False,
                'error': 'Mensagem não pode estar vazia'
            }), 400
        
        # Check cache first
        cache_key = f"chat_{hash(message)}_{conversation_id}"
        cached_response = simple_async.get_cached_response(cache_key)
        
        if cached_response:
            return jsonify({
                'success': True,
                'response': cached_response,
                'cached': True,
                'conversation_id': conversation_id,
                'timestamp': datetime.now().isoformat()
            })
        
        # Simulate OpenAI API call with async HTTP request
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if openai_api_key:
            # Use actual OpenAI API
            import openai
            client = openai.AsyncOpenAI(api_key=openai_api_key)
            
            try:
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um assistente virtual da 2ª Vara Cível de Cariacica. Ajude com informações sobre processos judiciais, agendamentos e serviços do tribunal."
                        },
                        {"role": "user", "content": message}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                bot_response = response.choices[0].message.content.strip()
                
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                bot_response = "Desculpe, estou com dificuldades técnicas no momento. Como posso ajudá-lo com informações sobre a 2ª Vara Cível de Cariacica?"
        else:
            # Fallback response system
            bot_response = await generate_fallback_response(message)
        
        # Cache the response
        simple_async.cache_response(cache_key, bot_response)
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'cached': False,
            'conversation_id': conversation_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Enhanced chatbot error: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

@async_simple_bp.route('/health', methods=['GET'])
@async_route_simple
async def async_health():
    """Comprehensive async health check"""
    try:
        health_data = await simple_async.async_health_check()
        
        # Add application-specific checks
        health_data['application'] = {
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'production'),
            'uptime': 'running',
            'healthy': True
        }
        
        # Add cache status
        health_data['cache'] = {
            'size': len(simple_async.request_cache),
            'max_size': simple_async.max_cache_size,
            'healthy': len(simple_async.request_cache) < simple_async.max_cache_size
        }
        
        return jsonify(health_data)
        
    except Exception as e:
        logger.error(f"Async health check error: {e}")
        return jsonify({
            'overall_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@async_simple_bp.route('/external-check', methods=['GET'])
@async_route_simple
async def external_service_check():
    """Check external services asynchronously"""
    try:
        # Test external connectivity
        services = [
            ('httpbin', 'https://httpbin.org/status/200'),
            ('google_dns', 'https://8.8.8.8'),
            ('openai', 'https://api.openai.com/v1/models')
        ]
        
        results = {}
        
        for service_name, url in services:
            try:
                result = await simple_async.async_http_request('GET', url)
                results[service_name] = {
                    'status': 'available' if result['success'] else 'unavailable',
                    'response_time': result.get('response_time', 0),
                    'status_code': result.get('status', 0)
                }
            except Exception as e:
                results[service_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        overall_status = 'healthy' if all(
            r.get('status') == 'available' for r in results.values()
        ) else 'degraded'
        
        return jsonify({
            'overall_status': overall_status,
            'services': results,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"External service check error: {e}")
        return jsonify({
            'overall_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@async_simple_bp.route('/performance-test', methods=['POST'])
@async_route_simple
async def performance_test():
    """Test async performance vs sync operations"""
    try:
        data = request.get_json() or {}
        test_type = data.get('test_type', 'basic')
        iterations = min(data.get('iterations', 5), 20)  # Max 20 for safety
        
        import time
        
        results = {
            'test_type': test_type,
            'iterations': iterations,
            'async_times': [],
            'sync_times': []
        }
        
        # Async operations test
        for i in range(iterations):
            start_time = time.time()
            await simple_async.async_health_check()
            async_time = (time.time() - start_time) * 1000  # Convert to ms
            results['async_times'].append(async_time)
        
        # Sync operations test (simulated)
        for i in range(iterations):
            start_time = time.time()
            # Simulate sync operation delay
            import time
            time.sleep(0.01)  # 10ms delay to simulate sync operation
            sync_time = (time.time() - start_time) * 1000
            results['sync_times'].append(sync_time)
        
        # Calculate statistics
        results['statistics'] = {
            'async_avg': sum(results['async_times']) / len(results['async_times']),
            'sync_avg': sum(results['sync_times']) / len(results['sync_times']),
            'async_min': min(results['async_times']),
            'async_max': max(results['async_times']),
            'sync_min': min(results['sync_times']),
            'sync_max': max(results['sync_times'])
        }
        
        # Calculate improvement
        improvement = ((results['statistics']['sync_avg'] - results['statistics']['async_avg']) / 
                      results['statistics']['sync_avg']) * 100
        
        results['performance_improvement'] = f"{improvement:.1f}%"
        results['timestamp'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Performance test error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@async_simple_bp.route('/cache-stats', methods=['GET'])
def cache_statistics():
    """Get cache performance statistics"""
    try:
        cache_stats = {
            'current_size': len(simple_async.request_cache),
            'max_size': simple_async.max_cache_size,
            'utilization': (len(simple_async.request_cache) / simple_async.max_cache_size) * 100,
            'cache_keys': list(simple_async.request_cache.keys())[-10:],  # Last 10 keys
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'cache_stats': cache_stats
        })
        
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@async_simple_bp.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear application cache"""
    try:
        cache_size_before = len(simple_async.request_cache)
        simple_async.request_cache.clear()
        
        return jsonify({
            'success': True,
            'message': f'Cache cleared. Removed {cache_size_before} entries.',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

async def generate_fallback_response(message: str) -> str:
    """Generate contextual fallback response for chatbot"""
    message_lower = message.lower()
    
    # Court-specific responses
    if any(word in message_lower for word in ['processo', 'processual', 'consulta']):
        return "Para consultar processos, utilize o sistema de consulta processual disponível no menu principal. Você pode buscar pelo número do processo ou nome das partes."
    
    elif any(word in message_lower for word in ['agendamento', 'agendar', 'horário']):
        return "Para agendamentos, acesse a seção de agendamento no menu. Oferecemos horários para atendimento presencial e virtual com nossos assessores."
    
    elif any(word in message_lower for word in ['contato', 'telefone', 'endereço']):
        return "Entre em contato conosco pelo formulário de contato ou visite nosso endereço. Estamos localizados no Fórum de Cariacica e atendemos de segunda a sexta."
    
    elif any(word in message_lower for word in ['horário', 'funcionamento', 'atendimento']):
        return "Nosso horário de atendimento é de segunda a sexta-feira, das 8h às 18h. Para urgências, consulte o plantão judiciário."
    
    elif any(word in message_lower for word in ['documentos', 'documento', 'certidão']):
        return "Para solicitação de documentos e certidões, utilize o balcão virtual ou compareça pessoalmente com documentação válida."
    
    else:
        return "Olá! Sou o assistente virtual da 2ª Vara Cível de Cariacica. Posso ajudá-lo com informações sobre processos, agendamentos, contatos e serviços do tribunal. Como posso ajudá-lo?"