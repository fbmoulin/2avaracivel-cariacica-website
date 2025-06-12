/**
 * Icon Fallback System for Service Icons
 * Detects FontAwesome loading failures and shows emoji fallbacks
 */

class IconFallbackManager {
    constructor() {
        this.fallbackDelay = 2000; // Wait 2 seconds for FontAwesome to load
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.checkIcons());
        } else {
            this.checkIcons();
        }
    }

    checkIcons() {
        // Wait a bit for FontAwesome to load, then check
        setTimeout(() => {
            this.detectFontAwesomeFailure();
        }, this.fallbackDelay);
    }

    detectFontAwesomeFailure() {
        // Test if FontAwesome is loaded by checking computed styles
        const testIcon = document.createElement('i');
        testIcon.className = 'fas fa-test';
        testIcon.style.position = 'absolute';
        testIcon.style.left = '-9999px';
        document.body.appendChild(testIcon);

        const computedStyle = window.getComputedStyle(testIcon, '::before');
        const fontFamily = computedStyle.getPropertyValue('font-family');
        
        document.body.removeChild(testIcon);

        // If FontAwesome isn't loaded, font-family won't contain "Font Awesome"
        const isFontAwesomeLoaded = fontFamily.toLowerCase().includes('font awesome') || 
                                    fontFamily.toLowerCase().includes('fontawesome');

        if (!isFontAwesomeLoaded) {
            this.showFallbackIcons();
        }
    }

    showFallbackIcons() {
        console.log('FontAwesome not detected, showing emoji fallbacks');
        
        // Hide all FontAwesome icons
        const fontAwesomeIcons = document.querySelectorAll('.service-icon-container i[class*="fa"]');
        fontAwesomeIcons.forEach(icon => {
            icon.style.display = 'none';
        });

        // Show all fallback icons
        const fallbackIcons = document.querySelectorAll('.service-icon-fallback');
        fallbackIcons.forEach(fallback => {
            fallback.style.display = 'flex';
        });

        // Update CSS for emoji fallbacks
        this.updateFallbackStyles();
    }

    updateFallbackStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .service-icon-fallback {
                display: flex !important;
                align-items: center;
                justify-content: center;
                width: 80px;
                height: 80px;
                margin: 0 auto;
                background: linear-gradient(135deg, rgba(30, 64, 175, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
                border-radius: 50%;
                border: 2px solid rgba(30, 64, 175, 0.1);
                font-size: 2.5rem;
                transition: all 0.3s ease;
                position: relative;
            }

            .service-icon-fallback::before {
                content: '';
                position: absolute;
                top: -3px;
                left: -3px;
                right: -3px;
                bottom: -3px;
                background: linear-gradient(135deg, #1e40af, #3b82f6);
                border-radius: 50%;
                z-index: -1;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .quick-access-card:hover .service-icon-fallback::before {
                opacity: 1;
            }

            .quick-access-card:hover .service-icon-fallback {
                background: white;
                transform: scale(1.15);
                box-shadow: 0 8px 25px rgba(30, 64, 175, 0.2);
                border-color: transparent;
            }
        `;
        document.head.appendChild(style);
    }

    // Force show fallbacks (for testing)
    forceFallback() {
        this.showFallbackIcons();
    }
}

// Initialize the fallback manager
const iconFallbackManager = new IconFallbackManager();

// Make it globally accessible for debugging
window.iconFallbackManager = iconFallbackManager;