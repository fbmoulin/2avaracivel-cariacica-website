/**
 * Tutorial Toggle System for GIF and Step-by-Step Views
 * 2ª Vara Cível de Cariacica - Enhanced User Experience
 */

window.TutorialToggle = window.TutorialToggle || class TutorialToggle {
    constructor() {
        this.currentView = 'animation';
        this.isGifPaused = false;
        this.gifElement = null;
        this.staticImageIndex = 0;
        this.images = [];
        this.autoAdvanceInterval = null;
        this.isInitialized = false;
        
        this.init();
    }

    init() {
        if (this.isInitialized) return;
        
        this.setupTabs();
        this.setupGifControls();
        this.setupImageModal();
        this.loadImages();
        this.initializeView();
        
        this.isInitialized = true;
        console.log('Tutorial Toggle Manager initialized');
    }

    setupTabs() {
        const tabs = document.querySelectorAll('.tutorial-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const targetView = tab.dataset.view;
                this.switchView(targetView);
            });
            
            // Keyboard support
            tab.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    tab.click();
                }
            });
        });
    }

    setupGifControls() {
        const playPauseBtn = document.getElementById('gif-play-pause');
        const restartBtn = document.getElementById('gif-restart');
        const speedBtn = document.getElementById('gif-speed');
        
        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', () => this.toggleGifPlayback());
        }
        
        if (restartBtn) {
            restartBtn.addEventListener('click', () => this.restartGif());
        }
        
        if (speedBtn) {
            speedBtn.addEventListener('click', () => this.changeGifSpeed());
        }
    }

    setupImageModal() {
        const modal = document.querySelector('.image-modal');
        const closeBtn = modal?.querySelector('.modal-close');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeImageModal());
        }
        
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeImageModal();
                }
            });
        }
        
        // Setup click handlers for step images
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('step-image')) {
                this.openImageModal(e.target);
            }
        });
    }

    loadImages() {
        this.images = [
            {
                src: '/static/images/zoom_tutorial/zoom_audio_config_1_pt.png',
                alt: 'Passo 1: Acessando as configurações do Zoom',
                description: 'Tela principal do Zoom com destaque no ícone de configurações'
            },
            {
                src: '/static/images/zoom_tutorial/zoom_audio_config_2_pt.png',
                alt: 'Passo 2: Navegando para configurações de áudio',
                description: 'Janela de configurações aberta com a aba Áudio selecionada'
            },
            {
                src: '/static/images/zoom_tutorial/zoom_audio_config_3_pt.png',
                alt: 'Passo 3: Testando configurações de áudio',
                description: 'Seção de teste de áudio com botões para testar microfone e alto-falantes'
            }
        ];
        
        this.gifElement = document.querySelector('.tutorial-gif');
    }

    switchView(viewType) {
        const tabs = document.querySelectorAll('.tutorial-tab');
        const sections = document.querySelectorAll('.content-section');
        
        // Update tab states
        tabs.forEach(tab => {
            tab.classList.remove('active');
            tab.setAttribute('aria-selected', 'false');
        });
        
        const activeTab = document.querySelector(`[data-view="${viewType}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
            activeTab.setAttribute('aria-selected', 'true');
        }
        
        // Update content sections
        sections.forEach(section => {
            section.classList.remove('active');
        });
        
        const activeSection = document.getElementById(`${viewType}-view`);
        if (activeSection) {
            activeSection.classList.add('active');
        }
        
        this.currentView = viewType;
        this.announceViewChange(viewType);
        
        // Initialize view-specific features
        if (viewType === 'animation') {
            this.initializeAnimationView();
        } else if (viewType === 'step-by-step') {
            this.initializeStepByStepView();
        }
    }

    initializeAnimationView() {
        if (this.gifElement) {
            this.gifElement.style.display = 'block';
            this.updateGifControls();
        }
    }

    initializeStepByStepView() {
        const steps = document.querySelectorAll('.tutorial-step');
        steps.forEach((step, index) => {
            this.enhanceStepInteractivity(step, index);
        });
    }

    enhanceStepInteractivity(step, index) {
        const image = step.querySelector('.step-image');
        if (image) {
            // Add hover effects and descriptions
            image.addEventListener('mouseenter', () => {
                this.showImageTooltip(image, this.images[index]?.description);
            });
            
            image.addEventListener('mouseleave', () => {
                this.hideImageTooltip();
            });
            
            // Add keyboard accessibility
            image.setAttribute('tabindex', '0');
            image.setAttribute('role', 'button');
            image.setAttribute('aria-label', `Ampliar imagem: ${this.images[index]?.alt}`);
        }
    }

    toggleGifPlayback() {
        const btn = document.getElementById('gif-play-pause');
        const icon = btn?.querySelector('i');
        
        if (this.isGifPaused) {
            this.resumeGif();
            if (icon) icon.className = 'fas fa-pause';
            btn.setAttribute('aria-label', 'Pausar animação');
            this.announceToScreenReader('Animação retomada');
        } else {
            this.pauseGif();
            if (icon) icon.className = 'fas fa-play';
            btn.setAttribute('aria-label', 'Reproduzir animação');
            this.announceToScreenReader('Animação pausada');
        }
    }

    pauseGif() {
        this.isGifPaused = true;
        if (this.gifElement) {
            // Create static image overlay
            const staticOverlay = document.createElement('img');
            staticOverlay.src = this.images[this.staticImageIndex]?.src || this.images[0].src;
            staticOverlay.className = 'tutorial-gif-static';
            staticOverlay.alt = this.images[this.staticImageIndex]?.alt || 'Tutorial pausado';
            
            this.gifElement.style.display = 'none';
            this.gifElement.parentNode.appendChild(staticOverlay);
        }
    }

    resumeGif() {
        this.isGifPaused = false;
        const staticOverlay = document.querySelector('.tutorial-gif-static');
        if (staticOverlay) {
            staticOverlay.remove();
        }
        if (this.gifElement) {
            this.gifElement.style.display = 'block';
        }
    }

    restartGif() {
        if (this.gifElement) {
            const src = this.gifElement.src;
            this.gifElement.src = '';
            this.gifElement.src = src;
            
            this.isGifPaused = false;
            this.staticImageIndex = 0;
            this.updateGifControls();
            this.announceToScreenReader('Animação reiniciada');
        }
    }

    changeGifSpeed() {
        // Note: GIF speed cannot be changed directly, but we can cycle through different versions
        const speedBtn = document.getElementById('gif-speed');
        const currentSpeed = speedBtn.dataset.speed || 'normal';
        
        let newSpeed;
        switch (currentSpeed) {
            case 'slow':
                newSpeed = 'normal';
                break;
            case 'normal':
                newSpeed = 'fast';
                break;
            case 'fast':
                newSpeed = 'slow';
                break;
            default:
                newSpeed = 'normal';
        }
        
        speedBtn.dataset.speed = newSpeed;
        speedBtn.querySelector('span').textContent = this.getSpeedLabel(newSpeed);
        this.announceToScreenReader(`Velocidade alterada para: ${this.getSpeedLabel(newSpeed)}`);
    }

    getSpeedLabel(speed) {
        const labels = {
            'slow': 'Lenta',
            'normal': 'Normal',
            'fast': 'Rápida'
        };
        return labels[speed] || 'Normal';
    }

    updateGifControls() {
        const playPauseBtn = document.getElementById('gif-play-pause');
        const icon = playPauseBtn?.querySelector('i');
        
        if (this.isGifPaused) {
            if (icon) icon.className = 'fas fa-play';
            playPauseBtn.setAttribute('aria-label', 'Reproduzir animação');
        } else {
            if (icon) icon.className = 'fas fa-pause';
            playPauseBtn.setAttribute('aria-label', 'Pausar animação');
        }
    }

    openImageModal(image) {
        const modal = document.querySelector('.image-modal');
        const modalImage = modal.querySelector('.modal-image');
        const modalContent = modal.querySelector('.modal-content');
        
        modalImage.src = image.src;
        modalImage.alt = image.alt;
        modal.classList.add('active');
        
        // Add image details to modal
        this.addImageDetails(modalContent, image);
        
        // Focus management
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.focus();
        
        // Prevent background scrolling
        document.body.style.overflow = 'hidden';
        
        this.announceToScreenReader('Imagem ampliada. Use as setas para navegar ou Escape para fechar.');
        
        // Setup keyboard navigation in modal
        this.setupModalKeyboardNav(modal, image);
    }

    addImageDetails(modalContent, image) {
        // Remove existing details
        const existingDetails = modalContent.querySelector('.image-details');
        if (existingDetails) {
            existingDetails.remove();
        }
        
        // Find image index and add navigation
        const imageIndex = Array.from(document.querySelectorAll('.step-image')).indexOf(image);
        if (imageIndex >= 0 && this.images[imageIndex]) {
            const details = document.createElement('div');
            details.className = 'image-details';
            details.innerHTML = `
                <h3>Passo ${imageIndex + 1} de ${this.images.length}</h3>
                <p>${this.images[imageIndex].description}</p>
                <div class="modal-navigation">
                    <button class="modal-nav-btn" id="modal-prev" ${imageIndex === 0 ? 'disabled' : ''}>
                        <i class="fas fa-chevron-left"></i> Anterior
                    </button>
                    <button class="modal-nav-btn" id="modal-next" ${imageIndex === this.images.length - 1 ? 'disabled' : ''}>
                        <i class="fas fa-chevron-right"></i> Próximo
                    </button>
                </div>
            `;
            
            modalContent.appendChild(details);
            
            // Setup navigation buttons
            const prevBtn = details.querySelector('#modal-prev');
            const nextBtn = details.querySelector('#modal-next');
            
            if (prevBtn) {
                prevBtn.addEventListener('click', () => this.navigateModalImage(-1));
            }
            if (nextBtn) {
                nextBtn.addEventListener('click', () => this.navigateModalImage(1));
            }
        }
    }

    setupModalKeyboardNav(modal, image) {
        const keyHandler = (e) => {
            switch (e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.navigateModalImage(-1);
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.navigateModalImage(1);
                    break;
                case 'Escape':
                    e.preventDefault();
                    this.closeImageModal();
                    break;
            }
        };
        
        modal.addEventListener('keydown', keyHandler);
        modal.dataset.keyHandler = 'attached';
    }

    navigateModalImage(direction) {
        const modalImage = document.querySelector('.modal-image');
        const currentSrc = modalImage.src;
        const currentIndex = this.images.findIndex(img => modalImage.src.includes(img.src.split('/').pop()));
        
        const newIndex = currentIndex + direction;
        if (newIndex >= 0 && newIndex < this.images.length) {
            const newImage = this.images[newIndex];
            modalImage.src = newImage.src;
            modalImage.alt = newImage.alt;
            
            // Update details
            const modalContent = document.querySelector('.modal-content');
            this.addImageDetails(modalContent, { src: newImage.src, alt: newImage.alt });
            
            this.announceToScreenReader(`Imagem ${newIndex + 1} de ${this.images.length}: ${newImage.alt}`);
        }
    }

    closeImageModal() {
        const modal = document.querySelector('.image-modal');
        modal.classList.remove('active');
        
        // Remove keyboard handler
        if (modal.dataset.keyHandler) {
            delete modal.dataset.keyHandler;
        }
        
        // Restore focus to the trigger element
        const activeImage = document.querySelector('.step-image[tabindex="0"]:focus');
        if (activeImage) {
            activeImage.focus();
        }
        
        // Restore background scrolling
        document.body.style.overflow = 'auto';
        
        this.announceToScreenReader('Modal fechado');
    }

    showImageTooltip(image, description) {
        if (!description) return;
        
        const tooltip = document.createElement('div');
        tooltip.className = 'image-tooltip';
        tooltip.textContent = description;
        tooltip.setAttribute('role', 'tooltip');
        
        image.parentNode.appendChild(tooltip);
        
        // Position tooltip
        const rect = image.getBoundingClientRect();
        tooltip.style.position = 'absolute';
        tooltip.style.top = `${rect.bottom + 10}px`;
        tooltip.style.left = `${rect.left}px`;
        tooltip.style.zIndex = '1000';
    }

    hideImageTooltip() {
        const tooltip = document.querySelector('.image-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    announceViewChange(viewType) {
        const messages = {
            'animation': 'Visualização em animação ativada',
            'step-by-step': 'Visualização passo a passo ativada'
        };
        
        this.announceToScreenReader(messages[viewType] || 'Visualização alterada');
    }

    announceToScreenReader(message) {
        // Use the accessibility manager if available
        if (window.tutorialAccessibility) {
            window.tutorialAccessibility.announceToScreenReader(message);
        } else {
            // Fallback method
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'polite');
            announcement.className = 'sr-only';
            announcement.textContent = message;
            document.body.appendChild(announcement);
            
            setTimeout(() => {
                if (document.body.contains(announcement)) {
                    document.body.removeChild(announcement);
                }
            }, 1000);
        }
    }

    // Public methods for external control
    switchToAnimation() {
        this.switchView('animation');
    }

    switchToStepByStep() {
        this.switchView('step-by-step');
    }

    getCurrentView() {
        return this.currentView;
    }

    getViewState() {
        return {
            currentView: this.currentView,
            isGifPaused: this.isGifPaused,
            staticImageIndex: this.staticImageIndex,
            totalImages: this.images.length
        };
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (!window.tutorialToggle) {
        window.tutorialToggle = new TutorialToggle();
    }
});

// Integration with voice accessibility
if (window.voiceAccessibilityManager) {
    window.voiceAccessibilityManager.registerComponent('tutorialToggle', {
        describe: () => 'Sistema de alternância entre visualização animada e passo a passo do tutorial',
        getStatus: () => {
            const toggle = window.tutorialToggle;
            if (toggle) {
                const state = toggle.getViewState();
                return `Visualização atual: ${state.currentView}. ${state.isGifPaused ? 'Animação pausada' : 'Animação em execução'}`;
            }
            return 'Sistema de alternância não inicializado';
        }
    });
}