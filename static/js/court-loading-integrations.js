/*!
 * Court Loading Integrations
 * 2ª Vara Cível de Cariacica - Smart Loading Integration
 * Automatically applies court-themed loading animations to forms and actions
 */

(function() {
    'use strict';

    // Wait for court loader to be available
    function waitForCourtLoader(callback, maxAttempts = 50) {
        let attempts = 0;
        const checkInterval = setInterval(() => {
            attempts++;
            if (window.courtLoader || attempts >= maxAttempts) {
                clearInterval(checkInterval);
                if (window.courtLoader) {
                    callback();
                } else {
                    console.warn('Court Loading Manager not available');
                }
            }
        }, 100);
    }

    // Form integration
    function integrateWithForms() {
        // Contact form
        const contactForm = document.querySelector('form[action*="contato"]');
        if (contactForm) {
            contactForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                window.courtLoader.show('contact', {
                    animation: 'document-processor',
                    showProgress: true
                });

                // Simulate form processing
                setTimeout(() => {
                    // Actually submit the form
                    this.submit();
                }, 1000);
            });
        }

        // Process consultation form
        const processForm = document.querySelector('form[action*="consulta"]');
        if (processForm) {
            processForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                window.courtLoader.show('process_consultation', {
                    animation: 'justice-scales',
                    showProgress: true
                });

                setTimeout(() => {
                    this.submit();
                }, 1500);
            });
        }

        // Scheduling form
        const schedulingForm = document.querySelector('form[action*="agendamento"]');
        if (schedulingForm) {
            schedulingForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                window.courtLoader.show('scheduling', {
                    animation: 'courthouse',
                    showProgress: true
                });

                setTimeout(() => {
                    this.submit();
                }, 1200);
            });
        }

        // All other forms - generic loading
        const otherForms = document.querySelectorAll('form:not([action*="contato"]):not([action*="consulta"]):not([action*="agendamento"])');
        otherForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                window.courtLoader.show('default', {
                    animation: 'spinner',
                    duration: 2000
                });

                setTimeout(() => {
                    this.submit();
                }, 800);
            });
        });
    }

    // Navigation integration
    function integrateWithNavigation() {
        // Service links
        const serviceLinks = document.querySelectorAll('a[href*="/servicos/"]');
        serviceLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                
                if (href.includes('balcao-virtual')) {
                    window.courtLoader.show('default', {
                        animation: 'courthouse',
                        customText: {
                            main: "Acessando Balcão Virtual...",
                            sub: "Carregando serviços online"
                        },
                        duration: 1500
                    });
                } else if (href.includes('consulta')) {
                    window.courtLoader.show('process_consultation', {
                        animation: 'justice-scales',
                        duration: 1200
                    });
                } else if (href.includes('agendamento')) {
                    window.courtLoader.show('scheduling', {
                        animation: 'courthouse',
                        duration: 1000
                    });
                }
            });
        });

        // External links (TJES portal, etc.)
        const externalLinks = document.querySelectorAll('a[href^="http"]:not([href*="localhost"]):not([href*="replit.dev"])');
        externalLinks.forEach(link => {
            link.addEventListener('click', function() {
                window.courtLoader.show('default', {
                    animation: 'legal-code',
                    customText: {
                        main: "Redirecionando...",
                        sub: "Acessando portal externo"
                    },
                    duration: 2000
                });
            });
        });
    }

    // Chatbot integration
    function integrateWithChatbot() {
        // Enhanced chatbot integration
        const chatMessages = document.querySelector('.chat-messages');
        const chatInput = document.querySelector('#user-input');
        const sendButton = document.querySelector('#send-message');

        if (chatInput && sendButton) {
            sendButton.addEventListener('click', function() {
                const message = chatInput.value.trim();
                if (message) {
                    // Show brief loading for chatbot response
                    window.courtLoader.show('chatbot', {
                        animation: 'legal-code',
                        customText: {
                            main: "Consultando assistente jurídico...",
                            sub: "Processando sua pergunta"
                        },
                        duration: 1500
                    });
                }
            });

            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendButton.click();
                }
            });
        }
    }

    // AJAX request integration
    function integrateWithAjax() {
        // Enhance existing fetch wrapper to show contextual loading
        if (window.fetch) {
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                const options = args[1] || {};
                
                // Determine loading context from URL
                let context = 'default';
                let animation = 'spinner';
                
                if (typeof url === 'string') {
                    if (url.includes('chatbot') || url.includes('chat')) {
                        context = 'chatbot';
                        animation = 'legal-code';
                    } else if (url.includes('contact') || url.includes('contato')) {
                        context = 'contact';
                        animation = 'document-processor';
                    } else if (url.includes('process') || url.includes('consulta')) {
                        context = 'process_consultation';
                        animation = 'justice-scales';
                    } else if (url.includes('schedule') || url.includes('agendamento')) {
                        context = 'scheduling';
                        animation = 'courthouse';
                    }
                }

                // Only show loading for non-GET requests or specific endpoints
                const method = options.method || 'GET';
                if (method !== 'GET' || url.includes('/api/') || url.includes('/chatbot/')) {
                    window.courtLoader.show(context, {
                        animation: animation,
                        duration: null // Will be hidden when response arrives
                    });
                }

                return originalFetch.apply(this, args)
                    .then(response => {
                        // Hide loading on success
                        setTimeout(() => window.courtLoader.hide(), 300);
                        return response;
                    })
                    .catch(error => {
                        // Hide loading on error
                        setTimeout(() => window.courtLoader.hide(), 300);
                        throw error;
                    });
            };
        }
    }

    // Page transition effects
    function integratePageTransitions() {
        // Show loading during page transitions
        window.addEventListener('beforeunload', function() {
            window.courtLoader.show('default', {
                animation: 'courthouse',
                customText: {
                    main: "Carregando página...",
                    sub: "Aguarde um momento"
                }
            });
        });

        // Hide loading when page loads
        window.addEventListener('load', function() {
            setTimeout(() => {
                if (window.courtLoader && window.courtLoader.isVisible()) {
                    window.courtLoader.hide();
                }
            }, 500);
        });

        // Handle back/forward navigation
        window.addEventListener('popstate', function() {
            window.courtLoader.show('default', {
                animation: 'spinner',
                duration: 800
            });
        });
    }

    // Special integrations for specific pages
    function integrateSpecialPages() {
        const currentPath = window.location.pathname;

        // Judge page - special animation
        if (currentPath.includes('/juiz')) {
            setTimeout(() => {
                window.courtLoader.show('default', {
                    animation: 'gavel',
                    customText: {
                        main: "Carregando informações do magistrado...",
                        sub: "Preparando dados da vara"
                    },
                    duration: 2000
                });
            }, 500);
        }

        // News page - document processing
        if (currentPath.includes('/noticias')) {
            setTimeout(() => {
                window.courtLoader.show('default', {
                    animation: 'document-processor',
                    customText: {
                        main: "Carregando notícias...",
                        sub: "Buscando informações atualizadas"
                    },
                    duration: 1500
                });
            }, 300);
        }

        // FAQ page - legal code
        if (currentPath.includes('/faq')) {
            setTimeout(() => {
                window.courtLoader.show('default', {
                    animation: 'legal-code',
                    customText: {
                        main: "Carregando perguntas frequentes...",
                        sub: "Organizando informações jurídicas"
                    },
                    duration: 1200
                });
            }, 400);
        }
    }

    // Accessibility integration
    function integrateAccessibility() {
        // Respect user's motion preferences
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        if (prefersReducedMotion) {
            // Disable automatic loading animations for accessibility
            console.log('Reduced motion preference detected - limiting loading animations');
            
            // Override courtLoader to use simpler animations
            if (window.courtLoader) {
                const originalShow = window.courtLoader.show;
                window.courtLoader.show = function(context, options = {}) {
                    options.animation = 'spinner'; // Always use simple spinner
                    options.duration = Math.min(options.duration || 1000, 1000); // Max 1 second
                    return originalShow.call(this, context, options);
                };
            }
        }

        // Keyboard accessibility
        document.addEventListener('keydown', function(e) {
            // ESC key hides loading
            if (e.key === 'Escape' && window.courtLoader && window.courtLoader.isVisible()) {
                window.courtLoader.hide();
            }
        });
    }

    // Error handling
    function setupErrorHandling() {
        window.addEventListener('error', function() {
            // Hide loading on JavaScript errors
            if (window.courtLoader && window.courtLoader.isVisible()) {
                window.courtLoader.hide();
            }
        });

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', function() {
            if (window.courtLoader && window.courtLoader.isVisible()) {
                window.courtLoader.hide();
            }
        });
    }

    // Performance monitoring
    function setupPerformanceMonitoring() {
        // Track loading animation performance
        let loadingStartTime = null;
        
        if (window.courtLoader) {
            const originalShow = window.courtLoader.show;
            const originalHide = window.courtLoader.hide;
            
            window.courtLoader.show = function(...args) {
                loadingStartTime = performance.now();
                return originalShow.apply(this, args);
            };
            
            window.courtLoader.hide = function(...args) {
                if (loadingStartTime) {
                    const duration = performance.now() - loadingStartTime;
                    console.log(`Loading animation displayed for ${Math.round(duration)}ms`);
                    loadingStartTime = null;
                }
                return originalHide.apply(this, args);
            };
        }
    }

    // Initialize all integrations
    function initialize() {
        console.log('Initializing Court Loading Integrations...');
        
        integrateWithForms();
        integrateWithNavigation();
        integrateWithChatbot();
        integrateWithAjax();
        integratePageTransitions();
        integrateSpecialPages();
        integrateAccessibility();
        setupErrorHandling();
        setupPerformanceMonitoring();
        
        console.log('Court Loading Integrations initialized successfully');
    }

    // Wait for DOM and court loader, then initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            waitForCourtLoader(initialize);
        });
    } else {
        waitForCourtLoader(initialize);
    }

})();