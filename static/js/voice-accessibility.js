/**
 * Voice Accessibility System for 2ª Vara Cível de Cariacica
 * Provides comprehensive voice guidance and accessibility features
 */

class VoiceAccessibilityManager {
    constructor() {
        this.synthesis = window.speechSynthesis;
        this.recognition = null;
        this.isEnabled = false;
        this.isListening = false;
        this.voices = [];
        this.currentLanguage = 'pt-BR';
        this.speechRate = 1.0;
        this.speechVolume = 0.8;
        this.speechPitch = 1.0;
        
        this.init();
    }

    async init() {
        try {
            // Initialize voices
            this.loadVoices();
            
            // Initialize speech recognition
            this.initSpeechRecognition();
            
            // Setup keyboard shortcuts
            this.setupKeyboardShortcuts();
            
            // Setup focus management
            this.setupFocusManagement();
            
            // Create accessibility controls
            this.createAccessibilityControls();
            
            console.log('Voice Accessibility Manager initialized successfully');
        } catch (error) {
            console.error('Error initializing Voice Accessibility Manager:', error);
        }
    }

    loadVoices() {
        this.voices = this.synthesis.getVoices();
        
        if (this.voices.length === 0) {
            // Voices might not be loaded yet
            this.synthesis.addEventListener('voiceschanged', () => {
                this.voices = this.synthesis.getVoices();
                this.selectBestVoice();
            });
        } else {
            this.selectBestVoice();
        }
    }

    selectBestVoice() {
        // Prefer Portuguese Brazilian voices
        const preferredVoices = [
            'Microsoft Maria - Portuguese (Brazil)',
            'Google português do Brasil',
            'Luciana',
            'pt-BR'
        ];

        for (const preferred of preferredVoices) {
            const voice = this.voices.find(v => 
                v.name.includes(preferred) || 
                v.lang.includes('pt-BR') ||
                v.lang.includes('pt')
            );
            if (voice) {
                this.selectedVoice = voice;
                return;
            }
        }

        // Fallback to first available voice
        this.selectedVoice = this.voices[0] || null;
    }

    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = this.currentLanguage;

            this.recognition.onresult = (event) => {
                const command = event.results[0][0].transcript.toLowerCase();
                this.processVoiceCommand(command);
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.speak('Erro no reconhecimento de voz. Tente novamente.');
            };

