/**
 * Accessibility Integration System - Final Integration
 * 2ª Vara Cível de Cariacica - Complete system integration and initialization
 */

/**
 * Main Integration Manager - Orchestrates all accessibility components
 */
class AccessibilityIntegration {
    constructor() {
        this.version = '2.1.0';
        this.loadOrder = [
            'accessibility-core.js',
            'accessibility-modules.js', 
            'accessibility-ui.js',
            'accessibility-ui-complete.js'
        ];
        
        this.core = null;
        this.initialized = false;
        this.loadStartTime = performance.now();
        
        this.init();
    }

    async init() {
        try {
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }

            // Initialize core system
            await this.initializeCore();
            
            // Setup global accessibility API
            this.setupGlobalAPI();
            
            // Apply legacy compatibility
            this.setupLegacyCompatibility();
            
            // Final setup
            this.finalizeIntegration();
            
            this.initialized = true;
            this.logInitialization();
            
        } catch (error) {
            console.error('Accessibility Integration failed:', error);
            this.fallbackToBasicAccessibility();
        }
    }

    async initializeCore() {
        // Initialize core if available
        if (window.AccessibilityCore) {
            this.core = new window.AccessibilityCore();
            
            // Wait for core to be ready
            await new Promise(resolve => {
                if (this.core.initialized) {
                    resolve();
                } else {
                    this.core.on('accessibility:ready', resolve);
                }
            });
            
            console.log('Accessibility Core v2.1.0 initialized successfully');
        } else if (window.enhancedAccessibility) {
            // Fallback to enhanced system
            this.core = window.enhancedAccessibility;
            console.log('Fallback to Enhanced Accessibility Manager');
        } else {
            throw new Error('No accessibility core system available');
        }
    }

    setupGlobalAPI() {
        // Create unified global API
        window.accessibility = {
            version: this.version,
            
            // Core methods
            adjustFontSize: (delta) => this.core?.adjustFontSize?.(delta),
            toggleHighContrast: () => this.core?.toggleHighContrast?.(),
            toggleReducedMotion: () => this.core?.toggleReducedMotion?.(),
            announce: (message, priority) => this.core?.announce?.(message, priority),
            
            // Panel controls
            showPanel: () => this.core?.modules?.get('userInterface')?.showPanel?.(),
            hidePanel: () => this.core?.modules?.get('userInterface')?.hidePanel?.(),
            togglePanel: () => this.core?.modules?.get('userInterface')?.togglePanel?.(),
            
            // Settings
            getSetting: (path) => this.core?.getSetting?.(path),
            updateSetting: (path, value) => this.core?.updateSetting?.(path, value),
            resetSettings: () => this.core?.resetAllSettings?.(),
            exportSettings: () => this.core?.generateAccessibilityReport?.(),
            
            // Testing and diagnostics
            runTests: () => this.core?.runDiagnostics?.(),
            getStatus: () => this.core?.getStatus?.(),
            
            // Module access
            getModule: (name) => this.core?.modules?.get(name),
            
            // Event handling
            on: (event, callback) => this.core?.on?.(event, callback),
            off: (event, callback) => this.core?.off?.(event, callback),
            
            // Utility methods
            highlightFocusable: () => this.core?.modules?.get('focusManager')?.highlightAllFocusable?.(),
            showSkipLinks: () => this.core?.modules?.get('userInterface')?.showSkipLinks?.(),
            
            // Legacy compatibility
            increaseFontSize: () => this.adjustFontSize(2),
            decreaseFontSize: () => this.adjustFontSize(-2),
            toggleContrast: () => this.toggleHighContrast(),
            
            // System info
            isInitialized: () => this.initialized,
            getCore: () => this.core
        };

        // Add convenience methods
        window.a11y = window.accessibility; // Shorthand alias
        
        // jQuery-style chaining for settings
        window.accessibility.config = function(settings) {
            if (typeof settings === 'object') {
                Object.entries(settings).forEach(([key, value]) => {
                    window.accessibility.updateSetting(key, value);
                });
                return window.accessibility;
            }
            return window.accessibility.getStatus();
        };
    }

    setupLegacyCompatibility() {
        // Ensure legacy functions still work
        if (!window.increaseFontSize) {
            window.increaseFontSize = () => window.accessibility.adjustFontSize(2);
        }
        
        if (!window.decreaseFontSize) {
            window.decreaseFontSize = () => window.accessibility.adjustFontSize(-2);
        }
        
        if (!window.toggleHighContrast) {
            window.toggleHighContrast = () => window.accessibility.toggleHighContrast();
        }
        
        if (!window.announceToScreenReader) {
            window.announceToScreenReader = (message, priority) => 
                window.accessibility.announce(message, priority);
        }

        // Maintain compatibility with enhanced accessibility manager
        if (window.enhancedAccessibility && !this.core.modules) {
            // Bridge enhanced manager to new API
            const enhanced = window.enhancedAccessibility;
            
            window.accessibility.adjustFontSize = (delta) => {
                if (enhanced.adjustFontSize) {
                    enhanced.adjustFontSize(delta);
                }
            };
            
            window.accessibility.toggleHighContrast = () => {
                if (enhanced.toggleHighContrast) {
                    enhanced.toggleHighContrast();
                }
            };
            
            window.accessibility.announce = (message, priority) => {
                if (enhanced.announce) {
                    enhanced.announce(message, priority);
                }
            };
        }
    }

    finalizeIntegration() {
        // Add integration CSS if not already present
        this.injectIntegrationStyles();
        
        // Setup performance monitoring
        this.setupPerformanceMonitoring();
        
        // Add keyboard shortcuts
        this.setupGlobalKeyboardShortcuts();
        
        // Setup automatic enhancement
        this.setupAutomaticEnhancement();
        
        // Emit integration ready event
        document.dispatchEvent(new CustomEvent('accessibility:integration:ready', {
            detail: {
                version: this.version,
                core: this.core,
                loadTime: performance.now() - this.loadStartTime
            }
        }));
    }

    injectIntegrationStyles() {
        if (document.getElementById('accessibility-integration-styles')) return;
        
        const integrationCSS = `
            /* Integration-specific styles */
            .accessibility-integration-ready {
                --accessibility-system: active;
            }
            
            .accessibility-loading {
                pointer-events: none;
                opacity: 0.7;
            }
            
            .accessibility-error {
                border: 2px solid #ef4444 !important;
                background: #fef2f2 !important;
            }
            
            .accessibility-success {
                border: 2px solid #10b981 !important;
                background: #ecfdf5 !important;
            }
            
            /* Animation for system ready */
            @keyframes accessibilityReady {
                from { opacity: 0; transform: scale(0.95); }
                to { opacity: 1; transform: scale(1); }
            }
            
            .accessibility-integration-ready .accessibility-floating-toggle {
                animation: accessibilityReady 0.3s ease-out;
            }
        `;
        
        const style = document.createElement('style');
        style.id = 'accessibility-integration-styles';
        style.textContent = integrationCSS;
        document.head.appendChild(style);
        
        // Mark document as integration ready
        document.documentElement.classList.add('accessibility-integration-ready');
    }

    setupPerformanceMonitoring() {
        if (!this.core?.performance) return;
        
        // Monitor page load impact
        const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach(entry => {
                if (entry.name.includes('accessibility')) {
                    console.debug(`Accessibility resource: ${entry.name} - ${entry.duration.toFixed(2)}ms`);
                }
            });
        });
        
        try {
            observer.observe({ entryTypes: ['resource', 'measure'] });
        } catch (e) {
            // PerformanceObserver not supported
            console.debug('Performance monitoring not available');
        }
        
        // Track accessibility interactions
        let interactionCount = 0;
        document.addEventListener('click', (e) => {
            if (e.target.closest('.accessibility-floating-toggle, .accessibility-panel')) {
                interactionCount++;
                if (this.core?.performance?.recordInteraction) {
                    this.core.performance.recordInteraction();
                }
            }
        });
        
        // Report performance metrics periodically
        setInterval(() => {
            if (this.core?.getStatus) {
                const status = this.core.getStatus();
                console.debug('Accessibility Performance:', {
                    interactions: interactionCount,
                    modules: status.modules?.length || 0,
                    performance: status.performance
                });
            }
        }, 300000); // Every 5 minutes
    }

    setupGlobalKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Don't interfere with form inputs
            if (e.target.matches('input, textarea, select')) return;
            
            const { altKey, ctrlKey, shiftKey, key } = e;
            
            // Global accessibility shortcuts
            if (altKey && ctrlKey) {
                switch (key.toLowerCase()) {
                    case 'a':
                        e.preventDefault();
                        window.accessibility?.togglePanel?.();
                        break;
                    case '+':
                    case '=':
                        e.preventDefault();
                        window.accessibility?.adjustFontSize?.(2);
                        break;
                    case '-':
                        e.preventDefault();
                        window.accessibility?.adjustFontSize?.(-2);
                        break;
                    case 'c':
                        e.preventDefault();
                        window.accessibility?.toggleHighContrast?.();
                        break;
                    case 'r':
                        e.preventDefault();
                        window.accessibility?.toggleReducedMotion?.();
                        break;
                    case 't':
                        e.preventDefault();
                        window.accessibility?.runTests?.();
                        break;
                    case 'h':
                        e.preventDefault();
                        window.accessibility?.highlightFocusable?.();
                        break;
                }
            }
        });
        
        // Announce keyboard shortcuts on first Alt press
        let altAnnounced = false;
        document.addEventListener('keydown', (e) => {
            if (e.altKey && !altAnnounced) {
                altAnnounced = true;
                setTimeout(() => {
                    window.accessibility?.announce?.(
                        'Atalhos de acessibilidade disponíveis. Pressione Ctrl+Alt+A para abrir o painel.',
                        'polite'
                    );
                }, 1000);
            }
        });
    }

    setupAutomaticEnhancement() {
        // Automatically enhance new content
        const enhanceContent = () => {
            if (this.core?.modules) {
                // Trigger content change event for all modules
                this.core.emit('accessibility:contentChanged');
            }
        };
        
        // Monitor for dynamic content changes
        const observer = new MutationObserver((mutations) => {
            let shouldEnhance = false;
            
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Check for significant content additions
                            if (node.matches('form, img, input, button, a[href], video, audio') ||
                                node.querySelector('form, img, input, button, a[href], video, audio')) {
                                shouldEnhance = true;
                            }
                        }
                    });
                }
            });
            
            if (shouldEnhance) {
                // Debounce enhancement
                clearTimeout(this.enhanceTimeout);
                this.enhanceTimeout = setTimeout(enhanceContent, 300);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Store observer for cleanup
        this.contentObserver = observer;
    }

    fallbackToBasicAccessibility() {
        console.warn('Falling back to basic accessibility features');
        
        // Create minimal accessibility support
        window.accessibility = {
            version: 'fallback-1.0.0',
            adjustFontSize: (delta) => {
                const current = parseInt(document.documentElement.style.fontSize) || 16;
                const newSize = Math.max(12, Math.min(32, current + delta));
                document.documentElement.style.fontSize = `${newSize}px`;
            },
            toggleHighContrast: () => {
                document.body.classList.toggle('high-contrast');
            },
            announce: (message) => {
                console.log('Accessibility announcement:', message);
            },
            isInitialized: () => false
        };
        
        // Basic high contrast CSS
        const basicCSS = `
            .high-contrast * {
                background: white !important;
                color: black !important;
                border-color: black !important;
            }
            .high-contrast a, .high-contrast button {
                background: black !important;
                color: white !important;
            }
        `;
        
        const style = document.createElement('style');
        style.textContent = basicCSS;
        document.head.appendChild(style);
    }

    logInitialization() {
        const loadTime = performance.now() - this.loadStartTime;
        const moduleCount = this.core?.modules?.size || 0;
        
        console.group(`🔥 Accessibility Integration v${this.version}`);
        console.log(`✓ Initialized in ${loadTime.toFixed(2)}ms`);
        console.log(`✓ ${moduleCount} modules loaded`);
        console.log(`✓ Core system: ${this.core?.constructor?.name || 'fallback'}`);
        console.log(`✓ Global API available at window.accessibility`);
        console.log(`✓ Keyboard shortcuts enabled (Ctrl+Alt+A to open panel)`);
        console.groupEnd();
        
        // Announce to screen readers
        setTimeout(() => {
            window.accessibility?.announce?.(
                'Sistema de acessibilidade carregado e pronto para uso',
                'polite'
            );
        }, 1000);
    }

    // Public methods for external integration
    getIntegrationStatus() {
        return {
            version: this.version,
            initialized: this.initialized,
            core: this.core?.constructor?.name || 'none',
            modules: this.core?.modules?.size || 0,
            loadTime: performance.now() - this.loadStartTime
        };
    }

    destroy() {
        if (this.contentObserver) {
            this.contentObserver.disconnect();
        }
        
        if (this.core?.destroy) {
            this.core.destroy();
        }
        
        // Clean up global API
        delete window.accessibility;
        delete window.a11y;
        
        document.documentElement.classList.remove('accessibility-integration-ready');
        
        this.initialized = false;
    }
}

// Initialize integration when script loads
const accessibilityIntegration = new AccessibilityIntegration();

// Export for global access
window.accessibilityIntegration = accessibilityIntegration;

// Backwards compatibility exports
window.AccessibilityIntegration = AccessibilityIntegration;