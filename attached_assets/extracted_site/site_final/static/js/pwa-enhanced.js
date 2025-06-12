/**
 * Progressive Web App Enhanced Manager
 * Implements service worker, offline functionality, and installation prompts
 */

class PWAManager {
    constructor() {
        this.deferredPrompt = null;
        this.isInstalled = false;
        this.isOnline = navigator.onLine;
        this.init();
    }

    async init() {
        this.checkInstallation();
        this.registerServiceWorker();
        this.setupInstallPrompt();
        this.setupOfflineDetection();
        this.setupNotifications();
        this.handleAppShortcuts();
        console.log('PWA Manager initialized');
    }

    checkInstallation() {
        // Check if app is already installed
        if (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) {
            this.isInstalled = true;
            document.body.classList.add('pwa-installed');
            console.log('App running in standalone mode');
        }

        // Check if running as PWA
        if (window.navigator.standalone === true) {
            this.isInstalled = true;
            document.body.classList.add('pwa-installed');
        }
    }

    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
                console.log('Service Worker registered successfully');
                
                // Listen for updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateNotification();
                        }
                    });
                });
            } catch (error) {
                console.log('Service Worker registration failed:', error);
            }
        }
    }

    setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        window.addEventListener('appinstalled', () => {
            this.isInstalled = true;
            this.hideInstallButton();
            this.showInstallSuccess();
            console.log('App installed successfully');
        });
    }

    showInstallButton() {
        if (this.isInstalled) return;

        const installButton = document.createElement('div');
        installButton.id = 'pwa-install-prompt';
        installButton.className = 'pwa-install-prompt';
        installButton.innerHTML = `
            <div class="install-content">
                <div class="install-icon">📱</div>
                <div class="install-text">
                    <h4>Instalar App</h4>
                    <p>Acesse mais rapidamente instalando em seu dispositivo</p>
                </div>
                <div class="install-actions">
                    <button id="install-app-btn" class="btn btn-primary">Instalar</button>
                    <button id="dismiss-install-btn" class="btn btn-outline-secondary">Agora não</button>
                </div>
            </div>
        `;

        document.body.appendChild(installButton);

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .pwa-install-prompt {
                position: fixed;
                bottom: 20px;
                left: 20px;
                right: 20px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                z-index: 10000;
                padding: 20px;
                border: 1px solid #e0e0e0;
                animation: slideUp 0.3s ease;
            }

            @keyframes slideUp {
                from { transform: translateY(100%); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }

            .install-content {
                display: flex;
                align-items: center;
                gap: 15px;
            }

            .install-icon {
                font-size: 32px;
                min-width: 40px;
            }

            .install-text h4 {
                margin: 0 0 5px 0;
                font-size: 16px;
                color: #333;
            }

            .install-text p {
                margin: 0;
                font-size: 14px;
                color: #666;
            }

            .install-actions {
                display: flex;
                gap: 10px;
                flex-direction: column;
                min-width: 120px;
            }

            .install-actions .btn {
                font-size: 14px;
                padding: 8px 16px;
            }

            @media (min-width: 768px) {
                .pwa-install-prompt {
                    max-width: 400px;
                    left: auto;
                    right: 20px;
                }
                
                .install-actions {
                    flex-direction: row;
                }
            }
        `;
        document.head.appendChild(style);

        // Setup event listeners
        document.getElementById('install-app-btn').addEventListener('click', () => {
            this.installApp();
        });

        document.getElementById('dismiss-install-btn').addEventListener('click', () => {
            this.hideInstallButton();
            localStorage.setItem('pwa-install-dismissed', Date.now());
        });

        // Auto-dismiss after 10 seconds
        setTimeout(() => {
            if (document.getElementById('pwa-install-prompt')) {
                this.hideInstallButton();
            }
        }, 10000);
    }

    async installApp() {
        if (!this.deferredPrompt) return;

        this.deferredPrompt.prompt();
        const result = await this.deferredPrompt.userChoice;
        
        if (result.outcome === 'accepted') {
            console.log('User accepted the install prompt');
        } else {
            console.log('User dismissed the install prompt');
        }
        
        this.deferredPrompt = null;
        this.hideInstallButton();
    }

    hideInstallButton() {
        const prompt = document.getElementById('pwa-install-prompt');
        if (prompt) {
            prompt.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => prompt.remove(), 300);
        }
    }

    showInstallSuccess() {
        const notification = document.createElement('div');
        notification.className = 'pwa-notification success';
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">✅</span>
                <span>App instalado com sucesso!</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.className = 'pwa-notification update';
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">🔄</span>
                <span>Nova versão disponível</span>
                <button onclick="window.location.reload()" class="btn btn-sm btn-primary">Atualizar</button>
            </div>
        `;
        
        document.body.appendChild(notification);
    }

    setupOfflineDetection() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showOnlineNotification();
            document.body.classList.remove('offline');
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showOfflineNotification();
            document.body.classList.add('offline');
        });

        // Initial state
        if (!this.isOnline) {
            document.body.classList.add('offline');
        }
    }

    showOfflineNotification() {
        const notification = document.createElement('div');
        notification.id = 'offline-notification';
        notification.className = 'pwa-notification offline';
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">📡</span>
                <span>Modo offline ativo. Algumas funcionalidades podem estar limitadas.</span>
            </div>
        `;
        
        document.body.appendChild(notification);
    }

    showOnlineNotification() {
        const offlineNotification = document.getElementById('offline-notification');
        if (offlineNotification) {
            offlineNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = 'pwa-notification online';
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">✅</span>
                <span>Conexão reestabelecida</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    async setupNotifications() {
        if ('Notification' in window && 'serviceWorker' in navigator) {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('Notification permission granted');
            }
        }
    }

    handleAppShortcuts() {
        // Handle URL parameters for shortcuts
        const urlParams = new URLSearchParams(window.location.search);
        
        if (urlParams.get('chatbot') === 'open') {
            // Open chatbot if launched from shortcut
            setTimeout(() => {
                const chatbotToggle = document.getElementById('chatbot-toggle');
                if (chatbotToggle) {
                    chatbotToggle.click();
                }
            }, 1000);
        }
    }

    // Public API methods
    async shareContent(data) {
        if (navigator.share) {
            try {
                await navigator.share(data);
                console.log('Content shared successfully');
            } catch (error) {
                console.log('Error sharing:', error);
                this.fallbackShare(data);
            }
        } else {
            this.fallbackShare(data);
        }
    }

    fallbackShare(data) {
        // Fallback share implementation
        if (navigator.clipboard) {
            navigator.clipboard.writeText(data.url || data.text || '');
            this.showNotification('Link copiado para a área de transferência');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `pwa-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Offline data management
    async cacheUserData(key, data) {
        if ('localStorage' in window) {
            try {
                localStorage.setItem(`offline_${key}`, JSON.stringify({
                    data: data,
                    timestamp: Date.now()
                }));
            } catch (error) {
                console.log('Error caching data:', error);
            }
        }
    }

    async getOfflineData(key) {
        if ('localStorage' in window) {
            try {
                const cached = localStorage.getItem(`offline_${key}`);
                if (cached) {
                    const parsed = JSON.parse(cached);
                    // Return data if less than 24 hours old
                    if (Date.now() - parsed.timestamp < 24 * 60 * 60 * 1000) {
                        return parsed.data;
                    }
                }
            } catch (error) {
                console.log('Error retrieving offline data:', error);
            }
        }
        return null;
    }
}

