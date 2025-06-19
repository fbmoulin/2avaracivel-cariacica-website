/**
 * Enhanced Chatbot Implementation for 2ª Vara Cível de Cariacica
 * Advanced debugging, error handling, and performance monitoring
 */

class EnhancedChatbot {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.isOnline = true;
        this.messages = [];
        this.messageQueue = [];
        this.connectionAttempts = 0;
        this.maxRetries = 3;
        this.retryDelay = 1000;
        
        // Performance monitoring
        this.performanceMetrics = {
            totalMessages: 0,
            averageResponseTime: 0,
            errorCount: 0,
            successRate: 0,
            startTime: Date.now()
        };
        
        // Debug mode
        this.debugMode = localStorage.getItem('chatbot_debug') === 'true';
        
        this.init();
    }

    init() {
        this.log('Initializing Enhanced Chatbot...');
        this.bindEvents();
        this.loadChatHistory();
        this.setupHealthCheck();
        this.showWelcomeMessage();
        this.log('Enhanced Chatbot initialized successfully');
    }

    log(message, level = 'info') {
        if (this.debugMode) {
            const timestamp = new Date().toLocaleTimeString();
            console.log(`[Chatbot ${level.toUpperCase()}] ${timestamp}: ${message}`);
        }
    }

    bindEvents() {
        this.log('Binding chatbot events...');
        
        const elements = {
            toggle: document.getElementById('chatbot-toggle'),
            close: document.getElementById('chatbot-close'),
            send: document.getElementById('chatbot-send'),
            input: document.getElementById('chatbot-input'),
            window: document.getElementById('chatbot-window'),
            messages: document.getElementById('chatbot-messages')
        };

        this.log('Element availability: ' + JSON.stringify(Object.fromEntries(
            Object.entries(elements).map(([key, el]) => [key, !!el])
        )));

        if (elements.toggle) {
            elements.toggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.log('Toggle button clicked');
                this.toggleChat();
            });
        } else {
            this.log('Toggle button not found', 'error');
        }

        if (elements.close) {
            elements.close.addEventListener('click', (e) => {
                e.preventDefault();
                this.log('Close button clicked');
                this.closeChat();
            });
        }

        if (elements.send) {
            elements.send.addEventListener('click', (e) => {
                e.preventDefault();
                this.log('Send button clicked');
                this.sendMessage();
            });
        }

        if (elements.input) {
            elements.input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.log('Enter key pressed in input');
                    this.sendMessage();
                }
            });

            // Auto-resize textarea
            elements.input.addEventListener('input', () => {
                elements.input.style.height = 'auto';
                elements.input.style.height = elements.input.scrollHeight + 'px';
            });

            // Focus handling
            elements.input.addEventListener('focus', () => {
                this.log('Input focused');
            });
        }

        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.log('Escape key pressed - closing chat');
                this.closeChat();
            }
            
            // Debug toggle: Ctrl+Shift+D
            if (e.ctrlKey && e.shiftKey && e.key === 'D') {
                this.toggleDebugMode();
            }
        });

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (this.isOpen && elements.window && 
                !elements.window.contains(e.target) && 
                !elements.toggle.contains(e.target)) {
                this.log('Clicked outside chat window - closing');
                this.closeChat();
            }
        });

        // Online/offline detection
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.log('Connection restored');
            this.processQueuedMessages();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.log('Connection lost', 'warn');
            this.showOfflineMessage();
        });
    }

    toggleChat() {
        this.log(`Toggling chat. Current state: ${this.isOpen ? 'open' : 'closed'}`);
        if (this.isOpen) {
            this.closeChat();
        } else {
            this.openChat();
        }
    }

    openChat() {
        this.log('Opening chat window');
        const chatWindow = document.getElementById('chatbot-window');
        const toggleButton = document.getElementById('chatbot-toggle');
        const input = document.getElementById('chatbot-input');

        if (chatWindow) {
            chatWindow.style.display = 'flex';
            chatWindow.setAttribute('aria-hidden', 'false');
            this.isOpen = true;
            
            // Update button appearance and accessibility
            if (toggleButton) {
                toggleButton.innerHTML = '<i class="fas fa-times" aria-hidden="true"></i>';
                toggleButton.setAttribute('aria-label', 'Fechar assistente virtual');
                toggleButton.setAttribute('aria-expanded', 'true');
            }

            // Focus management
            if (input) {
                setTimeout(() => {
                    input.focus();
                    this.log('Input focused after opening');
                }, 150);
            }

            // Announce to screen readers
            this.announceToScreenReader('Assistente virtual aberto. Use Tab para navegar pelos controles.');

            // Animation
            chatWindow.style.opacity = '0';
            chatWindow.style.transform = 'translateY(20px) scale(0.95)';
            
            requestAnimationFrame(() => {
                chatWindow.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                chatWindow.style.opacity = '1';
                chatWindow.style.transform = 'translateY(0) scale(1)';
            });

            // Track interaction
            this.trackInteraction('chat_opened');
            this.log('Chat window opened successfully');
        }
    }

    closeChat() {
        this.log('Closing chat window');
        const chatWindow = document.getElementById('chatbot-window');
        const toggleButton = document.getElementById('chatbot-toggle');

        if (chatWindow) {
            chatWindow.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            chatWindow.style.opacity = '0';
            chatWindow.style.transform = 'translateY(20px) scale(0.95)';
            
            setTimeout(() => {
                chatWindow.style.display = 'none';
                chatWindow.setAttribute('aria-hidden', 'true');
                this.isOpen = false;
            }, 300);

            // Update button appearance
            if (toggleButton) {
                toggleButton.innerHTML = '<i class="fas fa-comments" aria-hidden="true"></i>';
                toggleButton.setAttribute('aria-label', 'Abrir assistente virtual');
                toggleButton.setAttribute('aria-expanded', 'false');
                toggleButton.focus(); // Return focus to toggle button
            }

            // Announce to screen readers
            this.announceToScreenReader('Assistente virtual fechado');

            // Track interaction
            this.trackInteraction('chat_closed');
            this.log('Chat window closed successfully');
        }
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input?.value.trim();

        if (!message) {
            this.log('Empty message - not sending', 'warn');
            return;
        }

        this.log(`Sending message: "${message}"`);
        const startTime = Date.now();

        // Clear input immediately
        input.value = '';
        input.style.height = 'auto';

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        // Check if online
        if (!this.isOnline) {
            this.log('Offline - queuing message', 'warn');
            this.messageQueue.push(message);
            this.hideTypingIndicator();
            this.addMessage('Você está offline. Sua mensagem será enviada quando a conexão for restaurada.', 'bot', 'warning');
            return;
        }

        try {
            // Send message with retry logic
            const response = await this.sendWithRetry(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add bot response
            this.addMessage(response, 'bot');

            // Update performance metrics
            const responseTime = Date.now() - startTime;
            this.updatePerformanceMetrics(responseTime, true);

            // Save to history
            this.saveChatHistory();

            // Track interaction
            this.trackInteraction('message_sent');

            this.log(`Message sent successfully in ${responseTime}ms`);

        } catch (error) {
            this.log(`Error sending message: ${error.message}`, 'error');
            this.hideTypingIndicator();
            
            // Update performance metrics
            const responseTime = Date.now() - startTime;
            this.updatePerformanceMetrics(responseTime, false);
            
            // Show error message
            this.addMessage(
                'Desculpe, ocorreu um erro ao processar sua mensagem. Verifique sua conexão e tente novamente.',
                'bot',
                'error'
            );

            // Show retry button for failed messages
            this.showRetryOption(message);
        }
    }

    async sendWithRetry(message, attempt = 1) {
        this.log(`Sending message (attempt ${attempt}/${this.maxRetries})`);
        
        try {
            const response = await this.sendToBackend(message);
            this.connectionAttempts = 0; // Reset on success
            return response;
        } catch (error) {
            if (attempt < this.maxRetries) {
                this.log(`Attempt ${attempt} failed, retrying in ${this.retryDelay}ms`, 'warn');
                await this.sleep(this.retryDelay * attempt); // Exponential backoff
                return this.sendWithRetry(message, attempt + 1);
            }
            this.connectionAttempts++;
            throw error;
        }
    }

    async sendToBackend(message) {
        this.log('Sending request to backend API');
        
        const response = await fetch('/chatbot/api/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ message: message }),
            timeout: 30000 // 30 second timeout
        });

        if (!response.ok) {
            const errorText = await response.text();
            this.log(`Backend error (${response.status}): ${errorText}`, 'error');
            throw new Error(`Erro do servidor: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
            this.log(`Backend returned error: ${data.error}`, 'error');
            throw new Error(data.error);
        }

        this.log('Backend response received successfully');
        return data.response;
    }

    addMessage(text, sender, type = 'normal') {
        this.log(`Adding ${sender} message: "${text}" (type: ${type})`);
        
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) {
            this.log('Messages container not found', 'error');
            return;
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message ${type}-message`;
        
        // Create message content with proper escaping
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = text;
        
        // Add timestamp
        const timestamp = document.createElement('div');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = new Date().toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(timestamp);

        // Accessibility attributes
        const timeStr = new Date().toLocaleTimeString('pt-BR');
        messageDiv.setAttribute('role', 'article');
        messageDiv.setAttribute('aria-label', 
            `${sender === 'user' ? 'Você' : 'Assistente'} às ${timeStr}: ${text}`
        );

        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom with smooth animation
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });

        // Add to messages array
        this.messages.push({
            text: text,
            sender: sender,
            type: type,
            timestamp: new Date().toISOString()
        });

        // Announce new bot messages to screen readers
        if (sender === 'bot') {
            this.announceToScreenReader(`Assistente respondeu: ${text}`);
        }

        // Animate message appearance
        this.animateMessage(messageDiv);

        this.log(`Message added successfully (total: ${this.messages.length})`);
    }

    animateMessage(messageDiv) {
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(15px)';
        
        requestAnimationFrame(() => {
            messageDiv.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        });
    }

    showTypingIndicator() {
        this.log('Showing typing indicator');
        this.isTyping = true;
        
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        // Remove existing indicator
        const existing = messagesContainer.querySelector('.typing-indicator');
        if (existing) existing.remove();

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-animation">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <div class="typing-text">Assistente está digitando...</div>
        `;
        typingDiv.setAttribute('aria-label', 'Assistente está digitando');

        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });

        this.animateMessage(typingDiv);
    }

    hideTypingIndicator() {
        this.log('Hiding typing indicator');
        this.isTyping = false;
        
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.style.transition = 'all 0.3s ease';
            typingIndicator.style.opacity = '0';
            typingIndicator.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                typingIndicator.remove();
            }, 300);
        }
    }

    showRetryOption(message) {
        this.log('Showing retry option for failed message');
        
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const retryDiv = document.createElement('div');
        retryDiv.className = 'message retry-message';
        retryDiv.innerHTML = `
            <button class="retry-button" aria-label="Tentar enviar mensagem novamente">
                <i class="fas fa-redo" aria-hidden="true"></i>
                Tentar novamente
            </button>
        `;

        const retryButton = retryDiv.querySelector('.retry-button');
        retryButton.addEventListener('click', () => {
            this.log('Retry button clicked');
            retryDiv.remove();
            // Simulate input and send
            const input = document.getElementById('chatbot-input');
            if (input) {
                input.value = message;
                this.sendMessage();
            }
        });

        messagesContainer.appendChild(retryDiv);
        this.animateMessage(retryDiv);
    }

    showWelcomeMessage() {
        if (this.messages.length === 0) {
            this.log('Showing welcome message');
            
            const welcomeText = `Olá! Sou o assistente virtual da 2ª Vara Cível de Cariacica. 

Posso ajudá-lo com:
• Informações sobre processos
• Agendamento de atendimentos
• Horários de funcionamento
• Serviços disponíveis
• Orientações gerais

Como posso ajudá-lo hoje?`;

            setTimeout(() => {
                this.addMessage(welcomeText, 'bot');
            }, 500);
        }
    }

    showOfflineMessage() {
        this.addMessage(
            'Conexão perdida. Suas mensagens serão enviadas quando a conexão for restaurada.',
            'bot',
            'warning'
        );
    }

    processQueuedMessages() {
        this.log(`Processing ${this.messageQueue.length} queued messages`);
        
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            // Re-add to input and send
            const input = document.getElementById('chatbot-input');
            if (input) {
                input.value = message;
                this.sendMessage();
                break; // Send one at a time to avoid overwhelming
            }
        }
    }

    updatePerformanceMetrics(responseTime, success) {
        this.performanceMetrics.totalMessages++;
        
        if (success) {
            const total = this.performanceMetrics.averageResponseTime * (this.performanceMetrics.totalMessages - 1);
            this.performanceMetrics.averageResponseTime = (total + responseTime) / this.performanceMetrics.totalMessages;
        } else {
            this.performanceMetrics.errorCount++;
        }
        
        this.performanceMetrics.successRate = 
            ((this.performanceMetrics.totalMessages - this.performanceMetrics.errorCount) / 
             this.performanceMetrics.totalMessages) * 100;

        this.log(`Performance updated: ${this.performanceMetrics.totalMessages} messages, ` +
                 `${this.performanceMetrics.averageResponseTime.toFixed(0)}ms avg, ` +
                 `${this.performanceMetrics.successRate.toFixed(1)}% success rate`);
    }

    setupHealthCheck() {
        // Check connection health every 30 seconds
        setInterval(() => {
            this.checkHealth();
        }, 30000);
    }

    async checkHealth() {
        if (!this.isOnline) return;
        
        try {
            const response = await fetch('/health', { 
                method: 'GET',
                timeout: 5000 
            });
            
            if (response.ok) {
                this.log('Health check passed');
            } else {
                this.log('Health check failed - server issues', 'warn');
            }
        } catch (error) {
            this.log(`Health check failed: ${error.message}`, 'error');
        }
    }

    saveChatHistory() {
        try {
            const recentMessages = this.messages.slice(-50); // Keep last 50 messages
            localStorage.setItem('enhanced_chatbot_history', JSON.stringify(recentMessages));
            this.log(`Saved ${recentMessages.length} messages to history`);
        } catch (error) {
            this.log(`Failed to save chat history: ${error.message}`, 'error');
        }
    }

    loadChatHistory() {
        try {
            const saved = localStorage.getItem('enhanced_chatbot_history');
            if (saved) {
                this.messages = JSON.parse(saved);
                this.log(`Loaded ${this.messages.length} messages from history`);
                
                // Restore messages to UI
                const messagesContainer = document.getElementById('chatbot-messages');
                if (messagesContainer) {
                    this.messages.forEach(msg => {
                        this.addMessage(msg.text, msg.sender, msg.type || 'normal');
                    });
                }
            }
        } catch (error) {
            this.log(`Failed to load chat history: ${error.message}`, 'error');
        }
    }

    toggleDebugMode() {
        this.debugMode = !this.debugMode;
        localStorage.setItem('chatbot_debug', this.debugMode.toString());
        this.log(`Debug mode ${this.debugMode ? 'enabled' : 'disabled'}`);
        
        // Show debug info if enabled
        if (this.debugMode) {
            this.showDebugInfo();
        }
    }

    showDebugInfo() {
        const debugInfo = {
            isOpen: this.isOpen,
            isOnline: this.isOnline,
            connectionAttempts: this.connectionAttempts,
            messageQueue: this.messageQueue.length,
            metrics: this.performanceMetrics
        };
        
        console.table(debugInfo);
        
        this.addMessage(
            `Debug Info:\n${JSON.stringify(debugInfo, null, 2)}`,
            'bot',
            'debug'
        );
    }

    // Utility methods
    sleep(ms) {
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
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    trackInteraction(action) {
        this.log(`Tracking interaction: ${action}`);
        
        // Integration with existing analytics
        if (window.Court && window.Court.trackUserInteraction) {
            window.Court.trackUserInteraction(action, 'enhanced_chatbot');
        }
        
        // Custom analytics
        if (window.gtag) {
            window.gtag('event', action, {
                event_category: 'chatbot',
                event_label: 'enhanced_chatbot'
            });
        }
    }

    // Public API methods
    getPerformanceMetrics() {
        return { ...this.performanceMetrics };
    }

    clearHistory() {
        this.log('Clearing chat history');
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

    // Accessibility methods
    setAccessibilityAttributes() {
        this.log('Setting accessibility attributes');
        
        const chatWindow = document.getElementById('chatbot-window');
        const messagesContainer = document.getElementById('chatbot-messages');
        const input = document.getElementById('chatbot-input');

        if (chatWindow) {
            chatWindow.setAttribute('role', 'dialog');
            chatWindow.setAttribute('aria-labelledby', 'chatbot-header');
            chatWindow.setAttribute('aria-describedby', 'chatbot-messages');
        }

        if (messagesContainer) {
            messagesContainer.setAttribute('role', 'log');
            messagesContainer.setAttribute('aria-live', 'polite');
            messagesContainer.setAttribute('aria-label', 'Conversa com assistente virtual');
        }

        if (input) {
            input.setAttribute('aria-label', 'Digite sua mensagem para o assistente virtual');
            input.setAttribute('placeholder', 'Digite sua pergunta...');
        }
    }
}

// Initialize enhanced chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Enhanced Chatbot...');
    
    // Check if elements exist
    const toggle = document.getElementById('chatbot-toggle');
    const chatWindow = document.getElementById('chatbot-window');
    
    if (!toggle) {
        console.error('Chatbot toggle element not found');
        return;
    }
    
    if (!chatWindow) {
        console.error('Chatbot window element not found');
        return;
    }
    
    console.log('Chatbot elements found, creating enhanced instance...');
    
    try {
        window.enhancedChatbot = new EnhancedChatbot();
        window.enhancedChatbot.setAccessibilityAttributes();
        console.log('Enhanced Chatbot initialized successfully');
        
        // Add global debug commands
        window.chatbotDebug = {
            toggle: () => window.enhancedChatbot.toggleDebugMode(),
            metrics: () => window.enhancedChatbot.getPerformanceMetrics(),
            health: () => window.enhancedChatbot.getHealthStatus(),
            clear: () => window.enhancedChatbot.clearHistory()
        };
        
    } catch (error) {
        console.error('Error initializing Enhanced Chatbot:', error);
    }
});