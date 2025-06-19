"""
Frontend Application Entry Point - Modular Architecture
Modern vanilla JavaScript with component-based architecture
"""

import { ApiService } from './services/ApiService.js';
import { UIManager } from './components/UIManager.js';
import { ChatbotComponent } from './components/ChatbotComponent.js';
import { ContactFormComponent } from './components/ContactFormComponent.js';
import { SchedulingComponent } from './components/SchedulingComponent.js';
import { ProcessConsultationComponent } from './components/ProcessConsultationComponent.js';
import { AccessibilityManager } from './services/AccessibilityManager.js';
import { PerformanceMonitor } from './services/PerformanceMonitor.js';

class CourtApplication {
    constructor() {
        this.components = new Map();
        this.services = new Map();
        this.init();
    }

    async init() {
        try {
            // Initialize core services
            this.services.set('api', new ApiService());
            this.services.set('ui', new UIManager());
            this.services.set('accessibility', new AccessibilityManager());
            this.services.set('performance', new PerformanceMonitor());

            // Initialize components
            await this.initializeComponents();

            // Setup event listeners
            this.setupEventListeners();

            // Start performance monitoring
            this.services.get('performance').startMonitoring();

            console.log('Court Application initialized successfully');
        } catch (error) {
            console.error('Application initialization failed:', error);
            this.handleInitializationError(error);
        }
    }

    async initializeComponents() {
        const componentConfigs = [
            { name: 'chatbot', component: ChatbotComponent, selector: '#chatbot-container' },
            { name: 'contact', component: ContactFormComponent, selector: '#contact-form' },
            { name: 'scheduling', component: SchedulingComponent, selector: '#scheduling-form' },
            { name: 'process', component: ProcessConsultationComponent, selector: '#process-consultation' }
        ];

        for (const config of componentConfigs) {
            const element = document.querySelector(config.selector);
            if (element) {
                const componentInstance = new config.component({
                    element,
                    apiService: this.services.get('api'),
                    uiManager: this.services.get('ui')
                });
                
                await componentInstance.init();
                this.components.set(config.name, componentInstance);
            }
        }
    }

    setupEventListeners() {
        // Global error handling
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.services.get('ui').showNotification('Ocorreu um erro inesperado', 'error');
        });

        // Accessibility keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey && event.altKey) {
                this.services.get('accessibility').handleKeyboardShortcut(event);
            }
        });

        // Performance monitoring
        window.addEventListener('load', () => {
            this.services.get('performance').recordPageLoad();
        });

        // Service worker registration for PWA
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => console.log('SW registered'))
                .catch(error => console.log('SW registration failed'));
        }
    }

    handleInitializationError(error) {
        const errorContainer = document.getElementById('error-container');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Erro de Inicialização</h5>
                    <p>Ocorreu um erro ao carregar a aplicação. Recarregue a página ou tente novamente mais tarde.</p>
                    <button class="btn btn-primary" onclick="window.location.reload()">
                        Recarregar Página
                    </button>
                </div>
            `;
            errorContainer.style.display = 'block';
        }
    }

    getComponent(name) {
        return this.components.get(name);
    }

    getService(name) {
        return this.services.get(name);
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.courtApp = new CourtApplication();
});

export { CourtApplication };