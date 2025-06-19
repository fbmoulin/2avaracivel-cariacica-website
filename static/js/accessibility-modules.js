/**
 * Accessibility Modules - Refined Modular Components
 * 2ª Vara Cível de Cariacica - Specialized accessibility modules
 */

/**
 * Skip Links Module - Automatic skip navigation generation
 */
class SkipLinksModule extends AccessibilityModule {
    async setup() {
        this.skipLinks = [
            { href: '#main-content', text: 'Pular para conteúdo principal' },
            { href: '#main-navigation', text: 'Pular para navegação' },
            { href: '#footer', text: 'Pular para rodapé' },
            { href: '#accessibility-controls', text: 'Pular para controles de acessibilidade' }
        ];
        
        this.createSkipLinks();
        this.ensureTargets();
    }

    createSkipLinks() {
        // Remove existing skip links
        const existing = document.querySelector('.skip-links-container');
        if (existing) existing.remove();

        const container = document.createElement('div');
        container.className = 'skip-links-container';
        container.setAttribute('role', 'navigation');
        container.setAttribute('aria-label', 'Links de navegação rápida');

        this.skipLinks.forEach(link => {
            const skipLink = document.createElement('a');
            skipLink.href = link.href;
            skipLink.className = 'skip-link';
            skipLink.textContent = link.text;
            skipLink.addEventListener('focus', () => this.onSkipLinkFocus(skipLink));
            container.appendChild(skipLink);
        });

        document.body.insertBefore(container, document.body.firstChild);
    }

    ensureTargets() {
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

    onSkipLinkFocus(skipLink) {
        this.core.announce(`Link de navegação: ${skipLink.textContent}`);
    }

    async runDiagnostics() {
        const skipLinksCount = document.querySelectorAll('.skip-link').length;
        const targetsExist = this.skipLinks.every(link => 
            document.querySelector(link.href)
        );

        return {
            ...await super.runDiagnostics(),
            skipLinksCount,
            targetsExist,
            status: skipLinksCount > 0 && targetsExist ? 'ok' : 'warning'
        };
    }
}

/**
 * Keyboard Navigation Module - Enhanced keyboard support
 */
class KeyboardNavigationModule extends AccessibilityModule {
    async setup() {
        this.focusableElements = [];
        this.currentFocusIndex = -1;
        this.focusRing = new Map();
        
        this.updateFocusableElements();
        this.setupFocusTrapping();
    }

    bindEvents() {
        document.addEventListener('keydown', this.handleKeyNavigation.bind(this));
        document.addEventListener('focusin', this.handleFocusIn.bind(this));
        document.addEventListener('focusout', this.handleFocusOut.bind(this));
    }

    updateFocusableElements() {
        this.focusableElements = Array.from(document.querySelectorAll(`
            a[href]:not([disabled]):not([tabindex="-1"]),
            button:not([disabled]):not([tabindex="-1"]),
            textarea:not([disabled]):not([tabindex="-1"]),
            input:not([disabled]):not([tabindex="-1"]),
            select:not([disabled]):not([tabindex="-1"]),
            [tabindex]:not([tabindex="-1"]):not([disabled])
        `)).filter(el => {
            const rect = el.getBoundingClientRect();
            return rect.width > 0 && rect.height > 0 && 
                   window.getComputedStyle(el).visibility !== 'hidden';
        });
    }

    handleKeyNavigation(event) {
        const { key, shiftKey, ctrlKey, altKey } = event;

        // Tab navigation enhancement
        if (key === 'Tab') {
            this.updateFocusableElements();
            setTimeout(() => this.announceFocusedElement(), 50);
        }

        // Arrow key navigation in certain contexts
        if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) {
            this.handleArrowNavigation(event);
        }

        // Escape key handling
        if (key === 'Escape') {
            this.handleEscape(event);
        }
    }

    handleArrowNavigation(event) {
        const activeElement = document.activeElement;
        
        // Navigation in menus, lists, or grids
        if (activeElement.closest('[role="menu"], [role="listbox"], [role="grid"]')) {
            event.preventDefault();
            this.navigateInContainer(activeElement, event.key);
        }
    }

