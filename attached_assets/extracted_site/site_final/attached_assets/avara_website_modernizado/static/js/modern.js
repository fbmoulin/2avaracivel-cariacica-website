/**
 * Modernização do JavaScript - 2ª Vara Cível de Cariacica
 * Funções e comportamentos modernos para melhorar a interatividade do site
 */

// Esperar pelo carregamento completo do DOM
document.addEventListener('DOMContentLoaded', function() {
  // Inicializar componentes modernos
  initModernComponents();
  
  // Configurar animações de entrada
  setupScrollAnimations();
  
  // Inicializar chatbot moderno
  initModernChatbot();
  
  // Configurar tutoriais interativos
  setupTutorials();
  
  // Inicializar acessibilidade aprimorada
  initAccessibilityFeatures();
});

/**
 * Inicializa todos os componentes modernos da UI
 */
function initModernComponents() {
  // Adicionar classe moderna ao body para ativar estilos
  document.body.classList.add('modern-ui');
  
  // Inicializar dropdowns modernos
  const dropdowns = document.querySelectorAll('.dropdown-toggle');
  dropdowns.forEach(dropdown => {
    dropdown.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      const menu = this.nextElementSibling;
      const isOpen = menu.classList.contains('show');
      
      // Fechar todos os dropdowns abertos
      document.querySelectorAll('.dropdown-menu.show').forEach(openMenu => {
        if (openMenu !== menu) {
          openMenu.classList.remove('show');
        }
      });
      
      // Alternar o estado do dropdown atual
      menu.classList.toggle('show');
      
      // Adicionar listener para fechar ao clicar fora
      if (!isOpen) {
        document.addEventListener('click', function closeDropdown(e) {
          if (!menu.contains(e.target) && e.target !== dropdown) {
            menu.classList.remove('show');
            document.removeEventListener('click', closeDropdown);
          }
        });
      }
    });
  });
  
  // Inicializar accordions modernos
  const accordionButtons = document.querySelectorAll('.accordion-button-modern');
  accordionButtons.forEach(button => {
    button.addEventListener('click', function() {
      const isCollapsed = this.classList.contains('collapsed');
      const target = document.querySelector(this.getAttribute('data-bs-target'));
      
      if (isCollapsed) {
        this.classList.remove('collapsed');
        target.classList.add('show');
        target.style.maxHeight = target.scrollHeight + 'px';
      } else {
        this.classList.add('collapsed');
        target.classList.remove('show');
        target.style.maxHeight = '0';
      }
    });
  });
  
  // Adicionar efeito de ripple aos botões
  const buttons = document.querySelectorAll('.btn');
  buttons.forEach(button => {
    button.addEventListener('click', function(e) {
      const rect = button.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const ripple = document.createElement('span');
      ripple.classList.add('ripple');
      ripple.style.left = x + 'px';
      ripple.style.top = y + 'px';
      
      this.appendChild(ripple);
      
      setTimeout(() => {
        ripple.remove();
      }, 600);
    });
  });
  
  // Inicializar tooltips
  const tooltips = document.querySelectorAll('[data-tooltip]');
  tooltips.forEach(tooltip => {
    tooltip.addEventListener('mouseenter', function() {
      const tooltipText = this.getAttribute('data-tooltip');
      const tooltipEl = document.createElement('div');
      tooltipEl.classList.add('tooltip-modern');
      tooltipEl.textContent = tooltipText;
      
      document.body.appendChild(tooltipEl);
      
      const rect = this.getBoundingClientRect();
      tooltipEl.style.top = (rect.top - tooltipEl.offsetHeight - 10) + 'px';
      tooltipEl.style.left = (rect.left + (rect.width / 2) - (tooltipEl.offsetWidth / 2)) + 'px';
      
      tooltipEl.classList.add('show');
      
      this.addEventListener('mouseleave', function onMouseLeave() {
        tooltipEl.classList.remove('show');
        setTimeout(() => {
          tooltipEl.remove();
        }, 200);
        this.removeEventListener('mouseleave', onMouseLeave);
      });
    });
  });
  
  // Inicializar contadores animados
  const counters = document.querySelectorAll('.counter-value');
  counters.forEach(counter => {
    const target = parseInt(counter.getAttribute('data-target'));
    const duration = 2000; // 2 segundos
    const step = target / (duration / 16); // 60fps
    let current = 0;
    
    const updateCounter = () => {
      current += step;
      if (current < target) {
        counter.textContent = Math.floor(current);
        requestAnimationFrame(updateCounter);
      } else {
        counter.textContent = target;
      }
    };
    
    // Iniciar contador quando elemento estiver visível
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          updateCounter();
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    
    observer.observe(counter);
  });
}

