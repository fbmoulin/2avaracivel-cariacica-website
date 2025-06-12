#!/usr/bin/env python3
"""
Optimized workflow execution script for 2ª Vara Cível de Cariacica
Comprehensive automation with monitoring, diagnostics, and performance optimization
"""
import os
import sys
import time
import logging
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workflow_optimization.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class OptimizedWorkflowRunner:
    """Comprehensive workflow automation system"""
    
    def __init__(self):
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=6)
        self.workflows = {}
        
    def initialize_environment(self):
        """Initialize and validate environment for optimal performance"""
        logger.info("Initializing optimized environment")
        
        # Validate critical environment variables
        required_vars = ['DATABASE_URL', 'SESSION_SECRET']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            return False
        
        # Set performance optimizations
        os.environ.setdefault('PYTHONOPTIMIZE', '1')
        os.environ.setdefault('PYTHONUNBUFFERED', '1')
        
        logger.info("Environment initialized successfully")
        return True
    
    def start_database_optimization_workflow(self):
        """Start database optimization and maintenance workflow"""
        logger.info("Starting database optimization workflow")
        
        def database_workflow():
            try:
                from app import app
                with app.app_context():
                    from services.database_service_optimized import db_service
                    from sqlalchemy import text
                    from models import db
                    
                    while self.running:
                        # Health check
                        health, msg = db_service.check_connection()
                        if health:
                            logger.info(f"Database health: {msg}")
                            
                            # Periodic optimization
                            try:
                                db.session.execute(text("ANALYZE"))
                                db.session.commit()
                                logger.info("Database statistics updated")
                            except Exception as e:
                                logger.warning(f"Database optimization warning: {e}")
                        else:
                            logger.error(f"Database health issue: {msg}")
                        
                        time.sleep(1800)  # Run every 30 minutes
                        
            except Exception as e:
                logger.error(f"Database workflow error: {e}")
        
        future = self.executor.submit(database_workflow)
        self.workflows['database'] = future
        return future
    
    def start_cache_management_workflow(self):
        """Start intelligent cache management workflow"""
        logger.info("Starting cache management workflow")
        
        def cache_workflow():
            try:
                from services.cache_service_optimized import cache_service
                
                while self.running:
                    stats = cache_service.get_stats()
                    primary_backend = stats.get('primary_backend', {})
                    hit_rate = primary_backend.get('hit_rate', 0)
                    
                    logger.info(f"Cache performance: {hit_rate:.1f}% hit rate")
                    
                    # Optimize cache if performance is poor
                    if hit_rate < 40 and primary_backend.get('total_keys', 0) > 50:
                        logger.info("Optimizing cache due to low hit rate")
                        cache_service.clear()
                    
                    time.sleep(900)  # Run every 15 minutes
                    
            except Exception as e:
                logger.error(f"Cache workflow error: {e}")
        
        future = self.executor.submit(cache_workflow)
        self.workflows['cache'] = future
        return future
    
    def start_performance_monitoring_workflow(self):
        """Start comprehensive performance monitoring"""
        logger.info("Starting performance monitoring workflow")
        
        def monitoring_workflow():
            try:
                import psutil
                import requests
                
                while self.running:
                    # System metrics
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory_percent = psutil.virtual_memory().percent
                    
                    # Application health
                    try:
                        start_time = time.time()
                        response = requests.get('http://localhost:5000/health', timeout=10)
                        response_time = (time.time() - start_time) * 1000
                        
                        logger.info(f"Performance: CPU {cpu_percent:.1f}% | Memory {memory_percent:.1f}% | Response {response_time:.0f}ms")
                        
                        # Alert on performance issues
                        if cpu_percent > 80:
                            logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
                        if memory_percent > 85:
                            logger.warning(f"High memory usage: {memory_percent:.1f}%")
                        if response_time > 2000:
                            logger.warning(f"Slow response time: {response_time:.0f}ms")
                            
                    except Exception as e:
                        logger.error(f"Application health check failed: {e}")
                    
                    time.sleep(60)  # Monitor every minute
                    
            except Exception as e:
                logger.error(f"Monitoring workflow error: {e}")
        
        future = self.executor.submit(monitoring_workflow)
        self.workflows['monitoring'] = future
        return future
    
    def start_chatbot_optimization_workflow(self):
        """Start chatbot performance optimization workflow"""
        logger.info("Starting chatbot optimization workflow")
        
        def chatbot_workflow():
            try:
                from services.chatbot_optimized import chatbot_service
                
                while self.running:
                    stats = chatbot_service.get_statistics()
                    cache_stats = stats.get('cache_statistics', {})
                    hit_rate = cache_stats.get('hit_rate', 0)
                    
                    logger.info(f"Chatbot performance: {hit_rate:.1f}% cache hit rate, {stats.get('active_sessions', 0)} sessions")
                    
                    # Optimize if needed
                    if hit_rate < 50:
                        logger.info("Chatbot cache performance below optimal")
                    
                    time.sleep(600)  # Check every 10 minutes
                    
            except Exception as e:
                logger.error(f"Chatbot workflow error: {e}")
        
        future = self.executor.submit(chatbot_workflow)
        self.workflows['chatbot'] = future
        return future
    
    def start_content_optimization_workflow(self):
        """Start content management and optimization workflow"""
        logger.info("Starting content optimization workflow")
        
        def content_workflow():
            try:
                from services.content_optimized import content_service
                
                while self.running:
                    # Refresh content cache periodically
                    cache_stats = content_service.get_cache_stats()
                    logger.info(f"Content cache: {cache_stats.get('entries', 0)} entries")
                    
                    # Pre-load critical content
                    content_service.get_homepage_content()
                    content_service.get_faq_data()
                    
                    time.sleep(3600)  # Refresh every hour
                    
            except Exception as e:
                logger.error(f"Content workflow error: {e}")
        
        future = self.executor.submit(content_workflow)
        self.workflows['content'] = future
        return future
    
    def start_system_diagnostics_workflow(self):
        """Start automated system diagnostics workflow"""
        logger.info("Starting system diagnostics workflow")
        
        def diagnostics_workflow():
            try:
                from utils.system_diagnostics import run_system_diagnostics
                
                while self.running:
                    diagnostic_result = run_system_diagnostics()
                    
                    recommendations = diagnostic_result.get('recommendations', [])
                    if recommendations:
                        logger.info(f"System diagnostics: {len(recommendations)} recommendations")
                        for i, rec in enumerate(recommendations[:3], 1):
                            logger.info(f"  {i}. {rec}")
                    else:
                        logger.info("System diagnostics: All systems optimal")
                    
                    time.sleep(7200)  # Run diagnostics every 2 hours
                    
            except Exception as e:
                logger.error(f"Diagnostics workflow error: {e}")
        
        future = self.executor.submit(diagnostics_workflow)
        self.workflows['diagnostics'] = future
        return future
    
    def start_all_workflows(self):
        """Start all optimization workflows"""
        if not self.initialize_environment():
            logger.error("Environment initialization failed")
            return False
        
        self.running = True
        logger.info("Starting all optimization workflows")
        
        try:
            # Start all workflow components
            self.start_database_optimization_workflow()
            self.start_cache_management_workflow()
            self.start_performance_monitoring_workflow()
            self.start_chatbot_optimization_workflow()
            self.start_content_optimization_workflow()
            self.start_system_diagnostics_workflow()
            
            # Start scheduler service
            try:
                from services.scheduler_service import start_automated_workflows
                start_automated_workflows()
                logger.info("Scheduler service started")
            except ImportError as e:
                logger.warning(f"Scheduler service not available: {e}")
            
            logger.info(f"All workflows started successfully - {len(self.workflows)} active workflows")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start workflows: {e}")
            self.stop_all_workflows()
            return False
    
    def stop_all_workflows(self):
        """Stop all workflows gracefully"""
        logger.info("Stopping all workflows")
        self.running = False
        
        # Stop scheduler service
        try:
            from services.scheduler_service import stop_automated_workflows
            stop_automated_workflows()
            logger.info("Scheduler service stopped")
        except ImportError:
            pass
        
        # Wait for workflows to complete
        for name, future in self.workflows.items():
            try:
                future.result(timeout=5)
                logger.info(f"Workflow {name} stopped")
            except Exception as e:
                logger.warning(f"Workflow {name} stop warning: {e}")
        
        self.executor.shutdown(wait=True)
        logger.info("All workflows stopped")
    
    def get_workflow_status(self):
        """Get status of all running workflows"""
        status = {
            'running': self.running,
            'active_workflows': len(self.workflows),
            'workflow_details': {}
        }
        
        for name, future in self.workflows.items():
            status['workflow_details'][name] = {
                'running': not future.done(),
                'done': future.done(),
                'cancelled': future.cancelled()
            }
        
        return status
    
    def run_interactive_mode(self):
        """Run workflows in interactive mode with status updates"""
        print("🚀 Court Website Optimization System")
        print("=" * 50)
        
        if not self.start_all_workflows():
            print("❌ Failed to start workflows")
            return
        
        print("✅ All workflows started successfully")
        print("Press Ctrl+C to stop gracefully")
        print()
        
        def signal_handler(signum, frame):
            print("\n🛑 Stopping workflows...")
            self.stop_all_workflows()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            while self.running:
                status = self.get_workflow_status()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Active workflows: {status['active_workflows']}")
                
                # Show brief status
                for name, details in status['workflow_details'].items():
                    status_icon = "✅" if details['running'] else "❌"
                    print(f"  {status_icon} {name.capitalize()}")
                
                time.sleep(30)  # Update every 30 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping workflows...")
            self.stop_all_workflows()


