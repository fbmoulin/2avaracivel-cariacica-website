/**
 * Coordinated Card and Icon Animation System
 * Orchestrates entrance animations for service cards and their icons
 */

class CardAnimationOrchestrator {
    constructor() {
        this.cardDelay = 150; // Delay between card animations
        this.iconDelay = 300; // Additional delay for icon animations after card
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupCardAnimations());
        } else {
            this.setupCardAnimations();
        }
    }

    setupCardAnimations() {
        this.prepareCards();
        this.observeCardsInViewport();
        this.animateVisibleCards();
    }

    prepareCards() {
        const cards = document.querySelectorAll('.quick-access-card');
        cards.forEach((card, index) => {
            // Set initial hidden state
            card.style.opacity = '0';
            card.style.transform = 'translateY(50px) scale(0.95)';
            card.style.transition = 'none';
            
            // Store animation timing
            card.dataset.animationIndex = index;
        });
    }

    observeCardsInViewport() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateCard(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.2,
            rootMargin: '100px'
        });

        document.querySelectorAll('.quick-access-card').forEach(card => {
            observer.observe(card);
        });
    }

    animateVisibleCards() {
        const quickAccessSection = document.querySelector('.quick-access-section');
        if (!quickAccessSection) return;

        const rect = quickAccessSection.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom > 0;

        if (isVisible) {
            const cards = document.querySelectorAll('.quick-access-card');
            cards.forEach((card, index) => {
                setTimeout(() => {
                    this.animateCard(card);
                }, index * this.cardDelay);
            });
        }
    }

    animateCard(card) {
        const index = parseInt(card.dataset.animationIndex) || 0;
        
        // Reset transition
        card.style.transition = 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        
        // Animate card entrance
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0) scale(1)';
            card.classList.add('animate-in');
            
            // Add entrance effect
            this.addCardEntranceEffect(card);
            
            // Trigger icon animation after card settles
            setTimeout(() => {
                this.triggerIconAnimation(card);
            }, this.iconDelay);
            
        }, 50);
    }

    addCardEntranceEffect(card) {
        // Brief glow effect on card entrance
        const originalBoxShadow = card.style.boxShadow;
        card.style.boxShadow = '0 0 40px rgba(30, 64, 175, 0.3), 0 20px 40px rgba(0, 0, 0, 0.1)';
        
        setTimeout(() => {
            card.style.boxShadow = originalBoxShadow;
        }, 1000);
    }

    triggerIconAnimation(card) {
        const iconContainer = card.querySelector('.service-icon-container');
        if (iconContainer && window.animatedIconLoader) {
            window.animatedIconLoader.animateIcon(iconContainer);
        }
    }

    // Enhanced hover effects for animated cards
    setupEnhancedHoverEffects() {
        const cards = document.querySelectorAll('.quick-access-card.animate-in');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                this.onCardHover(card);
            });
            
            card.addEventListener('mouseleave', () => {
                this.onCardLeave(card);
            });
        });
    }

    onCardHover(card) {
        // Enhanced hover animation
        card.style.transform = 'translateY(-12px) scale(1.03)';
        card.style.boxShadow = '0 25px 50px rgba(30, 64, 175, 0.2), 0 0 30px rgba(30, 64, 175, 0.1)';
        
        // Icon pulse effect
        const icon = card.querySelector('.service-icon-container i, .service-icon-fallback');
        if (icon) {
            icon.style.transform = 'scale(1.2)';
            icon.style.filter = 'drop-shadow(0 6px 12px rgba(30, 64, 175, 0.4))';
        }
    }

    onCardLeave(card) {
        // Return to normal state
        card.style.transform = 'translateY(0) scale(1)';
        card.style.boxShadow = '';
        
        // Reset icon
        const icon = card.querySelector('.service-icon-container i, .service-icon-fallback');
        if (icon) {
            icon.style.transform = '';
            icon.style.filter = '';
        }
    }

    // Performance-optimized animation reset
    resetAllAnimations() {
        const cards = document.querySelectorAll('.quick-access-card');
        cards.forEach(card => {
            card.classList.remove('animate-in');
            card.style.opacity = '0';
            card.style.transform = 'translateY(50px) scale(0.95)';
            card.style.transition = 'none';
        });
        
        // Reset icons too
        if (window.animatedIconLoader) {
            window.animatedIconLoader.resetAnimations();
        }
    }

    // Trigger animations manually (for testing)
    triggerAllAnimations() {
        this.animateVisibleCards();
    }
}

// Initialize the card animation orchestrator
const cardAnimationOrchestrator = new CardAnimationOrchestrator();

// Make it globally accessible
window.cardAnimationOrchestrator = cardAnimationOrchestrator;

// Setup enhanced hover effects after initial animations
setTimeout(() => {
    cardAnimationOrchestrator.setupEnhancedHoverEffects();
}, 2000);

// Integration with page load performance
window.addEventListener('load', () => {
    // Ensure animations trigger even if intersection observer misses
    setTimeout(() => {
        const unanimatedCards = document.querySelectorAll('.quick-access-card:not(.animate-in)');
        if (unanimatedCards.length > 0) {
            cardAnimationOrchestrator.triggerAllAnimations();
        }
    }, 1000);
});