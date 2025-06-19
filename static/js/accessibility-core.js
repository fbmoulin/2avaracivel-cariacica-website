/**
 * Accessibility Core System - Refined and Refactored
 * 2ª Vara Cível de Cariacica - Optimized accessibility framework
 */

class AccessibilityCore {
    constructor() {
        this.version = '2.1.0';
        this.initialized = false;
        this.modules = new Map();
        this.config = this.getDefaultConfig();
        this.eventBus = new EventTarget();
        this.performance = new AccessibilityPerformanceMonitor();
        
        this.init();
    }

    getDefaultConfig() {
        return {
            fontSize: {
                min: 12,
                max: 32,
                default: 16,
                step: 2
            },
            contrast: {
                enabled: false,
                mode: 'high'
            },
            motion: {
                reduced: false
            },
            focus: {
                enhanced: true,
                thickness: 3,
                color: '#1e40af'
            },
            voice: {
                enabled: false,
                rate: 1.0,
                volume: 0.8
            },
            keyboard: {
                shortcuts: true,
                navigation: true
            },
            debug: false
        };
    }

    async init() {
        if (this.initialized) return;

        try {
            this.performance.startTimer('initialization');
            
            await this.loadSettings();
            await this.initializeModules();
            await this.setupEventHandlers();
            await this.applySettings();
            
            this.initialized = true;
            this.performance.endTimer('initialization');
            
            this.emit('accessibility:ready', {
                version: this.version,
                modules: Array.from(this.modules.keys()),
                performance: this.performance.getMetrics()
            });

            if (this.config.debug) {
                console.log('Accessibility Core initialized', {
                    version: this.version,
                    modules: this.modules.size,
                    loadTime: this.performance.getTimer('initialization')
                });
            }
        } catch (error) {
            console.error('Accessibility Core initialization failed:', error);
            this.emit('accessibility:error', { error, phase: 'initialization' });
        }
    }

    async initializeModules() {
        const moduleConfigs = [
            { name: 'skipLinks', class: SkipLinksModule, priority: 1 },
            { name: 'keyboardNav', class: KeyboardNavigationModule, priority: 1 },
            { name: 'focusManager', class: FocusManagerModule, priority: 2 },
            { name: 'screenReader', class: ScreenReaderModule, priority: 2 },
            { name: 'visualControls', class: VisualControlsModule, priority: 3 },
            { name: 'formEnhancer', class: FormEnhancerModule, priority: 3 },
            { name: 'colorContrast', class: ColorContrastModule, priority: 4 },
            { name: 'mediaAccessibility', class: MediaAccessibilityModule, priority: 4 },
            { name: 'userInterface', class: AccessibilityUIModule, priority: 5 }
        ];

        // Sort by priority and initialize
        moduleConfigs.sort((a, b) => a.priority - b.priority);

        for (const moduleConfig of moduleConfigs) {
            try {
                this.performance.startTimer(`module:${moduleConfig.name}`);
                
                const module = new moduleConfig.class(this);
                await module.initialize();
                
                this.modules.set(moduleConfig.name, module);
                this.performance.endTimer(`module:${moduleConfig.name}`);
                
                if (this.config.debug) {
                    console.log(`Module ${moduleConfig.name} initialized`);
                }
            } catch (error) {
                console.error(`Failed to initialize module ${moduleConfig.name}:`, error);
                this.emit('accessibility:moduleError', { 
                    module: moduleConfig.name, 
                    error 
                });
            }
        }
    }

