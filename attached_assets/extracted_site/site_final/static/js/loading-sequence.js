/**
 * Loading Sequence Manager
 * Orchestrates progressive loading animations for enhanced user experience
 */

class LoadingSequenceManager {
    constructor() {
        this.loadingStages = [
            { name: 'structure', duration: 200 },
            { name: 'content', duration: 300 },
            { name: 'icons', duration: 500 },
            { name: 'interactions', duration: 200 }
        ];
        this.currentStage = 0;
        this.init();
    }

    init() {
        this.createLoadingIndicators();
        this.startLoadingSequence();
    }

    createLoadingIndicators() {
        // Create subtle loading progress indicator
        const progressBar = document.createElement('div');
        progressBar.id = 'loading-progress-bar';
        progressBar.innerHTML = `
            <div class="progress-fill"></div>
            <div class="progress-pulse"></div>
        `;
        
        const progressStyles = `
            #loading-progress-bar {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: rgba(30, 64, 175, 0.1);
                z-index: 9999;
                opacity: 1;
                transition: opacity 0.5s ease;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #1e40af, #3b82f6, #60a5fa);
                width: 0%;
                transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }
            
            .progress-pulse {
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
                animation: progressPulse 2s infinite;
            }
            
            @keyframes progressPulse {
                0% { left: -100%; }
                100% { left: 100%; }
            }
            
            .loading-stage-indicator {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: rgba(30, 64, 175, 0.9);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                z-index: 9998;
                opacity: 0;
                transform: translateY(20px);
                transition: all 0.3s ease;
            }
            
            .loading-stage-indicator.show {
                opacity: 1;
                transform: translateY(0);
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = progressStyles;
        document.head.appendChild(styleSheet);
        
        document.body.appendChild(progressBar);
        
        // Create stage indicator
        const stageIndicator = document.createElement('div');
        stageIndicator.className = 'loading-stage-indicator';
        stageIndicator.id = 'loading-stage-indicator';
        document.body.appendChild(stageIndicator);
    }

    startLoadingSequence() {
        this.showStageIndicator('Carregando estrutura...');
        this.progressToStage(0);
        
        // Start the sequence
        this.executeStage(0);
    }

    executeStage(stageIndex) {
        if (stageIndex >= this.loadingStages.length) {
            this.completeLoading();
            return;
        }

        const stage = this.loadingStages[stageIndex];
        this.updateStageIndicator(this.getStageMessage(stage.name));
        
        // Execute stage-specific logic
        switch (stage.name) {
            case 'structure':
                this.loadStructure();
                break;
            case 'content':
                this.loadContent();
                break;
            case 'icons':
                this.loadIcons();
                break;
            case 'interactions':
                this.enableInteractions();
                break;
        }

        // Progress to next stage
        setTimeout(() => {
            this.progressToStage(stageIndex + 1);
            this.executeStage(stageIndex + 1);
        }, stage.duration);
    }

    loadStructure() {
        // Prepare card containers
        const cards = document.querySelectorAll('.quick-access-card');
        cards.forEach(card => {
            card.style.visibility = 'visible';
            card.classList.add('structure-loaded');
        });
    }

    loadContent() {
        // Reveal text content with typing effect
        const titles = document.querySelectorAll('.quick-access-card .card-title');
        const descriptions = document.querySelectorAll('.quick-access-card .card-text');
        
        [...titles, ...descriptions].forEach((element, index) => {
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, index * 50);
        });
    }

    loadIcons() {
        // Trigger coordinated icon animations
        if (window.cardAnimationOrchestrator) {
            window.cardAnimationOrchestrator.triggerAllAnimations();
        }
    }

    enableInteractions() {
        // Enable hover effects and button interactions
        const buttons = document.querySelectorAll('.quick-access-card .btn');
        buttons.forEach((button, index) => {
            setTimeout(() => {
                button.style.pointerEvents = 'auto';
                button.style.opacity = '1';
                button.classList.add('interaction-ready');
            }, index * 100);
        });
    }

    progressToStage(stageIndex) {
        const progress = ((stageIndex + 1) / this.loadingStages.length) * 100;
        const progressFill = document.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = `${progress}%`;
        }
    }

    updateStageIndicator(message) {
        const indicator = document.getElementById('loading-stage-indicator');
        if (indicator) {
            indicator.textContent = message;
            indicator.classList.add('show');
        }
    }

    showStageIndicator(message) {
        const indicator = document.getElementById('loading-stage-indicator');
        if (indicator) {
            indicator.textContent = message;
            indicator.classList.add('show');
        }
    }

    getStageMessage(stageName) {
        const messages = {
            'structure': 'Preparando layout...',
            'content': 'Carregando conteúdo...',
            'icons': 'Animando ícones...',
            'interactions': 'Habilitando interações...'
        };
        return messages[stageName] || 'Carregando...';
    }

    completeLoading() {
        // Hide loading indicators
        setTimeout(() => {
            const progressBar = document.getElementById('loading-progress-bar');
            const stageIndicator = document.getElementById('loading-stage-indicator');
            
            if (progressBar) {
                progressBar.style.opacity = '0';
                setTimeout(() => progressBar.remove(), 500);
            }
            
            if (stageIndicator) {
                stageIndicator.style.opacity = '0';
                setTimeout(() => stageIndicator.remove(), 500);
            }
            
            // Trigger completion effects
            this.triggerCompletionEffects();
        }, 300);
    }

    triggerCompletionEffects() {
        // Brief success animation
        const cards = document.querySelectorAll('.quick-access-card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.style.boxShadow = '0 0 30px rgba(34, 197, 94, 0.3)';
                setTimeout(() => {
                    card.style.boxShadow = '';
                }, 600);
            }, index * 100);
        });
        
        // Announce completion to accessibility tools
        this.announceCompletion();
    }

    announceCompletion() {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.style.position = 'absolute';
        announcement.style.left = '-10000px';
        announcement.textContent = 'Página carregada com sucesso. Todos os serviços estão disponíveis.';
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            announcement.remove();
        }, 3000);
    }

    // Manual controls for testing
    skipToEnd() {
        this.currentStage = this.loadingStages.length;
        this.completeLoading();
    }

    restart() {
        // Reset all states
        const cards = document.querySelectorAll('.quick-access-card');
        cards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(50px)';
            card.classList.remove('structure-loaded', 'animate-in');
        });
        
        // Restart sequence
        this.currentStage = 0;
        this.startLoadingSequence();
    }
}

// Initialize loading sequence manager
const loadingSequenceManager = new LoadingSequenceManager();

// Make globally accessible
window.loadingSequenceManager = loadingSequenceManager;

// Integrate with existing systems
document.addEventListener('DOMContentLoaded', () => {
    // Coordinate with other animation systems
    if (window.animatedIconLoader) {
        const originalTrigger = window.animatedIconLoader.triggerIconAnimations;
        window.animatedIconLoader.triggerIconAnimations = function() {
            // Only trigger if loading sequence allows
            if (loadingSequenceManager.currentStage >= 2) {
                originalTrigger.call(this);
            }
        };
    }
});