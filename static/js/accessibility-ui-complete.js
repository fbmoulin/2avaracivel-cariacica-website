/**
 * Accessibility UI Complete Module - Final UI Component
 * 2ª Vara Cível de Cariacica - Complete accessibility user interface system
 */

/**
 * Accessibility UI Module - Main user interface component
 */
class AccessibilityUIModule extends AccessibilityModule {
    async setup() {
        this.panelVisible = false;
        this.compactMode = window.innerWidth < 768;
        
        this.createMainPanel();
        this.createFloatingToggle();
        this.setupResponsiveHandling();
    }

    bindEvents() {
        // Listen for core events
        this.core.on('accessibility:settingChanged', this.updateUI.bind(this));
        this.core.on('accessibility:ready', this.onCoreReady.bind(this));
        
        // Window resize handling
        window.addEventListener('resize', this.handleResize.bind(this));
        
        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
    }

    createMainPanel() {
        const panel = document.createElement('div');
        panel.id = 'accessibility-main-panel';
        panel.className = 'accessibility-panel';
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-labelledby', 'accessibility-panel-title');
        panel.setAttribute('aria-hidden', 'true');
        
        panel.innerHTML = `
            <div class="accessibility-panel-header">
                <h2 id="accessibility-panel-title">
                    <i class="fas fa-universal-access" aria-hidden="true"></i>
                    Opções de Acessibilidade
                </h2>
                <button id="accessibility-panel-close" class="panel-close-btn" aria-label="Fechar painel de acessibilidade">
                    <i class="fas fa-times" aria-hidden="true"></i>
                </button>
            </div>
            
            <div class="accessibility-panel-content">
                ${this.createFontSizeSection()}
                ${this.createVisualSection()}
                ${this.createNavigationSection()}
                ${this.createAdvancedSection()}
                ${this.createQuickActionsSection()}
            </div>
            
            <div class="accessibility-panel-footer">
                <button id="accessibility-reset-all" class="btn-secondary">
                    <i class="fas fa-undo" aria-hidden="true"></i>
                    Restaurar Padrão
                </button>
                <button id="accessibility-export-settings" class="btn-secondary">
                    <i class="fas fa-download" aria-hidden="true"></i>
                    Exportar Configurações
                </button>
            </div>
        `;

        document.body.appendChild(panel);
        this.mainPanel = panel;
        this.bindPanelEvents();
    }

    createFontSizeSection() {
        return `
            <div class="accessibility-section">
                <h3>
                    <i class="fas fa-font" aria-hidden="true"></i>
                    Tamanho da Fonte
                </h3>
                <div class="font-size-controls">
                    <button id="decrease-font" class="control-btn" aria-label="Diminuir fonte">
                        <i class="fas fa-minus" aria-hidden="true"></i>
                        A-
                    </button>
                    <div class="font-size-display">
                        <span id="current-font-size" aria-live="polite">16px</span>
                        <input type="range" id="font-size-slider" 
                               min="12" max="32" step="2" value="16"
                               aria-label="Controle deslizante do tamanho da fonte">
                    </div>
                    <button id="increase-font" class="control-btn" aria-label="Aumentar fonte">
                        <i class="fas fa-plus" aria-hidden="true"></i>
                        A+
                    </button>
                </div>
            </div>
        `;
    }

    createVisualSection() {
        return `
            <div class="accessibility-section">
                <h3>
                    <i class="fas fa-eye" aria-hidden="true"></i>
                    Aparência Visual
                </h3>
                <div class="visual-controls">
                    <div class="control-group">
                        <button id="toggle-high-contrast" class="toggle-btn" 
                                role="switch" aria-checked="false"
                                aria-labelledby="high-contrast-label">
                            <span class="toggle-switch"></span>
                        </button>
                        <label id="high-contrast-label" for="toggle-high-contrast">Alto Contraste</label>
                    </div>
                    
                    <div class="control-group">
                        <button id="toggle-dark-mode" class="toggle-btn" 
                                role="switch" aria-checked="false"
                                aria-labelledby="dark-mode-label">
                            <span class="toggle-switch"></span>
                        </button>
                        <label id="dark-mode-label" for="toggle-dark-mode">Modo Escuro</label>
                    </div>
                    
                    <div class="control-group">
                        <button id="toggle-reduced-motion" class="toggle-btn" 
                                role="switch" aria-checked="false"
                                aria-labelledby="reduced-motion-label">
                            <span class="toggle-switch"></span>
                        </button>
                        <label id="reduced-motion-label" for="toggle-reduced-motion">Reduzir Animações</label>
                    </div>
                </div>
            </div>
        `;
    }