            this.recognition.onend = () => {
                this.isListening = false;
                this.updateListeningIndicator(false);
            };
        }
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            // Alt + V: Toggle voice guidance
            if (event.altKey && event.key === 'v') {
                event.preventDefault();
                this.toggleVoiceGuidance();
            }
            
            // Alt + L: Start voice command listening
            if (event.altKey && event.key === 'l') {
                event.preventDefault();
                this.startListening();
            }
            
            // Alt + R: Read current page content
            if (event.altKey && event.key === 'r') {
                event.preventDefault();
                this.readPageContent();
            }
            
            // Alt + H: Voice help
            if (event.altKey && event.key === 'h') {
                event.preventDefault();
                this.provideVoiceHelp();
            }
        });
    }

    setupFocusManagement() {
        // Announce focused elements
        document.addEventListener('focusin', (event) => {
            if (this.isEnabled) {
                this.announceFocusedElement(event.target);
            }
        });

        // Announce link destinations
        document.addEventListener('mouseenter', (event) => {
            if (this.isEnabled && event.target.tagName === 'A') {
                const linkText = event.target.textContent.trim();
                const href = event.target.href;
                if (linkText && href) {
                    this.speak(`Link: ${linkText}`);
                }
            }
        }, true);
    }

    createAccessibilityControls() {
        // Create the main accessibility toggle button
        const accessibilityToggle = document.createElement('button');
        accessibilityToggle.id = 'accessibility-toggle';
        accessibilityToggle.className = 'accessibility-toggle-btn';
        accessibilityToggle.innerHTML = `
            <i class="fas fa-universal-access"></i>
            <span>Acessibilidade</span>
        `;
        accessibilityToggle.title = 'Abrir controles de acessibilidade';

        // Create the main controls container
        const controlsContainer = document.createElement('div');
        controlsContainer.id = 'accessibility-controls-container';
        controlsContainer.style.display = 'none';
        controlsContainer.innerHTML = `
            <div class="accessibility-boxcard">
                <div class="accessibility-header">
                    <h6><i class="fas fa-universal-access me-2"></i>Controles de Acessibilidade</h6>
                    <button id="close-accessibility" class="close-btn" title="Fechar controles">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="accessibility-content">
                    <!-- Voice Controls Section -->
                    <div class="control-section">
                        <h7><i class="fas fa-volume-up me-2"></i>Controles de Voz</h7>
                        <div class="controls-grid">
                            <button id="toggle-voice" class="control-btn" title="Ativar/Desativar guia de voz (Alt+V)">
                                <i class="fas fa-volume-up"></i>
                                <span>Guia de Voz</span>
                            </button>
                            <button id="voice-listen" class="control-btn" title="Comando de voz (Alt+L)">
                                <i class="fas fa-microphone"></i>
                                <span>Escutar</span>
                            </button>
                            <button id="read-page" class="control-btn" title="Ler página (Alt+R)">
                                <i class="fas fa-book-reader"></i>
                                <span>Ler Página</span>
                            </button>
                            <button id="voice-help" class="control-btn" title="Ajuda de voz (Alt+H)">
                                <i class="fas fa-question-circle"></i>
                                <span>Ajuda</span>
                            </button>
                        </div>
                        
                        <div class="voice-settings">
                            <div class="setting-item">
                                <label for="speech-rate">Velocidade da Fala:</label>
                                <input type="range" id="speech-rate" min="0.5" max="2" step="0.1" value="1">
                                <span class="range-value">1.0x</span>
                            </div>
                            <div class="setting-item">
                                <label for="speech-volume">Volume:</label>
                                <input type="range" id="speech-volume" min="0" max="1" step="0.1" value="0.8">
                                <span class="range-value">80%</span>
                            </div>
                        </div>
                    </div>

                    <!-- Visual Controls Section -->
                    <div class="control-section">
                        <h7><i class="fas fa-eye me-2"></i>Controles Visuais</h7>
                        <div class="controls-grid">
                            <button id="increase-font" class="control-btn" title="Aumentar tamanho da fonte">
                                <i class="fas fa-plus"></i>
                                <span>Fonte +</span>
                            </button>
                            <button id="decrease-font" class="control-btn" title="Diminuir tamanho da fonte">
                                <i class="fas fa-minus"></i>
                                <span>Fonte -</span>
                            </button>
                            <button id="toggle-contrast" class="control-btn" title="Alto contraste">
                                <i class="fas fa-adjust"></i>
                                <span>Contraste</span>
                            </button>
                            <button id="reset-visual" class="control-btn" title="Restaurar configurações visuais">
                                <i class="fas fa-undo"></i>
                                <span>Restaurar</span>
                            </button>
                        </div>
                    </div>

                    <!-- Navigation Controls Section -->
                    <div class="control-section">
                        <h7><i class="fas fa-keyboard me-2"></i>Navegação e Atalhos</h7>
                        <div class="shortcuts-info">
                            <div class="shortcut-item">
                                <kbd>Alt + V</kbd>
                                <span>Ativar/Desativar guia de voz</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>Alt + L</kbd>
                                <span>Comando de voz</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>Alt + R</kbd>
                                <span>Ler conteúdo da página</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>Alt + H</kbd>
                                <span>Ajuda de acessibilidade</span>
                            </div>
                        </div>
                    </div>

                    <!-- Status Indicators -->
                    <div class="status-section">
                        <div id="listening-indicator" class="status-indicator" style="display: none;">
                            <i class="fas fa-microphone pulse"></i>
                            <span>Escutando comando de voz...</span>
                        </div>
                        <div id="voice-status" class="status-indicator">
                            <i class="fas fa-volume-mute"></i>
                            <span>Guia de voz desativado</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(accessibilityToggle);
        document.body.appendChild(controlsContainer);
        this.setupControlsEventListeners();
    }

    setupControlsEventListeners() {
        // Toggle accessibility panel
        document.getElementById('accessibility-toggle').addEventListener('click', () => {
            this.toggleAccessibilityPanel();
        });

        document.getElementById('close-accessibility').addEventListener('click', () => {
            this.toggleAccessibilityPanel();
        });

        // Voice controls
        document.getElementById('toggle-voice').addEventListener('click', () => {
            this.toggleVoiceGuidance();
        });

        document.getElementById('voice-listen').addEventListener('click', () => {
            this.startListening();
        });

        document.getElementById('read-page').addEventListener('click', () => {
            this.readPageContent();
        });

        document.getElementById('voice-help').addEventListener('click', () => {
            this.provideVoiceHelp();
        });

        // Voice settings with value display
        document.getElementById('speech-rate').addEventListener('input', (event) => {
            const value = parseFloat(event.target.value);
            this.speechRate = value;
            event.target.nextElementSibling.textContent = `${value.toFixed(1)}x`;
        });

        document.getElementById('speech-volume').addEventListener('input', (event) => {
            const value = parseFloat(event.target.value);
            this.speechVolume = value;
            event.target.nextElementSibling.textContent = `${Math.round(value * 100)}%`;
        });

        // Visual controls
        document.getElementById('increase-font').addEventListener('click', () => {
            this.increaseFontSize();
        });

        document.getElementById('decrease-font').addEventListener('click', () => {
            this.decreaseFontSize();
        });

        document.getElementById('toggle-contrast').addEventListener('click', () => {
            this.toggleHighContrast();
        });

        document.getElementById('reset-visual').addEventListener('click', () => {
            this.resetVisualSettings();
        });

        // Close panel when clicking outside
        document.addEventListener('click', (event) => {
            const panel = document.getElementById('accessibility-controls-container');
            const toggle = document.getElementById('accessibility-toggle');
            
            if (panel.style.display === 'block' && 
                !panel.contains(event.target) && 
                !toggle.contains(event.target)) {
                this.toggleAccessibilityPanel();
            }
        });
    }

    toggleAccessibilityPanel() {
        const panel = document.getElementById('accessibility-controls-container');
        const isVisible = panel.style.display === 'block';
        
        if (isVisible) {
            panel.style.display = 'none';
        } else {
            panel.style.display = 'block';
        }
    }

    toggleVoiceGuidance() {
        this.isEnabled = !this.isEnabled;
        const toggleBtn = document.getElementById('toggle-voice');
        const statusIndicator = document.getElementById('voice-status');
        
        if (this.isEnabled) {
            toggleBtn.classList.add('active');
            statusIndicator.innerHTML = `
                <i class="fas fa-volume-up"></i>
                <span>Guia de voz ativado</span>
            `;
            statusIndicator.classList.add('active');
            this.speak('Guia de voz ativado. Use Alt + H para obter ajuda sobre comandos de voz.');
            this.announcePageInformation();
        } else {
            toggleBtn.classList.remove('active');
            statusIndicator.innerHTML = `
                <i class="fas fa-volume-mute"></i>
                <span>Guia de voz desativado</span>
            `;
            statusIndicator.classList.remove('active');
            this.speak('Guia de voz desativado.');
        }

        // Store preference
        localStorage.setItem('voiceGuidanceEnabled', this.isEnabled);
    }

    increaseFontSize() {
        const currentSize = parseFloat(getComputedStyle(document.body).fontSize);
        const newSize = Math.min(currentSize + 2, 24); // Max 24px
        document.body.style.fontSize = newSize + 'px';
        localStorage.setItem('fontSize', newSize);
        
        if (this.isEnabled) {
            this.speak(`Tamanho da fonte aumentado para ${newSize} pixels`);
        }
    }

    decreaseFontSize() {
        const currentSize = parseFloat(getComputedStyle(document.body).fontSize);
        const newSize = Math.max(currentSize - 2, 12); // Min 12px
        document.body.style.fontSize = newSize + 'px';
        localStorage.setItem('fontSize', newSize);
        
        if (this.isEnabled) {
            this.speak(`Tamanho da fonte diminuído para ${newSize} pixels`);
        }
    }

    toggleHighContrast() {
        const body = document.body;
        const isHighContrast = body.classList.contains('high-contrast');
        
        if (isHighContrast) {
            body.classList.remove('high-contrast');
            localStorage.setItem('highContrast', 'false');
            if (this.isEnabled) {
                this.speak('Alto contraste desativado');
            }
        } else {
            body.classList.add('high-contrast');
            localStorage.setItem('highContrast', 'true');
            if (this.isEnabled) {
                this.speak('Alto contraste ativado');
            }
        }
    }

    resetVisualSettings() {
        document.body.style.fontSize = '';
        document.body.classList.remove('high-contrast');
        localStorage.removeItem('fontSize');
        localStorage.removeItem('highContrast');
        
        if (this.isEnabled) {
            this.speak('Configurações visuais restauradas ao padrão');
        }
    }

    speak(text, options = {}) {
        if (!this.synthesis || this.synthesis.speaking) {
            this.synthesis.cancel();
        }

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = this.selectedVoice;
        utterance.rate = options.rate || this.speechRate;
        utterance.volume = options.volume || this.speechVolume;
        utterance.pitch = options.pitch || this.speechPitch;
        utterance.lang = this.currentLanguage;

        this.synthesis.speak(utterance);
    }

    startListening() {
        if (!this.recognition) {
            this.speak('Reconhecimento de voz não disponível neste navegador.');
            return;
        }

        if (this.isListening) {
            this.recognition.stop();
            return;
        }

        this.isListening = true;
        this.updateListeningIndicator(true);
        this.speak('Diga um comando');
        
        setTimeout(() => {
            this.recognition.start();
        }, 1000);
    }

    processVoiceCommand(command) {
        console.log('Voice command received:', command);

        // Navigation commands
        if (command.includes('ir para') || command.includes('navegar')) {
            if (command.includes('início') || command.includes('home')) {
                this.navigateToPage('/', 'Navegando para a página inicial');
            } else if (command.includes('serviços') || command.includes('servicos')) {
                this.navigateToPage('/servicos/', 'Navegando para a página de serviços');
            } else if (command.includes('contato')) {
                this.navigateToPage('/contato', 'Navegando para a página de contato');
            } else if (command.includes('sobre') || command.includes('juiz')) {
                this.navigateToPage('/juiz', 'Navegando para a página sobre o juiz');
            } else if (command.includes('notícias') || command.includes('noticias')) {
                this.navigateToPage('/noticias', 'Navegando para a página de notícias');
            }
        }
        
        // Action commands
        else if (command.includes('consultar processo')) {
            this.navigateToPage('/servicos/consulta-processual', 'Abrindo consulta processual');
        }
        else if (command.includes('agendar audiência') || command.includes('agendamento')) {
            this.navigateToPage('/servicos/agendamento', 'Abrindo agendamento de audiências');
        }
        else if (command.includes('abrir chatbot') || command.includes('chat')) {
            this.openChatbot();
        }
        else if (command.includes('ler página') || command.includes('ler conteúdo')) {
            this.readPageContent();
        }
        else if (command.includes('parar') || command.includes('silêncio')) {
            this.synthesis.cancel();
            this.speak('Audio interrompido');
        }
        else if (command.includes('ajuda')) {
            this.provideVoiceHelp();
        }
        else {
            this.speak('Comando não reconhecido. Diga "ajuda" para obter uma lista de comandos disponíveis.');
        }
    }

    navigateToPage(url, announcement) {
        this.speak(announcement);
        setTimeout(() => {
            window.location.href = url;
        }, 1500);
    }

    openChatbot() {
        const chatbotToggle = document.getElementById('chatbot-toggle');
        if (chatbotToggle) {
            chatbotToggle.click();
            this.speak('Chatbot aberto. Você pode digitar sua pergunta ou usar comandos de voz.');
        } else {
            this.speak('Chatbot não disponível nesta página.');
        }
    }

    readPageContent() {
        this.synthesis.cancel();
        
        const content = this.extractPageContent();
        if (content) {
            this.speak(`Lendo o conteúdo da página: ${content}`);
        } else {
            this.speak('Nenhum conteúdo encontrado para leitura.');
        }
    }

    extractPageContent() {
        // Get main content areas
        const selectors = [
            'main',
            '.hero-section p',
            '.card-body',
            '.content',
            'article',
            '.description'
        ];

        let content = '';
        
        for (const selector of selectors) {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                const text = element.textContent.trim();
                if (text && text.length > 20) {
                    content += text + '. ';
                }
            });
        }

        // Limit content length for reasonable speech duration
        return content.length > 500 ? content.substring(0, 500) + '...' : content;
    }

    announcePageInformation() {
        const pageTitle = document.title;
        const mainHeading = document.querySelector('h1');
        const headingText = mainHeading ? mainHeading.textContent.trim() : '';
        
        let announcement = `Página: ${pageTitle}`;
        if (headingText && headingText !== pageTitle) {
            announcement += `. Título principal: ${headingText}`;
        }
        
        this.speak(announcement);
    }

    announceFocusedElement(element) {
        if (!element) return;

        const tagName = element.tagName.toLowerCase();
        const text = element.textContent.trim();
        const placeholder = element.placeholder;
        const alt = element.alt;
        const title = element.title;

        let announcement = '';

        switch (tagName) {
            case 'button':
                announcement = `Botão: ${text || title || 'sem título'}`;
                break;
            case 'a':
                announcement = `Link: ${text || title || 'sem título'}`;
                break;
            case 'input':
                const type = element.type;
                announcement = `Campo ${type}: ${placeholder || title || 'sem rótulo'}`;
                break;
            case 'textarea':
                announcement = `Área de texto: ${placeholder || title || 'sem rótulo'}`;
                break;
            case 'select':
                announcement = `Lista de seleção: ${title || 'sem rótulo'}`;
                break;
            case 'img':
                announcement = `Imagem: ${alt || title || 'sem descrição'}`;
                break;
            case 'h1':
            case 'h2':
            case 'h3':
            case 'h4':
            case 'h5':
            case 'h6':
                announcement = `Título nível ${tagName.charAt(1)}: ${text}`;
                break;
            default:
                if (text && text.length > 0 && text.length < 100) {
                    announcement = text;
                }
        }

        if (announcement) {
            this.speak(announcement, { rate: 1.2 });
        }
    }

    provideVoiceHelp() {
        const helpText = `
            Comandos de voz disponíveis:
            
            Navegação: Diga "ir para início", "ir para serviços", "ir para contato", "ir para sobre", ou "ir para notícias".
            
            Ações: "consultar processo", "agendar audiência", "abrir chatbot".
            
            Leitura: "ler página" ou "ler conteúdo".
            
            Controle: "parar" para interromper a fala, "ajuda" para esta mensagem.
            
            Atalhos do teclado: Alt + V para ativar guia de voz, Alt + L para comando de voz, Alt + R para ler página, Alt + H para ajuda.
        `;
        
        this.speak(helpText);
    }

    updateListeningIndicator(isListening) {
        const indicator = document.getElementById('listening-indicator');
        if (indicator) {
            indicator.style.display = isListening ? 'flex' : 'none';
        }
    }

    // Initialize on page load
    static init() {
        if (window.voiceAccessibility) return;
        
        window.voiceAccessibility = new VoiceAccessibilityManager();
        
        // Auto-enable if previously enabled
        const wasEnabled = localStorage.getItem('voiceGuidanceEnabled') === 'true';
        if (wasEnabled) {
            setTimeout(() => {
                window.voiceAccessibility.toggleVoiceGuidance();
            }, 1000);
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', VoiceAccessibilityManager.init);
} else {
    VoiceAccessibilityManager.init();
}