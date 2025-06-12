"""
Error Monitoring Dashboard Routes
2ª Vara Cível de Cariacica - Real-time error tracking and analysis
"""

from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from utils.error_logger import error_logger
from datetime import datetime, timedelta
import json
import os

# Create error monitoring blueprint
error_bp = Blueprint('error_monitoring', __name__, url_prefix='/admin/errors')

@error_bp.route('/')
def dashboard():
    """Error monitoring dashboard"""
    try:
        # Get error summary for different time periods
        summary_24h = error_logger.get_error_summary(24)
        summary_1h = error_logger.get_error_summary(1)
        
        # Get recent critical errors
        recent_critical = [
            error for error in error_logger.critical_errors[-10:]
        ]
        
        return render_template('admin/error_dashboard.html',
                             summary_24h=summary_24h,
                             summary_1h=summary_1h,
                             recent_critical=recent_critical,
                             total_errors=error_logger.error_count)
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@error_bp.route('/api/summary')
def api_summary():
    """API endpoint for error summary"""
    hours = request.args.get('hours', 24, type=int)
    summary = error_logger.get_error_summary(hours)
    return jsonify(summary)

@error_bp.route('/api/recent')
def api_recent_errors():
    """API endpoint for recent errors"""
    limit = request.args.get('limit', 50, type=int)
    recent_errors = error_logger.errors_today[-limit:]
    return jsonify({
        'errors': recent_errors,
        'total_count': len(error_logger.errors_today)
    })

@error_bp.route('/api/critical')
def api_critical_errors():
    """API endpoint for critical errors"""
    return jsonify({
        'critical_errors': error_logger.critical_errors,
        'count': len(error_logger.critical_errors)
    })

@error_bp.route('/export')
def export_errors():
    """Export errors to JSON file"""
    hours = request.args.get('hours', 24, type=int)
    try:
        filename = error_logger.export_errors(hours=hours)
        flash(f'Erros exportados para {filename}', 'success')
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/admin/errors/download/{filename}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@error_bp.route('/download/<filename>')
def download_export(filename):
    """Download exported error file"""
    try:
        if os.path.exists(filename):
            from flask import send_file
            return send_file(filename, as_attachment=True)
        else:
            flash('Arquivo não encontrado', 'error')
            return redirect(url_for('error_monitoring.dashboard'))
    except Exception as e:
        flash(f'Erro ao baixar arquivo: {str(e)}', 'error')
        return redirect(url_for('error_monitoring.dashboard'))

@error_bp.route('/logs')
def view_logs():
    """View raw error logs"""
    log_type = request.args.get('type', 'error')
    lines = request.args.get('lines', 100, type=int)
    
    log_files = {
        'error': 'app_errors.log',
        'debug': 'app_debug.log',
        'critical': 'critical_errors.log',
        'alerts': 'error_alerts.log'
    }
    
    log_file = log_files.get(log_type, 'app_errors.log')
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_lines = f.readlines()
                # Get last N lines
                recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
                
            return render_template('admin/error_logs.html',
                                 log_lines=recent_lines,
                                 log_type=log_type,
                                 total_lines=len(log_lines))
        else:
            flash(f'Arquivo de log {log_file} não encontrado', 'warning')
            return render_template('admin/error_logs.html',
                                 log_lines=[],
                                 log_type=log_type,
                                 total_lines=0)
    except Exception as e:
        flash(f'Erro ao ler logs: {str(e)}', 'error')
        return redirect(url_for('error_monitoring.dashboard'))

@error_bp.route('/clear')
def clear_logs():
    """Clear error logs (admin only)"""
    try:
        # Clear memory logs
        error_logger.errors_today.clear()
        error_logger.critical_errors.clear()
        error_logger.error_count = 0
        
        # Archive current log files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_files = ['app_errors.log', 'app_debug.log', 'critical_errors.log']
        
        for log_file in log_files:
            if os.path.exists(log_file):
                archive_name = f"{log_file}.{timestamp}.archived"
                os.rename(log_file, archive_name)
        
        flash('Logs limpos com sucesso', 'success')
        
    except Exception as e:
        flash(f'Erro ao limpar logs: {str(e)}', 'error')
    
    return redirect(url_for('error_monitoring.dashboard'))

@error_bp.route('/test-error')
def test_error():
    """Test error logging system"""
    try:
        # Trigger different types of test errors
        error_type = request.args.get('type', 'general')
        
        if error_type == 'critical':
            raise SystemError("Test critical error for monitoring system")
        elif error_type == 'database':
            raise ConnectionError("Test database connection error")
        elif error_type == 'validation':
            raise ValueError("Test validation error with invalid data")
        else:
            raise Exception("Test general error for monitoring system")
            
    except Exception as e:
        error_logger.log_error(e, {
            'test_error': True,
            'error_type': error_type,
            'triggered_by': 'admin_test'
        })
        
        flash(f'Erro de teste {error_type} gerado com sucesso', 'info')
        return redirect(url_for('error_monitoring.dashboard'))

@error_bp.route('/stats')
def error_stats():
    """Detailed error statistics"""
    try:
        # Calculate various statistics
        stats = {
            'total_errors': error_logger.error_count,
            'critical_errors': len(error_logger.critical_errors),
            'errors_today': len(error_logger.errors_today),
            'summary_24h': error_logger.get_error_summary(24),
            'summary_7d': error_logger.get_error_summary(168),  # 7 days
            'log_file_sizes': {}
        }
        
        # Get log file sizes
        log_files = ['app_errors.log', 'app_debug.log', 'critical_errors.log', 'error_alerts.log']
        for log_file in log_files:
            if os.path.exists(log_file):
                size = os.path.getsize(log_file)
                stats['log_file_sizes'][log_file] = {
                    'bytes': size,
                    'mb': round(size / (1024 * 1024), 2)
                }
        
        return render_template('admin/error_stats.html', stats=stats)
        
    except Exception as e:
        flash(f'Erro ao carregar estatísticas: {str(e)}', 'error')
        return redirect(url_for('error_monitoring.dashboard'))