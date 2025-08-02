/**
 * API Integration Module
 * Provides robust frontend-backend communication
 */

class APIClient {
    constructor() {
        this.baseURL = window.location.origin;
        this.defaultTimeout = 30000; // 30 seconds
        this.retryAttempts = 3;
        this.retryDelay = 1000; // 1 second
    }

    /**
     * Make API request with error handling and retries
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                ...options.headers
            },
            credentials: 'same-origin',
            ...options
        };

        // Add body for POST/PUT requests
        if (options.body && ['POST', 'PUT', 'PATCH'].includes(config.method)) {
            config.body = JSON.stringify(options.body);
        }

        // Retry logic
        for (let attempt = 0; attempt < this.retryAttempts; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.defaultTimeout);
                
                const response = await fetch(url, {
                    ...config,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);

                // Handle different response types
                if (!response.ok) {
                    const error = await this.handleErrorResponse(response);
                    throw error;
                }

                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return await response.json();
                } else {
                    return await response.text();
                }

            } catch (error) {
                // If it's the last attempt, throw the error
                if (attempt === this.retryAttempts - 1) {
                    throw this.enhanceError(error);
                }

                // Wait before retrying
                await this.sleep(this.retryDelay * (attempt + 1));
                console.warn(`Retrying request to ${endpoint} (attempt ${attempt + 2}/${this.retryAttempts})`);
            }
        }
    }

    /**
     * Handle error responses
     */
    async handleErrorResponse(response) {
        let errorData;
        try {
            errorData = await response.json();
        } catch {
            errorData = { error: 'Unknown error occurred' };
        }

        const error = new Error(errorData.error || `HTTP ${response.status} error`);
        error.status = response.status;
        error.type = errorData.type || 'http_error';
        error.details = errorData;
        
        return error;
    }

    /**
     * Enhance error with additional context
     */
    enhanceError(error) {
        if (error.name === 'AbortError') {
            error.message = 'Request timeout - please try again';
            error.type = 'timeout';
        } else if (!navigator.onLine) {
            error.message = 'No internet connection';
            error.type = 'offline';
        }
        return error;
    }

    /**
     * Sleep utility for delays
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Convenience methods
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    async post(endpoint, data = {}) {
        return this.request(endpoint, { method: 'POST', body: data });
    }

    async put(endpoint, data = {}) {
        return this.request(endpoint, { method: 'PUT', body: data });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// Create global API client instance
window.apiClient = new APIClient();

/**
 * Chat API Integration
 */
class ChatAPI {
    constructor(apiClient) {
        this.api = apiClient;
        this.sessionId = this.getOrCreateSessionId();
    }

    getOrCreateSessionId() {
        let sessionId = localStorage.getItem('chat_session_id');
        if (!sessionId) {
            sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            localStorage.setItem('chat_session_id', sessionId);
        }
        return sessionId;
    }

    async sendMessage(message) {
        try {
            const response = await this.api.post('/api/chat', {
                message: message,
                session_id: this.sessionId
            });
            return response;
        } catch (error) {
            console.error('Chat API error:', error);
            throw error;
        }
    }
}

/**
 * Search API Integration
 */
class SearchAPI {
    constructor(apiClient) {
        this.api = apiClient;
        this.searchCache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    async search(query, type = 'all') {
        const cacheKey = `${query}_${type}`;
        
        // Check cache
        const cached = this.searchCache.get(cacheKey);
        if (cached && (Date.now() - cached.timestamp < this.cacheTimeout)) {
            return cached.data;
        }

        try {
            const response = await this.api.get('/api/search', { query, type });
            
            // Cache the result
            this.searchCache.set(cacheKey, {
                data: response,
                timestamp: Date.now()
            });
            
            return response;
        } catch (error) {
            console.error('Search API error:', error);
            throw error;
        }
    }

    clearCache() {
        this.searchCache.clear();
    }
}

/**
 * Schedule API Integration
 */
class ScheduleAPI {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async getAvailableSlots(date, serviceType = 'presencial') {
        try {
            const response = await this.api.get('/api/schedule', {
                date: date,
                service_type: serviceType
            });
            return response;
        } catch (error) {
            console.error('Schedule API error:', error);
            throw error;
        }
    }

    async bookSlot(slotData) {
        try {
            const response = await this.api.post('/api/schedule/book', slotData);
            return response;
        } catch (error) {
            console.error('Schedule booking error:', error);
            throw error;
        }
    }
}

/**
 * Form Submission Handler
 */
class FormHandler {
    constructor(apiClient) {
        this.api = apiClient;
    }

    async submitForm(formElement, endpoint) {
        const formData = new FormData(formElement);
        const data = Object.fromEntries(formData.entries());

        // Show loading state
        const submitButton = formElement.querySelector('[type="submit"]');
        const originalText = submitButton?.innerHTML;
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
        }

        try {
            const response = await this.api.post(endpoint, data);
            
            // Show success message
            this.showNotification('Formulário enviado com sucesso!', 'success');
            
            // Reset form
            formElement.reset();
            
            return response;
        } catch (error) {
            // Show error message
            this.showNotification(
                error.message || 'Erro ao enviar formulário. Tente novamente.',
                'error'
            );
            throw error;
        } finally {
            // Restore button state
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Add to page
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(notification, container.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialize API services
document.addEventListener('DOMContentLoaded', function() {
    window.chatAPI = new ChatAPI(window.apiClient);
    window.searchAPI = new SearchAPI(window.apiClient);
    window.scheduleAPI = new ScheduleAPI(window.apiClient);
    window.formHandler = new FormHandler(window.apiClient);
    
    console.log('API integration initialized');
});