    navigateInContainer(element, direction) {
        const container = element.closest('[role="menu"], [role="listbox"], [role="grid"]');
        const items = Array.from(container.querySelectorAll('[role="menuitem"], [role="option"], [role="gridcell"]'));
        const currentIndex = items.indexOf(element);

        let nextIndex;
        switch (direction) {
            case 'ArrowDown':
            case 'ArrowRight':
                nextIndex = (currentIndex + 1) % items.length;
                break;
            case 'ArrowUp':
            case 'ArrowLeft':
                nextIndex = currentIndex === 0 ? items.length - 1 : currentIndex - 1;
                break;
        }

        if (items[nextIndex]) {
            items[nextIndex].focus();
        }
    }

    handleEscape(event) {
        const activeElement = document.activeElement;
        
        // Close modal or dropdown
        const modal = activeElement.closest('.modal, [role="dialog"]');
        const dropdown = activeElement.closest('.dropdown, [aria-expanded="true"]');
        
        if (modal) {
            this.closeModal(modal);
        } else if (dropdown) {
            this.closeDropdown(dropdown);
        }
    }

    handleFocusIn(event) {
        const element = event.target;
        this.focusRing.set(element, Date.now());
        
        // Announce element if voice guidance is enabled
        if (this.core.getSetting('voice.enabled')) {
            setTimeout(() => this.announceFocusedElement(), 100);
        }
    }

    handleFocusOut(event) {
        // Track focus history for debugging
        this.core.performance.recordInteraction();
    }

    announceFocusedElement() {
        const focused = document.activeElement;
        if (!focused || focused === document.body) return;

        const announcement = this.getElementAnnouncement(focused);
        if (announcement) {
            this.core.announce(announcement, 'polite');
        }
    }

    getElementAnnouncement(element) {
        const tagName = element.tagName.toLowerCase();
        const label = this.getElementLabel(element);
        const role = element.getAttribute('role') || tagName;

        switch (tagName) {
            case 'button':
                return `Botão ${label}`;
            case 'a':
                return `Link ${label}`;
            case 'input':
                const type = element.type || 'text';
                return `Campo ${type} ${label}`;
            case 'select':
                return `Lista de seleção ${label}`;
            case 'textarea':
                return `Área de texto ${label}`;
            default:
                return `${role} ${label}`;
        }
    }

    getElementLabel(element) {
        return element.getAttribute('aria-label') ||
               element.getAttribute('title') ||
               element.textContent?.trim() ||
               element.getAttribute('placeholder') ||
               element.getAttribute('alt') ||
               'sem nome';
    }

    setupFocusTrapping() {
        // Focus trapping for modals
        this.core.on('modal:opened', ({ modal }) => {
            this.trapFocus(modal);
        });
    }

