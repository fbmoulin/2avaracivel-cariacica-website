/*!
 * Court Loading Manager
 * 2ª Vara Cível de Cariacica - Advanced Loading System
 * Manages court-themed loading animations with smart context detection
 */

class CourtLoadingManager {
    constructor() {
        this.loadingElement = null;
        this.currentAnimation = null;
        this.loadingTexts = {
            default: {
                main: "Processando solicitação...",
                sub: "Aguarde enquanto preparamos sua consulta"
            },
            process_consultation: {
                main: "Consultando processo...",
                sub: "Verificando dados no sistema judicial"
            },
            scheduling: {
                main: "Processando agendamento...",
                sub: "Validando disponibilidade de horários"
            },
            contact: {
                main: "Enviando mensagem...",
                sub: "Registrando sua solicitação"
            },
            chatbot: {
                main: "Consultando assistente jurídico...",
                sub: "Processando sua pergunta"
            },
            document_processing: {
                main: "Processando documentos...",
                sub: "Analisando arquivos enviados"
            },
            authentication: {
                main: "Verificando credenciais...",
                sub: "Autenticando acesso ao sistema"
            },
            database: {
                main: "Acessando banco de dados...",
                sub: "Recuperando informações"
            }
        };
        
        this.animations = [
            'justice-scales',
            'gavel',
            'document-processor',
            'legal-code',
            'courthouse',
            'spinner'
        ];
        
        this.init();
    }

    init() {
        // Create loading element
        this.createLoadingElement();
        
        // Bind to common loading events
        this.bindLoadingEvents();
        
        // Handle page load
        this.handlePageLoad();
        
        console.log('Court Loading Manager initialized');
    }

    createLoadingElement() {
        // Remove existing loader if present
        const existingLoader = document.getElementById('court-loading-overlay');
        if (existingLoader) {
            existingLoader.remove();
        }

        this.loadingElement = document.createElement('div');
        this.loadingElement.id = 'court-loading-overlay';
        this.loadingElement.className = 'court-loading-container hidden';
        
        document.body.appendChild(this.loadingElement);
    }

    bindLoadingEvents() {
        // Form submissions
        document.addEventListener('submit', (e) => {
            if (e.target.tagName === 'FORM') {
                const formAction = e.target.action || window.location.pathname;
                const context = this.detectContext(formAction);
                this.show(context);
            }
        });

        // AJAX requests (if using fetch)
        if (window.fetch) {
            const originalFetch = window.fetch;
            window.fetch = (...args) => {
                const context = this.detectContext(args[0]);
                this.show(context);
                
                return originalFetch(...args)
                    .then(response => {
                        this.hide();
                        return response;
                    })
                    .catch(error => {
                        this.hide();
                        throw error;
                    });
            };
        }

        // Navigation events
        window.addEventListener('beforeunload', () => {
            this.show('default');
        });

        // Back/forward navigation
        window.addEventListener('popstate', () => {
            this.show('default');
            setTimeout(() => this.hide(), 500);
        });
    }

    handlePageLoad() {
        // Show loader for slow loading pages
        if (document.readyState === 'loading') {
            this.show('default');
            
            window.addEventListener('load', () => {
                setTimeout(() => this.hide(), 300);
            });
        }
    }

    detectContext(url = '') {
        const pathname = typeof url === 'string' ? url : window.location.pathname;
        
        if (pathname.includes('consulta') || pathname.includes('process')) {
            return 'process_consultation';
        } else if (pathname.includes('agendamento') || pathname.includes('schedule')) {
            return 'scheduling';
        } else if (pathname.includes('contato') || pathname.includes('contact')) {
            return 'contact';
        } else if (pathname.includes('chatbot') || pathname.includes('chat')) {
            return 'chatbot';
        } else if (pathname.includes('upload') || pathname.includes('document')) {
            return 'document_processing';
        } else if (pathname.includes('login') || pathname.includes('auth')) {
            return 'authentication';
        } else {
            return 'default';
        }
    }

    getRandomAnimation() {
        return this.animations[Math.floor(Math.random() * this.animations.length)];
    }

    getContextualAnimation(context) {
        const contextAnimations = {
            'process_consultation': 'document-processor',
            'scheduling': 'courthouse',
            'contact': 'document-processor',
            'chatbot': 'legal-code',
            'document_processing': 'document-processor',
            'authentication': 'courthouse',
            'database': 'legal-code',
            'default': 'justice-scales'
        };
        
        return contextAnimations[context] || 'justice-scales';
    }

