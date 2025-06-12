/**
 * Arquivo JavaScript modernizado para o site da 2ª Vara Cível de Cariacica
 * Contém funções otimizadas para interatividade, acessibilidade e experiência do usuário
 */

// Namespace principal para evitar conflitos
const AvaraApp = {
    // Configurações globais
    config: {
        animationDuration: 300,
        prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
        highContrast: localStorage.getItem('high-contrast') === 'true',
        largeText: localStorage.getItem('large-text') === 'true',
        increasedSpacing: localStorage.getItem('increased-spacing') === 'true'
    },
    
    // Inicialização do aplicativo
    init: function() {
        // Inicializar componentes
        this.setupAccessibility();
        this.setupNavigation();
        this.setupAnimations();
        this.setupTutorials();
        this.setupForms();
        this.setupChatbot();
        this.setupCounters();
        
        // Registrar eventos globais
        window.addEventListener('resize', this.handleResize.bind(this));
        document.addEventListener('keydown', this.handleKeyboardNavigation.bind(this));
        
        // Notificar que a inicialização está completa
        console.log('AvaraApp inicializado com sucesso');
    },
    
    // Configurações de acessibilidade
    setupAccessibility: function() {
        // Aplicar configurações salvas
        if (this.config.highContrast) {
            document.body.classList.add('high-contrast');
        }
        
        if (this.config.largeText) {
            document.body.classList.add('large-text');
        }
        
        if (this.config.increasedSpacing) {
            document.body.classList.add('increased-spacing');
        }
        
        // Configurar painel de acessibilidade
        const accessibilityToggle = document.getElementById('accessibility-toggle');
        const accessibilityPanel = document.getElementById('accessibility-panel');
        
        if (accessibilityToggle && accessibilityPanel) {
            accessibilityToggle.addEventListener('click', function() {
                accessibilityPanel.classList.toggle('active');
                
                // Atualizar atributo aria-expanded
                const isExpanded = accessibilityPanel.classList.contains('active');
                accessibilityToggle.setAttribute('aria-expanded', isExpanded);
            });
            
            // Configurar opções de acessibilidade
            const highContrastToggle = document.getElementById('high-contrast-toggle');
            const largeTextToggle = document.getElementById('large-text-toggle');
            const increasedSpacingToggle = document.getElementById('increased-spacing-toggle');
            
            if (highContrastToggle) {
                highContrastToggle.checked = this.config.highContrast;
                highContrastToggle.addEventListener('change', function() {
                    document.body.classList.toggle('high-contrast');
                    localStorage.setItem('high-contrast', this.checked);
                });
            }
            
            if (largeTextToggle) {
                largeTextToggle.checked = this.config.largeText;
                largeTextToggle.addEventListener('change', function() {
                    document.body.classList.toggle('large-text');
                    localStorage.setItem('large-text', this.checked);
                });
            }
            
            if (increasedSpacingToggle) {
                increasedSpacingToggle.checked = this.config.increasedSpacing;
                increasedSpacingToggle.addEventListener('change', function() {
                    document.body.classList.toggle('increased-spacing');
                    localStorage.setItem('increased-spacing', this.checked);
                });
            }
        }
        
        // Adicionar skip link para acessibilidade
        const skipLink = document.querySelector('.skip-link');
        if (skipLink) {
            skipLink.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.setAttribute('tabindex', '-1');
                    target.focus();
                }
            });
        }
    },
    
    // Configurações de navegação
    setupNavigation: function() {
        // Header fixo com transição
        const header = document.querySelector('.header-section');
        if (header) {
            window.addEventListener('scroll', function() {
                if (window.scrollY > 50) {
                    header.classList.add('header-scrolled');
                } else {
                    header.classList.remove('header-scrolled');
                }
            });
        }
        
        // Dropdown de navegação móvel
        const navbarToggler = document.querySelector('.navbar-toggler');
        if (navbarToggler) {
            navbarToggler.addEventListener('click', function() {
                // Adicionar classe para animação
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse) {
                    if (navbarCollapse.classList.contains('show')) {
                        navbarCollapse.classList.add('collapsing-out');
                        setTimeout(() => {
                            navbarCollapse.classList.remove('collapsing-out');
                        }, 300);
                    }
                }
            });
        }
        
        // Destacar item de navegação ativo
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const linkPath = link.getAttribute('href');
            if (linkPath && currentPath.includes(linkPath) && linkPath !== '/') {
                link.classList.add('active');
                
                // Se estiver em um dropdown, destacar também o item pai
                const dropdownParent = link.closest('.dropdown');
                if (dropdownParent) {
                    const dropdownToggle = dropdownParent.querySelector('.dropdown-toggle');
                    if (dropdownToggle) {
                        dropdownToggle.classList.add('active');
                    }
                }
            } else if (linkPath === '/' && currentPath === '/') {
                link.classList.add('active');
            }
        });
    },
    
    // Configurações de animações
    setupAnimations: function() {
        // Pular animações se o usuário preferir movimento reduzido
        if (this.config.prefersReducedMotion) {
            return;
        }
        
        // Animações de entrada
        const animateElements = document.querySelectorAll('.animate-fade-in, .animate-slide-up, .animate-slide-in');
        
        if (animateElements.length > 0) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animated');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });
            
            animateElements.forEach(element => {
                observer.observe(element);
            });
        }
    },
    
    // Configurações de tutoriais
    setupTutorials: function() {
        // Toggle entre GIF e imagens estáticas
        const tutorialToggles = document.querySelectorAll('.zoom-tutorial-toggle');
        
        tutorialToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const gifContainer = this.closest('.tutorial-container').querySelector('.zoom-tutorial-gif');
                const imagesContainer = this.closest('.tutorial-container').querySelector('.zoom-tutorial-images');
                
                if (gifContainer && imagesContainer) {
                    if (gifContainer.style.display === 'none') {
                        gifContainer.style.display = 'block';
                        imagesContainer.style.display = 'none';
                        this.innerHTML = '<i class="fas fa-images me-2"></i>Ver passo a passo em imagens';
                    } else {
                        gifContainer.style.display = 'none';
                        imagesContainer.style.display = 'block';
                        this.innerHTML = '<i class="fas fa-play-circle me-2"></i>Ver animação completa';
                    }
                }
            });
        });
        
        // Zoom para imagens
        const tutorialImages = document.querySelectorAll('.tutorial-image, .tutorial-gif');
        
        tutorialImages.forEach(image => {
            image.addEventListener('click', function() {
                // Verificar se já existe um overlay
                let overlay = document.querySelector('.tutorial-zoom-overlay');
                
                if (!overlay) {
                    // Criar overlay
                    overlay = document.createElement('div');
                    overlay.className = 'tutorial-zoom-overlay';
                    
                    // Criar imagem ampliada
                    const zoomImage = document.createElement('img');
                    zoomImage.className = 'tutorial-zoom-image';
                    zoomImage.src = this.src;
                    zoomImage.alt = this.alt;
                    
                    // Criar botão de fechar
                    const closeButton = document.createElement('button');
                    closeButton.className = 'tutorial-zoom-close';
                    closeButton.innerHTML = '<i class="fas fa-times"></i>';
                    closeButton.setAttribute('aria-label', 'Fechar imagem ampliada');
                    
                    // Criar legenda
                    const caption = document.createElement('div');
                    caption.className = 'tutorial-zoom-caption';
                    caption.textContent = this.alt;
                    
                    // Adicionar elementos ao overlay
                    overlay.appendChild(zoomImage);
                    overlay.appendChild(closeButton);
                    overlay.appendChild(caption);
                    
                    // Adicionar overlay ao body
                    document.body.appendChild(overlay);
                    
                    // Adicionar evento de fechar
                    closeButton.addEventListener('click', function() {
                        overlay.classList.remove('active');
                        setTimeout(() => {
                            overlay.remove();
                        }, 300);
                    });
                    
                    // Adicionar evento de fechar com ESC
                    document.addEventListener('keydown', function(e) {
                        if (e.key === 'Escape') {
                            closeButton.click();
                        }
                    });
                    
                    // Adicionar evento de fechar com clique fora da imagem
                    overlay.addEventListener('click', function(e) {
                        if (e.target === overlay) {
                            closeButton.click();
                        }
                    });
                    
                    // Mostrar overlay
                    setTimeout(() => {
                        overlay.classList.add('active');
                    }, 10);
                }
            });
        });
    },
    
    // Configurações de formulários
    setupForms: function() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // Adicionar validação em tempo real
            const inputs = form.querySelectorAll('input, textarea, select');
            
            inputs.forEach(input => {
                // Validar ao perder o foco
                input.addEventListener('blur', function() {
                    validateInput(this);
                });
                
                // Validar ao digitar (com debounce)
                let debounceTimeout;
                input.addEventListener('input', function() {
                    clearTimeout(debounceTimeout);
                    debounceTimeout = setTimeout(() => {
                        validateInput(this);
                    }, 500);
                });
            });
            
            // Validar ao enviar
            form.addEventListener('submit', function(e) {
                let isValid = true;
                
                inputs.forEach(input => {
                    if (!validateInput(input)) {
                        isValid = false;
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    
                    // Focar no primeiro campo inválido
                    const firstInvalid = form.querySelector('.is-invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                    }
                    
                    // Mostrar mensagem de erro
                    const formError = form.querySelector('.form-error-message');
                    if (formError) {
                        formError.style.display = 'block';
                        
                        // Rolar para a mensagem de erro
                        formError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
            });
            
            // Função para validar input
            function validateInput(input) {
                // Pular elementos desabilitados ou somente leitura
                if (input.disabled || input.readOnly) {
                    return true;
                }
                
                let isValid = true;
                const errorElement = input.nextElementSibling?.classList.contains('invalid-feedback') 
                    ? input.nextElementSibling 
                    : null;
                
                // Verificar se é obrigatório
                if (input.hasAttribute('required') && !input.value.trim()) {
                    isValid = false;
                    setInvalidState(input, errorElement, 'Este campo é obrigatório');
                }
                
                // Verificar tipo de email
                else if (input.type === 'email' && input.value.trim() && !validateEmail(input.value)) {
                    isValid = false;
                    setInvalidState(input, errorElement, 'Digite um email válido');
                }
                
                // Verificar CPF
                else if (input.dataset.type === 'cpf' && input.value.trim() && !validateCPF(input.value)) {
                    isValid = false;
                    setInvalidState(input, errorElement, 'Digite um CPF válido');
                }
                
                // Verificar número de processo
                else if (input.dataset.type === 'processo' && input.value.trim() && !validateProcesso(input.value)) {
                    isValid = false;
                    setInvalidState(input, errorElement, 'Digite um número de processo válido');
                }
                
                // Verificar padrão personalizado
                else if (input.pattern && input.value.trim()) {
                    const regex = new RegExp(input.pattern);
                    if (!regex.test(input.value)) {
                        isValid = false;
                        setInvalidState(input, errorElement, input.dataset.errorMessage || 'Formato inválido');
                    }
                }
                
                // Verificar comprimento mínimo
                else if (input.minLength && input.value.trim() && input.value.length < input.minLength) {
                    isValid = false;
                    setInvalidState(input, errorElement, `Mínimo de ${input.minLength} caracteres`);
                }
                
                // Se válido, remover classes de erro
                if (isValid) {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                    
                    if (errorElement) {
                        errorElement.textContent = '';
                    }
                }
                
                return isValid;
            }
            
            // Função para definir estado inválido
            function setInvalidState(input, errorElement, message) {
                input.classList.remove('is-valid');
                input.classList.add('is-invalid');
                
                if (errorElement) {
                    errorElement.textContent = message;
                }
            }
            
            // Funções de validação específicas
            function validateEmail(email) {
                const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return re.test(email);
            }
            
            function validateCPF(cpf) {
                cpf = cpf.replace(/[^\d]/g, '');
                
                if (cpf.length !== 11 || /^(.)\1+$/.test(cpf)) {
                    return false;
                }
                
                // Validação completa de CPF omitida para brevidade
                return true;
            }
            
            function validateProcesso(processo) {
                // Formato CNJ: NNNNNNN-NN.NNNN.N.NN.NNNN
                const re = /^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$/;
                return re.test(processo);
            }
        });
    },
    
    // Configurações do chatbot
    setupChatbot: function() {
        const chatbotToggle = document.getElementById('chatbot-toggle');
        const chatbotWindow = document.getElementById('chatbot-window');
        const chatbotClose = document.getElementById('chatbot-close');
        const chatbotInput = document.getElementById('chatbot-input');
        const chatbotSend = document.getElementById('chatbot-send');
        const chatbotMessages = document.getElementById('chatbot-messages');
        const chatbotSuggestions = document.querySelectorAll('.chatbot-suggestion');
        
        if (chatbotToggle && chatbotWindow) {
            // Alternar visibilidade do chatbot
            chatbotToggle.addEventListener('click', function() {
                chatbotWindow.style.display = chatbotWindow.style.display === 'none' ? 'flex' : 'none';
                
                // Focar no input quando abrir
                if (chatbotWindow.style.display === 'flex') {
                    chatbotInput.focus();
                    
                    // Rolar para o final das mensagens
                    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
                }
            });
            
            // Fechar chatbot
            chatbotClose.addEventListener('click', function() {
                chatbotWindow.style.display = 'none';
            });
            
            // Enviar mensagem
            function sendMessage() {
                const message = chatbotInput.value.trim();
                if (message === '') return;
                
                // Adicionar mensagem do usuário
                const userMessageElement = document.createElement('div');
                userMessageElement.classList.add('chatbot-message-user');
                userMessageElement.textContent = message;
                chatbotMessages.appendChild(userMessageElement);
                
                // Limpar input
                chatbotInput.value = '';
                
                // Rolar para o final
                chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
                
                // Mostrar indicador de digitação
                const typingElement = document.createElement('div');
                typingElement.classList.add('chatbot-typing');
                typingElement.id = 'chatbot-typing';
                
                for (let i = 0; i < 3; i++) {
                    const dot = document.createElement('div');
                    dot.classList.add('chatbot-typing-dot');
                    typingElement.appendChild(dot);
                }
                
                chatbotMessages.appendChild(typingElement);
                chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
                
                // Simular resposta do chatbot após um pequeno atraso
                setTimeout(() => {
                    // Remover indicador de digitação
                    const typingIndicator = document.getElementById('chatbot-typing');
                    if (typingIndicator) {
                        typingIndicator.remove();
                    }
                    
                    // Adicionar resposta do bot
                    const botMessageElement = document.createElement('div');
                    botMessageElement.classList.add('chatbot-message-bot');
                    
                    // Resposta simulada baseada na mensagem
                    let response = "Obrigado por sua mensagem. Um de nossos atendentes irá analisá-la em breve.";
                    
                    const lowerMessage = message.toLowerCase();
                    if (lowerMessage.includes('processo') || lowerMessage.includes('consulta')) {
                        response = "Para consultar seu processo, você precisa do número no formato CNJ. Com esse número, você pode acessar a consulta processual no menu Serviços > Consulta Processual.";
                    } else if (lowerMessage.includes('audiência') || lowerMessage.includes('audiencia') || lowerMessage.includes('zoom')) {
                        response = "As audiências podem ser realizadas de forma híbrida. Você pode participar presencialmente ou pelo aplicativo Zoom. Temos um tutorial disponível em Serviços > Tutorial Zoom.";
                    } else if (lowerMessage.includes('horário') || lowerMessage.includes('horario') || lowerMessage.includes('funcionamento')) {
                        response = "A 2ª Vara Cível de Cariacica funciona das 12h às 18h em dias úteis.";
                    } else if (lowerMessage.includes('contato') || lowerMessage.includes('telefone') || lowerMessage.includes('email')) {
                        response = "Você pode entrar em contato pelo telefone (27) 3246-XXXX ou pelo e-mail 2varacivel.cariacica@tjes.jus.br.";
                    }
                    
                    botMessageElement.textContent = response;
                    chatbotMessages.appendChild(botMessageElement);
                    
                    // Rolar para o final
                    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
                }, 1500);
            }
            
            // Enviar ao clicar no botão
            chatbotSend.addEventListener('click', sendMessage);
            
            // Enviar ao pressionar Enter
            chatbotInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Usar sugestões de perguntas
            chatbotSuggestions.forEach(suggestion => {
                suggestion.addEventListener('click', function() {
                    const message = this.textContent;
                    chatbotInput.value = message;
                    sendMessage();
                });
            });
        }
    },
    
    // Configurações de contadores
    setupCounters: function() {
        // Pular animações se o usuário preferir movimento reduzido
        if (this.config.prefersReducedMotion) {
            // Definir valores finais diretamente
            const counters = document.querySelectorAll('.counter-value');
            counters.forEach(counter => {
                const target = parseInt(counter.getAttribute('data-target'));
                counter.textContent = target;
            });
            return;
        }
        
        // Animação de contadores
        const counters = document.querySelectorAll('.counter-value');
        const speed = 200; // Velocidade da animação (ms)
        
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        let count = 0;
                        const increment = target / speed;
                        
                        const updateCount = () => {
                            if (count < target) {
                                count += increment;
                                counter.textContent = Math.floor(count);
                                requestAnimationFrame(updateCount);
                            } else {
                                counter.textContent = target;
                            }
                        };
                        
                        updateCount();
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });
            
            observer.observe(counter);
        });
    },
    
    // Manipulador de redimensionamento
    handleResize: function() {
        // Implementar lógica de redimensionamento se necessário
    },
    
    // Manipulador de navegação por teclado
    handleKeyboardNavigation: function(e) {
        // Implementar atalhos de teclado globais
        if (e.altKey && e.key === 'a') {
            // Alt+A: Abrir painel de acessibilidade
            const accessibilityToggle = document.getElementById('accessibility-toggle');
            if (accessibilityToggle) {
                accessibilityToggle.click();
            }
        }
    }
};

// Inicializar aplicativo quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    AvaraApp.init();
});
