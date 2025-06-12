// Test script to verify icon fallback system
document.addEventListener('DOMContentLoaded', function() {
    // Test both FontAwesome and fallback scenarios
    console.log('Testing icon display system...');
    
    // Check if FontAwesome is loaded
    const testIcon = document.createElement('i');
    testIcon.className = 'fas fa-test';
    testIcon.style.position = 'absolute';
    testIcon.style.left = '-9999px';
    document.body.appendChild(testIcon);
    
    const computedStyle = window.getComputedStyle(testIcon, '::before');
    const fontFamily = computedStyle.getPropertyValue('font-family');
    
    document.body.removeChild(testIcon);
    
    const isFontAwesome = fontFamily.toLowerCase().includes('font awesome') || 
                         fontFamily.toLowerCase().includes('fontawesome');
    
    console.log('FontAwesome detected:', isFontAwesome);
    console.log('Font family:', fontFamily);
    
    // If FontAwesome isn't working, force fallbacks immediately
    if (!isFontAwesome) {
        console.log('Activating fallback icons immediately...');
        if (window.iconFallbackManager) {
            window.iconFallbackManager.forceFallback();
        }
    }
    
    // Also provide a manual trigger for testing
    window.testFallbackIcons = function() {
        console.log('Manual fallback activation...');
        if (window.iconFallbackManager) {
            window.iconFallbackManager.forceFallback();
        }
    };
    
    // Show current icon status
    setTimeout(() => {
        const visibleIcons = document.querySelectorAll('.service-icon-container i[style*="display: none"], .service-icon-fallback[style*="display: flex"], .service-icon-fallback[style*="display: block"]');
        console.log('Visible fallback icons:', visibleIcons.length);
        
        const hiddenIcons = document.querySelectorAll('.service-icon-container i:not([style*="display: none"])');
        console.log('FontAwesome icons:', hiddenIcons.length);
    }, 3000);
});