def main():
    """Main entry point for workflow optimization"""
    parser = argparse.ArgumentParser(description='Court Website Workflow Optimization')
    parser.add_argument('--mode', choices=['interactive', 'daemon', 'test'], 
                       default='interactive', help='Execution mode')
    parser.add_argument('--diagnostics-only', action='store_true', 
                       help='Run diagnostics only')
    
    args = parser.parse_args()
    
    if args.diagnostics_only:
        print("Running system diagnostics...")
        from utils.system_diagnostics import run_system_diagnostics
        result = run_system_diagnostics()
        
        print(f"\nDiagnostic Results ({result['timestamp']}):")
        print(f"Recommendations: {len(result.get('recommendations', []))}")
        
        if result.get('recommendations'):
            print("\nKey Recommendations:")
            for i, rec in enumerate(result['recommendations'][:5], 1):
                print(f"{i}. {rec}")
        
        return
    
    runner = OptimizedWorkflowRunner()
    
    if args.mode == 'interactive':
        runner.run_interactive_mode()
    elif args.mode == 'daemon':
        if runner.start_all_workflows():
            print("Workflows started in daemon mode")
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                runner.stop_all_workflows()
        else:
            print("Failed to start workflows")
            sys.exit(1)
    elif args.mode == 'test':
        print("Testing workflow initialization...")
        if runner.start_all_workflows():
            print("✅ All workflows started successfully")
            time.sleep(5)
            runner.stop_all_workflows()
            print("✅ All workflows stopped successfully")
        else:
            print("❌ Workflow initialization failed")
            sys.exit(1)


if __name__ == '__main__':
    main()