/**
 * Configura animações baseadas em scroll
 */
function setupScrollAnimations() {
  // Verificar se o navegador prefere movimento reduzido
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) return;
  
  // Elementos para animar ao scroll
  const animatedElements = document.querySelectorAll('.animate-on-scroll');
  
  // Configurar o observador de interseção
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animated');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  
  // Observar cada elemento
  animatedElements.forEach(element => {
    observer.observe(element);
  });
  
  // Adicionar classes de animação com atraso para elementos em sequência
  const staggeredElements = document.querySelectorAll('.staggered-animation');
  staggeredElements.forEach((element, index) => {
    element.style.animationDelay = (index * 0.1) + 's';
  });
}

/**
 * Inicializa o chatbot moderno
 */
function initModernChatbot() {
  const chatbotToggle = document.getElementById('chatbot-toggle');
  const chatbotWindow = document.getElementById('chatbot-window');
  const chatbotClose = document.getElementById('chatbot-close');
  const chatbotInput = document.getElementById('chatbot-input');
  const chatbotSend = document.getElementById('chatbot-send');
  const chatbotMessages = document.getElementById('chatbot-messages');
  const chatbotSuggestions = document.querySelectorAll('.chatbot-suggestion');
  
  if (!chatbotToggle) return;
  
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
    addUserMessage(message);
    
    // Limpar input
    chatbotInput.value = '';
    
    // Mostrar indicador de digitação
    showTypingIndicator();
    
    // Simular resposta do chatbot após um pequeno atraso
    setTimeout(() => {
      // Remover indicador de digitação
      removeTypingIndicator();
      
      // Adicionar resposta do bot
      addBotMessage(getChatbotResponse(message));
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
  
  // Função para adicionar mensagem do usuário
  function addUserMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('chatbot-message-modern', 'chatbot-message-user');
    messageElement.textContent = message;
    chatbotMessages.appendChild(messageElement);
    
    // Rolar para o final
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }
  
  // Função para adicionar mensagem do bot
  function addBotMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('chatbot-message-modern', 'chatbot-message-bot');
    messageElement.textContent = message;
    chatbotMessages.appendChild(messageElement);
    
    // Rolar para o final
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }
  
  // Função para mostrar indicador de digitação
  function showTypingIndicator() {
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
  }
  
  // Função para remover indicador de digitação
  function removeTypingIndicator() {
    const typingElement = document.getElementById('chatbot-typing');
    if (typingElement) {
      typingElement.remove();
    }
  }
  
  // Função para obter resposta do chatbot (simulada)
  function getChatbotResponse(message) {
    message = message.toLowerCase();
    
    if (message.includes('processo') || message.includes('consulta')) {
      return "Para consultar seu processo, você precisa do número no formato CNJ. Com esse número, você pode acessar a consulta processual no site do TJES.";
    } else if (message.includes('audiência') || message.includes('audiencia')) {
      return "As audiências podem ser realizadas de forma híbrida. Você pode participar presencialmente ou pelo aplicativo Zoom. Temos tutoriais disponíveis para ajudar na configuração.";
    } else if (message.includes('horário') || message.includes('horario') || message.includes('funcionamento')) {
      return "A 2ª Vara Cível de Cariacica funciona das 12h às 18h em dias úteis.";
    } else if (message.includes('contato') || message.includes('telefone') || message.includes('email')) {
      return "Você pode entrar em contato pelo telefone (27) 3246-XXXX ou pelo e-mail 2varacivel.cariacica@tjes.jus.br.";
    } else if (message.includes('juiz') || message.includes('titular')) {
      return "O Juiz Titular da 2ª Vara Cível de Cariacica é o Dr. Felipe Bertrand S. Moulin.";
    } else if (message.includes('endereço') || message.includes('endereco') || message.includes('localização')) {
      return "O endereço é: Fórum de Cariacica, Av. Principal, nº 100, Centro, Cariacica/ES.";
    } else if (message.includes('certidão') || message.includes('certidao')) {
      return "Para solicitar certidões, acesse o serviço 'Certidões Online' em nosso site ou compareça pessoalmente à vara.";
    } else if (message.includes('prazo')) {
      return "Os prazos processuais variam conforme o tipo de ato. Em geral: 15 dias para contestação, 15 dias para recurso de apelação, 5 dias para embargos de declaração. Consulte seu advogado para orientações específicas.";
    } else if (message.includes('documento')) {
      return "Para informações sobre documentos necessários para cada tipo de procedimento, consulte a seção de FAQ do nosso site ou entre em contato com a secretaria da vara.";
    } else if (message.includes('zoom') || message.includes('tutorial')) {
      return "Temos tutoriais disponíveis sobre como configurar e usar o Zoom para audiências virtuais. Acesse a seção de Tutoriais em nosso site para mais informações.";
    } else {
      return "Olá! Sou o assistente virtual da 2ª Vara Cível de Cariacica. Como posso ajudar você hoje? Posso fornecer informações sobre processos, audiências, horários de funcionamento, entre outros serviços.";
    }
  }
}

