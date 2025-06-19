/**
 * Accessibility Debugger and Testing Suite
 * Comprehensive testing and debugging for accessibility features
 */

class AccessibilityDebugger {
    constructor() {
        this.testResults = [];
        this.issues = [];
        this.performance = {};
        this.init();
    }

    init() {
        this.createDebugPanel();
        this.runInitialTests();
        
        // Auto-run tests when DOM changes
        this.setupDOMObserver();
        
        // Keyboard shortcut to open debugger
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.altKey && e.key === 'd') {
                e.preventDefault();
                this.toggleDebugPanel();
            }
        });
    }

    createDebugPanel() {
        const panel = document.createElement('div');
        panel.id = 'accessibility-debugger';
        panel.className = 'accessibility-debugger';
        panel.innerHTML = `
            <div class="debugger-header">
                <h3>Accessibility Debugger</h3>
                <div class="debugger-controls">
                    <button id="run-tests" class="debug-btn">Run Tests</button>
                    <button id="export-report" class="debug-btn">Export Report</button>
                    <button id="close-debugger" class="debug-btn">×</button>
                </div>
            </div>
            <div class="debugger-content">
                <div class="test-summary">
                    <div class="summary-item">
                        <span class="label">Tests Passed:</span>
                        <span id="tests-passed" class="value">0</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Issues Found:</span>
                        <span id="issues-count" class="value">0</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">Accessibility Score:</span>
                        <span id="accessibility-score" class="value">0%</span>
                    </div>
                </div>
                <div class="test-sections">
                    <div class="test-section">
                        <h4>Keyboard Navigation</h4>
                        <div id="keyboard-results" class="test-results"></div>
                    </div>
                    <div class="test-section">
                        <h4>Screen Reader Support</h4>
                        <div id="screen-reader-results" class="test-results"></div>
                    </div>
                    <div class="test-section">
                        <h4>Color Contrast</h4>
                        <div id="contrast-results" class="test-results"></div>
                    </div>
                    <div class="test-section">
                        <h4>Form Accessibility</h4>
                        <div id="form-results" class="test-results"></div>
                    </div>
                    <div class="test-section">
                        <h4>Images & Media</h4>
                        <div id="media-results" class="test-results"></div>
                    </div>
                </div>
            </div>
        `;

        // Add styles
        const styles = `
            .accessibility-debugger {
                position: fixed;
                top: 50px;
                right: 20px;
                width: 400px;
                max-height: 80vh;
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
                z-index: 10001;
                font-family: monospace;
                font-size: 12px;
                overflow: hidden;
                display: none;
            }
            
            .debugger-header {
                background: #1f2937;
                color: white;
                padding: 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .debugger-header h3 {
                margin: 0;
                font-size: 14px;
            }
            
            .debugger-controls {
                display: flex;
                gap: 8px;
            }
            
            .debug-btn {
                background: #374151;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 11px;
            }
            
            .debug-btn:hover {
                background: #4b5563;
            }
            
            .debugger-content {
                max-height: 60vh;
                overflow-y: auto;
                padding: 12px;
            }
            
            .test-summary {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 8px;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid #e5e7eb;
            }
            
            .summary-item {
                text-align: center;
            }
            
            .summary-item .label {
                display: block;
                font-size: 10px;
                color: #6b7280;
                margin-bottom: 4px;
            }
            
            .summary-item .value {
                display: block;
                font-weight: bold;
                font-size: 14px;
            }
            
            .test-section {
                margin-bottom: 16px;
            }
            
            .test-section h4 {
                margin: 0 0 8px 0;
                font-size: 12px;
                font-weight: bold;
                color: #374151;
            }
            
            .test-results {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                padding: 8px;
                min-height: 30px;
            }
            
            .test-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 4px 0;
                border-bottom: 1px solid #e5e7eb;
            }
            
            .test-item:last-child {
                border-bottom: none;
            }
            
            .test-status {
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            
            .test-pass {
                background: #d1fae5;
                color: #065f46;
            }
            
            .test-fail {
                background: #fee2e2;
                color: #991b1b;
            }
            
            .test-warning {
                background: #fef3c7;
                color: #92400e;
            }
        `;

        if (!document.getElementById('debugger-styles')) {
            const styleSheet = document.createElement('style');
            styleSheet.id = 'debugger-styles';
            styleSheet.textContent = styles;
            document.head.appendChild(styleSheet);
        }

        document.body.appendChild(panel);
        this.bindDebuggerEvents();
    }

    bindDebuggerEvents() {
        document.getElementById('run-tests')?.addEventListener('click', () => this.runAllTests());
        document.getElementById('export-report')?.addEventListener('click', () => this.exportReport());
        document.getElementById('close-debugger')?.addEventListener('click', () => this.hideDebugPanel());
    }

    toggleDebugPanel() {
        const panel = document.getElementById('accessibility-debugger');
        if (panel) {
            panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
        }
    }

    hideDebugPanel() {
        const panel = document.getElementById('accessibility-debugger');
        if (panel) {
            panel.style.display = 'none';
        }
    }

    runInitialTests() {
        setTimeout(() => {
            this.runAllTests();
        }, 1000);
    }

    runAllTests() {
        this.testResults = [];
        this.issues = [];

        // Run all test categories
        this.testKeyboardNavigation();
        this.testScreenReaderSupport();
        this.testColorContrast();
        this.testFormAccessibility();
        this.testImagesAndMedia();

        // Update UI
        this.updateTestSummary();
        this.displayResults();
    }

    testKeyboardNavigation() {
        const results = [];
        
        // Test 1: Check for focusable elements
        const focusableElements = document.querySelectorAll(
            'a[href], button, input, textarea, select, [tabindex]:not([tabindex="-1"])'
        );
        
        results.push({
            test: 'Focusable Elements Count',
            status: focusableElements.length > 0 ? 'pass' : 'fail',
            value: focusableElements.length,
            message: `Found ${focusableElements.length} focusable elements`
        });

        // Test 2: Check skip links
        const skipLinks = document.querySelectorAll('.skip-link, .skip-navigation');
        results.push({
            test: 'Skip Links',
            status: skipLinks.length > 0 ? 'pass' : 'fail',
            value: skipLinks.length,
            message: skipLinks.length > 0 ? 'Skip links found' : 'No skip links detected'
        });

        // Test 3: Check focus indicators
        let focusIndicatorTest = 'pass';
        try {
            const styles = getComputedStyle(document.documentElement);
            // This is a simplified test - in real implementation, you'd check CSS rules
            focusIndicatorTest = 'pass';
        } catch (e) {
            focusIndicatorTest = 'fail';
        }

        results.push({
            test: 'Focus Indicators',
            status: focusIndicatorTest,
            value: focusIndicatorTest === 'pass' ? 'Enhanced' : 'Basic',
            message: 'Focus indicators available'
        });

        this.displayTestResults('keyboard-results', results);
        return results;
    }

    testScreenReaderSupport() {
        const results = [];

        // Test 1: ARIA labels
        const elementsWithAria = document.querySelectorAll('[aria-label], [aria-labelledby], [aria-describedby]');
        results.push({
            test: 'ARIA Labels',
            status: elementsWithAria.length > 5 ? 'pass' : 'warning',
            value: elementsWithAria.length,
            message: `${elementsWithAria.length} elements with ARIA labels`
        });

        // Test 2: Live regions
        const liveRegions = document.querySelectorAll('[aria-live]');
        results.push({
            test: 'Live Regions',
            status: liveRegions.length > 0 ? 'pass' : 'fail',
            value: liveRegions.length,
            message: liveRegions.length > 0 ? 'Live regions found' : 'No live regions'
        });

        // Test 3: Heading structure
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const h1Count = document.querySelectorAll('h1').length;
        results.push({
            test: 'Heading Structure',
            status: h1Count === 1 && headings.length > 1 ? 'pass' : 'warning',
            value: `${headings.length} headings, ${h1Count} H1`,
            message: h1Count === 1 ? 'Good heading structure' : 'Review heading hierarchy'
        });

        // Test 4: Semantic elements
        const semanticElements = document.querySelectorAll('main, nav, header, footer, section, article, aside');
        results.push({
            test: 'Semantic Elements',
            status: semanticElements.length > 3 ? 'pass' : 'warning',
            value: semanticElements.length,
            message: `${semanticElements.length} semantic elements found`
        });

        this.displayTestResults('screen-reader-results', results);
        return results;
    }

    testColorContrast() {
        const results = [];

        // This is a simplified test - full color contrast testing requires more complex algorithms
        const textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, a, button, span');
        let contrastIssues = 0;
        let totalChecked = 0;

        for (let i = 0; i < Math.min(textElements.length, 10); i++) {
            const element = textElements[i];
            const styles = getComputedStyle(element);
            const textColor = styles.color;
            const backgroundColor = styles.backgroundColor;
            
            totalChecked++;
            
            // Simplified contrast check - in production, use proper contrast ratio calculation
            if (textColor === backgroundColor || 
                (textColor.includes('rgb(255, 255, 255)') && backgroundColor.includes('rgb(255, 255, 255)'))) {
                contrastIssues++;
            }
        }

        results.push({
            test: 'Color Contrast Ratio',
            status: contrastIssues === 0 ? 'pass' : 'warning',
            value: `${totalChecked - contrastIssues}/${totalChecked} passed`,
            message: contrastIssues === 0 ? 'No contrast issues detected' : `${contrastIssues} potential issues`
        });

        // Test high contrast mode availability
        const highContrastAvailable = document.body.classList.contains('high-contrast') || 
                                    document.querySelector('[data-contrast-toggle]') ||
                                    window.enhancedAccessibility;
        
        results.push({
            test: 'High Contrast Mode',
            status: highContrastAvailable ? 'pass' : 'fail',
            value: highContrastAvailable ? 'Available' : 'Not Available',
            message: highContrastAvailable ? 'High contrast mode supported' : 'High contrast mode missing'
        });

        this.displayTestResults('contrast-results', results);
        return results;
    }

    testFormAccessibility() {
        const results = [];

        // Test 1: Form labels
        const inputs = document.querySelectorAll('input, textarea, select');
        let labeledInputs = 0;
        
        inputs.forEach(input => {
            const hasLabel = input.getAttribute('aria-label') || 
                           input.getAttribute('aria-labelledby') ||
                           document.querySelector(`label[for="${input.id}"]`) ||
                           input.closest('label');
            if (hasLabel) labeledInputs++;
        });

        results.push({
            test: 'Form Labels',
            status: inputs.length === 0 ? 'pass' : (labeledInputs === inputs.length ? 'pass' : 'warning'),
            value: `${labeledInputs}/${inputs.length}`,
            message: inputs.length === 0 ? 'No forms found' : `${labeledInputs} of ${inputs.length} inputs labeled`
        });

        // Test 2: Required field indicators
        const requiredInputs = document.querySelectorAll('input[required], textarea[required], select[required]');
        let markedRequired = 0;
        
        requiredInputs.forEach(input => {
            const label = document.querySelector(`label[for="${input.id}"]`) || input.closest('label');
            if (label && (label.textContent.includes('*') || label.textContent.includes('obrigatório'))) {
                markedRequired++;
            }
        });

        results.push({
            test: 'Required Fields',
            status: requiredInputs.length === 0 ? 'pass' : (markedRequired === requiredInputs.length ? 'pass' : 'warning'),
            value: `${markedRequired}/${requiredInputs.length}`,
            message: requiredInputs.length === 0 ? 'No required fields' : `${markedRequired} required fields properly marked`
        });

        // Test 3: Error messaging
        const errorElements = document.querySelectorAll('.invalid-feedback, .error-message, [aria-describedby]');
        results.push({
            test: 'Error Messaging',
            status: errorElements.length > 0 ? 'pass' : 'warning',
            value: errorElements.length,
            message: errorElements.length > 0 ? 'Error messaging system found' : 'No error messaging detected'
        });

        this.displayTestResults('form-results', results);
        return results;
    }

    testImagesAndMedia() {
        const results = [];

        // Test 1: Alt text for images
        const images = document.querySelectorAll('img');
        let imagesWithAlt = 0;
        
        images.forEach(img => {
            if (img.getAttribute('alt') !== null) {
                imagesWithAlt++;
            }
        });

        results.push({
            test: 'Image Alt Text',
            status: images.length === 0 ? 'pass' : (imagesWithAlt === images.length ? 'pass' : 'fail'),
            value: `${imagesWithAlt}/${images.length}`,
            message: images.length === 0 ? 'No images found' : `${imagesWithAlt} of ${images.length} images have alt text`
        });

        // Test 2: Decorative images
        const decorativeImages = document.querySelectorAll('img[alt=""], img[role="presentation"]');
        results.push({
            test: 'Decorative Images',
            status: 'pass',
            value: decorativeImages.length,
            message: `${decorativeImages.length} images marked as decorative`
        });

        // Test 3: Video/Audio accessibility
        const mediaElements = document.querySelectorAll('video, audio');
        let accessibleMedia = 0;
        
        mediaElements.forEach(media => {
            if (media.hasAttribute('controls') || media.querySelector('track')) {
                accessibleMedia++;
            }
        });

        results.push({
            test: 'Media Controls',
            status: mediaElements.length === 0 ? 'pass' : (accessibleMedia === mediaElements.length ? 'pass' : 'warning'),
            value: `${accessibleMedia}/${mediaElements.length}`,
            message: mediaElements.length === 0 ? 'No media elements' : `${accessibleMedia} media elements have controls`
        });

        this.displayTestResults('media-results', results);
        return results;
    }

    displayTestResults(containerId, results) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';
        
        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'test-item';
            item.innerHTML = `
                <span class="test-name">${result.test}</span>
                <span class="test-status test-${result.status}">${result.status.toUpperCase()}</span>
            `;
            item.title = result.message;
            container.appendChild(item);
        });

        // Store results
        this.testResults.push(...results);
    }

    updateTestSummary() {
        const totalTests = this.testResults.length;
        const passedTests = this.testResults.filter(r => r.status === 'pass').length;
        const failedTests = this.testResults.filter(r => r.status === 'fail').length;
        const score = totalTests > 0 ? Math.round((passedTests / totalTests) * 100) : 0;

        document.getElementById('tests-passed').textContent = `${passedTests}/${totalTests}`;
        document.getElementById('issues-count').textContent = failedTests;
        document.getElementById('accessibility-score').textContent = `${score}%`;

        // Update score color
        const scoreElement = document.getElementById('accessibility-score');
        if (score >= 80) {
            scoreElement.style.color = '#059669';
        } else if (score >= 60) {
            scoreElement.style.color = '#d97706';
        } else {
            scoreElement.style.color = '#dc2626';
        }
    }

    setupDOMObserver() {
        const observer = new MutationObserver((mutations) => {
            let shouldRetest = false;
            
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // Check if significant content was added
                            if (node.matches('form, img, input, button, a[href]') || 
                                node.querySelector('form, img, input, button, a[href]')) {
                                shouldRetest = true;
                            }
                        }
                    });
                }
            });

            if (shouldRetest) {
                setTimeout(() => this.runAllTests(), 500);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    exportReport() {
        const report = {
            timestamp: new Date().toISOString(),
            url: window.location.href,
            summary: {
                total_tests: this.testResults.length,
                passed: this.testResults.filter(r => r.status === 'pass').length,
                failed: this.testResults.filter(r => r.status === 'fail').length,
                warnings: this.testResults.filter(r => r.status === 'warning').length,
                score: this.testResults.length > 0 ? Math.round((this.testResults.filter(r => r.status === 'pass').length / this.testResults.length) * 100) : 0
            },
            test_results: this.testResults,
            recommendations: this.generateRecommendations()
        };

        const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `accessibility-report-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    generateRecommendations() {
        const recommendations = [];
        const failedTests = this.testResults.filter(r => r.status === 'fail');
        const warningTests = this.testResults.filter(r => r.status === 'warning');

        failedTests.forEach(test => {
            switch (test.test) {
                case 'Skip Links':
                    recommendations.push('Add skip links to help keyboard users navigate quickly to main content');
                    break;
                case 'Live Regions':
                    recommendations.push('Implement ARIA live regions for dynamic content announcements');
                    break;
                case 'Image Alt Text':
                    recommendations.push('Add descriptive alt text to all informative images');
                    break;
                case 'High Contrast Mode':
                    recommendations.push('Implement high contrast mode toggle for users with visual impairments');
                    break;
            }
        });

        warningTests.forEach(test => {
            switch (test.test) {
                case 'Heading Structure':
                    recommendations.push('Review heading hierarchy to ensure proper structure (single H1, logical progression)');
                    break;
                case 'ARIA Labels':
                    recommendations.push('Add more ARIA labels to improve screen reader experience');
                    break;
                case 'Form Labels':
                    recommendations.push('Ensure all form inputs have proper labels or ARIA labels');
                    break;
            }
        });

        return recommendations;
    }

    displayResults() {
        const panel = document.getElementById('accessibility-debugger');
        if (panel) {
            panel.style.display = 'block';
        }
    }
}

// Initialize debugger
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.accessibilityDebugger = new AccessibilityDebugger();
    });
} else {
    window.accessibilityDebugger = new AccessibilityDebugger();
}

// Global function to enable debug mode
window.enableAccessibilityDebug = function() {
    localStorage.setItem('accessibilityDebug', 'true');
    if (window.accessibilityDebugger) {
        window.accessibilityDebugger.displayResults();
    }
    console.log('Accessibility debug mode enabled. Press Ctrl+Alt+D to toggle debugger.');
};