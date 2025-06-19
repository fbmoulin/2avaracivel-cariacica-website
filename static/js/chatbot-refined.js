/**
 * Refined Chatbot Frontend for 2ª Vara Cível de Cariacica
 * Advanced UI with comprehensive features and analytics integration
 */

class RefinedChatbotUI {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.isOnline = navigator.onLine;
        this.messageQueue = [];
        this.sessionId = this.generateSessionId();
        this.conversationHistory = [];
        
        // Performance tracking
        this.metrics = {
            totalMessages: 0,
            averageResponseTime: 0,
            errorCount: 0,
            lastResponseTime: 0
        };
        
        // Configuration
        this.config = {
            apiEndpoint: '/chatbot/api/message',
            healthEndpoint: '/chatbot/api/health',
            metricsEndpoint: '/chatbot/api/metrics',
            maxRetries: 3,
            retryDelay: 1000,
            typingDelay: 1500,
            maxMessageLength: 1000
        };
        
        this.init();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    init() {
        this.createChatInterface();
        this.bindEvents();
        this.setupHealthMonitoring();
        this.loadConversationHistory();
        this.showWelcomeMessage();
        
        console.log('Refined Chatbot UI initialized with session:', this.sessionId);
    }

    createChatInterface() {
        // Enhanced chat toggle button
        const toggleButton = document.getElementById('chatbot-toggle');
        if (toggleButton) {
            toggleButton.innerHTML = `
                <i class="fas fa-comments" aria-hidden="true"></i>
                <span class="sr-only">Assistente Virtual</span>
            `;
            toggleButton.setAttribute('aria-label', 'Abrir assistente virtual da 2ª Vara Cível');
            toggleButton.setAttribute('title', 'Assistente Virtual - Clique para abrir');
        }

        // Enhanced chat window
        const chatWindow = document.getElementById('chatbot-window');
        if (chatWindow) {
            chatWindow.innerHTML = `
                <div class="chatbot-header">
                    <div class="chatbot-title">
                        <i class="fas fa-balance-scale" aria-hidden="true"></i>
                        <span>Assistente Virtual - 2ª Vara Cível</span>
                        <div class="connection-status ${this.isOnline ? 'online' : 'offline'}" 
                             title="${this.isOnline ? 'Online' : 'Offline'}"></div>
                    </div>
                    <div class="chatbot-actions">
                        <button id="chatbot-minimize" class="chatbot-action-btn" 
                                aria-label="Minimizar chat" title="Minimizar">
                            <i class="fas fa-minus"></i>
                        </button>
                        <button id="chatbot-close" class="chatbot-action-btn" 
                                aria-label="Fechar chat" title="Fechar">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="chatbot-messages" id="chatbot-messages" 
                     role="log" aria-live="polite" aria-label="Conversa com assistente virtual">
                </div>
                <div class="chatbot-input-container">
                    <div class="input-wrapper">
                        <textarea id="chatbot-input" 
                                placeholder="Digite sua pergunta sobre serviços da 2ª Vara Cível..."
                                maxlength="${this.config.maxMessageLength}"
                                rows="1"
                                aria-label="Digite sua mensagem"
                                aria-describedby="char-counter"></textarea>
                        <div class="input-actions">
                            <span id="char-counter" class="char-counter">0/${this.config.maxMessageLength}</span>
                            <button id="chatbot-send" class="send-btn" 
                                    aria-label="Enviar mensagem" title="Enviar (Enter)">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>
                    <div class="quick-actions" id="quick-actions">
                        <button class="quick-action-btn" data-message="Horário de funcionamento">
                            <i class="fas fa-clock"></i> Horários
                        </button>
                        <button class="quick-action-btn" data-message="Informações de contato">
                            <i class="fas fa-phone"></i> Contato
                        </button>
                        <button class="quick-action-btn" data-message="Como consultar meu processo">
                            <i class="fas fa-search"></i> Consulta
                        </button>
                        <button class="quick-action-btn" data-message="Agendar atendimento">
                            <i class="fas fa-calendar"></i> Agendar
                        </button>
                    </div>
                </div>
            `;
            
            chatWindow.setAttribute('role', 'dialog');
            chatWindow.setAttribute('aria-labelledby', 'chatbot-title');
            chatWindow.setAttribute('aria-modal', 'true');
        }
    }

