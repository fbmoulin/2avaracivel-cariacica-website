/**
 * Enhanced Accessibility Manager for 2ª Vara Cível de Cariacica
 * Comprehensive accessibility features with debugging and improvement capabilities
 */

class EnhancedAccessibilityManager {
    constructor() {
        this.isInitialized = false;
        this.accessibilitySettings = {
            fontSize: 16,
            highContrast: false,
            reducedMotion: false,
            screenReaderMode: false,
            keyboardNavigation: true,
            voiceGuidance: false
        };
        
        this.focusHistory = [];
        this.announcements = [];
        this.debugMode = localStorage.getItem('accessibilityDebug') === 'true';
        
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        
        this.loadSettings();
        this.createAccessibilityControls();
        this.setupKeyboardNavigation();
        this.setupFocusManagement();
        this.setupScreenReaderSupport();
        this.addSkipLinks();
        this.enhanceFormAccessibility();
        this.setupLiveRegions();
        this.debugAccessibility();
        
        this.isInitialized = true;
        this.announce('Sistema de acessibilidade aprimorado carregado');
        
        if (this.debugMode) {
            console.log('Enhanced Accessibility Manager initialized with debug mode');
        }
    }

    loadSettings() {
        const saved = localStorage.getItem('accessibilitySettings');
        if (saved) {
            try {
                this.accessibilitySettings = { ...this.accessibilitySettings, ...JSON.parse(saved) };
                this.applySettings();
            } catch (e) {
                console.error('Error loading accessibility settings:', e);
            }
        }
    }

    saveSettings() {
        localStorage.setItem('accessibilitySettings', JSON.stringify(this.accessibilitySettings));
        this.announce('Configurações de acessibilidade salvas');
    }

