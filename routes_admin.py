"""
Advanced admin routes for system monitoring and management
Provides comprehensive dashboard for monitoring system health and performance
"""
from flask import Blueprint, render_template, jsonify, request
import logging
import json
from datetime import datetime, timedelta

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard with system overview"""
    return render_template('admin/dashboard.html')

@admin_bp.route('/api/system-status')
def system_status_api():
    """API endpoint for real-time system status"""
    try:
        # Integration service status
        integration_status = {}
        try:
            from services.integration_service import integration_service
            integration_status = integration_service.get_system_health()
        except ImportError:
            integration_status = {'status': 'not_available'}
        
        # Cache service status
        cache_status = {}
        try:
            from services.cache_service import cache_service
            cache_status = cache_service.get_stats()
        except ImportError:
            cache_status = {'status': 'not_available'}
        
        # API service status
        api_status = {}
        try:
            from services.api_service import api_service
            api_status = api_service.get_api_stats()
        except ImportError:
            api_status = {'status': 'not_available'}
        
        # Performance metrics
        performance_status = {}
        try:
            from performance_monitor import performance_monitor
            performance_status = performance_monitor.get_performance_stats()
        except ImportError:
            performance_status = {'status': 'not_available'}
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'integration': integration_status,
            'cache': cache_status,
            'api': api_status,
            'performance': performance_status
        })
        
    except Exception as e:
        logging.error(f"System status API error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@admin_bp.route('/api/diagnostics')
def diagnostics_api():
    """API endpoint for system diagnostics"""
    try:
        from utils.system_diagnostics import system_diagnostics
        diagnostics = system_diagnostics.run_full_diagnostic()
        return jsonify({
            'status': 'success',
            'diagnostics': diagnostics
        })
    except ImportError:
        return jsonify({
            'status': 'error',
            'error': 'System diagnostics not available'
        }), 503
    except Exception as e:
        logging.error(f"Diagnostics API error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@admin_bp.route('/api/cache/stats')
def cache_stats_api():
    """Cache statistics API"""
    try:
        from services.cache_service import cache_service
        stats = cache_service.get_stats()
        return jsonify({
            'status': 'success',
            'cache_stats': stats
        })
    except ImportError:
        return jsonify({
            'status': 'error',
            'error': 'Cache service not available'
        }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@admin_bp.route('/performance-metrics', methods=['POST'])
def performance_metrics():
    """Performance metrics collection endpoint"""
    try:
        metrics_data = request.get_json() or {}
        
        # Log performance metrics
        logging.info(f"Performance metrics received: {json.dumps(metrics_data, indent=2)}")
        
        # Store in performance monitor if available
        try:
            from performance_monitor import performance_monitor
            performance_monitor.record_metrics(metrics_data)
        except ImportError:
            pass
        
        return jsonify({
            'status': 'success',
            'message': 'Metrics recorded successfully'
        })
        
    except Exception as e:
        logging.error(f"Performance metrics error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@admin_bp.route('/api/cache/clear', methods=['POST'])
def clear_cache_api():
    """Clear cache API"""
    try:
        from services.cache_service import cache_service
        
        pattern = request.json.get('pattern', '*') if request.json else '*'
        cleared_count = cache_service.clear_pattern(pattern)
        
        return jsonify({
            'status': 'success',
            'message': f'Cleared {cleared_count} cache entries',
            'cleared_count': cleared_count
        })
    except ImportError:
        return jsonify({
            'status': 'error',
            'error': 'Cache service not available'
        }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@admin_bp.route('/api/integration/services')
def integration_services_api():
    """Integration services status API"""
    try:
        from services.integration_service import integration_service
        
        services_status = {}
        for service_name in integration_service._service_registry:
            services_status[service_name] = integration_service.get_service_status(service_name)
        
        return jsonify({
            'status': 'success',
            'services': services_status
        })
    except ImportError:
        return jsonify({
            'status': 'error',
            'error': 'Integration service not available'
        }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@admin_bp.route('/api/performance/metrics')
def performance_metrics_api():
    """Performance metrics API"""
    try:
        from performance_monitor import performance_monitor
        metrics = performance_monitor.get_performance_stats()
        
        return jsonify({
            'status': 'success',
            'metrics': metrics
        })
    except ImportError:
        return jsonify({
            'status': 'error',
            'error': 'Performance monitor not available'
        }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@admin_bp.route('/api/export/diagnostics')
def export_diagnostics_api():
    """Export system diagnostics"""
    try:
        from utils.system_diagnostics import system_diagnostics
        filepath = system_diagnostics.export_diagnostics()
        
        if filepath:
            return jsonify({
                'status': 'success',
                'message': f'Diagnostics exported to {filepath}',
                'filepath': filepath
            })
        else:
            return jsonify({
                'status': 'error',
                'error': 'Failed to export diagnostics'
            }), 500
            
    except ImportError:
        return jsonify({
            'status': 'error',
            'error': 'System diagnostics not available'
        }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@admin_bp.route('/logs')
def view_logs():
    """View application logs"""
    return render_template('admin/logs.html')

@admin_bp.route('/api/logs')
def logs_api():
    """API endpoint for application logs"""
    try:
        # Read recent log entries
        log_files = ['app.log', 'errors.log']
        logs = {}
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Get last 100 lines
                    logs[log_file] = lines[-100:] if len(lines) > 100 else lines
            except FileNotFoundError:
                logs[log_file] = ['Log file not found']
        
        return jsonify({
            'status': 'success',
            'logs': logs
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@admin_bp.route('/monitoring')
def monitoring():
    """Real-time monitoring dashboard"""
    return render_template('admin/monitoring.html')

# Error handlers for admin routes
@admin_bp.errorhandler(404)
def admin_not_found(error):
    return jsonify({'status': 'error', 'error': 'Admin endpoint not found'}), 404

@admin_bp.errorhandler(500)
def admin_server_error(error):
    return jsonify({'status': 'error', 'error': 'Internal server error'}), 500