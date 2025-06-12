/**
 * Mobile Optimization Script for 2ª Vara Cível de Cariacica
 * Enhances mobile user experience with touch interactions and performance optimizations
 */

window.MobileOptimizer = window.MobileOptimizer || class MobileOptimizer {
    constructor() {
        this.isMobile = this.detectMobile();
        this.isTouch = 'ontouchstart' in window;
        this.viewport = this.getViewportSize();
        
        this.init();
    }

    init() {
        if (this.isMobile) {
            this.setupMobileOptimizations();
            this.setupTouchInteractions();
            this.setupViewportHandling();
            this.setupPerformanceOptimizations();
            this.setupAccessibilityEnhancements();
            
            console.log('Mobile optimizations activated');
        }
    }

    detectMobile() {
        const userAgent = navigator.userAgent.toLowerCase();
        const mobileKeywords = ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'webos'];
        
        return mobileKeywords.some(keyword => userAgent.includes(keyword)) || 
               window.innerWidth <= 768;
    }

    getViewportSize() {
        return {
            width: window.innerWidth,
            height: window.innerHeight
        };
    }

    setupMobileOptimizations() {
        // Add mobile-specific classes
        document.body.classList.add('mobile-optimized');
        
        // Optimize font sizes for mobile
        this.optimizeFontSizes();
        
        // Enhance button sizes for touch
        this.enhanceButtonSizes();
        
        // Improve form interactions
        this.optimizeForms();
    }

    setupTouchInteractions() {
        // Add touch feedback to interactive elements
        const interactiveElements = document.querySelectorAll('button, .btn, a, .card, .service-card');
        
        interactiveElements.forEach(element => {
            element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
            element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });
        });

        // Improve scrolling on iOS
        this.optimizeScrolling();
        
        // Add swipe gestures where appropriate
        this.addSwipeGestures();
    }

    handleTouchStart(event) {
        const element = event.currentTarget;
        element.classList.add('touch-active');
        
        // Add haptic feedback if available
        if (navigator.vibrate) {
            navigator.vibrate(10);
        }
    }

    handleTouchEnd(event) {
        const element = event.currentTarget;
        setTimeout(() => {
            element.classList.remove('touch-active');
        }, 150);
    }

    optimizeScrolling() {
        // Add momentum scrolling for iOS
        const scrollableElements = document.querySelectorAll('.chatbot-messages, .accessibility-content');
        
        scrollableElements.forEach(element => {
            element.style.webkitOverflowScrolling = 'touch';
            element.style.overflowScrolling = 'touch';
        });
    }

    addSwipeGestures() {
        // Add swipe to close for modal-like elements
        const modals = document.querySelectorAll('.chatbot-window, .accessibility-boxcard');
        
        modals.forEach(modal => {
            this.addSwipeToClose(modal);
        });
    }

    addSwipeToClose(element) {
        let startY = 0;
        let currentY = 0;
        let isDragging = false;

        element.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
            isDragging = true;
        }, { passive: true });

        element.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            
            currentY = e.touches[0].clientY;
            const deltaY = currentY - startY;
            
            if (deltaY > 50) {
                element.style.transform = `translateY(${deltaY}px)`;
                element.style.opacity = Math.max(0.3, 1 - (deltaY / 200));
            }
        }, { passive: true });

        element.addEventListener('touchend', () => {
            if (!isDragging) return;
            
            const deltaY = currentY - startY;
            
            if (deltaY > 100) {
                // Close the element
                if (element.classList.contains('chatbot-window')) {
                    document.getElementById('chatbot-close')?.click();
                } else if (element.classList.contains('accessibility-boxcard')) {
                    document.getElementById('close-accessibility')?.click();
                }
            } else {
                // Reset position
                element.style.transform = '';
                element.style.opacity = '';
            }
            
            isDragging = false;
        }, { passive: true });
    }

    setupViewportHandling() {
        // Handle orientation changes
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleOrientationChange();
            }, 100);
        });

        // Handle viewport size changes
        window.addEventListener('resize', this.debounce(() => {
            this.handleViewportResize();
        }, 250));

        // Prevent zoom on double tap for specific elements
        this.preventDoubleTabZoom();
    }

    handleOrientationChange() {
        // Recalculate viewport
        this.viewport = this.getViewportSize();
        
        // Adjust accessibility controls position
        this.adjustAccessibilityControls();
        
        // Adjust chatbot position
        this.adjustChatbotPosition();
        
        // Trigger a reflow to fix any layout issues
        document.body.style.display = 'none';
        document.body.offsetHeight; // Force reflow
        document.body.style.display = '';
    }

    handleViewportResize() {
        this.viewport = this.getViewportSize();
        this.adjustAccessibilityControls();
    }

    adjustAccessibilityControls() {
        const toggleBtn = document.getElementById('accessibility-toggle');
        const container = document.getElementById('accessibility-controls-container');
        
        if (toggleBtn && this.viewport.width <= 768) {
            toggleBtn.style.bottom = '100px';
            toggleBtn.style.top = 'auto';
        }
        
        if (container && this.viewport.width <= 768) {
            container.style.maxWidth = '95vw';
            container.style.maxHeight = '90vh';
        }
    }

    adjustChatbotPosition() {
        const chatbotToggle = document.getElementById('chatbot-toggle');
        const chatbotWindow = document.getElementById('chatbot-window');
        
        if (chatbotToggle && this.viewport.width <= 768) {
            chatbotToggle.style.width = '60px';
            chatbotToggle.style.height = '60px';
        }
        
        if (chatbotWindow && this.viewport.width <= 768) {
            chatbotWindow.style.maxHeight = '60vh';
            chatbotWindow.style.left = '10px';
            chatbotWindow.style.right = '10px';
        }
    }

    preventDoubleTabZoom() {
        const elements = document.querySelectorAll('button, .btn, a');
        
        elements.forEach(element => {
            let lastTouchEnd = 0;
            
            element.addEventListener('touchend', (event) => {
                const now = Date.now();
                if (now - lastTouchEnd <= 300) {
                    event.preventDefault();
                }
                lastTouchEnd = now;
            }, false);
        });
    }

    setupPerformanceOptimizations() {
        // Lazy load images
        this.setupLazyLoading();
        
        // Optimize animations
        this.optimizeAnimations();
        
        // Reduce repaints and reflows
        this.optimizeRendering();
    }

    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const images = document.querySelectorAll('img[data-src]');
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        }
    }

    optimizeAnimations() {
        // Reduce animations on low-end devices
        if (this.isLowEndDevice()) {
            document.body.classList.add('reduce-motion');
            
            // Disable complex animations
            const style = document.createElement('style');
            style.textContent = `
                .reduce-motion * {
                    animation-duration: 0.01s !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01s !important;
                }
            `;
            document.head.appendChild(style);
        }
    }

    isLowEndDevice() {
        // Basic heuristic for low-end device detection
        const memory = navigator.deviceMemory || 4;
        const cores = navigator.hardwareConcurrency || 2;
        
        return memory <= 2 || cores <= 2;
    }

    optimizeRendering() {
        // Use transform3d to enable hardware acceleration for key elements
        const elements = document.querySelectorAll('.hero-banner-title-full, .accessibility-toggle-btn, .chatbot-toggle');
        
        elements.forEach(element => {
            element.style.transform = 'translate3d(0, 0, 0)';
            element.style.willChange = 'transform';
        });
    }

    setupAccessibilityEnhancements() {
        // Enhance focus management for mobile
        this.enhanceFocusManagement();
        
        // Improve voice over support
        this.improveVoiceOverSupport();
        
        // Add skip links for mobile navigation
        this.addMobileSkipLinks();
    }

    enhanceFocusManagement() {
        // Ensure focus is visible on mobile
        const focusableElements = document.querySelectorAll('button, a, input, select, textarea');
        
        focusableElements.forEach(element => {
            element.addEventListener('focus', () => {
                element.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
            });
        });
    }

    improveVoiceOverSupport() {
        // Add better ARIA labels for mobile screen readers
        const buttons = document.querySelectorAll('button:not([aria-label])');
        
        buttons.forEach(button => {
            const text = button.textContent.trim();
            if (text) {
                button.setAttribute('aria-label', text);
            }
        });
    }

    addMobileSkipLinks() {
        // Add mobile-specific skip links
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'Pular para o conteúdo principal';
        skipLink.className = 'skip-link mobile-skip-link';
        skipLink.style.cssText = `
            position: fixed;
            top: -40px;
            left: 6px;
            background: #2c5aa0;
            color: white;
            padding: 8px;
            text-decoration: none;
            z-index: 10000;
            border-radius: 0 0 4px 4px;
            font-size: 14px;
            transition: top 0.3s;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '0';
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
    }

    optimizeFontSizes() {
        // Ensure readable font sizes on mobile
        const elements = document.querySelectorAll('p, span, div, a');
        
        elements.forEach(element => {
            const computedStyle = window.getComputedStyle(element);
            const fontSize = parseFloat(computedStyle.fontSize);
            
            if (fontSize < 14) {
                element.style.fontSize = '14px';
            }
        });
    }

    enhanceButtonSizes() {
        // Ensure buttons meet touch target guidelines (44px minimum)
        const buttons = document.querySelectorAll('button, .btn, a');
        
        buttons.forEach(button => {
            const rect = button.getBoundingClientRect();
            
            if (rect.height < 44 || rect.width < 44) {
                button.style.minHeight = '44px';
                button.style.minWidth = '44px';
                button.style.display = 'inline-flex';
                button.style.alignItems = 'center';
                button.style.justifyContent = 'center';
            }
        });
    }

    optimizeForms() {
        // Optimize form inputs for mobile
        const inputs = document.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            // Prevent zoom on iOS
            if (input.type !== 'file') {
                input.style.fontSize = '16px';
            }
            
            // Add appropriate input modes
            switch (input.type) {
                case 'email':
                    input.setAttribute('inputmode', 'email');
                    break;
                case 'tel':
                    input.setAttribute('inputmode', 'tel');
                    break;
                case 'number':
                    input.setAttribute('inputmode', 'numeric');
                    break;
                case 'url':
                    input.setAttribute('inputmode', 'url');
                    break;
            }
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Public method to get mobile status
    static isMobileDevice() {
        return new MobileOptimizer().isMobile;
    }
}

// Add touch feedback styles
const touchStyles = document.createElement('style');
touchStyles.textContent = `
    .touch-active {
        transform: scale(0.98) !important;
        opacity: 0.8 !important;
        transition: all 0.1s ease !important;
    }
    
    .mobile-optimized .btn:active,
    .mobile-optimized button:active {
        transform: scale(0.95);
    }
    
    .mobile-skip-link:focus {
        outline: 2px solid #fff;
        outline-offset: 2px;
    }
`;
document.head.appendChild(touchStyles);

// Initialize mobile optimization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.mobileOptimizer = new MobileOptimizer();
    });
} else {
    window.mobileOptimizer = new MobileOptimizer();
}

// Export for use in other scripts
window.MobileOptimizer = MobileOptimizer;