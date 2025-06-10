/**
 * Main JavaScript file for 2ª Vara Cível de Cariacica
 * Handles general site functionality, accessibility features, and UI interactions
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeAccessibilityFeatures();
    initializeBootstrapComponents();
    initializeFormValidation();
    initializeLazyLoading();
    initializeSearchFunctionality();
    initializeTooltips();
    initializeSmoothScrolling();
});

/**
 * Accessibility Features
 */
function initializeAccessibilityFeatures() {
    // Font size adjustment
    let currentFontSize = 16;
    const minFontSize = 14;
    const maxFontSize = 24;

    window.increaseFontSize = function() {
        if (currentFontSize < maxFontSize) {
            currentFontSize += 2;
            document.documentElement.style.fontSize = currentFontSize + 'px';
            localStorage.setItem('fontSize', currentFontSize);
            announceToScreenReader('Fonte aumentada para ' + currentFontSize + ' pixels');
        }
    };

    window.decreaseFontSize = function() {
        if (currentFontSize > minFontSize) {
            currentFontSize -= 2;
            document.documentElement.style.fontSize = currentFontSize + 'px';
            localStorage.setItem('fontSize', currentFontSize);
            announceToScreenReader('Fonte diminuída para ' + currentFontSize + ' pixels');
        }
    };

    // High contrast toggle
    window.toggleHighContrast = function() {
        document.body.classList.toggle('high-contrast');
        const isHighContrast = document.body.classList.contains('high-contrast');
        localStorage.setItem('highContrast', isHighContrast);
        announceToScreenReader(isHighContrast ? 'Alto contraste ativado' : 'Alto contraste desativado');
    };

    // Load saved preferences
    const savedFontSize = localStorage.getItem('fontSize');
    if (savedFontSize) {
        currentFontSize = parseInt(savedFontSize);
        document.documentElement.style.fontSize = currentFontSize + 'px';
    }

    const savedHighContrast = localStorage.getItem('highContrast');
    if (savedHighContrast === 'true') {
        document.body.classList.add('high-contrast');
    }

    // Keyboard navigation improvements
    document.addEventListener('keydown', function(e) {
        // Skip to main content with Alt+1
        if (e.altKey && e.key === '1') {
            e.preventDefault();
            const mainContent = document.getElementById('main-content');
            if (mainContent) {
                mainContent.focus();
                mainContent.scrollIntoView();
            }
        }

        // Focus chatbot with Alt+C
        if (e.altKey && e.key === 'c') {
            e.preventDefault();
            const chatbotToggle = document.getElementById('chatbot-toggle');
            if (chatbotToggle) {
                chatbotToggle.click();
            }
        }
    });

    // Announce dynamic content changes to screen readers
    function announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.style.position = 'absolute';
        announcement.style.left = '-10000px';
        announcement.style.width = '1px';
        announcement.style.height = '1px';
        announcement.style.overflow = 'hidden';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    // Focus management for modals
    document.addEventListener('shown.bs.modal', function(e) {
        const modal = e.target;
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length > 0) {
            focusableElements[0].focus();
        }
    });
}

/**
 * Bootstrap Components Initialization
 */
function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
            if (alertInstance) {
                alertInstance.close();
            }
        }, 5000);
    });
}

/**
 * Form Validation Enhancement
 */
function initializeFormValidation() {
    // Add custom validation styles
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalidField = form.querySelector(':invalid');
                if (firstInvalidField) {
                    firstInvalidField.focus();
                    firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            
            form.classList.add('was-validated');
        }, false);

        // Real-time validation feedback
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                if (input.checkValidity()) {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                } else {
                    input.classList.remove('is-valid');
                    input.classList.add('is-invalid');
                }
            });

            input.addEventListener('input', function() {
                if (input.classList.contains('is-invalid') && input.checkValidity()) {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                }
            });
        });
    });

    // CPF formatting and validation
    const cpfInputs = document.querySelectorAll('input[name="cpf"], input[id="cpf"]');
    cpfInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
            e.target.value = value;
        });
    });

    // Phone formatting
    const phoneInputs = document.querySelectorAll('input[type="tel"], input[name="telefone"], input[name="phone"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 11) {
                value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
            } else if (value.length >= 10) {
                value = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
            } else if (value.length >= 6) {
                value = value.replace(/(\d{2})(\d{4})(\d)/, '($1) $2-$3');
            } else if (value.length >= 2) {
                value = value.replace(/(\d{2})(\d)/, '($1) $2');
            }
            e.target.value = value;
        });
    });
}