/**
 * Configura tutoriais interativos com GIFs e imagens
 */
function setupTutorials() {
  // Alternar entre GIF e imagens estáticas
  const tutorialToggles = document.querySelectorAll('.tutorial-toggle');
  tutorialToggles.forEach(toggle => {
    toggle.addEventListener('click', function() {
      const tutorialId = this.getAttribute('data-tutorial');
      const gif = document.querySelector(`.tutorial-gif[data-tutorial="${tutorialId}"]`);
      const images = document.querySelector(`.tutorial-images[data-tutorial="${tutorialId}"]`);
      
      if (gif.style.display === 'none') {
        gif.style.display = 'block';
        images.style.display = 'none';
        this.textContent = 'Ver passo a passo';
      } else {
        gif.style.display = 'none';
        images.style.display = 'block';
        this.textContent = 'Ver animação';
      }
    });
  });
  
  // Zoom em imagens de tutorial
  const tutorialImages = document.querySelectorAll('.tutorial-image');
  tutorialImages.forEach(image => {
    image.addEventListener('click', function() {
      // Criar overlay para zoom
      const overlay = document.createElement('div');
      overlay.classList.add('image-zoom-overlay');
      
      // Criar imagem ampliada
      const zoomedImage = document.createElement('img');
      zoomedImage.src = this.src;
      zoomedImage.classList.add('image-zoomed');
      
      // Adicionar ao overlay
      overlay.appendChild(zoomedImage);
      document.body.appendChild(overlay);
      
      // Fechar ao clicar
      overlay.addEventListener('click', function() {
        this.remove();
      });
    });
  });
}

/**
 * Inicializa recursos de acessibilidade aprimorados
 */
function initAccessibilityFeatures() {
  // Aumentar tamanho da fonte
  const increaseFontBtn = document.querySelector('.increase-font-btn');
  if (increaseFontBtn) {
    increaseFontBtn.addEventListener('click', function() {
      document.body.classList.toggle('font-size-increased');
      document.body.classList.remove('font-size-decreased');
      
      // Salvar preferência
      localStorage.setItem('fontSizePreference', document.body.classList.contains('font-size-increased') ? 'increased' : 'normal');
    });
  }
  
  // Diminuir tamanho da fonte
  const decreaseFontBtn = document.querySelector('.decrease-font-btn');
  if (decreaseFontBtn) {
    decreaseFontBtn.addEventListener('click', function() {
      document.body.classList.toggle('font-size-decreased');
      document.body.classList.remove('font-size-increased');
      
      // Salvar preferência
      localStorage.setItem('fontSizePreference', document.body.classList.contains('font-size-decreased') ? 'decreased' : 'normal');
    });
  }
  
  // Alternar alto contraste
  const contrastBtn = document.querySelector('.contrast-btn');
  if (contrastBtn) {
    contrastBtn.addEventListener('click', function() {
      document.body.classList.toggle('high-contrast');
      
      // Salvar preferência
      localStorage.setItem('contrastPreference', document.body.classList.contains('high-contrast') ? 'high' : 'normal');
    });
  }
  
  // Restaurar preferências salvas
  const fontSizePreference = localStorage.getItem('fontSizePreference');
  if (fontSizePreference === 'increased') {
    document.body.classList.add('font-size-increased');
  } else if (fontSizePreference === 'decreased') {
    document.body.classList.add('font-size-decreased');
  }
  
  const contrastPreference = localStorage.getItem('contrastPreference');
  if (contrastPreference === 'high') {
    document.body.classList.add('high-contrast');
  }
  
  // Navegação por teclado aprimorada
  document.addEventListener('keydown', function(e) {
    // Alt + 1: Ir para o conteúdo principal
    if (e.altKey && e.key === '1') {
      e.preventDefault();
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        mainContent.focus();
        mainContent.scrollIntoView({ behavior: 'smooth' });
      }
    }
    
    // Alt + 2: Ir para o menu de navegação
    if (e.altKey && e.key === '2') {
      e.preventDefault();
      const navMenu = document.querySelector('.navbar-nav');
      if (navMenu) {
        const firstLink = navMenu.querySelector('a');
        if (firstLink) {
          firstLink.focus();
        }
      }
    }
    
    // Alt + 3: Ir para o rodapé
    if (e.altKey && e.key === '3') {
      e.preventDefault();
      const footer = document.querySelector('footer');
      if (footer) {
        footer.focus();
        footer.scrollIntoView({ behavior: 'smooth' });
      }
    }
    
    // Alt + 4: Abrir/fechar chatbot
    if (e.altKey && e.key === '4') {
      e.preventDefault();
      const chatbotToggle = document.getElementById('chatbot-toggle');
      if (chatbotToggle) {
        chatbotToggle.click();
      }
    }
    
    // Esc: Fechar modais, overlays, etc.
    if (e.key === 'Escape') {
      // Fechar overlays de zoom
      const overlay = document.querySelector('.image-zoom-overlay');
      if (overlay) {
        overlay.remove();
      }
      
      // Fechar chatbot
      const chatbotWindow = document.getElementById('chatbot-window');
      if (chatbotWindow && chatbotWindow.style.display !== 'none') {
        const chatbotClose = document.getElementById('chatbot-close');
        if (chatbotClose) {
          chatbotClose.click();
        }
      }
    }
  });
}