    createNavigationSection() {
        return `
            <div class="accessibility-section">
                <h3>
                    <i class="fas fa-keyboard" aria-hidden="true"></i>
                    Navegação
                </h3>
                <div class="navigation-controls">
                    <div class="control-group">
                        <button id="toggle-voice-guidance" class="toggle-btn" 
                                role="switch" aria-checked="false"
                                aria-labelledby="voice-guidance-label">
                            <span class="toggle-switch"></span>
                        </button>
                        <label id="voice-guidance-label" for="toggle-voice-guidance">Guia de Voz</label>
                    </div>
                    
                    <div class="control-group">
                        <button id="show-skip-links" class="action-btn">
                            <i class="fas fa-link" aria-hidden="true"></i>
                            Mostrar Links de Navegação
                        </button>
                    </div>
                    
                    <div class="control-group">
                        <button id="highlight-focusable" class="action-btn">
                            <i class="fas fa-crosshairs" aria-hidden="true"></i>
                            Destacar Elementos Focáveis
                        </button>
                    </div>
                </div>
                
                <div class="keyboard-shortcuts">
                    <h4>Atalhos do Teclado</h4>
                    <ul>
                        <li><kbd>Alt + A</kbd> - Abrir acessibilidade</li>
                        <li><kbd>Alt + M</kbd> - Ir para conteúdo principal</li>
                        <li><kbd>Alt + N</kbd> - Ir para navegação</li>
                        <li><kbd>Ctrl + Alt + D</kbd> - Modo debug</li>
                    </ul>
                </div>
            </div>
        `;
    }

    createAdvancedSection() {
        return `
            <div class="accessibility-section advanced-section" id="advanced-section">
                <h3>
                    <button id="toggle-advanced" class="section-toggle" aria-expanded="false">
                        <i class="fas fa-cog" aria-hidden="true"></i>
                        Configurações Avançadas
                        <i class="fas fa-chevron-down toggle-icon" aria-hidden="true"></i>
                    </button>
                </h3>
                <div class="advanced-content" hidden>
                    <div class="control-group">
                        <label for="reading-speed">Velocidade de Leitura</label>
                        <input type="range" id="reading-speed" 
                               min="0.5" max="2" step="0.1" value="1"
                               aria-label="Velocidade de leitura para guia de voz">
                        <span id="reading-speed-value" aria-live="polite">1.0x</span>
                    </div>
                    
                    <div class="control-group">
                        <label for="announcement-frequency">Frequência de Anúncios</label>
                        <select id="announcement-frequency" aria-label="Frequência dos anúncios de navegação">
                            <option value="high">Alta</option>
                            <option value="medium" selected>Média</option>
                            <option value="low">Baixa</option>
                            <option value="minimal">Mínima</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <button id="toggle-debug-mode" class="toggle-btn" 
                                role="switch" aria-checked="false"
                                aria-labelledby="debug-mode-label">
                            <span class="toggle-switch"></span>
                        </button>
                        <label id="debug-mode-label" for="toggle-debug-mode">Modo Debug</label>
                    </div>
                </div>
            </div>
        `;
    }

    createQuickActionsSection() {
        return `
            <div class="accessibility-section">
                <h3>
                    <i class="fas fa-bolt" aria-hidden="true"></i>
                    Ações Rápidas
                </h3>
                <div class="quick-actions">
                    <button id="run-accessibility-test" class="action-btn">
                        <i class="fas fa-check-circle" aria-hidden="true"></i>
                        Testar Acessibilidade
                    </button>
                    <button id="generate-report" class="action-btn">
                        <i class="fas fa-file-alt" aria-hidden="true"></i>
                        Gerar Relatório
                    </button>
                    <button id="open-help" class="action-btn">
                        <i class="fas fa-question-circle" aria-hidden="true"></i>
                        Ajuda
                    </button>
                </div>
            </div>
        `;
    }