    createAccessibilityControls() {
        // Remove existing controls to prevent duplicates
        const existing = document.getElementById('accessibility-controls');
        if (existing) existing.remove();

        const controls = document.createElement('div');
        controls.id = 'accessibility-controls';
        controls.className = 'accessibility-controls';
        controls.setAttribute('role', 'toolbar');
        controls.setAttribute('aria-label', 'Controles de acessibilidade');
        
        controls.innerHTML = `
            <div class="accessibility-panel">
                <button id="accessibility-toggle" class="accessibility-btn" aria-expanded="false" aria-controls="accessibility-options">
                    <i class="fas fa-universal-access" aria-hidden="true"></i>
                    <span class="sr-only">Abrir opções de acessibilidade</span>
                </button>
                
                <div id="accessibility-options" class="accessibility-options" hidden>
                    <h3>Opções de Acessibilidade</h3>
                    
                    <div class="accessibility-group">
                        <label>Tamanho da Fonte</label>
                        <div class="font-controls">
                            <button id="decrease-font" class="accessibility-btn" aria-label="Diminuir fonte">A-</button>
                            <span id="font-size-display" aria-live="polite">${this.accessibilitySettings.fontSize}px</span>
                            <button id="increase-font" class="accessibility-btn" aria-label="Aumentar fonte">A+</button>
                        </div>
                    </div>
                    
                    <div class="accessibility-group">
                        <button id="toggle-contrast" class="accessibility-btn toggle-btn" 
                                aria-pressed="${this.accessibilitySettings.highContrast}" 
                                aria-label="Alternar alto contraste">
                            <i class="fas fa-adjust" aria-hidden="true"></i>
                            Alto Contraste
                        </button>
                    </div>
                    
                    <div class="accessibility-group">
                        <button id="toggle-motion" class="accessibility-btn toggle-btn" 
                                aria-pressed="${this.accessibilitySettings.reducedMotion}" 
                                aria-label="Reduzir animações">
                            <i class="fas fa-pause" aria-hidden="true"></i>
                            Reduzir Movimento
                        </button>
                    </div>
                    
                    <div class="accessibility-group">
                        <button id="toggle-voice" class="accessibility-btn toggle-btn" 
                                aria-pressed="${this.accessibilitySettings.voiceGuidance}" 
                                aria-label="Ativar guia de voz">
                            <i class="fas fa-volume-up" aria-hidden="true"></i>
                            Guia de Voz
                        </button>
                    </div>
                    
                    <div class="accessibility-group">
                        <button id="focus-outline" class="accessibility-btn" aria-label="Destacar elementos focáveis">
                            <i class="fas fa-search" aria-hidden="true"></i>
                            Mostrar Focos
                        </button>
                    </div>
                    
                    <div class="accessibility-group">
                        <button id="reset-accessibility" class="accessibility-btn" aria-label="Restaurar configurações padrão">
                            <i class="fas fa-redo" aria-hidden="true"></i>
                            Restaurar Padrão
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(controls);
        this.bindControlEvents();
    }

    bindControlEvents() {
        const toggle = document.getElementById('accessibility-toggle');
        const options = document.getElementById('accessibility-options');

        toggle?.addEventListener('click', () => {
            const isHidden = options.hasAttribute('hidden');
            if (isHidden) {
                options.removeAttribute('hidden');
                toggle.setAttribute('aria-expanded', 'true');
            } else {
                options.setAttribute('hidden', '');
                toggle.setAttribute('aria-expanded', 'false');
            }
        });

        // Font size controls
        document.getElementById('decrease-font')?.addEventListener('click', () => this.adjustFontSize(-2));
        document.getElementById('increase-font')?.addEventListener('click', () => this.adjustFontSize(2));

        // Toggle controls
        document.getElementById('toggle-contrast')?.addEventListener('click', () => this.toggleHighContrast());
        document.getElementById('toggle-motion')?.addEventListener('click', () => this.toggleReducedMotion());
        document.getElementById('toggle-voice')?.addEventListener('click', () => this.toggleVoiceGuidance());

        // Utility controls
        document.getElementById('focus-outline')?.addEventListener('click', () => this.highlightFocusableElements());
        document.getElementById('reset-accessibility')?.addEventListener('click', () => this.resetSettings());

        // Close on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !options.hasAttribute('hidden')) {
                options.setAttribute('hidden', '');
                toggle.setAttribute('aria-expanded', 'false');
                toggle.focus();
            }
        });
    }

    addSkipLinks() {
        // Remove existing skip links to prevent duplicates
        const existing = document.querySelector('.skip-links');
        if (existing) existing.remove();

        const skipLinks = document.createElement('div');
        skipLinks.className = 'skip-links';
        skipLinks.innerHTML = `
            <a href="#main-content" class="skip-link">Pular para conteúdo principal</a>
            <a href="#main-navigation" class="skip-link">Pular para navegação</a>
            <a href="#footer" class="skip-link">Pular para rodapé</a>
            <a href="#accessibility-controls" class="skip-link">Pular para controles de acessibilidade</a>
        `;

        document.body.insertBefore(skipLinks, document.body.firstChild);

        // Ensure target elements have proper IDs
        this.ensureSkipTargets();
    }

    ensureSkipTargets() {
        const targets = [
            { selector: 'main, .main-content, #content', id: 'main-content' },
            { selector: 'nav, .navbar, .navigation', id: 'main-navigation' },
            { selector: 'footer, .footer', id: 'footer' }
        ];

        targets.forEach(({ selector, id }) => {
            const element = document.querySelector(selector);
            if (element && !element.id) {
                element.id = id;
                element.setAttribute('tabindex', '-1');
            }
        });
    }

    setupKeyboardNavigation() {
        let focusableElements = [];
        let currentFocusIndex = -1;

        const updateFocusableElements = () => {
            focusableElements = Array.from(document.querySelectorAll(
                'a[href]:not([disabled]), button:not([disabled]), textarea:not([disabled]), ' +
                'input[type="text"]:not([disabled]), input[type="radio"]:not([disabled]), ' +
                'input[type="checkbox"]:not([disabled]), select:not([disabled]), ' +
                '[tabindex]:not([tabindex="-1"]):not([disabled])'
            )).filter(el => el.offsetParent !== null);
        };

        document.addEventListener('keydown', (e) => {
            // Alt + A: Open accessibility controls
            if (e.altKey && e.key === 'a') {
                e.preventDefault();
                document.getElementById('accessibility-toggle')?.click();
                return;
            }

            // Alt + M: Focus main content
            if (e.altKey && e.key === 'm') {
                e.preventDefault();
                const main = document.getElementById('main-content');
                if (main) {
                    main.focus();
                    this.announce('Focando no conteúdo principal');
                }
                return;
            }

            // Alt + N: Focus navigation
            if (e.altKey && e.key === 'n') {
                e.preventDefault();
                const nav = document.getElementById('main-navigation');
                if (nav) {
                    nav.focus();
                    this.announce('Focando na navegação');
                }
                return;
            }

            // Enhanced Tab navigation with announcements
            if (e.key === 'Tab') {
                updateFocusableElements();
                setTimeout(() => {
                    const focused = document.activeElement;
                    if (focused && this.accessibilitySettings.voiceGuidance) {
                        this.announceElement(focused);
                    }
                }, 100);
            }
        });

        // Track focus for debugging
        document.addEventListener('focusin', (e) => {
            this.focusHistory.push({
                element: e.target,
                timestamp: Date.now(),
                tagName: e.target.tagName,
                className: e.target.className,
                id: e.target.id
            });

            // Keep only last 10 focus events
            if (this.focusHistory.length > 10) {
                this.focusHistory.shift();
            }

            if (this.debugMode) {
                console.log('Focus changed to:', e.target);
            }
        });
    }

    setupFocusManagement() {
        // Enhanced focus indicators
        const style = document.createElement('style');
        style.textContent = `
            .enhanced-focus-mode *:focus {
                outline: 3px solid #ff6b35 !important;
                outline-offset: 2px !important;
                box-shadow: 0 0 0 5px rgba(255, 107, 53, 0.3) !important;
                border-radius: 4px !important;
            }
            
            .focus-highlight {
                outline: 2px dashed #1e40af !important;
                outline-offset: 1px !important;
                background-color: rgba(30, 64, 175, 0.1) !important;
            }
        `;
        document.head.appendChild(style);
    }

    setupScreenReaderSupport() {
        // Create live regions for announcements
        if (!document.getElementById('aria-live-polite')) {
            const politeRegion = document.createElement('div');
            politeRegion.id = 'aria-live-polite';
            politeRegion.setAttribute('aria-live', 'polite');
            politeRegion.setAttribute('aria-atomic', 'true');
            politeRegion.className = 'sr-only';
            document.body.appendChild(politeRegion);
        }

        if (!document.getElementById('aria-live-assertive')) {
            const assertiveRegion = document.createElement('div');
            assertiveRegion.id = 'aria-live-assertive';
            assertiveRegion.setAttribute('aria-live', 'assertive');
            assertiveRegion.setAttribute('aria-atomic', 'true');
            assertiveRegion.className = 'sr-only';
            document.body.appendChild(assertiveRegion);
        }

        // Add aria-labels to unlabeled interactive elements
        this.enhanceUnlabeledElements();
    }

    enhanceUnlabeledElements() {
        // Add labels to buttons without accessible names
        const unlabeledButtons = document.querySelectorAll('button:not([aria-label]):not([aria-labelledby])');
        unlabeledButtons.forEach((button, index) => {
            if (!button.textContent.trim()) {
                const iconClass = button.querySelector('i')?.className || '';
                let label = `Botão ${index + 1}`;
                
                if (iconClass.includes('search')) label = 'Buscar';
                else if (iconClass.includes('close')) label = 'Fechar';
                else if (iconClass.includes('menu')) label = 'Menu';
                else if (iconClass.includes('play')) label = 'Reproduzir';
                else if (iconClass.includes('pause')) label = 'Pausar';
                
                button.setAttribute('aria-label', label);
            }
        });

        // Add alt text to images without it
        const unlabeledImages = document.querySelectorAll('img:not([alt])');
        unlabeledImages.forEach((img, index) => {
            const src = img.src || '';
            let alt = '';
            
            if (src.includes('logo')) alt = 'Logo';
            else if (src.includes('banner')) alt = 'Banner';
            else if (src.includes('icon')) alt = 'Ícone';
            else alt = `Imagem ${index + 1}`;
            
            img.setAttribute('alt', alt);
        });
    }

    setupLiveRegions() {
        // Monitor form changes and announce them
        document.addEventListener('change', (e) => {
            if (e.target.matches('input, select, textarea')) {
                const label = this.getElementLabel(e.target);
                const value = e.target.value || 'vazio';
                this.announce(`${label} alterado para ${value}`, 'polite');
            }
        });

        // Monitor page changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Announce new content if it has important information
                            if (node.matches('.alert, .notification, .error, .success')) {
                                const text = node.textContent.trim();
                                if (text) {
                                    this.announce(text, 'assertive');
                                }
                            }
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    enhanceFormAccessibility() {
        const forms = document.querySelectorAll('form');
        forms.forEach((form) => {
            // Add form labels if missing
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach((input) => {
                if (!input.getAttribute('aria-label') && !input.getAttribute('aria-labelledby')) {
                    const label = form.querySelector(`label[for="${input.id}"]`);
                    if (!label) {
                        const previousElement = input.previousElementSibling;
                        if (previousElement && previousElement.textContent.trim()) {
                            input.setAttribute('aria-label', previousElement.textContent.trim());
                        }
                    }
                }

                // Add required indicators
                if (input.hasAttribute('required')) {
                    const label = this.getElementLabel(input);
                    if (!label.includes('obrigatório') && !label.includes('*')) {
                        input.setAttribute('aria-label', `${label} (obrigatório)`);
                    }
                }
            });

            // Form validation announcements
            form.addEventListener('submit', (e) => {
                const invalidInputs = form.querySelectorAll(':invalid');
                if (invalidInputs.length > 0) {
                    this.announce(`Formulário contém ${invalidInputs.length} erro(s). Por favor, corrija os campos destacados.`, 'assertive');
                }
            });
        });
    }

    // Utility methods
    adjustFontSize(change) {
        this.accessibilitySettings.fontSize = Math.max(12, Math.min(32, this.accessibilitySettings.fontSize + change));
        document.documentElement.style.fontSize = `${this.accessibilitySettings.fontSize}px`;
        
        const display = document.getElementById('font-size-display');
        if (display) display.textContent = `${this.accessibilitySettings.fontSize}px`;
        
        this.announce(`Tamanho da fonte: ${this.accessibilitySettings.fontSize} pixels`);
        this.saveSettings();
    }

    toggleHighContrast() {
        this.accessibilitySettings.highContrast = !this.accessibilitySettings.highContrast;
        document.body.classList.toggle('high-contrast', this.accessibilitySettings.highContrast);
        
        const button = document.getElementById('toggle-contrast');
        if (button) button.setAttribute('aria-pressed', this.accessibilitySettings.highContrast);
        
        this.announce(this.accessibilitySettings.highContrast ? 'Alto contraste ativado' : 'Alto contraste desativado');
        this.saveSettings();
    }

    toggleReducedMotion() {
        this.accessibilitySettings.reducedMotion = !this.accessibilitySettings.reducedMotion;
        document.body.classList.toggle('reduced-motion', this.accessibilitySettings.reducedMotion);
        
        const button = document.getElementById('toggle-motion');
        if (button) button.setAttribute('aria-pressed', this.accessibilitySettings.reducedMotion);
        
        this.announce(this.accessibilitySettings.reducedMotion ? 'Movimento reduzido ativado' : 'Movimento reduzido desativado');
        this.saveSettings();
    }

    toggleVoiceGuidance() {
        this.accessibilitySettings.voiceGuidance = !this.accessibilitySettings.voiceGuidance;
        
        const button = document.getElementById('toggle-voice');
        if (button) button.setAttribute('aria-pressed', this.accessibilitySettings.voiceGuidance);
        
        if (this.accessibilitySettings.voiceGuidance) {
            // Initialize voice guidance if available
            if (window.voiceAccessibility) {
                window.voiceAccessibility.enable();
            }
            this.announce('Guia de voz ativado');
        } else {
            if (window.voiceAccessibility) {
                window.voiceAccessibility.disable();
            }
            this.announce('Guia de voz desativado');
        }
        
        this.saveSettings();
    }

    highlightFocusableElements() {
        const focusable = document.querySelectorAll(
            'a[href], button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
        );
        
        focusable.forEach((el) => {
            el.classList.add('focus-highlight');
            setTimeout(() => el.classList.remove('focus-highlight'), 3000);
        });
        
        this.announce(`${focusable.length} elementos focáveis destacados por 3 segundos`);
    }

    resetSettings() {
        this.accessibilitySettings = {
            fontSize: 16,
            highContrast: false,
            reducedMotion: false,
            screenReaderMode: false,
            keyboardNavigation: true,
            voiceGuidance: false
        };
        
        this.applySettings();
        this.saveSettings();
        this.announce('Configurações de acessibilidade restauradas ao padrão');
        
        // Update UI
        document.getElementById('font-size-display').textContent = '16px';
        document.getElementById('toggle-contrast').setAttribute('aria-pressed', 'false');
        document.getElementById('toggle-motion').setAttribute('aria-pressed', 'false');
        document.getElementById('toggle-voice').setAttribute('aria-pressed', 'false');
    }

    applySettings() {
        document.documentElement.style.fontSize = `${this.accessibilitySettings.fontSize}px`;
        document.body.classList.toggle('high-contrast', this.accessibilitySettings.highContrast);
        document.body.classList.toggle('reduced-motion', this.accessibilitySettings.reducedMotion);
    }

    announce(message, priority = 'polite') {
        const region = document.getElementById(`aria-live-${priority}`);
        if (region) {
            region.textContent = message;
            
            this.announcements.push({
                message,
                priority,
                timestamp: Date.now()
            });
            
            // Keep only last 5 announcements
            if (this.announcements.length > 5) {
                this.announcements.shift();
            }
        }
        
        if (this.debugMode) {
            console.log(`Accessibility announcement (${priority}):`, message);
        }
    }

    announceElement(element) {
        const tagName = element.tagName.toLowerCase();
        const label = this.getElementLabel(element);
        const role = element.getAttribute('role') || tagName;
        
        let announcement = '';
        
        switch (tagName) {
            case 'button':
                announcement = `Botão ${label}`;
                break;
            case 'a':
                announcement = `Link ${label}`;
                break;
            case 'input':
                const type = element.type || 'text';
                announcement = `Campo ${type} ${label}`;
                break;
            case 'select':
                announcement = `Lista de seleção ${label}`;
                break;
            default:
                announcement = `${role} ${label}`;
        }
        
        this.announce(announcement, 'polite');
    }

    getElementLabel(element) {
        return element.getAttribute('aria-label') ||
               element.getAttribute('title') ||
               element.textContent?.trim() ||
               element.getAttribute('placeholder') ||
               element.getAttribute('name') ||
               'sem nome';
    }

    debugAccessibility() {
        if (!this.debugMode) return;
        
        console.group('Accessibility Debug Information');
        console.log('Settings:', this.accessibilitySettings);
        console.log('Focus History:', this.focusHistory);
        console.log('Recent Announcements:', this.announcements);
        
        // Check for common accessibility issues
        const issues = this.findAccessibilityIssues();
        if (issues.length > 0) {
            console.warn('Accessibility Issues Found:', issues);
        } else {
            console.log('No accessibility issues detected');
        }
        
        console.groupEnd();
    }

    findAccessibilityIssues() {
        const issues = [];
        
        // Check for images without alt text
        const imagesWithoutAlt = document.querySelectorAll('img:not([alt])');
        if (imagesWithoutAlt.length > 0) {
            issues.push(`${imagesWithoutAlt.length} images without alt text`);
        }
        
        // Check for buttons without accessible names
        const unlabeledButtons = document.querySelectorAll('button:not([aria-label]):not([aria-labelledby])');
        const emptyButtons = Array.from(unlabeledButtons).filter(btn => !btn.textContent.trim());
        if (emptyButtons.length > 0) {
            issues.push(`${emptyButtons.length} buttons without accessible names`);
        }
        
        // Check for form inputs without labels
        const unlabeledInputs = document.querySelectorAll('input:not([aria-label]):not([aria-labelledby])');
        const inputsWithoutLabels = Array.from(unlabeledInputs).filter(input => {
            return !document.querySelector(`label[for="${input.id}"]`);
        });
        if (inputsWithoutLabels.length > 0) {
            issues.push(`${inputsWithoutLabels.length} form inputs without labels`);
        }
        
        // Check heading hierarchy
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        if (headings.length === 0) {
            issues.push('No heading elements found');
        }
        
        return issues;
    }

    // Public API for external integration
    getAccessibilityReport() {
        return {
            settings: this.accessibilitySettings,
            focusHistory: this.focusHistory,
            announcements: this.announcements,
            issues: this.findAccessibilityIssues(),
            isInitialized: this.isInitialized
        };
    }
}

// CSS for accessibility controls
const accessibilityCSS = `
.accessibility-controls {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.accessibility-panel {
    position: relative;
}

.accessibility-btn {
    background: #1e40af;
    color: white;
    border: none;
    padding: 12px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
    transition: all 0.2s ease;
    min-width: 44px;
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.accessibility-btn:hover {
    background: #1d4ed8;
    transform: translateY(-2px);
}

.accessibility-btn:focus {
    outline: 3px solid #fbbf24;
    outline-offset: 2px;
}

#accessibility-toggle {
    border-radius: 50%;
    width: 56px;
    height: 56px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.accessibility-options {
    position: absolute;
    top: 70px;
    right: 0;
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px;
    min-width: 280px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    z-index: 10000;
}

.accessibility-options h3 {
    margin: 0 0 16px 0;
    color: #111827;
    font-size: 18px;
    font-weight: 600;
}

.accessibility-group {
    margin-bottom: 16px;
}

.accessibility-group label {
    display: block;
    color: #374151;
    font-weight: 500;
    margin-bottom: 8px;
}

.font-controls {
    display: flex;
    align-items: center;
    gap: 12px;
}

.font-controls .accessibility-btn {
    padding: 8px 12px;
    font-size: 14px;
    min-width: auto;
    min-height: auto;
}

#font-size-display {
    font-weight: 600;
    color: #1f2937;
    min-width: 40px;
    text-align: center;
}

.toggle-btn[aria-pressed="true"] {
    background: #059669;
}

.toggle-btn[aria-pressed="true"]:hover {
    background: #047857;
}

.skip-links {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 10000;
}

.skip-link {
    position: absolute;
    top: -40px;
    left: 6px;
    background: #1e40af;
    color: white;
    padding: 8px 12px;
    text-decoration: none;
    border-radius: 0 0 4px 4px;
    font-weight: 600;
    font-size: 14px;
    transition: top 0.2s ease;
}

.skip-link:focus {
    top: 0;
    outline: 2px solid #fbbf24;
    outline-offset: 2px;
}

.reduced-motion * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
}

@media (max-width: 768px) {
    .accessibility-controls {
        top: 10px;
        right: 10px;
    }
    
    .accessibility-options {
        right: -20px;
        min-width: 260px;
    }
}
`;

// Inject CSS
if (!document.getElementById('accessibility-enhanced-styles')) {
    const style = document.createElement('style');
    style.id = 'accessibility-enhanced-styles';
    style.textContent = accessibilityCSS;
    document.head.appendChild(style);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.enhancedAccessibility = new EnhancedAccessibilityManager();
    });
} else {
    window.enhancedAccessibility = new EnhancedAccessibilityManager();
}

// Debug mode toggle
window.toggleAccessibilityDebug = function() {
    const isDebug = localStorage.getItem('accessibilityDebug') === 'true';
    localStorage.setItem('accessibilityDebug', (!isDebug).toString());
    location.reload();
};