    trapFocus(container) {
        const focusableElements = container.querySelectorAll(`
            a[href], button, textarea, input, select, [tabindex]:not([tabindex="-1"])
        `);
        
        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        const trapHandler = (event) => {
            if (event.key === 'Tab') {
                if (event.shiftKey) {
                    if (document.activeElement === firstElement) {
                        event.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        event.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        };

        container.addEventListener('keydown', trapHandler);
        firstElement.focus();

        // Store handler for cleanup
        container._focusTrapHandler = trapHandler;
    }

    onContentChange() {
        this.updateFocusableElements();
    }

    async runDiagnostics() {
        this.updateFocusableElements();
        
        return {
            ...await super.runDiagnostics(),
            focusableElementsCount: this.focusableElements.length,
            focusHistorySize: this.focusRing.size,
            status: this.focusableElements.length > 0 ? 'ok' : 'warning'
        };
    }
}

/**
 * Focus Manager Module - Enhanced focus indicators and management
 */
class FocusManagerModule extends AccessibilityModule {
    async setup() {
        this.focusHistory = [];
        this.customIndicators = new Map();
        
        this.createFocusStyles();
        this.setupFocusEnhancements();
    }

    createFocusStyles() {
        const focusCSS = `
            .enhanced-focus *:focus-visible {
                outline: ${this.core.getSetting('focus.thickness')}px solid ${this.core.getSetting('focus.color')} !important;
                outline-offset: 2px !important;
                border-radius: 4px !important;
                box-shadow: 0 0 0 ${this.core.getSetting('focus.thickness') + 2}px rgba(30, 64, 175, 0.3) !important;
                position: relative !important;
                z-index: 1000 !important;
            }
            
            .focus-indicator {
                position: absolute;
                pointer-events: none;
                border: 2px dashed #1e40af;
                border-radius: 4px;
                background: rgba(30, 64, 175, 0.1);
                z-index: 999;
                transition: all 0.2s ease;
            }
            
            .focus-debug-mode .focus-indicator {
                border-color: #ef4444;
                background: rgba(239, 68, 68, 0.1);
            }
        `;

        const style = document.createElement('style');
        style.id = 'focus-manager-styles';
        style.textContent = focusCSS;
        document.head.appendChild(style);
    }

    setupFocusEnhancements() {
        document.addEventListener('focusin', this.handleFocusIn.bind(this));
        document.addEventListener('focusout', this.handleFocusOut.bind(this));
    }

    handleFocusIn(event) {
        const element = event.target;
        
        // Record focus history
        this.focusHistory.push({
            element,
            timestamp: Date.now(),
            bounds: element.getBoundingClientRect()
        });

        // Keep only last 20 focus events
        if (this.focusHistory.length > 20) {
            this.focusHistory.shift();
        }

        // Show custom focus indicator if debug mode
        if (this.core.getSetting('debug')) {
            this.showFocusIndicator(element);
        }
    }

    handleFocusOut(event) {
        // Remove custom focus indicator
        this.hideFocusIndicator();
    }

    showFocusIndicator(element) {
        this.hideFocusIndicator();

        const rect = element.getBoundingClientRect();
        const indicator = document.createElement('div');
        indicator.className = 'focus-indicator';
        indicator.style.cssText = `
            top: ${rect.top + window.scrollY - 4}px;
            left: ${rect.left + window.scrollX - 4}px;
            width: ${rect.width + 8}px;
            height: ${rect.height + 8}px;
        `;

        document.body.appendChild(indicator);
        this.currentIndicator = indicator;

        // Auto-remove after 3 seconds
        setTimeout(() => this.hideFocusIndicator(), 3000);
    }

    hideFocusIndicator() {
        if (this.currentIndicator) {
            this.currentIndicator.remove();
            this.currentIndicator = null;
        }
    }

    highlightAllFocusable() {
        const focusableElements = document.querySelectorAll(`
            a[href], button, input, textarea, select, [tabindex]:not([tabindex="-1"])
        `);

        focusableElements.forEach((element, index) => {
            const rect = element.getBoundingClientRect();
            if (rect.width > 0 && rect.height > 0) {
                const indicator = document.createElement('div');
                indicator.className = 'focus-indicator focus-debug-mode';
                indicator.style.cssText = `
                    top: ${rect.top + window.scrollY - 2}px;
                    left: ${rect.left + window.scrollX - 2}px;
                    width: ${rect.width + 4}px;
                    height: ${rect.height + 4}px;
                `;
                
                // Add index number
                const indexLabel = document.createElement('span');
                indexLabel.textContent = index + 1;
                indexLabel.style.cssText = `
                    position: absolute;
                    top: -10px;
                    left: -10px;
                    background: #ef4444;
                    color: white;
                    padding: 2px 6px;
                    border-radius: 12px;
                    font-size: 11px;
                    font-weight: bold;
                `;
                indicator.appendChild(indexLabel);

                document.body.appendChild(indicator);
                
                // Auto-remove after 5 seconds
                setTimeout(() => indicator.remove(), 5000);
            }
        });

        this.core.announce(`${focusableElements.length} elementos focáveis destacados`);
    }

    async runDiagnostics() {
        const focusableCount = document.querySelectorAll(`
            a[href], button, input, textarea, select, [tabindex]:not([tabindex="-1"])
        `).length;

        return {
            ...await super.runDiagnostics(),
            focusableElementsCount: focusableCount,
            focusHistoryLength: this.focusHistory.length,
            customIndicatorsActive: this.customIndicators.size,
            status: focusableCount > 0 ? 'ok' : 'warning'
        };
    }
}

/**
 * Screen Reader Module - Enhanced screen reader support
 */
class ScreenReaderModule extends AccessibilityModule {
    async setup() {
        this.announcements = [];
        this.liveRegions = new Map();
        
        this.createLiveRegions();
        this.enhanceSemantics();
    }

    createLiveRegions() {
        const regions = [
            { id: 'aria-live-polite', level: 'polite' },
            { id: 'aria-live-assertive', level: 'assertive' },
            { id: 'aria-live-status', level: 'polite', role: 'status' }
        ];

        regions.forEach(({ id, level, role }) => {
            let region = document.getElementById(id);
            if (!region) {
                region = document.createElement('div');
                region.id = id;
                region.setAttribute('aria-live', level);
                region.setAttribute('aria-atomic', 'true');
                if (role) region.setAttribute('role', role);
                region.className = 'sr-only';
                document.body.appendChild(region);
            }
            this.liveRegions.set(level, region);
        });
    }

    announce(message, priority = 'polite') {
        if (!message || typeof message !== 'string') return;

        const region = this.liveRegions.get(priority);
        if (region) {
            // Clear previous message
            region.textContent = '';
            
            // Set new message with slight delay for screen readers
            setTimeout(() => {
                region.textContent = message;
            }, 10);

            // Record announcement
            this.announcements.push({
                message,
                priority,
                timestamp: Date.now()
            });

            // Keep only last 10 announcements
            if (this.announcements.length > 10) {
                this.announcements.shift();
            }

            this.core.performance.recordAnnouncement();
        }
    }

    enhanceSemantics() {
        // Add missing ARIA labels
        this.addMissingLabels();
        
        // Enhance form associations
        this.enhanceFormLabels();
        
        // Add landmark roles where missing
        this.addLandmarkRoles();
        
        // Enhance image descriptions
        this.enhanceImageDescriptions();
    }

    addMissingLabels() {
        const unlabeledButtons = document.querySelectorAll(`
            button:not([aria-label]):not([aria-labelledby])
        `);

        unlabeledButtons.forEach((button, index) => {
            if (!button.textContent.trim()) {
                const iconClass = button.querySelector('i')?.className || '';
                let label = this.inferButtonLabel(iconClass, button);
                
                if (!label) {
                    label = `Botão ${index + 1}`;
                }
                
                button.setAttribute('aria-label', label);
            }
        });
    }

    inferButtonLabel(iconClass, button) {
        const iconMap = {
            'search': 'Buscar',
            'close': 'Fechar',
            'menu': 'Menu',
            'home': 'Início',
            'user': 'Usuário',
            'settings': 'Configurações',
            'edit': 'Editar',
            'delete': 'Excluir',
            'save': 'Salvar',
            'cancel': 'Cancelar',
            'submit': 'Enviar',
            'print': 'Imprimir',
            'download': 'Baixar',
            'upload': 'Enviar arquivo'
        };

        for (const [keyword, label] of Object.entries(iconMap)) {
            if (iconClass.includes(keyword)) {
                return label;
            }
        }

        // Check button context
        const form = button.closest('form');
        if (form) {
            if (button.type === 'submit') return 'Enviar formulário';
            if (button.type === 'reset') return 'Limpar formulário';
        }

        return null;
    }

    enhanceFormLabels() {
        const inputs = document.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            if (!this.hasAccessibleLabel(input)) {
                const label = this.findAssociatedLabel(input);
                if (label) {
                    input.setAttribute('aria-label', label);
                }
            }

            // Add required field announcements
            if (input.hasAttribute('required')) {
                const currentLabel = this.getAccessibleLabel(input);
                if (currentLabel && !currentLabel.includes('obrigatório')) {
                    input.setAttribute('aria-label', `${currentLabel} (obrigatório)`);
                }
            }
        });
    }

    hasAccessibleLabel(element) {
        return element.getAttribute('aria-label') ||
               element.getAttribute('aria-labelledby') ||
               document.querySelector(`label[for="${element.id}"]`) ||
               element.closest('label');
    }

    findAssociatedLabel(input) {
        // Check for explicit label
        if (input.id) {
            const label = document.querySelector(`label[for="${input.id}"]`);
            if (label) return label.textContent.trim();
        }

        // Check for implicit label (wrapped)
        const parentLabel = input.closest('label');
        if (parentLabel) {
            return parentLabel.textContent.replace(input.value, '').trim();
        }

        // Check previous sibling
        const prevElement = input.previousElementSibling;
        if (prevElement && ['LABEL', 'SPAN', 'DIV'].includes(prevElement.tagName)) {
            const text = prevElement.textContent.trim();
            if (text && text.length < 100) return text;
        }

        // Check placeholder as last resort
        return input.getAttribute('placeholder') || input.getAttribute('name') || null;
    }

    getAccessibleLabel(element) {
        return element.getAttribute('aria-label') ||
               element.getAttribute('title') ||
               element.textContent?.trim() ||
               this.findAssociatedLabel(element) ||
               'sem nome';
    }

    addLandmarkRoles() {
        const landmarks = [
            { selector: 'header:not([role])', role: 'banner' },
            { selector: 'nav:not([role])', role: 'navigation' },
            { selector: 'main:not([role])', role: 'main' },
            { selector: 'aside:not([role])', role: 'complementary' },
            { selector: 'footer:not([role])', role: 'contentinfo' }
        ];

        landmarks.forEach(({ selector, role }) => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                element.setAttribute('role', role);
            });
        });
    }

    enhanceImageDescriptions() {
        const images = document.querySelectorAll('img:not([alt])');
        
        images.forEach((img, index) => {
            const src = img.src || '';
            let alt = '';
            
            // Infer alt text from filename or context
            if (src.includes('logo')) {
                alt = 'Logo';
            } else if (src.includes('banner')) {
                alt = 'Banner';
            } else if (src.includes('icon')) {
                alt = 'Ícone';
            } else if (src.includes('avatar')) {
                alt = 'Avatar do usuário';
            } else {
                const filename = src.split('/').pop().split('.')[0];
                alt = filename.replace(/[-_]/g, ' ') || `Imagem ${index + 1}`;
            }
            
            img.setAttribute('alt', alt);
        });
    }

    onContentChange() {
        // Re-enhance semantics for new content
        setTimeout(() => this.enhanceSemantics(), 100);
    }

    async runDiagnostics() {
        const ariaElements = document.querySelectorAll('[aria-label], [aria-labelledby], [aria-describedby]');
        const liveRegions = document.querySelectorAll('[aria-live]');
        const unlabeledImages = document.querySelectorAll('img:not([alt])');
        const unlabeledButtons = document.querySelectorAll('button:not([aria-label]):not([aria-labelledby])');

        return {
            ...await super.runDiagnostics(),
            ariaElementsCount: ariaElements.length,
            liveRegionsCount: liveRegions.length,
            unlabeledImagesCount: unlabeledImages.length,
            unlabeledButtonsCount: unlabeledButtons.length,
            announcementsCount: this.announcements.length,
            status: unlabeledImages.length === 0 && unlabeledButtons.length < 5 ? 'ok' : 'warning'
        };
    }
}

// Export modules
window.SkipLinksModule = SkipLinksModule;
window.KeyboardNavigationModule = KeyboardNavigationModule;
window.FocusManagerModule = FocusManagerModule;
window.ScreenReaderModule = ScreenReaderModule;