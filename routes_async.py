"""
Asynchronous Routes for 2ª Vara Cível de Cariacica
Enhanced performance with async operations and concurrent processing
"""

from flask import Blueprint, request, jsonify, render_template
from utils.async_handler import async_route, async_handler, health_check_async
from services.async_chatbot import async_chatbot_service
from utils.security import sanitize_input, validate_email
import logging
import json
from datetime import datetime

# Create async blueprint
async_bp = Blueprint('async_operations', __name__, url_prefix='/async')

logger = logging.getLogger('async_routes')

@async_bp.route('/chatbot', methods=['POST'])
@async_route
async def async_chatbot():
    """Async chatbot endpoint for improved response times"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Mensagem é obrigatória'
            }), 400
        
        message = sanitize_input(data['message'])
        conversation_id = data.get('conversation_id')
        
        if not message.strip():
            return jsonify({
                'success': False,
                'error': 'Mensagem não pode estar vazia'
            }), 400
        
        # Get async response
        response_data = await async_chatbot_service.get_response(
            message, 
            conversation_id
        )
        
        return jsonify({
            'success': response_data.get('success', True),
            'response': response_data['response'],
            'conversation_id': response_data.get('conversation_id'),
            'processing_time': response_data.get('processing_time', 0),
            'cached': response_data.get('cached', False),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Async chatbot error: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor',
            'timestamp': datetime.now().isoformat()
        }), 500

@async_bp.route('/batch-chatbot', methods=['POST'])
@async_route
async def batch_chatbot():
    """Process multiple chatbot messages simultaneously"""
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({
                'success': False,
                'error': 'Lista de mensagens é obrigatória'
            }), 400
        
        messages = data['messages']
        
        if not isinstance(messages, list) or len(messages) == 0:
            return jsonify({
                'success': False,
                'error': 'Lista de mensagens deve conter pelo menos uma mensagem'
            }), 400
        
        # Validate and sanitize messages
        processed_messages = []
        for msg in messages:
            if 'message' not in msg:
                continue
            processed_messages.append({
                'message': sanitize_input(msg['message']),
                'conversation_id': msg.get('conversation_id')
            })
        
        # Process messages in parallel
        results = await async_chatbot_service.batch_process_messages(processed_messages)
        
        return jsonify({
            'success': True,
            'results': results,
            'total_processed': len(results),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Batch chatbot error: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro no processamento em lote',
            'timestamp': datetime.now().isoformat()
        }), 500

@async_bp.route('/health-check')
@async_route
async def async_health_check():
    """Comprehensive async health check"""
    try:
        # Run parallel health checks
        health_data = await health_check_async()
        
        # Add chatbot-specific health check
        chatbot_health = await async_chatbot_service.health_check()
        health_data['components'].append({
            'operation': 'chatbot',
            'success': chatbot_health['status'] == 'healthy',
            'result': chatbot_health,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(health_data)
        
    except Exception as e:
        logger.error(f"Async health check error: {e}")
        return jsonify({
            'overall_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@async_bp.route('/file-operations', methods=['POST'])
@async_route
async def async_file_operations():
    """Handle multiple file operations asynchronously"""
    try:
        data = request.get_json()
        
        if not data or 'operations' not in data:
            return jsonify({
                'success': False,
                'error': 'Lista de operações é obrigatória'
            }), 400
        
        operations = data['operations']
        
        # Validate operations
        valid_operations = []
        for op in operations:
            if op.get('type') in ['read', 'write'] and 'filepath' in op:
                valid_operations.append(op)
        
        if not valid_operations:
            return jsonify({
                'success': False,
                'error': 'Nenhuma operação válida encontrada'
            }), 400
        
        # Execute file operations
        results = await async_handler.async_file_operations(valid_operations)
        
        return jsonify({
            'success': True,
            'results': results,
            'total_operations': len(results),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Async file operations error: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro nas operações de arquivo',
            'timestamp': datetime.now().isoformat()
        }), 500

@async_bp.route('/background-task', methods=['POST'])
@async_route
async def start_background_task():
    """Start a background task asynchronously"""
    try:
        data = request.get_json()
        
        if not data or 'task_type' not in data:
            return jsonify({
                'success': False,
                'error': 'Tipo de tarefa é obrigatório'
            }), 400
        
        task_type = data['task_type']
        task_params = data.get('params', {})
        
        # Define available background tasks
        available_tasks = {
            'log_analysis': log_analysis_task,
            'database_cleanup': database_cleanup_task,
            'cache_optimization': cache_optimization_task,
            'report_generation': report_generation_task
        }
        
        if task_type not in available_tasks:
            return jsonify({
                'success': False,
                'error': f'Tipo de tarefa "{task_type}" não disponível'
            }), 400
        
        # Start background task
        task_id = await async_handler.background_task_manager(
            task_type,
            available_tasks[task_type],
            **task_params
        )
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'task_type': task_type,
            'status': 'started',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Background task error: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro ao iniciar tarefa em segundo plano',
            'timestamp': datetime.now().isoformat()
        }), 500

@async_bp.route('/task-status/<task_id>')
@async_route
async def get_task_status(task_id):
    """Get status of background task"""
    try:
        status = async_handler.get_task_status(task_id)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Task status error: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro ao obter status da tarefa',
            'timestamp': datetime.now().isoformat()
        }), 500

@async_bp.route('/conversation-summary', methods=['POST'])
@async_route
async def get_conversation_summary():
    """Get async conversation summary"""
    try:
        data = request.get_json()
        
        if not data or 'conversation_id' not in data:
            return jsonify({
                'success': False,
                'error': 'ID da conversa é obrigatório'
            }), 400
        
        conversation_id = sanitize_input(data['conversation_id'])
        
        # Get summary asynchronously
        summary_data = await async_chatbot_service.get_conversation_summary(conversation_id)
        
        return jsonify({
            'success': summary_data.get('success', True),
            'conversation_id': conversation_id,
            'summary': summary_data.get('summary'),
            'message_count': summary_data.get('message_count', 0),
            'error': summary_data.get('error'),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Conversation summary error: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro ao gerar resumo da conversa',
            'timestamp': datetime.now().isoformat()
        }), 500

@async_bp.route('/parallel-operations', methods=['POST'])
@async_route
async def parallel_operations():
    """Execute multiple operations in parallel"""
    try:
        data = request.get_json()
        
        if not data or 'operations' not in data:
            return jsonify({
                'success': False,
                'error': 'Lista de operações é obrigatória'
            }), 400
        
        operations_data = data['operations']
        
        # Prepare operations for parallel execution
        operations = []
        for op_data in operations_data:
            op_name = op_data.get('name', 'unnamed_operation')
            op_type = op_data.get('type')
            op_params = op_data.get('params', {})
            
            if op_type == 'database_query':
                operations.append((op_name, mock_database_operation, [], op_params))
            elif op_type == 'api_call':
                operations.append((op_name, mock_api_call, [], op_params))
            elif op_type == 'file_processing':
                operations.append((op_name, mock_file_processing, [], op_params))
        
        if not operations:
            return jsonify({
                'success': False,
                'error': 'Nenhuma operação válida encontrada'
            }), 400
        
        # Execute operations in parallel
        results = await async_handler.parallel_operations(operations)
        
        return jsonify({
            'success': True,
            'results': results,
            'total_operations': len(results),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Parallel operations error: {e}")
        return jsonify({
            'success': False,
            'error': 'Erro nas operações paralelas',
            'timestamp': datetime.now().isoformat()
        }), 500

# Background task functions
async def log_analysis_task(**params):
    """Background task for log analysis"""
    import asyncio
    await asyncio.sleep(2)  # Simulate processing
    return {
        'analyzed_files': 5,
        'errors_found': 12,
        'warnings': 25,
        'recommendations': ['Increase log retention', 'Add more detailed logging']
    }

async def database_cleanup_task(**params):
    """Background task for database cleanup"""
    import asyncio
    await asyncio.sleep(3)  # Simulate processing
    return {
        'cleaned_records': 150,
        'freed_space_mb': 25.5,
        'optimized_tables': ['chat_message', 'contact', 'process_consultation']
    }

async def cache_optimization_task(**params):
    """Background task for cache optimization"""
    import asyncio
    await asyncio.sleep(1)  # Simulate processing
    return {
        'cache_hit_rate_improvement': 15.2,
        'memory_freed_mb': 45.8,
        'optimized_keys': 234
    }

async def report_generation_task(**params):
    """Background task for report generation"""
    import asyncio
    await asyncio.sleep(4)  # Simulate processing
    return {
        'report_type': params.get('report_type', 'general'),
        'pages_generated': 25,
        'charts_created': 8,
        'file_path': '/reports/async_report_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.pdf'
    }

# Mock functions for parallel operations
def mock_database_operation(**params):
    """Mock database operation"""
    import time
    time.sleep(0.5)  # Simulate database query
    return {'rows_affected': 10, 'query_time': 0.5}

def mock_api_call(**params):
    """Mock API call"""
    import time
    time.sleep(0.3)  # Simulate API call
    return {'status_code': 200, 'response_time': 0.3, 'data_size': 1024}

def mock_file_processing(**params):
    """Mock file processing"""
    import time
    time.sleep(0.8)  # Simulate file processing
    return {'files_processed': 3, 'total_size_mb': 15.7, 'processing_time': 0.8}