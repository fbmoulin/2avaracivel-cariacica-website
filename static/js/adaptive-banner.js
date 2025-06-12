/**
 * Adaptive Banner Sizing for Different Devices
 * Dynamic banner optimization based on device characteristics
 */

class AdaptiveBannerManager {
    constructor() {
        this.banner = null;
        this.container = null;
        this.deviceInfo = this.getDeviceInfo();
        this.resizeTimeout = null;
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupBanner());
        } else {
            this.setupBanner();
        }
    }
    
    setupBanner() {
        this.banner = document.querySelector('.hero-banner-title');
        this.container = document.querySelector('.hero-banner-container');
        
        if (!this.banner || !this.container) return;
        
        // Apply initial sizing
        this.applyAdaptiveSizing();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Apply device-specific optimizations
        this.applyDeviceOptimizations();
    }
    
    getDeviceInfo() {
        const userAgent = navigator.userAgent;
        const screen = window.screen;
        const devicePixelRatio = window.devicePixelRatio || 1;
        
        return {
            isMobile: /Mobile|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent),
            isTablet: /iPad|Android/i.test(userAgent) && !/Mobile/i.test(userAgent),
            isDesktop: !/Mobile|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent),
            isRetina: devicePixelRatio >= 2,
            screenWidth: screen.width,
            screenHeight: screen.height,
            viewportWidth: window.innerWidth,
            viewportHeight: window.innerHeight,
            devicePixelRatio: devicePixelRatio,
            orientation: screen.width > screen.height ? 'landscape' : 'portrait',
            connection: navigator.connection || navigator.mozConnection || navigator.webkitConnection,
            isSlowConnection: this.isSlowConnection()
        };
    }
    
    isSlowConnection() {
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        if (!connection) return false;
        
        const slowTypes = ['slow-2g', '2g', 'bluetooth', 'cellular'];
        return slowTypes.includes(connection.effectiveType) || connection.downlink < 1.5;
    }
    
    applyAdaptiveSizing() {
        const { viewportWidth, viewportHeight, isMobile, isTablet, orientation } = this.deviceInfo;
        
        let maxHeight, minHeight, padding;
        
        // Ultra-wide screens (1400px+)
        if (viewportWidth >= 1400) {
            maxHeight = '450px';
            minHeight = '280px';
            padding = '0 3rem';
        }
        // Extra large screens (1200px+)
        else if (viewportWidth >= 1200) {
            maxHeight = '400px';
            minHeight = '250px';
            padding = '0 2rem';
        }
        // Large screens (992px-1199px)
        else if (viewportWidth >= 992) {
            maxHeight = '350px';
            minHeight = '220px';
            padding = '0 1.5rem';
        }
        // Medium screens (768px-991px)
        else if (viewportWidth >= 768) {
            maxHeight = '280px';
            minHeight = '180px';
            padding = '0 1rem';
        }
        // Small screens (576px-767px)
        else if (viewportWidth >= 576) {
            maxHeight = '220px';
            minHeight = '140px';
            padding = '0 0.75rem';
        }
        // Extra small screens (under 576px)
        else {
            maxHeight = '180px';
            minHeight = '120px';
            padding = '0 0.5rem';
        }
        
        // Adjust for landscape orientation on mobile
        if ((isMobile || isTablet) && orientation === 'landscape' && viewportHeight < 600) {
            maxHeight = Math.min(parseInt(maxHeight), 150) + 'px';
            minHeight = Math.min(parseInt(minHeight), 100) + 'px';
        }
        
        // Apply styles
        this.banner.style.maxHeight = maxHeight;
        this.banner.style.minHeight = minHeight;
        this.banner.style.padding = padding;
        
        // Log sizing for debugging
        console.log(`Adaptive Banner: ${viewportWidth}x${viewportHeight} -> ${maxHeight} (${this.getDeviceType()})`);
    }
    
    getDeviceType() {
        const { isMobile, isTablet, viewportWidth } = this.deviceInfo;
        
        if (isMobile) return 'Mobile';
        if (isTablet) return 'Tablet';
        if (viewportWidth >= 1400) return 'Ultra-wide Desktop';
        if (viewportWidth >= 1200) return 'Large Desktop';
        if (viewportWidth >= 992) return 'Desktop';
        return 'Small Desktop';
    }
    
    applyDeviceOptimizations() {
        const { isMobile, isRetina, isSlowConnection, devicePixelRatio } = this.deviceInfo;
        
        // Optimize for retina displays
        if (isRetina) {
            this.banner.style.imageRendering = 'crisp-edges';
            this.banner.style.imageRendering = '-webkit-optimize-contrast';
        }
        
        // Reduce animations on slow connections or mobile
        if (isSlowConnection || (isMobile && devicePixelRatio < 2)) {
            this.banner.style.animation = 'bannerGlowMobile 4s ease-in-out infinite alternate';
        }
        
        // Touch-friendly adjustments for mobile
        if (isMobile) {
            this.banner.style.touchAction = 'manipulation';
            this.container.style.userSelect = 'none';
        }
        
        // Performance optimizations
        this.banner.style.willChange = 'transform, filter';
        this.banner.style.backfaceVisibility = 'hidden';
    }
    
    setupEventListeners() {
        // Resize handler with debouncing
        window.addEventListener('resize', () => {
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                this.deviceInfo = this.getDeviceInfo();
                this.applyAdaptiveSizing();
                this.applyDeviceOptimizations();
            }, 250);
        });
        
        // Orientation change handler
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.deviceInfo = this.getDeviceInfo();
                this.applyAdaptiveSizing();
            }, 500); // Delay to ensure new dimensions are available
        });
        
        // Visibility change for performance
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.banner.style.animationPlayState = 'paused';
            } else {
                this.banner.style.animationPlayState = 'running';
            }
        });
        
        // Connection change handler
        if (navigator.connection) {
            navigator.connection.addEventListener('change', () => {
                this.deviceInfo.isSlowConnection = this.isSlowConnection();
                this.applyDeviceOptimizations();
            });
        }
    }
    
    // Manual refresh method for external use
    refresh() {
        this.deviceInfo = this.getDeviceInfo();
        this.applyAdaptiveSizing();
        this.applyDeviceOptimizations();
    }
    
    // Get current sizing info for debugging
    getSizingInfo() {
        return {
            deviceType: this.getDeviceType(),
            viewport: `${this.deviceInfo.viewportWidth}x${this.deviceInfo.viewportHeight}`,
            screen: `${this.deviceInfo.screenWidth}x${this.deviceInfo.screenHeight}`,
            devicePixelRatio: this.deviceInfo.devicePixelRatio,
            orientation: this.deviceInfo.orientation,
            currentBannerSize: {
                maxHeight: this.banner.style.maxHeight,
                minHeight: this.banner.style.minHeight,
                actualWidth: this.banner.offsetWidth,
                actualHeight: this.banner.offsetHeight
            }
        };
    }
}

// Initialize adaptive banner when script loads
let adaptiveBanner;

// Ensure script runs after DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        adaptiveBanner = new AdaptiveBannerManager();
    });
} else {
    adaptiveBanner = new AdaptiveBannerManager();
}

// Export for external access
window.AdaptiveBanner = {
    refresh: () => adaptiveBanner?.refresh(),
    getSizingInfo: () => adaptiveBanner?.getSizingInfo(),
    manager: adaptiveBanner
};