    bindEvents() {
        // Toggle button
        const toggleButton = document.getElementById('chatbot-toggle');
        if (toggleButton) {
            toggleButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleChat();
            });
        }

        // Close and minimize buttons
        document.getElementById('chatbot-close')?.addEventListener('click', () => this.closeChat());
        document.getElementById('chatbot-minimize')?.addEventListener('click', () => this.minimizeChat());

        // Send button and input
        document.getElementById('chatbot-send')?.addEventListener('click', () => this.sendMessage());
        
        const input = document.getElementById('chatbot-input');
        if (input) {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            input.addEventListener('input', () => {
                this.updateCharCounter();
                this.autoResizeInput();
            });

            input.addEventListener('paste', (e) => {
                setTimeout(() => this.updateCharCounter(), 10);
            });
        }

        // Quick action buttons
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                this.sendQuickMessage(message);
            });
        });

        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeChat();
            }
            
            // Ctrl+Shift+C to toggle chat
            if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                this.toggleChat();
            }
        });

        // Online/offline detection
        window.addEventListener('online', () => this.handleConnectionChange(true));
        window.addEventListener('offline', () => this.handleConnectionChange(false));

        // Click outside to close
        document.addEventListener('click', (e) => {
            const chatWindow = document.getElementById('chatbot-window');
            const toggleButton = document.getElementById('chatbot-toggle');
            
            if (this.isOpen && chatWindow && !chatWindow.contains(e.target) && 
                !toggleButton.contains(e.target)) {
                this.closeChat();
            }
        });
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
        
        if (!chatWindow) return;

        chatWindow.style.display = 'flex';
        chatWindow.setAttribute('aria-hidden', 'false');
        this.isOpen = true;

        // Update toggle button
        if (toggleButton) {
            toggleButton.innerHTML = '<i class="fas fa-times" aria-hidden="true"></i>';
            toggleButton.setAttribute('aria-label', 'Fechar assistente virtual');
            toggleButton.setAttribute('aria-expanded', 'true');
        }

        // Smooth animation
        requestAnimationFrame(() => {
            chatWindow.classList.add('opening');
            
            setTimeout(() => {
                chatWindow.classList.remove('opening');
                chatWindow.classList.add('open');
                
                // Focus on input
                const input = document.getElementById('chatbot-input');
                if (input) {
                    input.focus();
                }
            }, 300);
        });

        // Announce to screen readers
        this.announceToScreenReader('Assistente virtual aberto. Use Tab para navegar pelos controles.');
        
        // Track interaction
        this.trackInteraction('chat_opened');
    }

    closeChat() {
        const chatWindow = document.getElementById('chatbot-window');
        const toggleButton = document.getElementById('chatbot-toggle');
        
        if (!chatWindow) return;

        chatWindow.classList.remove('open');
        chatWindow.classList.add('closing');

        setTimeout(() => {
            chatWindow.style.display = 'none';
            chatWindow.setAttribute('aria-hidden', 'true');
            chatWindow.classList.remove('closing');
            this.isOpen = false;
        }, 300);

        // Update toggle button
        if (toggleButton) {
            toggleButton.innerHTML = '<i class="fas fa-comments" aria-hidden="true"></i>';
            toggleButton.setAttribute('aria-label', 'Abrir assistente virtual');
            toggleButton.setAttribute('aria-expanded', 'false');
            toggleButton.focus();
        }

        // Announce to screen readers
        this.announceToScreenReader('Assistente virtual fechado');
        
        // Track interaction
        this.trackInteraction('chat_closed');
    }

    minimizeChat() {
        const chatWindow = document.getElementById('chatbot-window');
        if (!chatWindow) return;

        chatWindow.classList.toggle('minimized');
        
        const minimizeBtn = document.getElementById('chatbot-minimize');
        if (minimizeBtn) {
            const isMinimized = chatWindow.classList.contains('minimized');
            minimizeBtn.innerHTML = isMinimized ? 
                '<i class="fas fa-plus"></i>' : 
                '<i class="fas fa-minus"></i>';
            minimizeBtn.setAttribute('aria-label', isMinimized ? 'Restaurar chat' : 'Minimizar chat');
        }
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input?.value.trim();

        if (!message) return;

        const startTime = performance.now();
        
        // Clear input and reset
        input.value = '';
        this.updateCharCounter();
        this.autoResizeInput();

        // Add user message
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        // Hide quick actions during conversation
        this.hideQuickActions();

        try {
            const response = await this.sendToAPI(message);
            
            // Calculate response time
            const responseTime = performance.now() - startTime;
            this.updateMetrics(responseTime, true);

            // Hide typing indicator
            this.hideTypingIndicator();

            // Add bot response
            this.addMessage(response.content, 'assistant', response.metadata);

            // Show suggestions if available
            if (response.suggestions && response.suggestions.length > 0) {
                this.showSuggestions(response.suggestions);
            }

            // Save conversation
            this.saveConversationHistory();

            this.trackInteraction('message_sent', {
                responseTime,
                responseType: response.response_type,
                confidence: response.confidence_score
            });

        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            
            const responseTime = performance.now() - startTime;
            this.updateMetrics(responseTime, false);
            
            this.addMessage(
                'Desculpe, ocorreu um erro ao processar sua mensagem. Verifique sua conexão e tente novamente.',
                'assistant',
                { error: true }
            );

            this.showRetryButton(message);
        }
    }

    async sendQuickMessage(message) {
        const input = document.getElementById('chatbot-input');
        if (input) {
            input.value = message;
            this.updateCharCounter();
            await this.sendMessage();
        }
    }

    async sendToAPI(message) {
        const payload = {
            message: message,
            session_id: this.sessionId
        };

        const response = await fetch(this.config.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        return {
            content: data.response,
            response_type: data.response_type || 'unknown',
            confidence_score: data.confidence_score || 0.5,
            suggestions: data.suggestions || [],
            metadata: data.metadata || {}
        };
    }

    addMessage(content, sender, metadata = {}) {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const messageId = `msg_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
        const timestamp = new Date();

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.id = messageId;
        
        if (metadata.error) {
            messageDiv.classList.add('error-message');
        }

        // Create message content with enhanced formatting
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Process special markers for action buttons
        let processedContent = content;
        if (content.includes('[AGENDAR_REUNIAO_ASSESSOR]')) {
            processedContent = content.replace('[AGENDAR_REUNIAO_ASSESSOR]', '');
            processedContent += '\n\n';
            
            const actionButton = document.createElement('button');
            actionButton.className = 'action-button primary';
            actionButton.innerHTML = '<i class="fas fa-calendar-plus"></i> Agendar Reunião';
            actionButton.onclick = () => window.open('/agendamento-assessor', '_blank');
            
            contentDiv.appendChild(document.createTextNode(processedContent));
            contentDiv.appendChild(actionButton);
        } else {
            contentDiv.textContent = processedContent;
        }

        // Add timestamp
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        timestampDiv.textContent = timestamp.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timestampDiv);

        // Accessibility attributes
        messageDiv.setAttribute('role', 'article');
        messageDiv.setAttribute('aria-label', 
            `${sender === 'user' ? 'Você' : 'Assistente'} às ${timestampDiv.textContent}: ${content}`
        );

        messagesContainer.appendChild(messageDiv);

        // Smooth scroll to bottom
        this.scrollToBottom();

        // Animate message appearance
        this.animateMessage(messageDiv);

        // Store in conversation history
        this.conversationHistory.push({
            id: messageId,
            content: content,
            sender: sender,
            timestamp: timestamp.toISOString(),
            metadata: metadata
        });

        // Announce to screen readers for assistant messages
        if (sender === 'assistant') {
            setTimeout(() => {
                this.announceToScreenReader(`Assistente respondeu: ${content}`);
            }, 500);
        }

        this.metrics.totalMessages++;
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        // Remove existing indicator
        const existing = messagesContainer.querySelector('.typing-indicator');
        if (existing) existing.remove();

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-animation">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            <div class="typing-text">Assistente está digitando...</div>
        `;
        typingDiv.setAttribute('aria-label', 'Assistente está digitando');

        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
        this.animateMessage(typingDiv);

        this.isTyping = true;
    }

    hideTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            typingIndicator.style.opacity = '0';
            typingIndicator.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                typingIndicator.remove();
            }, 300);
        }
        
        this.isTyping = false;
    }

    showSuggestions(suggestions) {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer || suggestions.length === 0) return;

        const suggestionsDiv = document.createElement('div');
        suggestionsDiv.className = 'suggestions-container';
        suggestionsDiv.innerHTML = `
            <div class="suggestions-header">
                <i class="fas fa-lightbulb"></i>
                <span>Sugestões:</span>
            </div>
            <div class="suggestions-list">
                ${suggestions.map(suggestion => `
                    <button class="suggestion-btn" data-suggestion="${suggestion}">
                        ${suggestion}
                    </button>
                `).join('')}
            </div>
        `;

        // Add click handlers for suggestions
        suggestionsDiv.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const suggestion = btn.getAttribute('data-suggestion');
                this.sendQuickMessage(suggestion);
                suggestionsDiv.remove();
            });
        });

        messagesContainer.appendChild(suggestionsDiv);
        this.scrollToBottom();
        this.animateMessage(suggestionsDiv);
    }

    showRetryButton(originalMessage) {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const retryDiv = document.createElement('div');
        retryDiv.className = 'retry-container';
        retryDiv.innerHTML = `
            <button class="retry-btn">
                <i class="fas fa-redo"></i>
                Tentar novamente
            </button>
        `;

        const retryBtn = retryDiv.querySelector('.retry-btn');
        retryBtn.addEventListener('click', () => {
            retryDiv.remove();
            this.sendQuickMessage(originalMessage);
        });

        messagesContainer.appendChild(retryDiv);
        this.scrollToBottom();
        this.animateMessage(retryDiv);
    }

    hideQuickActions() {
        const quickActions = document.getElementById('quick-actions');
        if (quickActions && this.conversationHistory.length === 0) {
            quickActions.style.opacity = '0.7';
            quickActions.style.pointerEvents = 'none';
        }
    }

    showWelcomeMessage() {
        if (this.conversationHistory.length === 0) {
            setTimeout(() => {
                const welcomeMessage = `Olá! Sou o assistente virtual da 2ª Vara Cível de Cariacica.

Posso ajudá-lo com:
• Informações sobre horários e localização
• Consulta de processos
• Agendamento de atendimentos
• Orientações sobre serviços
• Dúvidas sobre audiências
• Solicitação de documentos

Como posso ajudá-lo hoje?`;

                this.addMessage(welcomeMessage, 'assistant', { welcome: true });
            }, 800);
        }
    }

    updateCharCounter() {
        const input = document.getElementById('chatbot-input');
        const counter = document.getElementById('char-counter');
        
        if (input && counter) {
            const length = input.value.length;
            counter.textContent = `${length}/${this.config.maxMessageLength}`;
            
            if (length > this.config.maxMessageLength * 0.9) {
                counter.classList.add('warning');
            } else {
                counter.classList.remove('warning');
            }
        }
    }

    autoResizeInput() {
        const input = document.getElementById('chatbot-input');
        if (input) {
            input.style.height = 'auto';
            input.style.height = Math.min(input.scrollHeight, 120) + 'px';
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (messagesContainer) {
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: 'smooth'
            });
        }
    }

    animateMessage(element) {
        element.style.opacity = '0';
        element.style.transform = 'translateY(15px)';
        
        requestAnimationFrame(() => {
            element.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        });
    }

    handleConnectionChange(isOnline) {
        this.isOnline = isOnline;
        
        const statusIndicator = document.querySelector('.connection-status');
        if (statusIndicator) {
            statusIndicator.className = `connection-status ${isOnline ? 'online' : 'offline'}`;
            statusIndicator.title = isOnline ? 'Online' : 'Offline';
        }

        if (!isOnline) {
            this.addMessage(
                'Conexão perdida. Suas mensagens serão enviadas quando a conexão for restaurada.',
                'assistant',
                { system: true }
            );
        } else if (this.messageQueue.length > 0) {
            this.processMessageQueue();
        }
    }

    async processMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            await this.sendQuickMessage(message);
            await new Promise(resolve => setTimeout(resolve, 1000)); // Rate limiting
        }
    }

    setupHealthMonitoring() {
        // Health check every 2 minutes
        setInterval(async () => {
            try {
                const response = await fetch(this.config.healthEndpoint);
                const health = await response.json();
                
                console.log('Chatbot health check:', health.status);
            } catch (error) {
                console.warn('Health check failed:', error);
            }
        }, 120000);
    }

    updateMetrics(responseTime, success) {
        this.metrics.lastResponseTime = responseTime;
        
        if (success) {
            const totalTime = this.metrics.averageResponseTime * (this.metrics.totalMessages - 1);
            this.metrics.averageResponseTime = (totalTime + responseTime) / this.metrics.totalMessages;
        } else {
            this.metrics.errorCount++;
        }
    }

    saveConversationHistory() {
        try {
            const recentHistory = this.conversationHistory.slice(-50); // Keep last 50 messages
            localStorage.setItem(`chatbot_history_${this.sessionId}`, JSON.stringify(recentHistory));
        } catch (error) {
            console.warn('Failed to save conversation history:', error);
        }
    }

    loadConversationHistory() {
        try {
            const saved = localStorage.getItem(`chatbot_history_${this.sessionId}`);
            if (saved) {
                this.conversationHistory = JSON.parse(saved);
                
                // Restore messages to UI (limit to last 10 for performance)
                const recentMessages = this.conversationHistory.slice(-10);
                recentMessages.forEach(msg => {
                    this.addMessage(msg.content, msg.sender, msg.metadata || {});
                });
            }
        } catch (error) {
            console.warn('Failed to load conversation history:', error);
        }
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
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    trackInteraction(action, metadata = {}) {
        console.log(`Chatbot interaction: ${action}`, metadata);
        
        // Integration with existing analytics
        if (window.Court && window.Court.trackUserInteraction) {
            window.Court.trackUserInteraction(action, 'refined_chatbot', metadata);
        }
        
        // Custom analytics
        if (window.gtag) {
            window.gtag('event', action, {
                event_category: 'chatbot_refined',
                event_label: this.sessionId,
                custom_parameters: metadata
            });
        }
    }

    // Public API methods
    getMetrics() {
        return { ...this.metrics };
    }

    getSessionId() {
        return this.sessionId;
    }

    clearHistory() {
        this.conversationHistory = [];
        localStorage.removeItem(`chatbot_history_${this.sessionId}`);
        
        const messagesContainer = document.getElementById('chatbot-messages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
        
        this.showWelcomeMessage();
    }

    async getHealthStatus() {
        try {
            const response = await fetch(this.config.healthEndpoint);
            return await response.json();
        } catch (error) {
            return { status: 'error', error: error.message };
        }
    }
}

// Initialize refined chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Refined Chatbot UI...');
    
    // Check if required elements exist
    const toggleButton = document.getElementById('chatbot-toggle');
    const chatWindow = document.getElementById('chatbot-window');
    
    if (!toggleButton) {
        console.error('Chatbot toggle button not found');
        return;
    }
    
    if (!chatWindow) {
        console.error('Chatbot window element not found');
        return;
    }
    
    try {
        window.refinedChatbot = new RefinedChatbotUI();
        console.log('Refined Chatbot UI initialized successfully');
        
        // Global debug commands
        window.chatbotDebug = {
            getMetrics: () => window.refinedChatbot.getMetrics(),
            getSessionId: () => window.refinedChatbot.getSessionId(),
            clearHistory: () => window.refinedChatbot.clearHistory(),
            getHealth: () => window.refinedChatbot.getHealthStatus(),
            toggleDebug: () => {
                const debug = localStorage.getItem('chatbot_debug') === 'true';
                localStorage.setItem('chatbot_debug', (!debug).toString());
                console.log(`Debug mode ${!debug ? 'enabled' : 'disabled'}`);
            }
        };
        
    } catch (error) {
        console.error('Error initializing Refined Chatbot UI:', error);
    }
});