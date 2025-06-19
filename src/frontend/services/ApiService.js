/**
 * API Service - Frontend Module
 * Centralized HTTP client for backend communication
 */
class ApiService {
    constructor() {
        this.baseURL = '/api/v1';
        this.timeout = 10000;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: options.method || 'GET',
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        if (config.method !== 'GET' && options.data) {
            config.body = JSON.stringify(options.data);
        }

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            config.signal = controller.signal;
            
            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }

    // Contact API methods
    async submitContact(contactData) {
        return this.request('/contact', {
            method: 'POST',
            data: contactData
        });
    }

    async getContacts(page = 1, perPage = 10) {
        return this.request(`/contact?page=${page}&per_page=${perPage}`);
    }

    // Process consultation methods
    async submitProcessConsultation(consultationData) {
        return this.request('/process/consultation', {
            method: 'POST',
            data: consultationData
        });
    }

    async searchProcess(processNumber) {
        return this.request(`/process/search?number=${encodeURIComponent(processNumber)}`);
    }

    // Chatbot methods
    async sendChatMessage(message, sessionId = null) {
        return this.request('/chatbot/chat', {
            method: 'POST',
            data: { message, session_id: sessionId }
        });
    }

    async getChatHistory(sessionId) {
        return this.request(`/chatbot/history/${sessionId}`);
    }

    async getChatAnalytics() {
        return this.request('/chatbot/analytics');
    }

    // Scheduling methods
    async scheduleMeeting(meetingData) {
        return this.request('/scheduling/meeting', {
            method: 'POST',
            data: meetingData
        });
    }

    async getMeeting(meetingId) {
        return this.request(`/scheduling/meeting/${meetingId}`);
    }

    async checkAvailability(date) {
        return this.request(`/scheduling/availability?date=${date}`);
    }

    // Health check methods
    async getHealth() {
        return this.request('/health');
    }

    async getDetailedHealth() {
        return this.request('/health/detailed');
    }

    // Utility methods
    setAuthToken(token) {
        this.defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    removeAuthToken() {
        delete this.defaultHeaders['Authorization'];
    }

    setTimeout(timeout) {
        this.timeout = timeout;
    }
}

export { ApiService };