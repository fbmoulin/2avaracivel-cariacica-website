/**
 * Animated Icon Loading Transitions
 * Creates smooth entrance animations for service icons
 */

class AnimatedIconLoader {
    constructor() {
        this.animationDelay = 100; // Delay between each icon animation
        this.observerThreshold = 0.3; // When to trigger animations
        this.animations = [
            'fadeInScale',
            'slideInUp',
            'bounceIn',
            'rotateIn',
            'flipIn'
        ];
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupAnimations());
        } else {
            this.setupAnimations();
        }
    }

    setupAnimations() {
        this.addAnimationStyles();
        this.prepareIcons();
        this.setupIntersectionObserver();
        this.animateVisibleIcons();
    }

    addAnimationStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Icon Loading Animations */
            .icon-loading {
                opacity: 0;
                transform: scale(0.5);
                transition: none;
            }

            /* Fade In Scale Animation */
            @keyframes fadeInScale {
                0% {
                    opacity: 0;
                    transform: scale(0.3) rotate(-180deg);
                }
                50% {
                    opacity: 0.7;
                    transform: scale(1.1) rotate(-90deg);
                }
                100% {
                    opacity: 1;
                    transform: scale(1) rotate(0deg);
                }
            }

            .animate-fadeInScale {
                animation: fadeInScale 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            }

            /* Slide In Up Animation */
            @keyframes slideInUp {
                0% {
                    opacity: 0;
                    transform: translateY(50px) scale(0.8);
                }
                60% {
                    opacity: 0.8;
                    transform: translateY(-10px) scale(1.05);
                }
                100% {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }

            .animate-slideInUp {
                animation: slideInUp 0.7s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
            }

            /* Bounce In Animation */
            @keyframes bounceIn {
                0% {
                    opacity: 0;
                    transform: scale(0.1);
                }
                25% {
                    opacity: 0.5;
                    transform: scale(1.2);
                }
                50% {
                    opacity: 0.8;
                    transform: scale(0.9);
                }
                75% {
                    opacity: 0.9;
                    transform: scale(1.05);
                }
                100% {
                    opacity: 1;
                    transform: scale(1);
                }
            }

            .animate-bounceIn {
                animation: bounceIn 0.9s cubic-bezier(0.215, 0.61, 0.355, 1) forwards;
            }

            /* Rotate In Animation */
            @keyframes rotateIn {
                0% {
                    opacity: 0;
                    transform: rotate(-360deg) scale(0.1);
                }
                100% {
                    opacity: 1;
                    transform: rotate(0deg) scale(1);
                }
            }

            .animate-rotateIn {
                animation: rotateIn 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
            }

            /* Flip In Animation */
            @keyframes flipIn {
                0% {
                    opacity: 0;
                    transform: perspective(400px) rotateY(-90deg) scale(0.8);
                }
                50% {
                    opacity: 0.7;
                    transform: perspective(400px) rotateY(-45deg) scale(1.1);
                }
                100% {
                    opacity: 1;
                    transform: perspective(400px) rotateY(0deg) scale(1);
                }
            }

            .animate-flipIn {
                animation: flipIn 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
            }

            /* Container pulse while loading */
            .icon-container-loading {
                background: linear-gradient(45deg, rgba(30, 64, 175, 0.1), rgba(59, 130, 246, 0.1), rgba(30, 64, 175, 0.1));
                background-size: 200% 200%;
                animation: gradientPulse 1.5s ease-in-out infinite;
            }

            @keyframes gradientPulse {
                0%, 100% {
                    background-position: 0% 50%;
                }
                50% {
                    background-position: 100% 50%;
                }
            }

            /* Icon shimmer effect during load */
            .icon-shimmer {
                position: relative;
                overflow: hidden;
            }

            .icon-shimmer::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
                animation: shimmer 2s infinite;
            }

            @keyframes shimmer {
                0% {
                    left: -100%;
                }
                100% {
                    left: 100%;
                }
            }

            /* Staggered entrance for icon groups */
            .service-icons-group .service-icon-container:nth-child(1) {
                animation-delay: 0ms;
            }
            .service-icons-group .service-icon-container:nth-child(2) {
                animation-delay: 150ms;
            }
            .service-icons-group .service-icon-container:nth-child(3) {
                animation-delay: 300ms;
            }
            .service-icons-group .service-icon-container:nth-child(4) {
                animation-delay: 450ms;
            }
        `;
        document.head.appendChild(style);
    }

    prepareIcons() {
        const iconContainers = document.querySelectorAll('.service-icon-container');
        
        iconContainers.forEach((container, index) => {
            // Add loading state
            container.classList.add('icon-loading', 'icon-container-loading', 'icon-shimmer');
            
            // Store animation type
            const animationType = this.animations[index % this.animations.length];
            container.dataset.animation = animationType;
        });
    }

    setupIntersectionObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateIcon(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: this.observerThreshold,
            rootMargin: '50px'
        });

        document.querySelectorAll('.service-icon-container').forEach(container => {
            observer.observe(container);
        });
    }

    animateVisibleIcons() {
        // Animate icons that are already visible
        const visibleIcons = document.querySelectorAll('.service-icon-container');
        const quickAccessSection = document.querySelector('.quick-access-section');
        
        if (quickAccessSection) {
            const rect = quickAccessSection.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
            
            if (isVisible) {
                visibleIcons.forEach((container, index) => {
                    setTimeout(() => {
                        this.animateIcon(container);
                    }, index * this.animationDelay);
                });
            }
        }
    }

    animateIcon(container) {
        const animationType = container.dataset.animation || 'fadeInScale';
        
        // Remove loading states
        container.classList.remove('icon-loading', 'icon-container-loading', 'icon-shimmer');
        
        // Add entrance animation
        container.classList.add(`animate-${animationType}`);
        
        // Add success feedback
        setTimeout(() => {
            this.addSuccessEffect(container);
        }, 600);
    }

    addSuccessEffect(container) {
        // Brief glow effect to indicate successful load
        container.style.boxShadow = '0 0 30px rgba(30, 64, 175, 0.4)';
        container.style.transition = 'box-shadow 0.3s ease';
        
        setTimeout(() => {
            container.style.boxShadow = '';
        }, 800);
    }

    // Manual trigger for testing or delayed content
    triggerIconAnimations() {
        const iconContainers = document.querySelectorAll('.service-icon-container.icon-loading');
        iconContainers.forEach((container, index) => {
            setTimeout(() => {
                this.animateIcon(container);
            }, index * this.animationDelay);
        });
    }

    // Reset animations for testing
    resetAnimations() {
        const iconContainers = document.querySelectorAll('.service-icon-container');
        iconContainers.forEach(container => {
            // Remove all animation classes
            const animationClasses = container.className.split(' ').filter(cls => cls.startsWith('animate-'));
            animationClasses.forEach(cls => container.classList.remove(cls));
            
            // Reset to loading state
            container.classList.add('icon-loading', 'icon-container-loading', 'icon-shimmer');
        });
    }
}

// Initialize the animated icon loader
const animatedIconLoader = new AnimatedIconLoader();

// Make it globally accessible for testing
window.animatedIconLoader = animatedIconLoader;

// Integration with existing icon fallback system
document.addEventListener('DOMContentLoaded', () => {
    // If icon fallback is triggered, also animate the fallback icons
    const originalShowFallbackIcons = window.iconFallbackManager?.showFallbackIcons;
    if (originalShowFallbackIcons) {
        window.iconFallbackManager.showFallbackIcons = function() {
            originalShowFallbackIcons.call(this);
            // Re-trigger animations for fallback icons
            setTimeout(() => {
                animatedIconLoader.triggerIconAnimations();
            }, 100);
        };
    }
});