    createFloatingToggle() {
        const toggle = document.createElement('button');
        toggle.id = 'accessibility-floating-toggle';
        toggle.className = 'accessibility-floating-toggle';
        toggle.setAttribute('aria-label', 'Abrir opções de acessibilidade');
        toggle.setAttribute('title', 'Acessibilidade (Alt + A)');
        
        toggle.innerHTML = `
            <i class="fas fa-universal-access" aria-hidden="true"></i>
            <span class="sr-only">Acessibilidade</span>
        `;
        
        document.body.appendChild(toggle);
        this.floatingToggle = toggle;
    }

    bindPanelEvents() {
        // Panel toggle
        this.floatingToggle.addEventListener('click', () => this.togglePanel());
        document.getElementById('accessibility-panel-close').addEventListener('click', () => this.hidePanel());
        
        // Font size controls
        document.getElementById('decrease-font').addEventListener('click', () => this.adjustFontSize(-2));
        document.getElementById('increase-font').addEventListener('click', () => this.adjustFontSize(2));
        document.getElementById('font-size-slider').addEventListener('input', (e) => this.setFontSize(parseInt(e.target.value)));
        
        // Visual controls
        document.getElementById('toggle-high-contrast').addEventListener('click', () => this.toggleHighContrast());
        document.getElementById('toggle-dark-mode').addEventListener('click', () => this.toggleDarkMode());
        document.getElementById('toggle-reduced-motion').addEventListener('click', () => this.toggleReducedMotion());
        
        // Navigation controls
        document.getElementById('toggle-voice-guidance').addEventListener('click', () => this.toggleVoiceGuidance());
        document.getElementById('show-skip-links').addEventListener('click', () => this.showSkipLinks());
        document.getElementById('highlight-focusable').addEventListener('click', () => this.highlightFocusable());
        
        // Advanced controls
        document.getElementById('toggle-advanced').addEventListener('click', () => this.toggleAdvancedSection());
        document.getElementById('reading-speed').addEventListener('input', (e) => this.updateReadingSpeed(e.target.value));
        document.getElementById('announcement-frequency').addEventListener('change', (e) => this.updateAnnouncementFrequency(e.target.value));
        document.getElementById('toggle-debug-mode').addEventListener('click', () => this.toggleDebugMode());
        
        // Quick actions
        document.getElementById('run-accessibility-test').addEventListener('click', () => this.runAccessibilityTest());
        document.getElementById('generate-report').addEventListener('click', () => this.generateReport());
        document.getElementById('open-help').addEventListener('click', () => this.openHelp());
        
        // Footer actions
        document.getElementById('accessibility-reset-all').addEventListener('click', () => this.resetAllSettings());
        document.getElementById('accessibility-export-settings').addEventListener('click', () => this.exportSettings());
        
        // Panel overlay click to close
        this.mainPanel.addEventListener('click', (e) => {
            if (e.target === this.mainPanel) {
                this.hidePanel();
            }
        });
        
        // Escape key to close
        this.mainPanel.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hidePanel();
            }
        });
    }

    handleKeyboardShortcuts(event) {
        const { altKey, key } = event;
        
        if (altKey && key === 'a') {
            event.preventDefault();
            this.togglePanel();
        }
    }

    togglePanel() {
        if (this.panelVisible) {
            this.hidePanel();
        } else {
            this.showPanel();
        }
    }

    showPanel() {
        this.mainPanel.classList.add('visible');
        this.mainPanel.setAttribute('aria-hidden', 'false');
        this.floatingToggle.setAttribute('aria-expanded', 'true');
        this.panelVisible = true;
        
        // Focus management
        const firstFocusable = this.mainPanel.querySelector('button, input, select');
        if (firstFocusable) {
            firstFocusable.focus();
        }
        
        // Trap focus
        this.trapFocus();
        
        this.core.announce('Painel de acessibilidade aberto');
    }

    hidePanel() {
        this.mainPanel.classList.remove('visible');
        this.mainPanel.setAttribute('aria-hidden', 'true');
        this.floatingToggle.setAttribute('aria-expanded', 'false');
        this.panelVisible = false;
        
        // Return focus to toggle
        this.floatingToggle.focus();
        
        this.core.announce('Painel de acessibilidade fechado');
    }

    trapFocus() {
        const focusableElements = this.mainPanel.querySelectorAll(`
            button, input, select, textarea, [tabindex]:not([tabindex="-1"])
        `);
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        this.mainPanel.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        });
    }

    // Control methods
    adjustFontSize(delta) {
        const visualControls = this.core.modules.get('visualControls');
        if (visualControls) {
            const newSize = visualControls.adjustFontSize(delta);
            this.updateFontSizeDisplay(newSize);
        }
    }

    setFontSize(size) {
        this.core.updateSetting('fontSize.current', size);
        this.updateFontSizeDisplay(size);
    }

    updateFontSizeDisplay(size) {
        const display = document.getElementById('current-font-size');
        const slider = document.getElementById('font-size-slider');
        
        if (display) display.textContent = `${size}px`;
        if (slider) slider.value = size;
    }

    toggleHighContrast() {
        this.core.toggleHighContrast();
        this.updateToggleState('toggle-high-contrast', this.core.getSetting('contrast.enabled'));
    }

    toggleDarkMode() {
        const enabled = !this.core.getSetting('theme.dark');
        this.core.updateSetting('theme.dark', enabled);
        document.body.classList.toggle('dark-mode', enabled);
        this.updateToggleState('toggle-dark-mode', enabled);
        this.core.announce(enabled ? 'Modo escuro ativado' : 'Modo escuro desativado');
    }

    toggleReducedMotion() {
        this.core.toggleReducedMotion();
        this.updateToggleState('toggle-reduced-motion', this.core.getSetting('motion.reduced'));
    }

    toggleVoiceGuidance() {
        const enabled = !this.core.getSetting('voice.enabled');
        this.core.updateSetting('voice.enabled', enabled);
        this.updateToggleState('toggle-voice-guidance', enabled);
        this.core.announce(enabled ? 'Guia de voz ativado' : 'Guia de voz desativado');
    }

    toggleDebugMode() {
        this.core.toggleDebugMode();
        this.updateToggleState('toggle-debug-mode', this.core.getSetting('debug'));
    }

    updateToggleState(toggleId, isEnabled) {
        const toggle = document.getElementById(toggleId);
        if (toggle) {
            toggle.setAttribute('aria-checked', isEnabled.toString());
            toggle.classList.toggle('active', isEnabled);
        }
    }

    showSkipLinks() {
        const skipLinks = document.querySelectorAll('.skip-link');
        skipLinks.forEach(link => {
            link.style.position = 'static';
            link.style.left = 'auto';
            link.style.top = 'auto';
            link.style.background = '#1e40af';
            link.style.color = 'white';
            link.style.padding = '8px 12px';
            link.style.margin = '4px';
            link.style.display = 'inline-block';
            link.style.borderRadius = '4px';
        });
        
        this.core.announce(`${skipLinks.length} links de navegação destacados`);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            skipLinks.forEach(link => {
                link.style.cssText = '';
            });
        }, 5000);
    }

    highlightFocusable() {
        const focusManager = this.core.modules.get('focusManager');
        if (focusManager && focusManager.highlightAllFocusable) {
            focusManager.highlightAllFocusable();
        }
    }

    toggleAdvancedSection() {
        const toggle = document.getElementById('toggle-advanced');
        const content = document.querySelector('.advanced-content');
        const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
        
        toggle.setAttribute('aria-expanded', (!isExpanded).toString());
        content.hidden = isExpanded;
        
        const icon = toggle.querySelector('.toggle-icon');
        icon.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(180deg)';
    }

    updateReadingSpeed(speed) {
        this.core.updateSetting('voice.rate', parseFloat(speed));
        document.getElementById('reading-speed-value').textContent = `${speed}x`;
    }

    updateAnnouncementFrequency(frequency) {
        this.core.updateSetting('voice.frequency', frequency);
        this.core.announce(`Frequência de anúncios alterada para ${frequency}`);
    }

    runAccessibilityTest() {
        this.core.runDiagnostics().then(results => {
            const score = this.calculateOverallScore(results);
            this.core.announce(`Teste de acessibilidade concluído. Pontuação: ${score}%`);
            this.showTestResults(results, score);
        });
    }

    calculateOverallScore(results) {
        const modules = Object.values(results.tests);
        const totalTests = modules.length;
        const passedTests = modules.filter(test => test.status === 'ok').length;
        return Math.round((passedTests / totalTests) * 100);
    }

    showTestResults(results, score) {
        const statusClass = score >= 90 ? 'excellent' : score >= 70 ? 'good' : 'needs-improvement';
        
        // Create or update results display
        let resultsDiv = document.getElementById('test-results');
        if (!resultsDiv) {
            resultsDiv = document.createElement('div');
            resultsDiv.id = 'test-results';
            resultsDiv.className = 'test-results';
            this.mainPanel.querySelector('.accessibility-panel-content').appendChild(resultsDiv);
        }
        
        resultsDiv.innerHTML = `
            <h4>Resultados do Teste de Acessibilidade</h4>
            <div class="score-display ${statusClass}">
                <span class="score-number">${score}%</span>
                <span class="score-label">Pontuação Geral</span>
            </div>
            <div class="results-summary">
                ${Object.entries(results.tests).map(([name, test]) => `
                    <div class="result-item ${test.status}">
                        <span class="result-name">${name}</span>
                        <span class="result-status">${test.status}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    generateReport() {
        this.core.generateAccessibilityReport();
    }

    openHelp() {
        const helpContent = `
            <h3>Ajuda - Acessibilidade</h3>
            <p>Este painel oferece controles para personalizar a experiência de navegação:</p>
            <ul>
                <li><strong>Tamanho da Fonte:</strong> Ajuste o tamanho do texto para melhor legibilidade</li>
                <li><strong>Alto Contraste:</strong> Melhora a visibilidade para usuários com baixa visão</li>
                <li><strong>Reduzir Animações:</strong> Remove animações que podem causar desconforto</li>
                <li><strong>Guia de Voz:</strong> Fornece feedback sonoro durante a navegação</li>
            </ul>
            <p>Use os atalhos do teclado para acesso rápido às funcionalidades.</p>
        `;
        
        this.core.announce('Abrindo ajuda de acessibilidade');
        // Implementation for help modal would go here
    }

    resetAllSettings() {
        if (confirm('Tem certeza que deseja restaurar todas as configurações de acessibilidade ao padrão?')) {
            // Reset core settings
            this.core.config = this.core.getDefaultConfig();
            this.core.saveSettings();
            this.core.applySettings();
            
            // Update UI
            this.updateAllToggleStates();
            this.updateFontSizeDisplay(16);
            
            this.core.announce('Configurações de acessibilidade restauradas ao padrão');
        }
    }

    exportSettings() {
        const settings = {
            version: this.core.version,
            timestamp: new Date().toISOString(),
            settings: this.core.config
        };
        
        const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `accessibility-settings-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.core.announce('Configurações exportadas com sucesso');
    }

    updateAllToggleStates() {
        this.updateToggleState('toggle-high-contrast', this.core.getSetting('contrast.enabled'));
        this.updateToggleState('toggle-dark-mode', this.core.getSetting('theme.dark'));
        this.updateToggleState('toggle-reduced-motion', this.core.getSetting('motion.reduced'));
        this.updateToggleState('toggle-voice-guidance', this.core.getSetting('voice.enabled'));
        this.updateToggleState('toggle-debug-mode', this.core.getSetting('debug'));
    }

    setupResponsiveHandling() {
        this.handleResize();
    }

    handleResize() {
        const isCompact = window.innerWidth < 768;
        
        if (isCompact !== this.compactMode) {
            this.compactMode = isCompact;
            this.mainPanel.classList.toggle('compact', isCompact);
            this.floatingToggle.classList.toggle('compact', isCompact);
        }
    }

    updateUI({ detail: { path, value } }) {
        // Update UI elements when settings change
        switch (path) {
            case 'fontSize.current':
                this.updateFontSizeDisplay(value);
                break;
            case 'contrast.enabled':
                this.updateToggleState('toggle-high-contrast', value);
                break;
            case 'motion.reduced':
                this.updateToggleState('toggle-reduced-motion', value);
                break;
            case 'debug':
                this.updateToggleState('toggle-debug-mode', value);
                break;
        }
    }

    onCoreReady() {
        // Initialize UI state based on current settings
        this.updateAllToggleStates();
        this.updateFontSizeDisplay(this.core.getSetting('fontSize.current') || 16);
    }

    async runDiagnostics() {
        return {
            ...await super.runDiagnostics(),
            panelVisible: this.panelVisible,
            compactMode: this.compactMode,
            togglesCount: document.querySelectorAll('.toggle-btn').length,
            status: 'ok'
        };
    }
}

// Export module
window.AccessibilityUIModule = AccessibilityUIModule;