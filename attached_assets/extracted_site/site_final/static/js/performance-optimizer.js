/**
 * Performance Optimizer for 2ª Vara Cível de Cariacica
 * Implements lazy loading, resource prioritization, and runtime optimization
 */

class PerformanceOptimizer {
    constructor() {
        this.loadStartTime = performance.now();
        this.criticalResourcesLoaded = false;
        this.deferredComponents = new Set();
        this.init();
    }

    init() {
        this.optimizeCriticalPath();
        this.setupLazyLoading();
        this.optimizeImages();
        this.preloadCriticalResources();
        this.setupIntersectionObserver();
        this.monitorPerformance();
        console.log('Performance Optimizer initialized');
    }

    optimizeCriticalPath() {
        // Inline critical CSS for faster rendering
        const criticalCSS = document.getElementById('critical-css');
        if (!criticalCSS) {
            this.loadCriticalCSS();
        }

        // Defer non-critical JavaScript
        this.deferNonCriticalJS();
        
        // Optimize font loading
        this.optimizeFonts();
    }

    loadCriticalCSS() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = '/static/css/critical.css';
        link.id = 'critical-css';
        document.head.insertBefore(link, document.head.firstChild);
    }

    deferNonCriticalJS() {
        const nonCriticalScripts = [
            'form-microinteractions.js',
            'voice-accessibility.js',
            'mobile-optimization.js'
        ];

        // Load non-critical scripts after page load
        window.addEventListener('load', () => {
            setTimeout(() => {
                nonCriticalScripts.forEach(script => {
                    this.loadScriptAsync(`/static/js/${script}`);
                });
            }, 100);
        });
    }

    loadScriptAsync(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.async = true;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    optimizeFonts() {
        // Preload critical fonts
        const fontPreloads = [
            'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
            'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap'
        ];

        fontPreloads.forEach(href => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'style';
            link.href = href;
            link.onload = function() { this.rel = 'stylesheet'; };
            document.head.appendChild(link);
        });
    }

    setupLazyLoading() {
        // Lazy load images
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        }, { rootMargin: '50px' });

        images.forEach(img => imageObserver.observe(img));

        // Lazy load components
        this.lazyLoadComponents();
    }

    lazyLoadComponents() {
        const componentObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const componentName = element.dataset.component;
                    
                    if (componentName && !this.deferredComponents.has(componentName)) {
                        this.loadComponent(componentName);
                        this.deferredComponents.add(componentName);
                        componentObserver.unobserve(element);
                    }
                }
            });
        }, { rootMargin: '100px' });

        // Observe components marked for lazy loading
        document.querySelectorAll('[data-component]').forEach(el => {
            componentObserver.observe(el);
        });
    }

    loadComponent(componentName) {
        switch(componentName) {
            case 'chatbot':
                this.loadChatbot();
                break;
            case 'forms':
                this.loadFormEnhancements();
                break;
            case 'accessibility':
                this.loadAccessibilityFeatures();
                break;
            default:
                console.log(`Unknown component: ${componentName}`);
        }
    }

    async loadChatbot() {
        try {
            await this.loadScriptAsync('/static/js/chatbot.js');
            console.log('Chatbot loaded on demand');
        } catch (error) {
            console.error('Failed to load chatbot:', error);
        }
    }

    async loadFormEnhancements() {
        try {
            await this.loadScriptAsync('/static/js/forms.js');
            console.log('Form enhancements loaded');
        } catch (error) {
            console.error('Failed to load form enhancements:', error);
        }
    }

    async loadAccessibilityFeatures() {
        try {
            await this.loadScriptAsync('/static/js/accessibility-enhanced.js');
            console.log('Accessibility features loaded');
        } catch (error) {
            console.error('Failed to load accessibility features:', error);
        }
    }

    optimizeImages() {
        // Convert lazy loading attribute to modern standard
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.loading = 'lazy';
            img.decoding = 'async';
        });

        // Add responsive image optimization
        this.addResponsiveImages();
    }

    addResponsiveImages() {
        const images = document.querySelectorAll('img:not([srcset])');
        images.forEach(img => {
            const src = img.src || img.dataset.src;
            if (src && !src.includes('data:')) {
                // Add srcset for different screen densities
                const basePath = src.replace(/\.[^/.]+$/, '');
                const ext = src.split('.').pop();
                
                if (ext && ['jpg', 'jpeg', 'png'].includes(ext.toLowerCase())) {
                    img.srcset = `${src} 1x, ${basePath}@2x.${ext} 2x`;
                }
            }
        });
    }

    preloadCriticalResources() {
        const criticalResources = [
            '/static/css/style.css',
            '/static/js/main.js',
            '/static/images/banners/banner_principal.png'
        ];

        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = resource;
            document.head.appendChild(link);
        });
    }

    setupIntersectionObserver() {
        // Performance observer for monitoring
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    if (entry.entryType === 'measure') {
                        console.log(`Performance: ${entry.name} took ${entry.duration}ms`);
                    }
                });
            });
            
            observer.observe({ entryTypes: ['measure', 'navigation'] });
        }
    }

    monitorPerformance() {
        // Track key performance metrics
        window.addEventListener('load', () => {
            const loadTime = performance.now() - this.loadStartTime;
            console.log(`Page load completed in ${loadTime.toFixed(2)}ms`);
            
            // Report performance metrics
            this.reportPerformanceMetrics();
        });

        // Monitor Core Web Vitals
        this.trackCoreWebVitals();
    }

    reportPerformanceMetrics() {
        if ('performance' in window) {
            const navigation = performance.getEntriesByType('navigation')[0];
            const metrics = {
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
                loadComplete: navigation.loadEventEnd - navigation.fetchStart,
                firstByte: navigation.responseStart - navigation.fetchStart,
                domInteractive: navigation.domInteractive - navigation.fetchStart
            };

            // Send metrics to analytics (if available)
            this.sendMetrics(metrics);
        }
    }

    trackCoreWebVitals() {
        // Track Largest Contentful Paint (LCP)
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            const lastEntry = entries[entries.length - 1];
            console.log('LCP:', lastEntry.startTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });

        // Track First Input Delay (FID)
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            entries.forEach(entry => {
                console.log('FID:', entry.processingStart - entry.startTime);
            });
        }).observe({ entryTypes: ['first-input'] });

        // Track Cumulative Layout Shift (CLS)
        let clsValue = 0;
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            entries.forEach(entry => {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                }
            });
            console.log('CLS:', clsValue);
        }).observe({ entryTypes: ['layout-shift'] });
    }

    sendMetrics(metrics) {
        // Send to performance monitoring endpoint
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/admin/performance-metrics', JSON.stringify(metrics));
        }
    }

    // Public API for manual optimization
    optimizeElement(element) {
        if (element.tagName === 'IMG') {
            this.optimizeImage(element);
        } else if (element.classList.contains('lazy-component')) {
            this.loadComponentFromElement(element);
        }
    }

    optimizeImage(img) {
        img.loading = 'lazy';
        img.decoding = 'async';
        
        if (!img.srcset && img.src) {
            const src = img.src;
            const basePath = src.replace(/\.[^/.]+$/, '');
            const ext = src.split('.').pop();
            img.srcset = `${src} 1x, ${basePath}@2x.${ext} 2x`;
        }
    }

    loadComponentFromElement(element) {
        const componentName = element.dataset.component;
        if (componentName) {
            this.loadComponent(componentName);
        }
    }

    // Cache management
    clearPerformanceCache() {
        if ('caches' in window) {
            caches.keys().then(cacheNames => {
                cacheNames.forEach(cacheName => {
                    if (cacheName.includes('dynamic')) {
                        caches.delete(cacheName);
                    }
                });
            });
        }
    }

    preloadNextPage(url) {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = url;
        document.head.appendChild(link);
    }
}

// Initialize performance optimizer
let performanceOptimizer;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        performanceOptimizer = new PerformanceOptimizer();
        window.performanceOptimizer = performanceOptimizer;
    });
} else {
    performanceOptimizer = new PerformanceOptimizer();
    window.performanceOptimizer = performanceOptimizer;
}

// Export for global access
window.PerformanceOptimizer = PerformanceOptimizer;