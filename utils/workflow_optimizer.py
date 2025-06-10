"""
Workflow optimization and process management for court system
Implements intelligent task scheduling, resource management, and process automation
"""
import threading
import queue
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class Priority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class WorkflowTask:
    """Individual workflow task representation"""
    id: str
    name: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: Priority = Priority.NORMAL
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0


class WorkflowEngine:
    """Advanced workflow execution engine with optimization"""
    
    def __init__(self, max_workers: int = 4, enable_persistence: bool = True):
        self.max_workers = max_workers
        self.enable_persistence = enable_persistence
        self.tasks: Dict[str, WorkflowTask] = {}
        self.task_queue = queue.PriorityQueue()
        self.completed_tasks: Dict[str, WorkflowTask] = {}
        self.failed_tasks: Dict[str, WorkflowTask] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = False
        self.worker_threads = []
        self.metrics = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'average_execution_time': 0.0,
            'throughput_per_minute': 0.0
        }
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)
        
        if enable_persistence:
            self._load_persistent_state()
    
    def add_task(self, task: WorkflowTask) -> bool:
        """Add task to workflow with dependency validation"""
        try:
            with self._lock:
                # Validate dependencies
                for dep_id in task.dependencies:
                    if dep_id not in self.tasks and dep_id not in self.completed_tasks:
                        self._logger.error(f"Dependency {dep_id} not found for task {task.id}")
                        return False
                
                self.tasks[task.id] = task
                self.metrics['total_tasks'] += 1
                
                # Add to queue if dependencies are satisfied
                if self._dependencies_satisfied(task):
                    self.task_queue.put((task.priority.value, task.created_at.timestamp(), task))
                    self._logger.info(f"Task {task.id} added to queue")
                else:
                    self._logger.info(f"Task {task.id} waiting for dependencies")
                
                if self.enable_persistence:
                    self._save_persistent_state()
                
                return True
        except Exception as e:
            self._logger.error(f"Error adding task {task.id}: {e}")
            return False
    
    def start(self):
        """Start the workflow engine"""
        if self.running:
            return
        
        self.running = True
        self._logger.info("Starting workflow engine")
        
        # Start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, name=f"WorkflowWorker-{i}")
            worker.daemon = True
            worker.start()
            self.worker_threads.append(worker)
        
        # Start dependency resolver thread
        resolver = threading.Thread(target=self._dependency_resolver, name="DependencyResolver")
        resolver.daemon = True
        resolver.start()
        
        # Start metrics collector thread
        metrics_thread = threading.Thread(target=self._metrics_collector, name="MetricsCollector")
        metrics_thread.daemon = True
        metrics_thread.start()
    
    def stop(self, timeout: float = 30.0):
        """Stop the workflow engine gracefully"""
        self._logger.info("Stopping workflow engine")
        self.running = False
        
        # Wait for workers to finish current tasks
        start_time = time.time()
        while any(thread.is_alive() for thread in self.worker_threads) and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        self.executor.shutdown(wait=True, timeout=timeout)
        
        if self.enable_persistence:
            self._save_persistent_state()
        
        self._logger.info("Workflow engine stopped")
    
    def get_task_status(self, task_id: str) -> Optional[WorkflowStatus]:
        """Get status of specific task"""
        with self._lock:
            if task_id in self.tasks:
                return self.tasks[task_id].status
            elif task_id in self.completed_tasks:
                return self.completed_tasks[task_id].status
            elif task_id in self.failed_tasks:
                return self.failed_tasks[task_id].status
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get workflow execution metrics"""
        with self._lock:
            return self.metrics.copy()
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get comprehensive workflow status summary"""
        with self._lock:
            pending_count = sum(1 for task in self.tasks.values() if task.status == WorkflowStatus.PENDING)
            running_count = sum(1 for task in self.tasks.values() if task.status == WorkflowStatus.RUNNING)
            
            return {
                'total_tasks': self.metrics['total_tasks'],
                'pending_tasks': pending_count,
                'running_tasks': running_count,
                'completed_tasks': len(self.completed_tasks),
                'failed_tasks': len(self.failed_tasks),
                'queue_size': self.task_queue.qsize(),
                'average_execution_time': self.metrics['average_execution_time'],
                'throughput_per_minute': self.metrics['throughput_per_minute'],
                'engine_status': 'running' if self.running else 'stopped'
            }
    
    def _worker_loop(self):
        """Main worker loop for task execution"""
        while self.running:
            try:
                # Get task from queue with timeout
                try:
                    priority, timestamp, task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Update task status
                with self._lock:
                    task.status = WorkflowStatus.RUNNING
                    task.started_at = datetime.now()
                
                self._logger.info(f"Executing task {task.id}")
                
                # Execute task
                success = self._execute_task(task)
                
                # Update task status and move to appropriate collection
                with self._lock:
                    task.completed_at = datetime.now()
                    if success:
                        task.status = WorkflowStatus.COMPLETED
                        self.completed_tasks[task.id] = task
                        self.metrics['completed_tasks'] += 1
                        self._logger.info(f"Task {task.id} completed successfully")
                    else:
                        if task.retry_count < task.max_retries:
                            task.status = WorkflowStatus.RETRYING
                            task.retry_count += 1
                            time.sleep(task.retry_delay * task.retry_count)  # Exponential backoff
                            self.task_queue.put((task.priority.value, time.time(), task))
                            self._logger.warning(f"Task {task.id} retrying ({task.retry_count}/{task.max_retries})")
                        else:
                            task.status = WorkflowStatus.FAILED
                            self.failed_tasks[task.id] = task
                            self.metrics['failed_tasks'] += 1
                            self._logger.error(f"Task {task.id} failed after {task.max_retries} retries")
                    
                    # Remove from active tasks
                    if task.id in self.tasks:
                        del self.tasks[task.id]
                
                # Check for dependent tasks
                self._check_dependent_tasks(task.id)
                
            except Exception as e:
                self._logger.error(f"Worker error: {e}")
    
    def _execute_task(self, task: WorkflowTask) -> bool:
        """Execute individual task with timeout and error handling"""
        try:
            if task.timeout:
                future = self.executor.submit(task.function, *task.args, **task.kwargs)
                task.result = future.result(timeout=task.timeout)
            else:
                task.result = task.function(*task.args, **task.kwargs)
            
            return True
        except Exception as e:
            task.error = str(e)
            self._logger.error(f"Task {task.id} execution failed: {e}")
            return False
    
    def _dependencies_satisfied(self, task: WorkflowTask) -> bool:
        """Check if task dependencies are satisfied"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True
    
    def _dependency_resolver(self):
        """Background thread to check for tasks with satisfied dependencies"""
        while self.running:
            try:
                with self._lock:
                    ready_tasks = []
                    for task in self.tasks.values():
                        if (task.status == WorkflowStatus.PENDING and 
                            self._dependencies_satisfied(task)):
                            ready_tasks.append(task)
                    
                    for task in ready_tasks:
                        self.task_queue.put((task.priority.value, task.created_at.timestamp(), task))
                        self._logger.info(f"Task {task.id} dependencies satisfied, added to queue")
                
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                self._logger.error(f"Dependency resolver error: {e}")
    
    def _check_dependent_tasks(self, completed_task_id: str):
        """Check if any waiting tasks can now be executed"""
        with self._lock:
            for task in self.tasks.values():
                if (task.status == WorkflowStatus.PENDING and 
                    completed_task_id in task.dependencies and
                    self._dependencies_satisfied(task)):
                    self.task_queue.put((task.priority.value, task.created_at.timestamp(), task))
                    self._logger.info(f"Task {task.id} ready after dependency {completed_task_id}")
    
    def _metrics_collector(self):
        """Background thread to collect and update metrics"""
        while self.running:
            try:
                with self._lock:
                    if self.completed_tasks:
                        total_time = sum(
                            (task.completed_at - task.started_at).total_seconds()
                            for task in self.completed_tasks.values()
                            if task.started_at and task.completed_at
                        )
                        self.metrics['average_execution_time'] = total_time / len(self.completed_tasks)
                    
                    # Calculate throughput (tasks per minute)
                    current_time = datetime.now()
                    one_minute_ago = current_time - timedelta(minutes=1)
                    recent_completions = sum(
                        1 for task in self.completed_tasks.values()
                        if task.completed_at and task.completed_at > one_minute_ago
                    )
                    self.metrics['throughput_per_minute'] = recent_completions
                
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                self._logger.error(f"Metrics collector error: {e}")
    
    def _save_persistent_state(self):
        """Save workflow state to disk"""
        try:
            state = {
                'tasks': self.tasks,
                'completed_tasks': self.completed_tasks,
                'failed_tasks': self.failed_tasks,
                'metrics': self.metrics
            }
            with open('workflow_state.pkl', 'wb') as f:
                pickle.dump(state, f)
        except Exception as e:
            self._logger.error(f"Failed to save workflow state: {e}")
    
    def _load_persistent_state(self):
        """Load workflow state from disk"""
        try:
            with open('workflow_state.pkl', 'rb') as f:
                state = pickle.load(f)
                self.tasks = state.get('tasks', {})
                self.completed_tasks = state.get('completed_tasks', {})
                self.failed_tasks = state.get('failed_tasks', {})
                self.metrics = state.get('metrics', self.metrics)
                
            # Restore pending tasks to queue
            for task in self.tasks.values():
                if task.status == WorkflowStatus.PENDING and self._dependencies_satisfied(task):
                    self.task_queue.put((task.priority.value, task.created_at.timestamp(), task))
                    
            self._logger.info("Workflow state restored from persistence")
        except FileNotFoundError:
            self._logger.info("No persistent state found, starting fresh")
        except Exception as e:
            self._logger.error(f"Failed to load workflow state: {e}")


# Global workflow engine instance
workflow_engine = WorkflowEngine()


def create_workflow_task(task_id: str, name: str, function: Callable, 
                        args: tuple = (), kwargs: dict = None, 
                        priority: Priority = Priority.NORMAL,
                        dependencies: List[str] = None) -> WorkflowTask:
    """Helper function to create workflow tasks"""
    return WorkflowTask(
        id=task_id,
        name=name,
        function=function,
        args=args,
        kwargs=kwargs or {},
        priority=priority,
        dependencies=dependencies or []
    )


def schedule_task(task_id: str, name: str, function: Callable,
                 args: tuple = (), kwargs: dict = None,
                 priority: Priority = Priority.NORMAL,
                 dependencies: List[str] = None) -> bool:
    """Schedule a task for execution"""
    task = create_workflow_task(task_id, name, function, args, kwargs, priority, dependencies)
    return workflow_engine.add_task(task)


def get_workflow_status() -> Dict[str, Any]:
    """Get current workflow status"""
    return workflow_engine.get_workflow_summary()


def start_workflow_engine():
    """Start the global workflow engine"""
    workflow_engine.start()


def stop_workflow_engine():
    """Stop the global workflow engine"""
    workflow_engine.stop()