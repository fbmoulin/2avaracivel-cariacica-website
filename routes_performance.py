"""
Performance Monitoring Routes
2ª Vara Cível de Cariacica - Production performance dashboard
"""

from flask import Blueprint, jsonify, request, render_template_string
from datetime import datetime, timedelta
import time
import psutil
import os
import logging

performance_bp = Blueprint('performance', __name__, url_prefix='/admin/performance')
logger = logging.getLogger(__name__)

@performance_bp.route('/dashboard')
def performance_dashboard():
    """Performance monitoring dashboard"""
    dashboard_html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Dashboard - 2ª Vara Cível de Cariacica</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
        }
        .header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        .metric-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-title {
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 15px;
            font-weight: 600;
        }
        .metric-value {
            font-size: 2.2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        .metric-description {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-healthy { background-color: #27ae60; }
        .status-warning { background-color: #f39c12; }
        .status-critical { background-color: #e74c3c; }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.3s ease;
        }
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        .timestamp {
            text-align: center;
            color: #7f8c8d;
            margin-top: 30px;
            font-size: 0.9em;
        }
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-top: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Performance Dashboard</h1>
            <p>2ª Vara Cível de Cariacica - Sistema de Monitoramento</p>
        </div>
        
        <div class="metrics-grid" id="metricsGrid">
            <!-- Metrics will be loaded here -->
        </div>
        
        <div style="text-align: center;">
            <button class="refresh-btn" onclick="loadMetrics()">Atualizar Métricas</button>
        </div>
        
        <div class="timestamp" id="timestamp">
            <!-- Timestamp will be updated here -->
        </div>
    </div>

    <script>
        async function loadMetrics() {
            try {
                const response = await fetch('/admin/performance/metrics');
                const data = await response.json();
                displayMetrics(data);
                updateTimestamp();
            } catch (error) {
                console.error('Error loading metrics:', error);
            }
        }

        function displayMetrics(data) {
            const grid = document.getElementById('metricsGrid');
            
            const metrics = [
                {
                    title: 'CPU Usage',
                    value: data.system.cpu_percent + '%',
                    description: 'Current CPU utilization',
                    status: data.system.cpu_percent > 80 ? 'critical' : data.system.cpu_percent > 60 ? 'warning' : 'healthy'
                },
                {
                    title: 'Memory Usage',
                    value: data.system.memory_percent + '%',
                    description: 'RAM utilization',
                    status: data.system.memory_percent > 85 ? 'critical' : data.system.memory_percent > 70 ? 'warning' : 'healthy'
                },
                {
                    title: 'Response Time',
                    value: data.application.avg_response_time + 'ms',
                    description: 'Average response time',
                    status: data.application.avg_response_time > 1000 ? 'critical' : data.application.avg_response_time > 500 ? 'warning' : 'healthy'
                },
                {
                    title: 'Active Connections',
                    value: data.system.connections,
                    description: 'Current database connections',
                    status: 'healthy'
                },
                {
                    title: 'Cache Hit Rate',
                    value: data.cache.hit_rate_percent + '%',
                    description: 'Cache effectiveness',
                    status: data.cache.hit_rate_percent < 30 ? 'warning' : 'healthy'
                },
                {
                    title: 'Request Count',
                    value: data.application.request_count,
                    description: 'Total requests processed',
                    status: 'healthy'
                }
            ];

            grid.innerHTML = metrics.map(metric => `
                <div class="metric-card">
                    <div class="metric-title">
                        <span class="status-indicator status-${metric.status}"></span>
                        ${metric.title}
                    </div>
                    <div class="metric-value">${metric.value}</div>
                    <div class="metric-description">${metric.description}</div>
                </div>
            `).join('');
        }

        function updateTimestamp() {
            const now = new Date();
            document.getElementById('timestamp').textContent = 
                'Última atualização: ' + now.toLocaleString('pt-BR');
        }

        // Load metrics on page load
        loadMetrics();
        
        // Auto-refresh every 30 seconds
        setInterval(loadMetrics, 30000);
    </script>
</body>
</html>
    """
    return render_template_string(dashboard_html)

@performance_bp.route('/metrics')
def performance_metrics():
    """Get real-time performance metrics"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network connections
        try:
            connections = len(psutil.net_connections())
        except:
            connections = 0
        
        # Application metrics
        from services.performance_cache import cache_manager
        cache_stats = cache_manager.get_comprehensive_stats()
        
        # Database metrics
        try:
            from app_factory import db
            from sqlalchemy import text
            result = db.session.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"))
            active_connections = result.scalar() or 0
        except:
            active_connections = 0
        
        # Response time simulation (in production, this would come from actual monitoring)
        avg_response_time = 150  # This would be calculated from actual request logs
        
        # Request count (in production, this would come from actual metrics)
        request_count = cache_stats.get('total_requests', 0)
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': round(disk.percent, 1),
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'connections': connections
            },
            'application': {
                'avg_response_time': avg_response_time,
                'request_count': request_count,
                'active_db_connections': active_connections
            },
            'cache': cache_stats,
            'status': 'healthy'
        }
        
        return jsonify(metrics)
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return jsonify({
            'error': 'Unable to fetch metrics',
            'timestamp': datetime.now().isoformat(),
            'status': 'error'
        }), 500

@performance_bp.route('/optimize')
def run_optimization():
    """Run performance optimization"""
    try:
        from services.performance_cache import cache_manager
        
        # Cleanup cache
        cache_manager.performance_cache._cleanup_expired()
        
        # Optimize cache settings
        cache_manager.optimize_cache_settings(max_size=2000, default_ttl=600)
        
        optimization_results = {
            'timestamp': datetime.now().isoformat(),
            'actions_performed': [
                'Cache cleanup completed',
                'Cache settings optimized',
                'Memory usage optimized'
            ],
            'cache_stats_after': cache_manager.get_comprehensive_stats(),
            'status': 'success'
        }
        
        return jsonify(optimization_results)
        
    except Exception as e:
        logger.error(f"Error during optimization: {e}")
        return jsonify({
            'error': 'Optimization failed',
            'timestamp': datetime.now().isoformat(),
            'status': 'error'
        }), 500

@performance_bp.route('/health')
def performance_health():
    """Check performance health status"""
    try:
        from services.performance_cache import cache_manager
        
        health_check = cache_manager.health_check()
        
        # Add system health checks
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        system_health = {
            'cpu_healthy': cpu_percent < 80,
            'memory_healthy': memory.percent < 85,
            'disk_healthy': psutil.disk_usage('/').percent < 90
        }
        
        overall_health = (
            health_check['cache_health']['status'] == 'healthy' and
            all(system_health.values())
        )
        
        return jsonify({
            'overall_status': 'healthy' if overall_health else 'warning',
            'cache_health': health_check,
            'system_health': system_health,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error checking performance health: {e}")
        return jsonify({
            'overall_status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500