/**
 * Asynchronous Operations Frontend Interface
 * 2ª Vara Cível de Cariacica - Enhanced async functionality
 */

class AsyncOperationsManager {
    constructor() {
        this.pendingOperations = new Map();
        this.completedOperations = [];
        this.chatCache = new Map();
        this.conversationId = this.generateConversationId();
        this.init();
    }

    init() {
        console.log('AsyncOperationsManager initialized');
        this.setupEventListeners();
        this.initializeAsyncChatbot();
        this.setupPerformanceMonitoring();
    }

    generateConversationId() {
        return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    setupEventListeners() {
        // Enhanced chatbot with async capabilities
        const chatForm = document.getElementById('chatbot-form');
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAsyncChatMessage();
            });
        }

        // Batch processing button
        const batchBtn = document.getElementById('batch-process-btn');
        if (batchBtn) {
            batchBtn.addEventListener('click', () => this.handleBatchProcessing());
        }

        // Background task triggers
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-async-task]')) {
                const taskType = e.target.dataset.asyncTask;
                this.startBackgroundTask(taskType);
            }
        });
    }

    async handleAsyncChatMessage() {
        const messageInput = document.getElementById('user-message');
        const chatWindow = document.getElementById('chat-window');
        
        if (!messageInput || !messageInput.value.trim()) return;

        const message = messageInput.value.trim();
        const startTime = performance.now();

        // Show loading state
        this.addChatMessage('user', message);
        const loadingId = this.addChatMessage('bot', 'Processando...', true);

        try {
            const response = await this.sendAsyncChatMessage(message);
            
            // Remove loading message
            this.removeChatMessage(loadingId);
            
            // Add actual response
            this.addChatMessage('bot', response.response, false, {
                processingTime: response.processing_time,
                cached: response.cached,
                timestamp: response.timestamp
            });

            // Update performance metrics
            const totalTime = performance.now() - startTime;
            this.updatePerformanceMetrics('chat', totalTime, response.processing_time);

            messageInput.value = '';

        } catch (error) {
            this.removeChatMessage(loadingId);
            this.addChatMessage('bot', 'Erro ao processar mensagem. Tente novamente.', false, { error: true });
            console.error('Async chat error:', error);
        }
    }

    async sendAsyncChatMessage(message) {
        const response = await fetch('/async/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                message: message,
                conversation_id: this.conversationId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    async handleBatchProcessing() {
        const batchInput = document.getElementById('batch-messages');
        if (!batchInput || !batchInput.value.trim()) return;

        const messages = batchInput.value.split('\n').filter(msg => msg.trim());
        if (messages.length === 0) return;

        const batchData = messages.map(msg => ({
            message: msg.trim(),
            conversation_id: this.conversationId + '_batch'
        }));

        const startTime = performance.now();
        this.showBatchProgress('Processando mensagens em lote...', 0);

        try {
            const response = await fetch('/async/batch-chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ messages: batchData })
            });

            const result = await response.json();
            const totalTime = performance.now() - startTime;

            this.showBatchResults(result, totalTime);
            this.updatePerformanceMetrics('batch', totalTime, null);

        } catch (error) {
            this.showBatchProgress('Erro no processamento em lote', 100, true);
            console.error('Batch processing error:', error);
        }
    }

    async startBackgroundTask(taskType, params = {}) {
        try {
            const response = await fetch('/async/background-task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    task_type: taskType,
                    params: params
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.monitorBackgroundTask(result.task_id, taskType);
                this.showNotification(`Tarefa ${taskType} iniciada`, 'info');
            } else {
                this.showNotification(`Erro ao iniciar tarefa: ${result.error}`, 'error');
            }

        } catch (error) {
            console.error('Background task error:', error);
            this.showNotification('Erro ao iniciar tarefa em segundo plano', 'error');
        }
    }

    async monitorBackgroundTask(taskId, taskType) {
        const startTime = Date.now();
        const maxWaitTime = 300000; // 5 minutes

        const checkStatus = async () => {
            try {
                const response = await fetch(`/async/task-status/${taskId}`);
                const result = await response.json();

                if (result.success && result.status) {
                    if (result.status.status === 'completed' || result.status.done) {
                        this.showNotification(`Tarefa ${taskType} concluída`, 'success');
                        this.displayTaskResults(taskId, result.status);
                        return;
                    }

                    // Continue monitoring if task is still running
                    if (Date.now() - startTime < maxWaitTime) {
                        setTimeout(checkStatus, 2000); // Check every 2 seconds
                    } else {
                        this.showNotification(`Timeout monitorando tarefa ${taskType}`, 'warning');
                    }
                }

            } catch (error) {
                console.error('Task monitoring error:', error);
            }
        };

        setTimeout(checkStatus, 1000); // Start monitoring after 1 second
    }

    async runHealthCheck() {
        const startTime = performance.now();
        
        try {
            const response = await fetch('/async/health-check');
            const result = await response.json();
            const checkTime = performance.now() - startTime;

            this.displayHealthCheckResults(result, checkTime);

        } catch (error) {
            console.error('Health check error:', error);
            this.showNotification('Erro na verificação de saúde do sistema', 'error');
        }
    }

    async runParallelOperations() {
        const operations = [
            { name: 'database_check', type: 'database_query', params: { query: 'health_check' }},
            { name: 'api_test', type: 'api_call', params: { endpoint: '/health' }},
            { name: 'file_scan', type: 'file_processing', params: { scan_type: 'quick' }}
        ];

        const startTime = performance.now();

        try {
            const response = await fetch('/async/parallel-operations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ operations: operations })
            });

            const result = await response.json();
            const totalTime = performance.now() - startTime;

            this.displayParallelResults(result, totalTime);

        } catch (error) {
            console.error('Parallel operations error:', error);
            this.showNotification('Erro nas operações paralelas', 'error');
        }
    }

    // UI Helper Methods
    addChatMessage(type, content, isLoading = false, metadata = {}) {
        const chatWindow = document.getElementById('chat-window');
        if (!chatWindow) return null;

        const messageId = 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5);
        const messageDiv = document.createElement('div');
        messageDiv.id = messageId;
        messageDiv.className = `chat-message ${type}-message${isLoading ? ' loading' : ''}`;

        let metadataHtml = '';
        if (metadata.processingTime) {
            metadataHtml += `<small class="text-muted">Processado em ${metadata.processingTime.toFixed(2)}ms</small>`;
        }
        if (metadata.cached) {
            metadataHtml += `<small class="text-info"> (Cache)</small>`;
        }

        messageDiv.innerHTML = `
            <div class="message-content">${content}</div>
            ${metadataHtml ? `<div class="message-metadata">${metadataHtml}</div>` : ''}
        `;

        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        return messageId;
    }

    removeChatMessage(messageId) {
        const message = document.getElementById(messageId);
        if (message) {
            message.remove();
        }
    }

    showBatchProgress(message, progress, isError = false) {
        const progressContainer = document.getElementById('batch-progress');
        if (!progressContainer) return;

        progressContainer.innerHTML = `
            <div class="progress mb-2">
                <div class="progress-bar ${isError ? 'bg-danger' : 'bg-primary'}" 
                     style="width: ${progress}%"></div>
            </div>
            <small class="${isError ? 'text-danger' : 'text-muted'}">${message}</small>
        `;

        if (progress === 100) {
            setTimeout(() => {
                progressContainer.innerHTML = '';
            }, 3000);
        }
    }

    showBatchResults(result, totalTime) {
        const resultsContainer = document.getElementById('batch-results');
        if (!resultsContainer) return;

        const successCount = result.results.filter(r => r.success).length;
        const errorCount = result.results.length - successCount;

        resultsContainer.innerHTML = `
            <div class="alert alert-info">
                <h6>Processamento em Lote Concluído</h6>
                <p>Tempo total: ${totalTime.toFixed(2)}ms</p>
                <p>Sucessos: ${successCount} | Erros: ${errorCount}</p>
            </div>
        `;

        this.showBatchProgress('Concluído', 100);
    }

    displayHealthCheckResults(result, checkTime) {
        const container = document.getElementById('health-results');
        if (!container) return;

        const statusClass = result.overall_status === 'healthy' ? 'success' : 'warning';
        const componentsHtml = result.components.map(comp => `
            <li class="list-group-item d-flex justify-content-between align-items-center">
                ${comp.operation}
                <span class="badge badge-${comp.success ? 'success' : 'danger'}">
                    ${comp.success ? 'OK' : 'ERRO'}
                </span>
            </li>
        `).join('');

        container.innerHTML = `
            <div class="alert alert-${statusClass}">
                <h6>Verificação de Saúde - ${result.overall_status.toUpperCase()}</h6>
                <p>Tempo de verificação: ${checkTime.toFixed(2)}ms</p>
            </div>
            <ul class="list-group">${componentsHtml}</ul>
        `;
    }

    displayParallelResults(result, totalTime) {
        const container = document.getElementById('parallel-results');
        if (!container) return;

        const resultsHtml = result.results.map(res => `
            <div class="card mb-2">
                <div class="card-body py-2">
                    <h6 class="card-title">${res.operation}</h6>
                    <p class="card-text">
                        Status: <span class="badge badge-${res.success ? 'success' : 'danger'}">
                            ${res.success ? 'Sucesso' : 'Erro'}
                        </span>
                    </p>
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="alert alert-info">
                <h6>Operações Paralelas Concluídas</h6>
                <p>Tempo total: ${totalTime.toFixed(2)}ms</p>
                <p>Operações: ${result.total_operations}</p>
            </div>
            ${resultsHtml}
        `;
    }

    updatePerformanceMetrics(operation, totalTime, serverTime) {
        const metricsContainer = document.getElementById('performance-metrics');
        if (!metricsContainer) return;

        const metric = {
            operation: operation,
            totalTime: totalTime,
            serverTime: serverTime,
            networkTime: serverTime ? totalTime - serverTime : totalTime,
            timestamp: new Date().toISOString()
        };

        this.completedOperations.push(metric);

        // Keep only last 20 operations
        if (this.completedOperations.length > 20) {
            this.completedOperations = this.completedOperations.slice(-20);
        }

        this.renderPerformanceMetrics();
    }

    renderPerformanceMetrics() {
        const container = document.getElementById('performance-metrics');
        if (!container || this.completedOperations.length === 0) return;

        const avgTotalTime = this.completedOperations.reduce((sum, op) => sum + op.totalTime, 0) / this.completedOperations.length;
        const avgServerTime = this.completedOperations
            .filter(op => op.serverTime)
            .reduce((sum, op) => sum + op.serverTime, 0) / this.completedOperations.filter(op => op.serverTime).length;

        container.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h6 class="card-title">Métricas de Performance</h6>
                            <p>Tempo médio total: ${avgTotalTime.toFixed(2)}ms</p>
                            <p>Tempo médio servidor: ${avgServerTime ? avgServerTime.toFixed(2) : 'N/A'}ms</p>
                            <p>Operações realizadas: ${this.completedOperations.length}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    setupPerformanceMonitoring() {
        // Monitor page performance
        if ('performance' in window) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    console.log('Page load performance:', {
                        loadTime: perfData.loadEventEnd - perfData.loadEventStart,
                        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                        totalTime: perfData.loadEventEnd - perfData.fetchStart
                    });
                }, 1000);
            });
        }
    }

    initializeAsyncChatbot() {
        // Initialize async chatbot with enhanced features
        console.log('Async chatbot initialized with conversation ID:', this.conversationId);
    }

    showNotification(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="close" data-dismiss="alert">
                <span>&times;</span>
            </button>
        `;

        document.body.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }

    displayTaskResults(taskId, results) {
        console.log(`Task ${taskId} completed:`, results);
        // Implementation depends on specific task results structure
    }
}

// Initialize async operations manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.asyncOpsManager === 'undefined') {
        window.asyncOpsManager = new AsyncOperationsManager();
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AsyncOperationsManager;
}