    show(context = 'default', options = {}) {
        if (!this.loadingElement) {
            this.createLoadingElement();
        }

        const {
            animation = this.getContextualAnimation(context),
            duration = null,
            customText = null,
            showProgress = false
        } = options;

        this.currentAnimation = animation;
        const textConfig = customText || this.loadingTexts[context] || this.loadingTexts.default;

        // Build loading content
        const loadingContent = this.buildLoadingContent(animation, textConfig, showProgress);
        this.loadingElement.innerHTML = loadingContent;

        // Show with animation
        this.loadingElement.classList.remove('hidden');
        document.body.style.overflow = 'hidden';

        // Auto-hide if duration specified
        if (duration) {
            setTimeout(() => this.hide(), duration);
        }

        console.log(`Court loader shown: ${animation} (${context})`);
    }

    buildLoadingContent(animation, textConfig, showProgress) {
        const animationHTML = this.getAnimationHTML(animation);
        
        return `
            ${animationHTML}
            <div class="court-loading-text">${textConfig.main}</div>
            <div class="court-loading-subtext">${textConfig.sub}</div>
            ${showProgress ? '<div class="court-progress-bar"><div class="court-progress-fill"></div></div>' : ''}
        `;
    }

    getAnimationHTML(animation) {
        const animations = {
            'justice-scales': `
                <div class="justice-scales-loader">
                    <div class="scales-base"></div>
                    <div class="scales-beam">
                        <div class="scale-chain"></div>
                    </div>
                    <div class="scale-pan left">
                        <div class="scale-chain"></div>
                    </div>
                    <div class="scale-pan right">
                        <div class="scale-chain"></div>
                    </div>
                </div>
            `,
            'gavel': `
                <div class="gavel-loader">
                    <div class="gavel-head"></div>
                    <div class="gavel-handle"></div>
                    <div class="gavel-block"></div>
                </div>
            `,
            'document-processor': `
                <div class="document-processor">
                    <div class="document"></div>
                    <div class="document"></div>
                    <div class="document"></div>
                </div>
            `,
            'legal-code': `
                <div class="legal-code-loader">
                    <div class="code-book"></div>
                    <div class="code-book"></div>
                    <div class="code-book"></div>
                </div>
            `,
            'courthouse': `
                <div class="courthouse-loader">
                    <div class="courthouse-base"></div>
                    <div class="courthouse-column"></div>
                    <div class="courthouse-column"></div>
                    <div class="courthouse-column"></div>
                    <div class="courthouse-column"></div>
                    <div class="courthouse-column"></div>
                    <div class="courthouse-column"></div>
                    <div class="courthouse-roof"></div>
                </div>
            `,
            'spinner': `
                <div class="court-spinner"></div>
            `
        };

        return animations[animation] || animations['justice-scales'];
    }

    hide() {
        if (this.loadingElement) {
            this.loadingElement.classList.add('hidden');
            document.body.style.overflow = '';
            
            setTimeout(() => {
                if (this.loadingElement) {
                    this.loadingElement.innerHTML = '';
                }
            }, 500);
        }

        console.log('Court loader hidden');
    }

    // Public API methods
    showJusticeScales(text = null, duration = null) {
        this.show('default', {
            animation: 'justice-scales',
            customText: text,
            duration: duration
        });
    }

    showGavel(text = null, duration = null) {
        this.show('default', {
            animation: 'gavel',
            customText: text,
            duration: duration
        });
    }

    showDocumentProcessing(text = null, duration = null) {
        this.show('document_processing', {
            animation: 'document-processor',
            customText: text,
            duration: duration,
            showProgress: true
        });
    }

    showCourthouse(text = null, duration = null) {
        this.show('default', {
            animation: 'courthouse',
            customText: text,
            duration: duration
        });
    }

    showLegalCode(text = null, duration = null) {
        this.show('chatbot', {
            animation: 'legal-code',
            customText: text,
            duration: duration
        });
    }

    // Utility methods
    isVisible() {
        return this.loadingElement && !this.loadingElement.classList.contains('hidden');
    }

    getCurrentAnimation() {
        return this.currentAnimation;
    }

    setCustomTexts(context, texts) {
        this.loadingTexts[context] = texts;
    }

    // Demo method for testing
    demo() {
        const animations = this.animations;
        let index = 0;

        const showNext = () => {
            if (index < animations.length) {
                this.show('default', {
                    animation: animations[index],
                    customText: {
                        main: `Demonstração: ${animations[index]}`,
                        sub: `Animação ${index + 1} de ${animations.length}`
                    },
                    duration: 3000
                });
                index++;
                setTimeout(showNext, 3500);
            }
        };

        showNext();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.courtLoader = new CourtLoadingManager();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CourtLoadingManager;
}