/**
 * Lazy Loading for Performance
 */
function initializeLazyLoading() {
    // Lazy load images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                img.classList.add('fade-in');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(function(img) {
        imageObserver.observe(img);
    });

    // Lazy load content sections
    const sections = document.querySelectorAll('.lazy-section');
    const sectionObserver = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });

    sections.forEach(function(section) {
        sectionObserver.observe(section);
    });
}

/**
 * Search Functionality
 */
function initializeSearchFunctionality() {
    const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
    
    searchInputs.forEach(function(input) {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                performSearch(input.value, input);
            }, 300);
        });
    });
}

function performSearch(query, inputElement) {
    const searchableElements = document.querySelectorAll('.searchable');
    const noResultsElement = document.getElementById('no-results');
    let hasResults = false;

    searchableElements.forEach(function(element) {
        const text = element.textContent.toLowerCase();
        const matches = text.includes(query.toLowerCase());
        
        if (matches || query === '') {
            element.style.display = '';
            hasResults = true;
        } else {
            element.style.display = 'none';
        }
    });

    if (noResultsElement) {
        noResultsElement.style.display = hasResults || query === '' ? 'none' : 'block';
    }
}

/**
 * Tooltips for Better UX
 */
function initializeTooltips() {
    // Add tooltips to form fields with help text
    const formControls = document.querySelectorAll('.form-control, .form-select');
    formControls.forEach(function(control) {
        const helpText = control.parentNode.querySelector('.form-text');
        if (helpText && !control.hasAttribute('title')) {
            control.setAttribute('title', helpText.textContent);
            control.setAttribute('data-bs-toggle', 'tooltip');
            new bootstrap.Tooltip(control);
        }
    });
}

/**
 * Smooth Scrolling
 */
function initializeSmoothScrolling() {
    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update focus for accessibility
                targetElement.setAttribute('tabindex', '-1');
                targetElement.focus();
            }
        });
    });

    // Back to top functionality
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-chevron-up"></i>';
    backToTopButton.className = 'btn btn-primary position-fixed';
    backToTopButton.style.cssText = `
        bottom: 120px;
        right: 2rem;
        z-index: 999;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: none;
        opacity: 0.8;
    `;
    backToTopButton.setAttribute('aria-label', 'Voltar ao topo');
    backToTopButton.setAttribute('title', 'Voltar ao topo');

    document.body.appendChild(backToTopButton);

    // Show/hide back to top button
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });

    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

/**
 * Loading States
 */
function showLoading(element) {
    element.classList.add('loading');
    element.setAttribute('disabled', 'disabled');
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.removeAttribute('disabled');
}

/**
 * Error Handling
 */
function showError(message, container) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    if (container) {
        container.insertBefore(errorDiv, container.firstChild);
    } else {
        document.querySelector('main').insertBefore(errorDiv, document.querySelector('main').firstChild);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        const alert = bootstrap.Alert.getOrCreateInstance(errorDiv);
        if (alert) {
            alert.close();
        }
    }, 5000);
}

function showSuccess(message, container) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success alert-dismissible fade show';
    successDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    if (container) {
        container.insertBefore(successDiv, container.firstChild);
    } else {
        document.querySelector('main').insertBefore(successDiv, document.querySelector('main').firstChild);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        const alert = bootstrap.Alert.getOrCreateInstance(successDiv);
        if (alert) {
            alert.close();
        }
    }, 5000);
}

/**
 * Utility Functions
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction() {
        const context = this;
        const args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Analytics and Tracking (Privacy-conscious)
 */
function trackUserInteraction(action, element) {
    // Only track if user has consented (implement cookie consent)
    if (localStorage.getItem('analyticsConsent') === 'true') {
        console.log('User interaction:', action, element);
        // Implement your analytics tracking here
    }
}

/**
 * Performance Monitoring
 */
function measurePerformance() {
    // Measure page load time
    window.addEventListener('load', function() {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        console.log('Page load time:', loadTime + 'ms');
        
        // Track slow loading pages
        if (loadTime > 3000) {
            console.warn('Slow page load detected:', loadTime + 'ms');
        }
    });
}

// Initialize performance monitoring
measurePerformance();

// Export functions for global use
window.Court = {
    showLoading,
    hideLoading,
    showError,
    showSuccess,
    trackUserInteraction,
    debounce,
    throttle
};