// Global styles for PWA notifications
const pwaStyles = document.createElement('style');
pwaStyles.textContent = `
    .pwa-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        z-index: 10001;
        padding: 15px;
        border-left: 4px solid #2c5aa0;
        animation: slideInRight 0.3s ease;
        max-width: 300px;
    }

    .pwa-notification.success {
        border-left-color: #28a745;
    }

    .pwa-notification.offline {
        border-left-color: #ffc107;
        background: #fff3cd;
    }

    .pwa-notification.online {
        border-left-color: #28a745;
        background: #d4edda;
    }

    .pwa-notification.update {
        border-left-color: #17a2b8;
        background: #d1ecf1;
    }

    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }

    @keyframes slideDown {
        from { transform: translateY(0); opacity: 1; }
        to { transform: translateY(100%); opacity: 0; }
    }

    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 14px;
    }

    .notification-icon {
        font-size: 16px;
    }

    .offline .chatbot-window,
    .offline .form-submit {
        opacity: 0.6;
        pointer-events: none;
    }

    .offline::before {
        content: "MODO OFFLINE";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background: #ffc107;
        color: #212529;
        text-align: center;
        padding: 5px;
        font-size: 12px;
        font-weight: bold;
        z-index: 10002;
    }

    body.offline {
        padding-top: 30px;
    }
`;
document.head.appendChild(pwaStyles);

// Initialize PWA Manager
let pwaManager;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        pwaManager = new PWAManager();
        window.pwaManager = pwaManager;
    });
} else {
    pwaManager = new PWAManager();
    window.pwaManager = pwaManager;
}