    setupEventHandlers() {
        // Global keyboard shortcuts
        document.addEventListener('keydown', this.handleGlobalKeyboard.bind(this), { passive: false });
        
        // Page navigation events
        window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
        window.addEventListener('focus', this.handleWindowFocus.bind(this));
        window.addEventListener('blur', this.handleWindowBlur.bind(this));

        // Visibility API for performance optimization
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));

        // Mutation observer for dynamic content
        this.setupMutationObserver();
    }

    setupMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            const significantChanges = mutations.some(mutation => 
                mutation.type === 'childList' && 
                Array.from(mutation.addedNodes).some(node => 
                    node.nodeType === Node.ELEMENT_NODE &&
                    (node.matches('form, input, button, a[href], img') ||
                     node.querySelector('form, input, button, a[href], img'))
                )
            );

            if (significantChanges) {
                this.debounce(() => this.handleContentChange(), 300);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: false
        });

        this.mutationObserver = observer;
    }

    handleGlobalKeyboard(event) {
        if (!this.config.keyboard.shortcuts) return;

        const { altKey, ctrlKey, shiftKey, key } = event;

        // Alt + A: Toggle accessibility panel
        if (altKey && key === 'a') {
            event.preventDefault();
            this.toggleAccessibilityPanel();
            return;
        }

        // Alt + M: Focus main content
        if (altKey && key === 'm') {
            event.preventDefault();
            this.focusMainContent();
            return;
        }

        // Alt + N: Focus navigation
        if (altKey && key === 'n') {
            event.preventDefault();
            this.focusNavigation();
            return;
        }

        // Ctrl + Alt + D: Toggle debug mode
        if (ctrlKey && altKey && key === 'd') {
            event.preventDefault();
            this.toggleDebugMode();
            return;
        }

        // Ctrl + Alt + R: Generate accessibility report
        if (ctrlKey && altKey && key === 'r') {
            event.preventDefault();
            this.generateAccessibilityReport();
            return;
        }

        // Pass to modules
        this.emit('accessibility:keydown', { event });
    }

    handleContentChange() {
        this.emit('accessibility:contentChanged');
        this.modules.forEach(module => {
            if (module.onContentChange) {
                module.onContentChange();
            }
        });
    }

    handleVisibilityChange() {
        const isVisible = !document.hidden;
        this.emit('accessibility:visibilityChange', { visible: isVisible });
        
        if (isVisible) {
            this.performance.resume();
        } else {
            this.performance.pause();
        }
    }

    // Settings management
    async loadSettings() {
        try {
            const stored = localStorage.getItem('accessibility-core-settings');
            if (stored) {
                const settings = JSON.parse(stored);
                this.config = { ...this.config, ...settings };
            }
        } catch (error) {
            console.warn('Failed to load accessibility settings:', error);
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('accessibility-core-settings', JSON.stringify(this.config));
            this.emit('accessibility:settingsSaved', { config: this.config });
        } catch (error) {
            console.error('Failed to save accessibility settings:', error);
            this.emit('accessibility:settingsError', { error });
        }
    }

    async applySettings() {
        // Apply font size
        if (this.config.fontSize.current) {
            document.documentElement.style.fontSize = `${this.config.fontSize.current}px`;
        }

        // Apply contrast mode
        document.body.classList.toggle('high-contrast', this.config.contrast.enabled);

        // Apply reduced motion
        document.body.classList.toggle('reduced-motion', this.config.motion.reduced);

        // Notify modules
        this.emit('accessibility:settingsApplied', { config: this.config });
    }

    // Public API methods
    updateSetting(path, value) {
        const keys = path.split('.');
        let current = this.config;
        
        for (let i = 0; i < keys.length - 1; i++) {
            if (!current[keys[i]]) current[keys[i]] = {};
            current = current[keys[i]];
        }
        
        current[keys[keys.length - 1]] = value;
        this.saveSettings();
        this.applySettings();
        
        this.emit('accessibility:settingChanged', { path, value });
    }

    getSetting(path) {
        const keys = path.split('.');
        let current = this.config;
        
        for (const key of keys) {
            if (current && typeof current === 'object') {
                current = current[key];
            } else {
                return undefined;
            }
        }
        
        return current;
    }

    adjustFontSize(delta) {
        const current = this.getSetting('fontSize.current') || this.config.fontSize.default;
        const newSize = Math.max(
            this.config.fontSize.min,
            Math.min(this.config.fontSize.max, current + delta)
        );
        
        this.updateSetting('fontSize.current', newSize);
        this.announce(`Tamanho da fonte alterado para ${newSize} pixels`);
    }

    toggleHighContrast() {
        const enabled = !this.getSetting('contrast.enabled');
        this.updateSetting('contrast.enabled', enabled);
        this.announce(enabled ? 'Alto contraste ativado' : 'Alto contraste desativado');
    }

    toggleReducedMotion() {
        const enabled = !this.getSetting('motion.reduced');
        this.updateSetting('motion.reduced', enabled);
        this.announce(enabled ? 'Movimento reduzido ativado' : 'Movimento reduzido desativado');
    }

    // Navigation helpers
    focusMainContent() {
        const main = document.querySelector('main, #main-content, .main-content');
        if (main) {
            main.focus();
            this.announce('Focando no conteúdo principal');
        }
    }

    focusNavigation() {
        const nav = document.querySelector('nav, #main-navigation, .navigation');
        if (nav) {
            nav.focus();
            this.announce('Focando na navegação');
        }
    }

    toggleAccessibilityPanel() {
        const uiModule = this.modules.get('userInterface');
        if (uiModule) {
            uiModule.togglePanel();
        }
    }

    toggleDebugMode() {
        this.updateSetting('debug', !this.config.debug);
        this.emit('accessibility:debugToggled', { enabled: this.config.debug });
    }

    // Announcement system
    announce(message, priority = 'polite') {
        const screenReaderModule = this.modules.get('screenReader');
        if (screenReaderModule) {
            screenReaderModule.announce(message, priority);
        }
    }

    // Event system
    on(event, callback) {
        this.eventBus.addEventListener(event, callback);
    }

    off(event, callback) {
        this.eventBus.removeEventListener(event, callback);
    }

    emit(event, data = {}) {
        this.eventBus.dispatchEvent(new CustomEvent(event, { detail: data }));
    }

    // Utility methods
    debounce(func, wait) {
        if (this.debounceTimer) clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(func, wait);
    }

    throttle(func, limit) {
        if (this.throttleTimer) return;
        this.throttleTimer = setTimeout(() => {
            func();
            this.throttleTimer = null;
        }, limit);
    }

    // Performance and diagnostics
    getStatus() {
        return {
            version: this.version,
            initialized: this.initialized,
            modules: Array.from(this.modules.keys()),
            config: this.config,
            performance: this.performance.getMetrics()
        };
    }

    async runDiagnostics() {
        const diagnostics = {
            timestamp: new Date().toISOString(),
            status: this.getStatus(),
            tests: {}
        };

        for (const [name, module] of this.modules) {
            if (module.runDiagnostics) {
                try {
                    diagnostics.tests[name] = await module.runDiagnostics();
                } catch (error) {
                    diagnostics.tests[name] = { error: error.message };
                }
            }
        }

        return diagnostics;
    }

    generateAccessibilityReport() {
        this.runDiagnostics().then(report => {
            this.emit('accessibility:reportGenerated', { report });
            
            // Download report as JSON
            const blob = new Blob([JSON.stringify(report, null, 2)], { 
                type: 'application/json' 
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `accessibility-report-${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
        });
    }

    // Cleanup
    destroy() {
        if (this.mutationObserver) {
            this.mutationObserver.disconnect();
        }

        this.modules.forEach(module => {
            if (module.destroy) {
                module.destroy();
            }
        });

        this.modules.clear();
        this.performance.stop();
        this.initialized = false;

        this.emit('accessibility:destroyed');
    }
}

/**
 * Performance monitoring for accessibility features
 */
class AccessibilityPerformanceMonitor {
    constructor() {
        this.timers = new Map();
        this.metrics = {
            startTime: performance.now(),
            interactions: 0,
            announcements: 0,
            errors: 0
        };
        this.active = true;
    }

    startTimer(name) {
        if (!this.active) return;
        this.timers.set(name, performance.now());
    }

    endTimer(name) {
        if (!this.active) return;
        const startTime = this.timers.get(name);
        if (startTime) {
            const duration = performance.now() - startTime;
            this.timers.delete(name);
            return duration;
        }
        return 0;
    }

    getTimer(name) {
        const startTime = this.timers.get(name);
        return startTime ? performance.now() - startTime : 0;
    }

    recordInteraction() {
        if (this.active) this.metrics.interactions++;
    }

    recordAnnouncement() {
        if (this.active) this.metrics.announcements++;
    }

    recordError() {
        if (this.active) this.metrics.errors++;
    }

    getMetrics() {
        return {
            ...this.metrics,
            uptime: performance.now() - this.metrics.startTime,
            activeTimers: this.timers.size
        };
    }

    pause() {
        this.active = false;
    }

    resume() {
        this.active = true;
    }

    stop() {
        this.active = false;
        this.timers.clear();
    }
}

/**
 * Base class for accessibility modules
 */
class AccessibilityModule {
    constructor(core) {
        this.core = core;
        this.name = this.constructor.name;
        this.initialized = false;
    }

    async initialize() {
        if (this.initialized) return;
        
        try {
            await this.setup();
            this.bindEvents();
            this.initialized = true;
            
            this.core.emit(`module:${this.name}:ready`);
        } catch (error) {
            this.core.emit(`module:${this.name}:error`, { error });
            throw error;
        }
    }

    async setup() {
        // Override in subclasses
    }

    bindEvents() {
        // Override in subclasses
    }

    onContentChange() {
        // Override in subclasses
    }

    async runDiagnostics() {
        return {
            name: this.name,
            initialized: this.initialized,
            status: 'ok'
        };
    }

    destroy() {
        this.initialized = false;
    }
}

// Export for global use
window.AccessibilityCore = AccessibilityCore;
window.AccessibilityModule = AccessibilityModule;

// Auto-initialize if not in module environment
if (typeof module === 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.accessibilityCore = new AccessibilityCore();
        });
    } else {
        window.accessibilityCore = new AccessibilityCore();
    }
}