/**
 * Lazy loading de imagens para melhor performance
 */
function setupLazyLoading() {
  // Verificar se o navegador suporta IntersectionObserver
  if ('IntersectionObserver' in window) {
    const lazyImages = document.querySelectorAll('img.lazy');
    
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          
          if (img.dataset.srcset) {
            img.srcset = img.dataset.srcset;
          }
          
          img.classList.remove('lazy');
          imageObserver.unobserve(img);
        }
      });
    });
    
    lazyImages.forEach(img => {
      imageObserver.observe(img);
    });
  } else {
    // Fallback para navegadores que não suportam IntersectionObserver
    const lazyImages = document.querySelectorAll('img.lazy');
    lazyImages.forEach(img => {
      img.src = img.dataset.src;
      
      if (img.dataset.srcset) {
        img.srcset = img.dataset.srcset;
      }
      
      img.classList.remove('lazy');
    });
  }
}

// Inicializar lazy loading após o carregamento da página
window.addEventListener('load', setupLazyLoading);

/**
 * Detectar preferências do sistema
 */
function detectSystemPreferences() {
  // Detectar preferência de esquema de cores
  const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (prefersDarkMode) {
    // Preparado para implementação futura do modo escuro
    console.log('Usuário prefere modo escuro');
  }
  
  // Detectar preferência de movimento reduzido
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) {
    // Desativar animações
    document.body.classList.add('reduced-motion');
  }
}

// Detectar preferências do sistema ao carregar
detectSystemPreferences();

/**
 * Inicializar tutoriais específicos do Zoom
 */
function initZoomTutorials() {
  const zoomTutorialContainer = document.querySelector('.zoom-tutorial-container');
  if (!zoomTutorialContainer) return;
  
  // Carregar GIF do tutorial do Zoom
  const zoomGif = document.querySelector('.zoom-tutorial-gif');
  if (zoomGif) {
    // Verificar se o GIF já tem src definido
    if (!zoomGif.src && zoomGif.dataset.src) {
      // Mostrar indicador de carregamento
      const loadingIndicator = document.createElement('div');
      loadingIndicator.classList.add('loading-indicator');
      loadingIndicator.innerHTML = '<div class="spinner"></div><p>Carregando tutorial...</p>';
      zoomTutorialContainer.prepend(loadingIndicator);
      
      // Carregar GIF
      const img = new Image();
      img.onload = function() {
        zoomGif.src = zoomGif.dataset.src;
        loadingIndicator.remove();
      };
      img.src = zoomGif.dataset.src;
    }
  }
  
  // Alternar entre GIF e imagens estáticas
  const toggleButton = document.querySelector('.zoom-tutorial-toggle');
  if (toggleButton) {
    toggleButton.addEventListener('click', function() {
      const gif = document.querySelector('.zoom-tutorial-gif');
      const images = document.querySelector('.zoom-tutorial-images');
      
      if (gif.style.display === 'none') {
        gif.style.display = 'block';
        images.style.display = 'none';
        this.textContent = 'Ver passo a passo em imagens';
      } else {
        gif.style.display = 'none';
        images.style.display = 'flex';
        this.textContent = 'Ver animação completa';
      }
    });
  }
}

// Inicializar tutoriais do Zoom após o carregamento da página
window.addEventListener('load', initZoomTutorials);
