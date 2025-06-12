/**
 * Enhanced Chatbot functionality for 2ª Vara Cível de Cariacica
 * Robust implementation with comprehensive error handling and performance optimization
 */

class EnhancedChatbot {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.messages = [];
        this.connectionAttempts = 0;
        this.maxRetries = 3;
        this.retryDelay = 1000;
        this.messageQueue = [];
        this.isOnline = navigator.onLine;
        this.performanceMetrics = {
            totalMessages: 0,
            totalResponseTime: 0,
            averageResponseTime: 0,
            errorCount: 0
        };
        
        this.init();
        this.setupNetworkMonitoring();
        this.setupPerformanceMonitoring();
    }

    init() {
        this.bindEvents();
        this.loadChatHistory();
        this.setupAccessibility();
        this.validateElements();
        this.showWelcomeMessage();
    }

    validateElements() {
        const requiredElements = [
            'chatbot-toggle',
            'chatbot-window',
            'chatbot-close',
            'chatbot-send',
            'chatbot-input',
            'chatbot-messages'
        ];

        const missingElements = requiredElements.filter(id => !document.getElementById(id));
        
        if (missingElements.length > 0) {
            console.error('Chatbot: Missing required elements:', missingElements);
            this.showSystemError('Erro na inicialização do chatbot. Recarregue a página.');
            return false;
        }
        
        return true;
    }

    bindEvents() {
        console.log('Configurando eventos do chatbot...');
        
        const toggleButton = document.getElementById('chatbot-toggle');
        const closeButton = document.getElementById('chatbot-close');
        const sendButton = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input');
        const chatWindow = document.getElementById('chatbot-window');

        if (toggleButton) {
            console.log('Adicionando evento de clique ao botão toggle');
            toggleButton.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('Botão toggle clicado!');
                this.toggleChat();
            });
        }

        if (closeButton) {
            closeButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeChat();
            });
        }

        if (sendButton) {
            sendButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }

        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Auto-resize and validation
            input.addEventListener('input', (e) => {
                this.handleInputChange(e);
            });

            // Character limit indicator
            input.addEventListener('keyup', () => {
                this.updateCharacterCount();
            });
        }

        // Enhanced keyboard navigation
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (this.isOpen && chatWindow && 
                !chatWindow.contains(e.target) && 
                !toggleButton.contains(e.target)) {
                this.closeChat();
            }
        });
    }

    handleInputChange(e) {
        const input = e.target;
        const maxLength = 2000;
        
        // Auto-resize
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 100) + 'px';
        
        // Character validation
        if (input.value.length > maxLength) {
            input.value = input.value.substring(0, maxLength);
            this.showWarning(`Mensagem limitada a ${maxLength} caracteres`);
        }
        
        // Input sanitization
        input.value = this.sanitizeInput(input.value);
    }

    sanitizeInput(text) {
        // Remove potentially dangerous characters while preserving functionality
        return text.replace(/[<>]/g, '').replace(/javascript:/gi, '');
    }

    updateCharacterCount() {
        const input = document.getElementById('chatbot-input');
        if (!input) return;
        
        const currentLength = input.value.length;
        const maxLength = 2000;
        
        let indicator = document.getElementById('char-indicator');
        if (!indicator) {
            indicator = document.createElement('small');
            indicator.id = 'char-indicator';
            indicator.className = 'text-muted mt-1';
            input.parentNode.appendChild(indicator);
        }
        
        indicator.textContent = `${currentLength}/${maxLength}`;
        
        if (currentLength > maxLength * 0.9) {
            indicator.className = 'text-warning mt-1';
        } else {
            indicator.className = 'text-muted mt-1';
        }
    }

    handleKeyboardShortcuts(e) {
        // Escape to close
        if (e.key === 'Escape' && this.isOpen) {
            this.closeChat();
        }
        
        // Ctrl+Enter to send message
        if (e.ctrlKey && e.key === 'Enter' && this.isOpen) {
            e.preventDefault();
            this.sendMessage();
        }
        
        // Alt+C to toggle chat
        if (e.altKey && e.key === 'c') {
            e.preventDefault();
            this.toggleChat();
        }
    }

    setupAccessibility() {
        const toggleButton = document.getElementById('chatbot-toggle');
        const chatWindow = document.getElementById('chatbot-window');
        
        if (toggleButton) {
            toggleButton.setAttribute('aria-label', 'Abrir assistente virtual');
            toggleButton.setAttribute('role', 'button');
            toggleButton.setAttribute('tabindex', '0');
        }
        
        if (chatWindow) {
            chatWindow.setAttribute('role', 'dialog');
            chatWindow.setAttribute('aria-label', 'Janela do assistente virtual');
        }
    }

    setupNetworkMonitoring() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.processQueuedMessages();
            this.hideSystemError();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showSystemError('Sem conexão com a internet. Mensagens serão enviadas quando a conexão for restabelecida.');
        });
    }

    setupPerformanceMonitoring() {
        // Monitor chatbot performance
        this.performanceObserver = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach(entry => {
                if (entry.name.includes('chatbot')) {
                    console.log(`Chatbot performance: ${entry.name} - ${entry.duration}ms`);
                }
            });
        });
        
        if (this.performanceObserver) {
            this.performanceObserver.observe({ entryTypes: ['measure'] });
        }
    }

    toggleChat() {
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        const chatWindow = document.getElementById('chatbot-window');
        const toggleButton = document.getElementById('chatbot-toggle');
        const input = document.getElementById('chatbot-input');

        if (chatWindow) {
            chatWindow.style.display = 'flex';
            chatWindow.setAttribute('aria-hidden', 'false');
            this.isOpen = true;
            
            // Update button appearance
            if (toggleButton) {
                toggleButton.innerHTML = '<i class="fas fa-times"></i>';
                toggleButton.setAttribute('aria-label', 'Fechar assistente virtual');
            }

            // Focus management
            if (input) {
                setTimeout(() => {
                    input.focus();
                    input.setAttribute('aria-expanded', 'true');
                }, 100);
            }

            // Announce to screen readers
            this.announceToScreenReader('Assistente virtual aberto');

            // Animation
            chatWindow.style.opacity = '0';
            chatWindow.style.transform = 'translateY(20px)';
            
            requestAnimationFrame(() => {
                chatWindow.style.transition = 'all 0.3s ease';
                chatWindow.style.opacity = '1';
                chatWindow.style.transform = 'translateY(0)';
            });

            // Track interaction
            this.trackInteraction('chatbot_opened');
        }
    }

    closeChat() {
        const chatWindow = document.getElementById('chatbot-window');
        const toggleButton = document.getElementById('chatbot-toggle');
        const input = document.getElementById('chatbot-input');

        if (chatWindow) {
            chatWindow.style.display = 'none';
            chatWindow.setAttribute('aria-hidden', 'true');
            this.isOpen = false;

            // Update button appearance
            if (toggleButton) {
                toggleButton.innerHTML = '<i class="fas fa-comments"></i>';
                toggleButton.setAttribute('aria-label', 'Abrir assistente virtual');
            }

            // Focus management
            if (input) {
                input.setAttribute('aria-expanded', 'false');
            }

            // Announce to screen readers
            this.announceToScreenReader('Assistente virtual fechado');

            // Track interaction
            this.trackInteraction('chatbot_closed');
        }
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input?.value?.trim();

        if (!message) {
            this.showWarning('Digite uma mensagem antes de enviar');
            return;
        }

        if (!this.isOnline) {
            this.queueMessage(message);
            this.showWarning('Sem conexão. Mensagem adicionada à fila para envio posterior.');
            return;
        }

        const startTime = performance.now();

        // Clear input immediately
        input.value = '';
        input.style.height = 'auto';
        this.updateCharacterCount();

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send message with retry logic
            const response = await this.sendToBackendWithRetry(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Calculate response time
            const responseTime = performance.now() - startTime;
            this.updatePerformanceMetrics(responseTime, false);
            
            // Add bot response
            this.addMessage(response.response || response, 'bot');

            // Save to history
            this.saveChatHistory();

            // Track successful interaction
            this.trackInteraction('message_sent_success', { responseTime });

            // Reset connection attempts on success
            this.connectionAttempts = 0;

        } catch (error) {
            console.error('Chatbot error:', error);
            this.hideTypingIndicator();
            this.updatePerformanceMetrics(0, true);
            
            // Show appropriate error message
            const errorMessage = this.getErrorMessage(error);
            this.addMessage(errorMessage, 'bot', 'error');
            
            // Track error
            this.trackInteraction('message_sent_error', { error: error.message });
        }
    }

    async sendToBackendWithRetry(message, attempt = 1) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout

            const response = await fetch('/chatbot/api/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                
                if (response.status === 429) {
                    throw new Error('rate_limit');
                } else if (response.status === 400) {
                    throw new Error(errorData.error || 'Dados inválidos');
                } else if (response.status >= 500) {
                    throw new Error('server_error');
                } else {
                    throw new Error(errorData.error || 'Erro na comunicação');
                }
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            return data;

        } catch (error) {
            this.connectionAttempts++;

            // Handle specific error types
            if (error.name === 'AbortError') {
                throw new Error('timeout');
            }

            // Retry logic for network errors
            if (attempt < this.maxRetries && 
                (error.message === 'server_error' || error.message.includes('fetch'))) {
                
                await this.delay(this.retryDelay * attempt);
                return this.sendToBackendWithRetry(message, attempt + 1);
            }

            throw error;
        }
    }

    getErrorMessage(error) {
        const errorMessages = {
            'rate_limit': 'Muitas mensagens enviadas. Aguarde um momento antes de tentar novamente.',
            'timeout': 'Tempo limite excedido. Verifique sua conexão e tente novamente.',
            'server_error': 'Erro temporário no servidor. Tente novamente em alguns instantes.',
            'network': 'Erro de conexão. Verifique sua internet e tente novamente.'
        };

        const errorType = error.message.toLowerCase();
        return errorMessages[errorType] || 
               'Desculpe, ocorreu um erro. Tente novamente ou entre em contato conosco pelo telefone (27) 3246-8200.';
    }

    queueMessage(message) {
        this.messageQueue.push({
            message,
            timestamp: Date.now()
        });
    }

    async processQueuedMessages() {
        if (this.messageQueue.length === 0) return;

        this.showInfo('Processando mensagens em fila...');

        for (const item of this.messageQueue) {
            try {
                await this.sendMessage();
                await this.delay(1000); // Delay between queued messages
            } catch (error) {
                console.error('Error processing queued message:', error);
            }
        }

        this.messageQueue = [];
        this.hideInfo();
    }

    addMessage(text, sender, type = 'normal') {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        if (type === 'error') {
            messageDiv.classList.add('error-message');
        }
        
        this.setMessageContent(messageDiv, text);

        // Add timestamp for accessibility
        const timestamp = new Date().toLocaleTimeString('pt-BR');
        messageDiv.setAttribute('aria-label', 
            `${sender === 'user' ? 'Você' : 'Assistente'} às ${timestamp}: ${text}`);

        // Add message metadata
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        metaDiv.innerHTML = `<small class="text-muted">${timestamp}</small>`;
        messageDiv.appendChild(metaDiv);

        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom with smooth animation
        this.scrollToBottom(messagesContainer);

        // Add to messages array
        this.messages.push({
            text: text,
            sender: sender,
            timestamp: new Date().toISOString(),
            type: type
        });

        // Announce new messages to screen readers
        if (sender === 'bot') {
            this.announceToScreenReader(`Assistente respondeu: ${text}`);
        }

        // Animate message appearance
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(10px)';
        
        requestAnimationFrame(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        });
    }

    setMessageContent(messageDiv, text) {
        // Safely set text content and apply formatting
        messageDiv.textContent = text;
        
        const content = messageDiv.textContent;
        messageDiv.innerHTML = '';
        
        this.addFormattedContent(messageDiv, content);
    }

    addFormattedContent(container, text) {
        // Enhanced text formatting with security
        const patterns = {
            url: /(https?:\/\/[^\s]+)/g,
            email: /([\w.-]+@[\w.-]+\.\w+)/g,
            phone: /(\(?\d{2}\)?\s?\d{4,5}-?\d{4})/g,
            actionLink: /\*\*\[([^\]]+)\]\(([^)]+)\)\*\*/g,
            bold: /\*\*([^*]+)\*\*/g
        };
        
        let processedText = text;
        const elements = [];
        
        // Process action links first
        processedText = processedText.replace(patterns.actionLink, (match, linkText, url) => {
            const safeUrl = this.sanitizeUrl(url);
            const button = document.createElement('a');
            button.href = safeUrl;
            button.className = 'btn btn-primary btn-sm me-2 mb-2';
            button.innerHTML = `<i class="fas fa-external-link-alt me-1"></i>${linkText}`;
            button.target = '_blank';
            button.rel = 'noopener noreferrer';
            
            elements.push(button);
            return `__ELEMENT_${elements.length - 1}__`;
        });
        
        // Process other patterns
        processedText = processedText.replace(patterns.url, (match) => {
            const safeUrl = this.sanitizeUrl(match);
            const link = document.createElement('a');
            link.href = safeUrl;
            link.textContent = match;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            
            elements.push(link);
            return `__ELEMENT_${elements.length - 1}__`;
        });
        
        // Split by line breaks and process
        const lines = processedText.split('\n');
        lines.forEach((line, i) => {
            if (i > 0) {
                container.appendChild(document.createElement('br'));
            }
            
            if (line.trim()) {
                this.processLineContent(container, line, elements);
            }
        });
    }

    processLineContent(container, line, elements) {
        const parts = line.split(/(__ELEMENT_\d+__)/);
        
        parts.forEach(part => {
            if (part.startsWith('__ELEMENT_')) {
                const index = parseInt(part.match(/\d+/)[0]);
                if (elements[index]) {
                    container.appendChild(elements[index]);
                }
            } else if (part.trim()) {
                // Process bold text
                const boldRegex = /\*\*([^*]+)\*\*/g;
                let lastIndex = 0;
                let match;
                
                while ((match = boldRegex.exec(part)) !== null) {
                    // Add text before bold
                    if (match.index > lastIndex) {
                        container.appendChild(
                            document.createTextNode(part.substring(lastIndex, match.index))
                        );
                    }
                    
                    // Add bold text
                    const bold = document.createElement('strong');
                    bold.textContent = match[1];
                    container.appendChild(bold);
                    
                    lastIndex = match.index + match[0].length;
                }
                
                // Add remaining text
                if (lastIndex < part.length) {
                    container.appendChild(
                        document.createTextNode(part.substring(lastIndex))
                    );
                }
            }
        });
    }

    sanitizeUrl(url) {
        // Basic URL sanitization
        if (!url.startsWith('http://') && !url.startsWith('https://') && !url.startsWith('/')) {
            return '#';
        }
        return url.replace(/javascript:/gi, '');
    }

    showTypingIndicator() {
        if (this.isTyping) return;

        this.isTyping = true;
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.setAttribute('aria-label', 'Assistente está digitando');
        typingDiv.innerHTML = `
            <div class="typing-animation">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <small class="typing-text">Digitando...</small>
        `;

        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom(messagesContainer);

        // Add CSS if not exists
        this.injectTypingStyles();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.style.opacity = '0';
            setTimeout(() => typingIndicator.remove(), 300);
        }
    }

    injectTypingStyles() {
        if (document.getElementById('typing-styles')) return;

        const style = document.createElement('style');
        style.id = 'typing-styles';
        style.textContent = `
            .typing-animation {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                margin-right: 8px;
            }
            .typing-animation span {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: rgba(255, 255, 255, 0.7);
                animation: typing-bounce 1.4s infinite ease-in-out;
            }
            .typing-animation span:nth-child(1) { animation-delay: 0s; }
            .typing-animation span:nth-child(2) { animation-delay: 0.2s; }
            .typing-animation span:nth-child(3) { animation-delay: 0.4s; }
            
            @keyframes typing-bounce {
                0%, 60%, 100% { 
                    transform: translateY(0); 
                    opacity: 0.4; 
                }
                30% { 
                    transform: translateY(-8px); 
                    opacity: 1; 
                }
            }
            
            .error-message {
                border-left: 3px solid #dc3545;
                background-color: #f8d7da;
                color: #721c24;
            }
            
            .typing-text {
                color: rgba(255, 255, 255, 0.8);
                font-style: italic;
            }
        `;
        
        document.head.appendChild(style);
    }

    scrollToBottom(container) {
        if (!container) return;
        
        container.scrollTo({
            top: container.scrollHeight,
            behavior: 'smooth'
        });
    }

    showWelcomeMessage() {
        if (this.messages.length === 0) {
            setTimeout(() => {
                this.addMessage(
                    'Olá! Sou o assistente virtual da 2ª Vara Cível de Cariacica. Como posso ajudá-lo hoje?', 
                    'bot'
                );
                setTimeout(() => {
                    this.addQuickResponses();
                }, 500);
            }, 1000);
        }
    }

    addQuickResponses() {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const quickResponses = [
            'Horário de funcionamento',
            'Localização',
            'Consulta processual',
            'Agendamento',
            'Audiências'
        ];

        const quickResponsesDiv = document.createElement('div');
        quickResponsesDiv.className = 'quick-responses';
        quickResponsesDiv.innerHTML = `
            <p class="small text-muted mb-2">Perguntas frequentes:</p>
            <div class="d-flex flex-wrap gap-2">
                ${quickResponses.map(response => 
                    `<button class="btn btn-outline-primary btn-sm quick-response-btn" 
                             data-response="${response}" 
                             aria-label="Enviar pergunta: ${response}">
                        ${response}
                     </button>`
                ).join('')}
            </div>
        `;

        messagesContainer.appendChild(quickResponsesDiv);
        this.scrollToBottom(messagesContainer);

        // Add event listeners
        quickResponsesDiv.querySelectorAll('.quick-response-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const input = document.getElementById('chatbot-input');
                if (input) {
                    input.value = btn.dataset.response;
                    this.sendMessage();
                }
            });
        });
    }

    // Utility methods
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.style.position = 'absolute';
        announcement.style.left = '-10000px';
        announcement.style.width = '1px';
        announcement.style.height = '1px';
        announcement.style.overflow = 'hidden';
        
        document.body.appendChild(announcement);
        announcement.textContent = message;
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    showWarning(message) {
        this.showNotification(message, 'warning');
    }

    showInfo(message) {
        this.showNotification(message, 'info');
    }

    showSystemError(message) {
        this.showNotification(message, 'error', true);
    }

    hideSystemError() {
        const errorNotification = document.querySelector('.system-error');
        if (errorNotification) {
            errorNotification.remove();
        }
    }

    hideInfo() {
        const infoNotification = document.querySelector('.system-info');
        if (infoNotification) {
            infoNotification.remove();
        }
    }

    showNotification(message, type = 'info', persistent = false) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} system-${type} position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 300px;
            animation: slideInRight 0.3s ease;
        `;
        notification.innerHTML = `
            <strong>${type === 'error' ? 'Erro' : type === 'warning' ? 'Aviso' : 'Info'}:</strong>
            ${message}
            ${!persistent ? '<button type="button" class="btn-close ms-2" aria-label="Fechar"></button>' : ''}
        `;

        document.body.appendChild(notification);

        // Close button functionality
        const closeBtn = notification.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                notification.remove();
            });
        }

        // Auto-remove non-persistent notifications
        if (!persistent) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.style.animation = 'slideOutRight 0.3s ease';
                    setTimeout(() => notification.remove(), 300);
                }
            }, 5000);
        }
    }

    updatePerformanceMetrics(responseTime, isError) {
        this.performanceMetrics.totalMessages++;
        
        if (isError) {
            this.performanceMetrics.errorCount++;
        } else {
            this.performanceMetrics.totalResponseTime += responseTime;
            this.performanceMetrics.averageResponseTime = 
                this.performanceMetrics.totalResponseTime / 
                (this.performanceMetrics.totalMessages - this.performanceMetrics.errorCount);
        }
    }

    trackInteraction(event, data = {}) {
        // Track user interactions for analytics
        if (window.Court?.trackUserInteraction) {
            window.Court.trackUserInteraction(event, 'enhanced_chatbot', data);
        }
        
        // Console logging for development
        console.log(`Chatbot interaction: ${event}`, data);
    }

    saveChatHistory() {
        try {
            const recentMessages = this.messages.slice(-50);
            localStorage.setItem('enhanced_chatbot_history', JSON.stringify({
                messages: recentMessages,
                timestamp: Date.now(),
                version: '2.0'
            }));
        } catch (error) {
            console.warn('Could not save chat history:', error);
        }
    }

    loadChatHistory() {
        try {
            const history = localStorage.getItem('enhanced_chatbot_history');
            if (history) {
                const data = JSON.parse(history);
                
                // Check if history is not too old (24 hours)
                if (Date.now() - data.timestamp < 24 * 60 * 60 * 1000) {
                    this.messages = data.messages || [];
                    this.displayChatHistory();
                }
            }
        } catch (error) {
            console.warn('Could not load chat history:', error);
        }
    }

    displayChatHistory() {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer || this.messages.length === 0) return;

        this.messages.forEach(msg => {
            if (msg.sender && msg.text) {
                this.addMessageDirect(msg.text, msg.sender, msg.type || 'normal');
            }
        });
    }

    addMessageDirect(text, sender, type = 'normal') {
        // Add message without triggering animations or side effects
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        if (type === 'error') {
            messageDiv.classList.add('error-message');
        }
        
        messageDiv.textContent = text;
        messagesContainer.appendChild(messageDiv);
    }

    // Public API methods
    getPerformanceMetrics() {
        return { ...this.performanceMetrics };
    }

    clearHistory() {
        this.messages = [];
        localStorage.removeItem('enhanced_chatbot_history');
        
        const messagesContainer = document.getElementById('chatbot-messages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
        
        this.showWelcomeMessage();
    }

    getHealthStatus() {
        return {
            isOnline: this.isOnline,
            isOpen: this.isOpen,
            connectionAttempts: this.connectionAttempts,
            queuedMessages: this.messageQueue.length,
            totalMessages: this.performanceMetrics.totalMessages,
            errorRate: this.performanceMetrics.errorCount / Math.max(1, this.performanceMetrics.totalMessages),
            averageResponseTime: this.performanceMetrics.averageResponseTime
        };
    }
}

// Initialize enhanced chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        console.log('Inicializando chatbot aprimorado...');
        
        // Check if required elements exist
        const requiredElements = ['chatbot-toggle', 'chatbot-window'];
        const missingElements = requiredElements.filter(id => !document.getElementById(id));
        
        if (missingElements.length > 0) {
            console.error('Elementos do chatbot não encontrados:', missingElements);
            return;
        }
        
        console.log('Elementos do chatbot encontrados, criando instância...');
        window.enhancedChatbot = new EnhancedChatbot();
        console.log('Chatbot aprimorado inicializado com sucesso');
        
    } catch (error) {
        console.error('Erro ao inicializar chatbot aprimorado:', error);
    }
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedChatbot;
}