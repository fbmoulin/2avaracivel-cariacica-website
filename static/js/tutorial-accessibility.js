/**
 * Tutorial Accessibility System for Zoom Audio Configuration
 * 2ª Vara Cível de Cariacica - Comprehensive Accessibility Features
 */

window.TutorialAccessibility = window.TutorialAccessibility || class TutorialAccessibility {
    constructor() {
        this.isHighContrast = false;
        this.isLargeText = false;
        this.currentStep = 0;
        this.totalSteps = 0;
        this.isInitialized = false;
        
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        
        this.setupAccessibilityControls();
        this.setupKeyboardNavigation();
        this.setupScreenReaderSupport();
        this.setupFocusManagement();
        this.initializeStepCounter();
        
        this.isInitialized = true;
        console.log('Tutorial Accessibility Manager initialized');
    }

    setupAccessibilityControls() {
        const controls = document.querySelector('.accessibility-controls');
        if (!controls) return;

        // High Contrast Toggle
        const contrastBtn = controls.querySelector('#high-contrast-btn');
        if (contrastBtn) {
            contrastBtn.addEventListener('click', () => this.toggleHighContrast());
        }

        // Large Text Toggle
        const textBtn = controls.querySelector('#large-text-btn');
        if (textBtn) {
            textBtn.addEventListener('click', () => this.toggleLargeText());
        }

        // Screen Reader Mode
        const screenReaderBtn = controls.querySelector('#screen-reader-btn');
        if (screenReaderBtn) {
            screenReaderBtn.addEventListener('click', () => this.activateScreenReaderMode());
        }

        // Audio Description
        const audioBtn = controls.querySelector('#audio-description-btn');
        if (audioBtn) {
            audioBtn.addEventListener('click', () => this.toggleAudioDescription());
        }
    }

    toggleHighContrast() {
        this.isHighContrast = !this.isHighContrast;
        const container = document.querySelector('.tutorial-container');
        const btn = document.querySelector('#high-contrast-btn');
        
        if (this.isHighContrast) {
            container.classList.add('high-contrast');
            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');
            this.announceToScreenReader('Modo alto contraste ativado');
        } else {
            container.classList.remove('high-contrast');
            btn.classList.remove('active');
            btn.setAttribute('aria-pressed', 'false');
            this.announceToScreenReader('Modo alto contraste desativado');
        }
    }

    toggleLargeText() {
        this.isLargeText = !this.isLargeText;
        const container = document.querySelector('.tutorial-container');
        const btn = document.querySelector('#large-text-btn');
        
        if (this.isLargeText) {
            container.classList.add('large-text');
            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');
            this.announceToScreenReader('Texto grande ativado');
        } else {
            container.classList.remove('large-text');
            btn.classList.remove('active');
            btn.setAttribute('aria-pressed', 'false');
            this.announceToScreenReader('Texto grande desativado');
        }
    }

    activateScreenReaderMode() {
        const btn = document.querySelector('#screen-reader-btn');
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
        
        this.announceToScreenReader('Modo leitor de tela ativado. Use Tab para navegar pelos passos e Enter para ações.');
        this.enhanceScreenReaderExperience();
    }

    enhanceScreenReaderExperience() {
        // Add aria-live regions for dynamic content
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.id = 'tutorial-live-region';
        document.body.appendChild(liveRegion);

        // Enhance image descriptions
        const images = document.querySelectorAll('.step-image');
        images.forEach((img, index) => {
            const description = this.getImageDescription(index + 1);
            img.setAttribute('aria-describedby', `step-${index + 1}-description`);
            
            const descElement = document.createElement('div');
            descElement.id = `step-${index + 1}-description`;
            descElement.className = 'sr-only';
            descElement.textContent = description;
            img.parentNode.appendChild(descElement);
        });
    }

    getImageDescription(step) {
        const descriptions = {
            1: 'Tela do Zoom mostrando o ícone de configurações no canto superior direito. Uma seta aponta para o ícone de engrenagem.',
            2: 'Janela de configurações do Zoom aberta com a aba Áudio selecionada. Mostra opções de microfone e alto-falantes.',
            3: 'Seção de teste de áudio destacada, mostrando botões para testar microfone e alto-falantes com indicadores visuais de nível.'
        };
        return descriptions[step] || `Passo ${step} da configuração de áudio do Zoom`;
    }

    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (e.target.closest('.tutorial-container')) {
                this.handleKeyboardNavigation(e);
            }
        });
    }

    handleKeyboardNavigation(e) {
        switch (e.key) {
            case 'Tab':
                // Enhanced tab navigation - handled by browser
                break;
            case 'Enter':
            case ' ':
                if (e.target.classList.contains('step-image')) {
                    e.preventDefault();
                    this.openImageModal(e.target);
                }
                break;
            case 'Escape':
                this.closeImageModal();
                break;
            case 'ArrowRight':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.navigateToNextStep();
                }
                break;
            case 'ArrowLeft':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.navigateToPreviousStep();
                }
                break;
            case '1':
            case '2':
            case '3':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.navigateToStep(parseInt(e.key) - 1);
                }
                break;
        }
    }

    navigateToNextStep() {
        const steps = document.querySelectorAll('.tutorial-step');
        if (this.currentStep < steps.length - 1) {
            this.currentStep++;
            this.focusOnStep(this.currentStep);
            this.announceToScreenReader(`Navegando para o passo ${this.currentStep + 1} de ${steps.length}`);
        }
    }

    navigateToPreviousStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.focusOnStep(this.currentStep);
            this.announceToScreenReader(`Navegando para o passo ${this.currentStep + 1} de ${this.totalSteps}`);
        }
    }

    navigateToStep(stepIndex) {
        const steps = document.querySelectorAll('.tutorial-step');
        if (stepIndex >= 0 && stepIndex < steps.length) {
            this.currentStep = stepIndex;
            this.focusOnStep(stepIndex);
            this.announceToScreenReader(`Navegando para o passo ${stepIndex + 1} de ${steps.length}`);
        }
    }

    focusOnStep(stepIndex) {
        const steps = document.querySelectorAll('.tutorial-step');
        const step = steps[stepIndex];
        if (step) {
            step.scrollIntoView({ behavior: 'smooth', block: 'center' });
            const focusableElement = step.querySelector('.step-image, .step-title');
            if (focusableElement) {
                focusableElement.focus();
            }
        }
    }

    initializeStepCounter() {
        const steps = document.querySelectorAll('.tutorial-step');
        this.totalSteps = steps.length;
        
        // Add step counter for screen readers
        steps.forEach((step, index) => {
            const counter = document.createElement('span');
            counter.className = 'sr-only';
            counter.textContent = `Passo ${index + 1} de ${this.totalSteps}. `;
            step.querySelector('.step-title').prepend(counter);
        });
    }

    setupScreenReaderSupport() {
        // Add landmarks and roles
        const tutorial = document.querySelector('.tutorial-container');
        if (tutorial) {
            tutorial.setAttribute('role', 'main');
            tutorial.setAttribute('aria-label', 'Tutorial de configuração de áudio do Zoom');
        }

        const steps = document.querySelector('.step-by-step-container');
        if (steps) {
            steps.setAttribute('role', 'region');
            steps.setAttribute('aria-label', 'Passos do tutorial');
        }

        const faq = document.querySelector('.faq-section');
        if (faq) {
            faq.setAttribute('role', 'region');
            faq.setAttribute('aria-label', 'Perguntas frequentes');
        }

        // Enhance FAQ accessibility
        this.setupFAQAccessibility();
    }

    setupFAQAccessibility() {
        const faqItems = document.querySelectorAll('.faq-item');
        faqItems.forEach((item, index) => {
            const question = item.querySelector('.faq-question');
            const answer = item.querySelector('.faq-answer');
            
            if (question && answer) {
                const questionId = `faq-question-${index}`;
                const answerId = `faq-answer-${index}`;
                
                question.id = questionId;
                answer.id = answerId;
                question.setAttribute('aria-controls', answerId);
                question.setAttribute('aria-expanded', 'false');
                answer.setAttribute('aria-labelledby', questionId);
                
                question.addEventListener('click', () => {
                    const isExpanded = question.getAttribute('aria-expanded') === 'true';
                    question.setAttribute('aria-expanded', !isExpanded);
                    answer.classList.toggle('active');
                    
                    if (!isExpanded) {
                        this.announceToScreenReader('Resposta expandida');
                    } else {
                        this.announceToScreenReader('Resposta recolhida');
                    }
                });
            }
        });
    }

    setupFocusManagement() {
        // Trap focus in modals
        document.addEventListener('keydown', (e) => {
            const modal = document.querySelector('.image-modal.active');
            if (modal && e.key === 'Tab') {
                this.trapFocusInModal(e, modal);
            }
        });

        // Auto-focus management
        const tabs = document.querySelectorAll('.tutorial-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                this.manageFocusOnTabChange(tab);
            });
        });
    }

    trapFocusInModal(e, modal) {
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey && document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
        } else if (!e.shiftKey && document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
        }
    }

    manageFocusOnTabChange(activeTab) {
        const tabContent = document.querySelector('.content-section.active');
        if (tabContent) {
            const firstFocusable = tabContent.querySelector('img, button, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                setTimeout(() => firstFocusable.focus(), 100);
            }
        }
    }

    openImageModal(image) {
        const modal = document.querySelector('.image-modal');
        const modalImage = modal.querySelector('.modal-image');
        const closeBtn = modal.querySelector('.modal-close');
        
        modalImage.src = image.src;
        modalImage.alt = image.alt;
        modal.classList.add('active');
        
        // Focus management
        closeBtn.focus();
        this.announceToScreenReader('Imagem ampliada aberta. Pressione Escape para fechar.');
        
        // Prevent background scrolling
        document.body.style.overflow = 'hidden';
    }

    closeImageModal() {
        const modal = document.querySelector('.image-modal');
        modal.classList.remove('active');
        
        // Restore focus to the image that opened the modal
        const activeImage = document.querySelector('.step-image:focus');
        if (activeImage) {
            activeImage.focus();
        }
        
        // Restore background scrolling
        document.body.style.overflow = 'auto';
        this.announceToScreenReader('Imagem ampliada fechada');
    }

    toggleAudioDescription() {
        const btn = document.querySelector('#audio-description-btn');
        const isActive = btn.classList.contains('active');
        
        if (!isActive) {
            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');
            this.startAudioDescription();
            this.announceToScreenReader('Descrição em áudio ativada');
        } else {
            btn.classList.remove('active');
            btn.setAttribute('aria-pressed', 'false');
            this.stopAudioDescription();
            this.announceToScreenReader('Descrição em áudio desativada');
        }
    }

    startAudioDescription() {
        // Text-to-speech for step descriptions
        const steps = document.querySelectorAll('.tutorial-step');
        steps.forEach((step, index) => {
            step.addEventListener('mouseenter', () => {
                const description = step.querySelector('.step-description').textContent;
                this.speakText(`Passo ${index + 1}. ${description}`);
            });
            
            step.addEventListener('focus', () => {
                const description = step.querySelector('.step-description').textContent;
                this.speakText(`Passo ${index + 1}. ${description}`);
            });
        });
    }

    stopAudioDescription() {
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
    }

    speakText(text) {
        if (window.speechSynthesis) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'pt-BR';
            utterance.rate = 0.8;
            utterance.pitch = 1;
            window.speechSynthesis.speak(utterance);
        }
    }

    announceToScreenReader(message) {
        const liveRegion = document.getElementById('tutorial-live-region');
        if (liveRegion) {
            liveRegion.textContent = message;
        }
        
        // Also use aria-live polite announcement
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    // Utility methods
    getStepProgress() {
        return {
            current: this.currentStep + 1,
            total: this.totalSteps,
            percentage: Math.round(((this.currentStep + 1) / this.totalSteps) * 100)
        };
    }

    resetAccessibilitySettings() {
        this.isHighContrast = false;
        this.isLargeText = false;
        
        const container = document.querySelector('.tutorial-container');
        container.classList.remove('high-contrast', 'large-text');
        
        const buttons = document.querySelectorAll('.accessibility-btn');
        buttons.forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-pressed', 'false');
        });
        
        this.announceToScreenReader('Configurações de acessibilidade redefinidas');
    }

    // Keyboard shortcuts help
    showKeyboardShortcuts() {
        const shortcuts = [
            'Tab: Navegar pelos elementos',
            'Enter/Espaço: Ativar elemento focado',
            'Escape: Fechar modal',
            'Ctrl + Seta Direita: Próximo passo',
            'Ctrl + Seta Esquerda: Passo anterior',
            'Ctrl + 1,2,3: Ir para passo específico'
        ];
        
        this.announceToScreenReader('Atalhos de teclado: ' + shortcuts.join('. '));
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (!window.tutorialAccessibility) {
        window.tutorialAccessibility = new TutorialAccessibility();
    }
});

// Voice accessibility integration
if (window.voiceAccessibilityManager) {
    window.voiceAccessibilityManager.registerComponent('tutorialAccessibility', {
        describe: () => 'Sistema de acessibilidade do tutorial do Zoom com suporte para navegação por teclado e leitores de tela',
        getStatus: () => {
            const manager = window.tutorialAccessibility;
            if (manager) {
                const progress = manager.getStepProgress();
                return `Tutorial do Zoom: passo ${progress.current} de ${progress.total} (${progress.percentage}% concluído)`;
            }
            return 'Tutorial do Zoom não inicializado';
        }
    });
}