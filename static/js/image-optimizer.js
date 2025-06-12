/**
 * Image Loading Optimizer for 2ª Vara Cível de Cariacica
 * Handles lazy loading, retina display support, and error handling
 */

class ImageOptimizer {
    constructor() {
        this.images = new Map();
        this.retryCount = new Map();
        this.maxRetries = 3;
        this.retryDelay = 1000;
        
        this.init();
    }

    init() {
        // Initialize on DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupImages());
        } else {
            this.setupImages();
        }
    }

    setupImages() {
        // Find all images and optimize them
        const images = document.querySelectorAll('img');
        images.forEach(img => this.optimizeImage(img));

        // Setup lazy loading observer
        this.setupLazyLoading();

        // Setup error handling
        this.setupErrorHandling();
    }

    optimizeImage(img) {
        // Add loading attribute if not present
        if (!img.hasAttribute('loading')) {
            img.setAttribute('loading', 'lazy');
        }

        // Add error handling
        img.addEventListener('error', (e) => this.handleImageError(e.target));
        
        // Add load success handling
        img.addEventListener('load', (e) => this.handleImageLoad(e.target));

        // Store image reference
        this.images.set(img.src, img);
    }

    setupLazyLoading() {
        // Intersection Observer for lazy loading
        if ('IntersectionObserver' in window) {
            const lazyImageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        this.loadImage(img);
                        lazyImageObserver.unobserve(img);
                    }
                });
            });

            // Observe images with data-src attribute
            document.querySelectorAll('img[data-src]').forEach(img => {
                lazyImageObserver.observe(img);
            });
        }
    }

    setupErrorHandling() {
        // Global error handler for images
        window.addEventListener('error', (e) => {
            if (e.target.tagName === 'IMG') {
                this.handleImageError(e.target);
            }
        }, true);
    }

    loadImage(img) {
        if (img.dataset.src) {
            img.src = img.dataset.src;
            img.classList.add('loading');
        }
    }

    handleImageLoad(img) {
        img.classList.remove('loading');
        img.classList.add('loaded');
        console.log(`Image loaded successfully: ${img.src}`);
    }

    handleImageError(img) {
        const src = img.src;
        const retries = this.retryCount.get(src) || 0;

        if (retries < this.maxRetries) {
            // Retry loading the image
            setTimeout(() => {
                this.retryCount.set(src, retries + 1);
                img.src = src + '?retry=' + (retries + 1);
            }, this.retryDelay * (retries + 1));
        } else {
            // Use fallback image
            this.useFallbackImage(img);
        }
    }

    useFallbackImage(img) {
        // Create a placeholder SVG as fallback
        const fallbackSvg = this.createFallbackSvg(img.width || 300, img.height || 200);
        img.src = fallbackSvg;
        img.classList.add('fallback-image');
        img.alt = img.alt || 'Imagem não disponível';
        
        console.warn(`Image failed to load, using fallback: ${img.dataset.originalSrc || img.src}`);
    }

    createFallbackSvg(width, height) {
        const svg = `
            <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
                <rect width="100%" height="100%" fill="#f3f4f6"/>
                <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" 
                      font-family="Arial, sans-serif" font-size="14" fill="#6b7280">
                    Imagem não disponível
                </text>
            </svg>
        `;
        return 'data:image/svg+xml;base64,' + btoa(svg);
    }

    // Preload critical images
    preloadCriticalImages() {
        const criticalImages = [
            '/static/images/banners/banner_principal.png',
            '/static/images/institutional/forum_cariacica.png',
            '/static/images/chatbot/chatbot_avatar.png'
        ];

        criticalImages.forEach(src => {
            const img = new Image();
            img.src = src;
        });
    }

    // Check if retina display is available
    isRetinaDisplay() {
        return window.devicePixelRatio > 1;
    }

    // Get retina version of image path
    getRetinaImagePath(originalPath) {
        if (!this.isRetinaDisplay()) {
            return originalPath;
        }

        const lastDotIndex = originalPath.lastIndexOf('.');
        if (lastDotIndex === -1) {
            return originalPath;
        }

        const basePath = originalPath.substring(0, lastDotIndex);
        const extension = originalPath.substring(lastDotIndex);
        return `${basePath}@2x${extension}`;
    }

    // Update all images to use retina versions if available
    upgradeToRetina() {
        if (!this.isRetinaDisplay()) {
            return;
        }

        document.querySelectorAll('img').forEach(img => {
            const retinaPath = this.getRetinaImagePath(img.src);
            if (retinaPath !== img.src) {
                // Test if retina version exists
                const testImg = new Image();
                testImg.onload = () => {
                    img.src = retinaPath;
                };
                testImg.src = retinaPath;
            }
        });
    }
}

// Initialize the image optimizer
const imageOptimizer = new ImageOptimizer();

// Preload critical images after page load
window.addEventListener('load', () => {
    imageOptimizer.preloadCriticalImages();
    imageOptimizer.upgradeToRetina();
});

// Export for other modules
window.ImageOptimizer = ImageOptimizer;