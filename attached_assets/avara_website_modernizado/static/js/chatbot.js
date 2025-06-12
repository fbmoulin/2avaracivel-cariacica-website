/**
 * Chatbot functionality for 2ª Vara Cível de Cariacica
 * Handles chatbot UI interactions and API communication
 */

class Chatbot {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.messages = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadChatHistory();
        this.showWelcomeMessage();
    }

    bindEvents() {
        const toggleButton = document.getElementById('chatbot-toggle');
        const closeButton = document.getElementById('chatbot-close');
        const sendButton = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input');
        const chatWindow = document.getElementById('chatbot-window');

        if (toggleButton) {
            toggleButton.addEventListener('click', () => this.toggleChat());
        }

        if (closeButton) {
            closeButton.addEventListener('click', () => this.closeChat());
        }

        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }

        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Auto-resize input
            input.addEventListener('input', () => {
                input.style.height = 'auto';
                input.style.height = input.scrollHeight + 'px';
            });
        }

        // Close chat when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isOpen && chatWindow && !chatWindow.contains(e.target) && !toggleButton.contains(e.target)) {
                this.closeChat();
            }
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
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
        const input = document.getElementById('chatbot-input');

        if (chatWindow) {
            chatWindow.style.display = 'flex';
            this.isOpen = true;
            
            // Update button appearance
            if (toggleButton) {
                toggleButton.innerHTML = '<i class="fas fa-times"></i>';
                toggleButton.setAttribute('aria-label', 'Fechar assistente virtual');
            }

            // Focus on input
            if (input) {
                setTimeout(() => input.focus(), 100);
            }

            // Announce to screen readers
            this.announceToScreenReader('Assistente virtual aberto');

            // Track interaction
            if (window.Court) {
                window.Court.trackUserInteraction('chatbot_opened', 'chatbot');
            }
        }
    }

    closeChat() {
        const chatWindow = document.getElementById('chatbot-window');
        const toggleButton = document.getElementById('chatbot-toggle');

        if (chatWindow) {
            chatWindow.style.display = 'none';
            this.isOpen = false;

            // Update button appearance
            if (toggleButton) {
                toggleButton.innerHTML = '<i class="fas fa-comments"></i>';
                toggleButton.setAttribute('aria-label', 'Abrir assistente virtual');
            }

            // Announce to screen readers
            this.announceToScreenReader('Assistente virtual fechado');

            // Track interaction
            if (window.Court) {
                window.Court.trackUserInteraction('chatbot_closed', 'chatbot');
            }
        }
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();

        if (!message) return;

        // Clear input
        input.value = '';
        input.style.height = 'auto';

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send message to backend
            const response = await this.sendToBackend(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add bot response
            this.addMessage(response, 'bot');

            // Save to history
            this.saveChatHistory();

            // Track interaction
            if (window.Court) {
                window.Court.trackUserInteraction('chatbot_message_sent', 'chatbot');
            }

        } catch (error) {
            console.error('Chatbot error:', error);
            this.hideTypingIndicator();
            this.addMessage('Desculpe, ocorreu um erro. Tente novamente ou entre em contato conosco diretamente.', 'bot');
        }
    }

    async sendToBackend(message) {
        const response = await fetch('/chatbot/api/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error('Erro na comunicação com o servidor');
        }

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        return data.response;
    }

    addMessage(text, sender) {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        this.setMessageContent(messageDiv, text);

        // Add timestamp for accessibility
        const timestamp = new Date().toLocaleTimeString('pt-BR');
        messageDiv.setAttribute('aria-label', `${sender === 'user' ? 'Você' : 'Assistente'} às ${timestamp}: ${text}`);

        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Add to messages array
        this.messages.push({
            text: text,
            sender: sender,
            timestamp: new Date().toISOString()
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
        // Safely set text content without allowing HTML injection
        messageDiv.textContent = text;
        
        // Apply safe formatting by creating elements programmatically
        const content = messageDiv.textContent;
        messageDiv.innerHTML = '';
        
        this.addFormattedContent(messageDiv, content);
    }

    addFormattedContent(container, text) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const emailRegex = /([\w.-]+@[\w.-]+\.\w+)/g;
        const phoneRegex = /(\(?\d{2}\)?\s?\d{4,5}-?\d{4})/g;
        const actionLinkRegex = /\*\*\[([^\]]+)\]\(([^)]+)\)\*\*/g;
        
        let lastIndex = 0;
        const matches = [];
        let match;
        
        // Find action links first (priority)
        while ((match = actionLinkRegex.exec(text)) !== null) {
            matches.push({ 
                type: 'action_link', 
                match: match[0], 
                text: match[1], 
                url: match[2], 
                index: match.index 
            });
        }
        
        // Find other patterns
        while ((match = urlRegex.exec(text)) !== null) {
            // Skip if this URL is part of an action link
            const isPartOfActionLink = matches.some(m => 
                m.type === 'action_link' && 
                match.index >= m.index && 
                match.index < m.index + m.match.length
            );
            if (!isPartOfActionLink) {
                matches.push({ type: 'url', match: match[0], index: match.index });
            }
        }
        
        while ((match = emailRegex.exec(text)) !== null) {
            matches.push({ type: 'email', match: match[0], index: match.index });
        }
        while ((match = phoneRegex.exec(text)) !== null) {
            matches.push({ type: 'phone', match: match[0], index: match.index });
        }
        
        // Sort matches by position
        matches.sort((a, b) => a.index - b.index);
        
        // Build content with safe elements
        matches.forEach(({ type, match, text: linkText, url, index }) => {
            // Add text before this match
            if (index > lastIndex) {
                const textPart = text.substring(lastIndex, index);
                this.addTextWithLineBreaks(container, textPart);
            }
            
            // Add formatted element
            let element;
            if (type === 'action_link') {
                element = document.createElement('a');
                element.href = url;
                element.className = 'btn btn-primary btn-sm me-2 mb-2';
                element.innerHTML = `<i class="fas fa-calendar-plus me-1"></i>${linkText}`;
                element.style.cssText = 'text-decoration: none; color: white;';
            } else if (type === 'url') {
                element = document.createElement('a');
                element.href = match;
                element.target = '_blank';
                element.rel = 'noopener noreferrer';
                element.textContent = match;
            } else if (type === 'email') {
                element = document.createElement('a');
                element.href = `mailto:${match}`;
                element.textContent = match;
            } else if (type === 'phone') {
                element = document.createElement('strong');
                element.textContent = match;
            }
            
            container.appendChild(element);
            lastIndex = index + match.length;
        });
        
        // Add remaining text
        if (lastIndex < text.length) {
            const remainingText = text.substring(lastIndex);
            this.addTextWithLineBreaks(container, remainingText);
        }
    }
    
    addTextWithLineBreaks(container, text) {
        // Handle line breaks and markdown-style formatting
        const lines = text.split('\n');
        lines.forEach((line, i) => {
            if (i > 0) {
                container.appendChild(document.createElement('br'));
            }
            if (line) {
                // Handle bold text
                const boldRegex = /\*\*([^*]+)\*\*/g;
                let lastIdx = 0;
                let boldMatch;
                
                while ((boldMatch = boldRegex.exec(line)) !== null) {
                    // Add text before bold
                    if (boldMatch.index > lastIdx) {
                        const beforeText = line.substring(lastIdx, boldMatch.index);
                        container.appendChild(document.createTextNode(beforeText));
                    }
                    
                    // Add bold text
                    const boldElement = document.createElement('strong');
                    boldElement.textContent = boldMatch[1];
                    container.appendChild(boldElement);
                    
                    lastIdx = boldMatch.index + boldMatch[0].length;
                }
                
                // Add remaining text
                if (lastIdx < line.length) {
                    const remainingText = line.substring(lastIdx);
                    container.appendChild(document.createTextNode(remainingText));
                }
            }
        });
    }

    showTypingIndicator() {
        if (this.isTyping) return;

        this.isTyping = true;
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <span class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </span>
        `;

        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Add CSS for typing animation
        const style = document.createElement('style');
        style.textContent = `
            .typing-dots {
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }
            .typing-dots span {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background-color: rgba(255, 255, 255, 0.7);
                animation: typing 1.4s infinite ease-in-out;
            }
            .typing-dots span:nth-child(1) { animation-delay: 0s; }
            .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
            .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
            @keyframes typing {
                0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
                30% { transform: translateY(-10px); opacity: 1; }
            }
        `;
        
        if (!document.getElementById('typing-animation-styles')) {
            style.id = 'typing-animation-styles';
            document.head.appendChild(style);
        }
    }

    hideTypingIndicator() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    showWelcomeMessage() {
        // Show welcome message only if no chat history exists
        if (this.messages.length === 0) {
            setTimeout(() => {
                this.addMessage('Olá! Sou o assistente virtual da 2ª Vara Cível de Cariacica. Como posso ajudá-lo hoje?', 'bot');
            }, 1000);
        }
    }

    saveChatHistory() {
        // Save last 50 messages to localStorage
        const recentMessages = this.messages.slice(-50);
        try {
            localStorage.setItem('chatbot_history', JSON.stringify(recentMessages));
        } catch (error) {
            console.warn('Could not save chat history:', error);
        }
    }

    loadChatHistory() {
        try {
            const history = localStorage.getItem('chatbot_history');
            if (history) {
                this.messages = JSON.parse(history);
                this.displayChatHistory();
            }
        } catch (error) {
            console.warn('Could not load chat history:', error);
        }
    }

    displayChatHistory() {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        // Clear existing messages
        messagesContainer.innerHTML = '';

        // Display up to last 10 messages
        const recentMessages = this.messages.slice(-10);
        recentMessages.forEach(msg => {
            this.addMessageToDOM(msg.text, msg.sender);
        });
    }

    addMessageToDOM(text, sender) {
        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        this.setMessageContent(messageDiv, text);

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    clearHistory() {
        this.messages = [];
        localStorage.removeItem('chatbot_history');
        
        const messagesContainer = document.getElementById('chatbot-messages');
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
        
        this.showWelcomeMessage();
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

    // Quick responses for common questions
    addQuickResponses() {
        const quickResponses = [
            'Horário de funcionamento',
            'Localização',
            'Consulta processual',
            'Agendamento',
            'Contato'
        ];

        const messagesContainer = document.getElementById('chatbot-messages');
        if (!messagesContainer) return;

        const quickResponsesDiv = document.createElement('div');
        quickResponsesDiv.className = 'quick-responses';
        quickResponsesDiv.innerHTML = `
            <p class="small text-muted mb-2">Perguntas frequentes:</p>
            <div class="d-flex flex-wrap gap-2">
                ${quickResponses.map(response => 
                    `<button class="btn btn-outline-primary btn-sm quick-response-btn" data-response="${response}">${response}</button>`
                ).join('')}
            </div>
        `;

        messagesContainer.appendChild(quickResponsesDiv);

        // Add event listeners to quick response buttons
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

    // Accessibility: Provide text alternatives for screen readers
    setAccessibilityAttributes() {
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
        }
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chatbot = new Chatbot();
    window.chatbot.setAccessibilityAttributes();
});

// Export for global access
window.Chatbot = Chatbot;
