/**
 * Enhanced Accessibility Manager - 2ª Vara Cível de Cariacica
 * Comprehensive accessibility features with dark mode and preference management
 */

class AccessibilityManager {
    constructor() {
        this.preferences = this.loadPreferences();
        this.darkModeEnabled = this.preferences.darkMode || this.detectDarkModePreference();
        this.init();
    }

    init() {
        this.createAccessibilityPanel();
        this.setupKeyboardShortcuts();
        this.setupFocusManagement();
        this.setupSystemThemeListener();
        this.applyPreferences();
        this.setupAriaLiveRegions();
        this.enhanceFormValidation();
        console.log('Enhanced Accessibility Manager initialized');
    }

    detectDarkModePreference() {
        // Detect user's system preference for dark mode
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            console.log('Usuário prefere modo escuro');
            return true;
        }
        return false;
    }

    // Listen for system theme changes
    setupSystemThemeListener() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addListener((e) => {
                if (!this.preferences.darkMode) { // Only auto-switch if user hasn't manually set preference
                    this.preferences.darkMode = e.matches;
                    this.applyDarkMode();
                    this.announce(e.matches ? 'Modo escuro ativado automaticamente' : 'Modo claro ativado automaticamente');
                }
            });
        }
    }

    loadPreferences() {
        const saved = localStorage.getItem('accessibility-preferences');
        return saved ? JSON.parse(saved) : {
            darkMode: false,
            highContrast: false,
            largeText: false,
            reducedMotion: false,
            screenReader: false
        };
    }

    savePreferences() {
        localStorage.setItem('accessibility-preferences', JSON.stringify(this.preferences));
    }

    createAccessibilityPanel() {
        const panel = document.createElement('div');
        panel.id = 'accessibility-panel';
        panel.className = 'accessibility-panel';
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-labelledby', 'accessibility-title');
        panel.setAttribute('aria-hidden', 'true');
        
        panel.innerHTML = `
            <div class="accessibility-header">
                <h3 id="accessibility-title">Preferências de Acessibilidade</h3>
                <button class="accessibility-close" aria-label="Fechar painel de acessibilidade">×</button>
            </div>
            <div class="accessibility-content">
                <div class="accessibility-option">
                    <label>
                        <input type="checkbox" id="dark-mode-toggle" ${this.preferences.darkMode ? 'checked' : ''}>
                        <span>Modo Escuro</span>
                        <small>Reduz o brilho da tela para melhor conforto visual</small>
                    </label>
                </div>
                <div class="accessibility-option">
                    <label>
                        <input type="checkbox" id="high-contrast-toggle" ${this.preferences.highContrast ? 'checked' : ''}>
                        <span>Alto Contraste</span>
                        <small>Aumenta o contraste para melhor legibilidade</small>
                    </label>
                </div>
                <div class="accessibility-option">
                    <label>
                        <input type="checkbox" id="large-text-toggle" ${this.preferences.largeText ? 'checked' : ''}>
                        <span>Texto Grande</span>
                        <small>Aumenta o tamanho da fonte para facilitar a leitura</small>
                    </label>
                </div>
                <div class="accessibility-option">
                    <label>
                        <input type="checkbox" id="reduced-motion-toggle" ${this.preferences.reducedMotion ? 'checked' : ''}>
                        <span>Reduzir Animações</span>
                        <small>Minimiza animações para usuários sensíveis ao movimento</small>
                    </label>
                </div>
                <div class="accessibility-shortcuts">
                    <h4>Atalhos de Teclado</h4>
                    <ul>
                        <li><kbd>Alt + A</kbd> - Abrir/fechar painel de acessibilidade</li>
                        <li><kbd>Alt + C</kbd> - Abrir/fechar chatbot</li>
                        <li><kbd>Alt + H</kbd> - Ir para o início da página</li>
                        <li><kbd>Alt + M</kbd> - Ir para o menu principal</li>
                        <li><kbd>Alt + S</kbd> - Ir para a busca</li>
                    </ul>
                </div>
            </div>
        `;

        document.body.appendChild(panel);
        this.setupPanelEvents();
    }

    setupPanelEvents() {
        const panel = document.getElementById('accessibility-panel');
        const closeBtn = panel.querySelector('.accessibility-close');
        
        closeBtn.addEventListener('click', () => this.togglePanel(false));
        
        // Toggle preferences
        document.getElementById('dark-mode-toggle').addEventListener('change', (e) => {
            this.preferences.darkMode = e.target.checked;
            this.applyDarkMode();
            this.savePreferences();
        });

        document.getElementById('high-contrast-toggle').addEventListener('change', (e) => {
            this.preferences.highContrast = e.target.checked;
            this.applyHighContrast();
            this.savePreferences();
        });

        document.getElementById('large-text-toggle').addEventListener('change', (e) => {
            this.preferences.largeText = e.target.checked;
            this.applyLargeText();
            this.savePreferences();
        });

        document.getElementById('reduced-motion-toggle').addEventListener('change', (e) => {
            this.preferences.reducedMotion = e.target.checked;
            this.applyReducedMotion();
            this.savePreferences();
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.altKey) {
                switch(e.key) {
                    case 'a':
                    case 'A':
                        e.preventDefault();
                        this.togglePanel();
                        break;
                    case 'c':
                    case 'C':
                        e.preventDefault();
                        this.toggleChatbot();
                        break;
                    case 'h':
                    case 'H':
                        e.preventDefault();
                        this.skipToContent();
                        break;
                    case 'm':
                    case 'M':
                        e.preventDefault();
                        this.skipToMenu();
                        break;
                    case 's':
                    case 'S':
                        e.preventDefault();
                        this.skipToSearch();
                        break;
                }
            }
        });
    }

    setupFocusManagement() {
        // Enhanced focus indicators
        const style = document.createElement('style');
        style.textContent = `
            *:focus {
                outline: 3px solid #007bff !important;
                outline-offset: 2px !important;
                box-shadow: 0 0 0 5px rgba(0, 123, 255, 0.25) !important;
            }
            
            .accessibility-panel {
                position: fixed;
                top: 20px;
                right: 20px;
                width: 350px;
                background: white;
                border: 2px solid #333;
                border-radius: 8px;
                padding: 20px;
                z-index: 10000;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                transform: translateX(400px);
                transition: transform 0.3s ease;
            }
            
            .accessibility-panel.visible {
                transform: translateX(0);
            }
            
            .accessibility-panel h3 {
                margin: 0 0 15px 0;
                color: #333;
            }
            
            .accessibility-close {
                position: absolute;
                top: 10px;
                right: 10px;
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #666;
            }
            
            .accessibility-option {
                margin: 15px 0;
            }
            
            .accessibility-option label {
                display: block;
                cursor: pointer;
            }
            
            .accessibility-option input {
                margin-right: 10px;
            }
            
            .accessibility-option small {
                display: block;
                color: #666;
                margin-top: 5px;
                font-size: 12px;
            }
            
            .accessibility-shortcuts {
                margin-top: 20px;
                padding-top: 15px;
                border-top: 1px solid #eee;
            }
            
            .accessibility-shortcuts h4 {
                margin: 0 0 10px 0;
                font-size: 14px;
            }
            
            .accessibility-shortcuts ul {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            
            .accessibility-shortcuts li {
                margin: 5px 0;
                font-size: 12px;
            }
            
            .accessibility-shortcuts kbd {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 11px;
            }
            
            /* Dark mode styles */
            body.dark-mode {
                background-color: #121212 !important;
                color: #e0e0e0 !important;
            }
            
            body.dark-mode .accessibility-panel {
                background: #1e1e1e;
                border-color: #444;
                color: #e0e0e0;
            }
            
            body.dark-mode .accessibility-panel h3 {
                color: #e0e0e0;
            }
            
            body.dark-mode .card,
            body.dark-mode .navbar,
            body.dark-mode .footer {
                background-color: #1e1e1e !important;
                color: #e0e0e0 !important;
            }
            
            /* High contrast styles */
            body.high-contrast {
                filter: contrast(150%);
            }
            
            /* Large text styles */
            body.large-text {
                font-size: 120% !important;
            }
            
            body.large-text h1 { font-size: 3rem !important; }
            body.large-text h2 { font-size: 2.5rem !important; }
            body.large-text h3 { font-size: 2rem !important; }
            
            /* Reduced motion styles */
            body.reduced-motion *,
            body.reduced-motion *::before,
            body.reduced-motion *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        `;
        document.head.appendChild(style);
    }

    setupAriaLiveRegions() {
        // Create live regions for announcements
        const liveRegion = document.createElement('div');
        liveRegion.id = 'accessibility-announcements';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.style.position = 'absolute';
        liveRegion.style.left = '-10000px';
        liveRegion.style.width = '1px';
        liveRegion.style.height = '1px';
        liveRegion.style.overflow = 'hidden';
        document.body.appendChild(liveRegion);
    }

    announce(message) {
        const liveRegion = document.getElementById('accessibility-announcements');
        if (liveRegion) {
            liveRegion.textContent = message;
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    }

    enhanceFormValidation() {
        // Add enhanced form validation with better accessibility
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('invalid', (e) => {
                    const message = e.target.validationMessage;
                    this.announce(`Erro no campo ${e.target.labels[0]?.textContent || e.target.name}: ${message}`);
                });
            });
        });
    }

    applyPreferences() {
        this.applyDarkMode();
        this.applyHighContrast();
        this.applyLargeText();
        this.applyReducedMotion();
    }

    applyDarkMode() {
        document.body.classList.toggle('dark-mode', this.preferences.darkMode);
        if (this.preferences.darkMode) {
            this.announce('Modo escuro ativado');
        }
    }

    applyHighContrast() {
        document.body.classList.toggle('high-contrast', this.preferences.highContrast);
        if (this.preferences.highContrast) {
            this.announce('Alto contraste ativado');
        }
    }

    applyLargeText() {
        document.body.classList.toggle('large-text', this.preferences.largeText);
        if (this.preferences.largeText) {
            this.announce('Texto grande ativado');
        }
    }

    applyReducedMotion() {
        document.body.classList.toggle('reduced-motion', this.preferences.reducedMotion);
        if (this.preferences.reducedMotion) {
            this.announce('Animações reduzidas');
        }
    }

    togglePanel(show = null) {
        const panel = document.getElementById('accessibility-panel');
        const isVisible = panel.classList.contains('visible');
        
        if (show === null) {
            show = !isVisible;
        }
        
        panel.classList.toggle('visible', show);
        panel.setAttribute('aria-hidden', !show);
        
        if (show) {
            panel.querySelector('input').focus();
            this.announce('Painel de acessibilidade aberto');
        } else {
            this.announce('Painel de acessibilidade fechado');
        }
    }

    toggleChatbot() {
        const chatbot = document.getElementById('chatbot-toggle');
        if (chatbot) {
            chatbot.click();
            this.announce('Chatbot ativado');
        }
    }

    skipToContent() {
        const main = document.querySelector('main, #main-content, .main-content');
        if (main) {
            main.focus();
            main.scrollIntoView();
            this.announce('Navegado para o conteúdo principal');
        }
    }

    skipToMenu() {
        const nav = document.querySelector('nav, .navbar, #navigation');
        if (nav) {
            const firstLink = nav.querySelector('a');
            if (firstLink) {
                firstLink.focus();
                this.announce('Navegado para o menu principal');
            }
        }
    }

    skipToSearch() {
        const search = document.querySelector('#search, [type="search"], .search-input');
        if (search) {
            search.focus();
            this.announce('Navegado para a busca');
        }
    }
}

// Initialize accessibility manager when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.accessibilityManager = new AccessibilityManager();
    });
} else {
    window.accessibilityManager = new AccessibilityManager();
}

// Accessibility button functionality removed - using main navigation only