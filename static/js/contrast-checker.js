/**
 * Contrast Checker for 2ª Vara Cível de Cariacica
 * Automatically validates color contrast ratios for WCAG 2.1 AA compliance
 */

class ContrastChecker {
    constructor() {
        this.wcagAAThreshold = 4.5; // WCAG AA standard for normal text
        this.wcagAALargeThreshold = 3.0; // WCAG AA standard for large text
        this.results = [];
        this.init();
    }

    init() {
        this.checkPageContrast();
        this.generateReport();
    }

    // Convert RGB to relative luminance
    getLuminance(r, g, b) {
        const [rs, gs, bs] = [r, g, b].map(c => {
            c = c / 255;
            return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    }

    // Calculate contrast ratio between two colors
    getContrastRatio(color1, color2) {
        const lum1 = this.getLuminance(...color1);
        const lum2 = this.getLuminance(...color2);
        const brightest = Math.max(lum1, lum2);
        const darkest = Math.min(lum1, lum2);
        return (brightest + 0.05) / (darkest + 0.05);
    }

    // Parse RGB color from computed style
    parseRGB(colorString) {
        if (colorString.startsWith('rgb')) {
            const matches = colorString.match(/\d+/g);
            return matches ? matches.map(Number) : [0, 0, 0];
        }
        return [0, 0, 0];
    }

    // Check if text is considered large (18pt+ or 14pt+ bold)
    isLargeText(element) {
        const computedStyle = window.getComputedStyle(element);
        const fontSize = parseFloat(computedStyle.fontSize);
        const fontWeight = computedStyle.fontWeight;
        
        return fontSize >= 24 || (fontSize >= 19 && (fontWeight === 'bold' || parseInt(fontWeight) >= 700));
    }

    // Get background color considering inheritance
    getBackgroundColor(element) {
        let current = element;
        while (current && current !== document.body) {
            const bg = window.getComputedStyle(current).backgroundColor;
            if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                return this.parseRGB(bg);
            }
            current = current.parentElement;
        }
        return [255, 255, 255]; // Default to white
    }

    // Check contrast for specific elements
    checkPageContrast() {
        const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, a, .btn, .card-title, .card-text, .nav-link, .form-label, .alert');
        
        textElements.forEach((element, index) => {
            if (element.offsetParent === null) return; // Skip hidden elements
            
            const computedStyle = window.getComputedStyle(element);
            const textColor = this.parseRGB(computedStyle.color);
            const backgroundColor = this.getBackgroundColor(element);
            
            const contrastRatio = this.getContrastRatio(textColor, backgroundColor);
            const isLarge = this.isLargeText(element);
            const threshold = isLarge ? this.wcagAALargeThreshold : this.wcagAAThreshold;
            const passes = contrastRatio >= threshold;
            
            this.results.push({
                element: element.tagName.toLowerCase() + (element.className ? '.' + element.className.split(' ').join('.') : ''),
                textColor: `rgb(${textColor.join(', ')})`,
                backgroundColor: `rgb(${backgroundColor.join(', ')})`,
                contrastRatio: contrastRatio.toFixed(2),
                threshold: threshold,
                passes: passes,
                isLargeText: isLarge,
                text: element.textContent.trim().substring(0, 50) + (element.textContent.trim().length > 50 ? '...' : '')
            });
        });
    }

    // Generate accessibility report
    generateReport() {
        const passed = this.results.filter(r => r.passes).length;
        const failed = this.results.filter(r => !r.passes).length;
        const total = this.results.length;

        console.group('🎨 Relatório de Contraste de Cores');
        console.log(`Total de elementos verificados: ${total}`);
        console.log(`✅ Aprovados: ${passed}`);
        console.log(`❌ Reprovados: ${failed}`);
        console.log(`📊 Taxa de aprovação: ${((passed / total) * 100).toFixed(1)}%`);

        if (failed > 0) {
            console.group('❌ Elementos com contraste insuficiente:');
            this.results.filter(r => !r.passes).forEach(result => {
                console.warn(`${result.element}: ${result.contrastRatio}:1 (mínimo: ${result.threshold}:1)`);
                console.log(`   Texto: "${result.text}"`);
                console.log(`   Cor do texto: ${result.textColor}`);
                console.log(`   Cor de fundo: ${result.backgroundColor}`);
            });
            console.groupEnd();
        }

        console.group('✅ Elementos com bom contraste:');
        this.results.filter(r => r.passes).slice(0, 10).forEach(result => {
            console.log(`${result.element}: ${result.contrastRatio}:1 ✓`);
        });
        if (passed > 10) {
            console.log(`... e mais ${passed - 10} elementos`);
        }
        console.groupEnd();

        console.groupEnd();

        // Store results globally for debugging
        window.contrastResults = this.results;
    }

    // Get recommendations for failed elements
    getRecommendations() {
        const failedElements = this.results.filter(r => !r.passes);
        const recommendations = [];

        failedElements.forEach(result => {
            if (result.contrastRatio < 3) {
                recommendations.push({
                    element: result.element,
                    issue: 'Contraste muito baixo',
                    suggestion: 'Considere usar cores mais escuras para o texto ou mais claras para o fundo'
                });
            } else if (result.contrastRatio < result.threshold) {
                recommendations.push({
                    element: result.element,
                    issue: 'Contraste abaixo do padrão WCAG AA',
                    suggestion: 'Ajuste as cores para atingir pelo menos ' + result.threshold + ':1'
                });
            }
        });

        return recommendations;
    }

    // Manual test function for specific elements
    testElement(selector) {
        const element = document.querySelector(selector);
        if (!element) {
            console.log(`Elemento '${selector}' não encontrado`);
            return;
        }

        const computedStyle = window.getComputedStyle(element);
        const textColor = this.parseRGB(computedStyle.color);
        const backgroundColor = this.getBackgroundColor(element);
        const contrastRatio = this.getContrastRatio(textColor, backgroundColor);
        const isLarge = this.isLargeText(element);
        const threshold = isLarge ? this.wcagAALargeThreshold : this.wcagAAThreshold;

        console.group(`🔍 Teste de Contraste: ${selector}`);
        console.log(`Cor do texto: rgb(${textColor.join(', ')})`);
        console.log(`Cor de fundo: rgb(${backgroundColor.join(', ')})`);
        console.log(`Contraste: ${contrastRatio.toFixed(2)}:1`);
        console.log(`Texto grande: ${isLarge ? 'Sim' : 'Não'}`);
        console.log(`Limiar necessário: ${threshold}:1`);
        console.log(`Status: ${contrastRatio >= threshold ? '✅ Aprovado' : '❌ Reprovado'}`);
        console.groupEnd();

        return {
            contrastRatio: contrastRatio.toFixed(2),
            passes: contrastRatio >= threshold,
            threshold: threshold
        };
    }
}

// Initialize contrast checker
const contrastChecker = new ContrastChecker();

// Make globally accessible for testing
window.contrastChecker = contrastChecker;

// Add to accessibility tools
if (window.accessibilityTools) {
    window.accessibilityTools.contrastChecker = contrastChecker;
}

console.log('🎨 Verificador de contraste inicializado. Use contrastChecker.testElement(selector) para testar elementos específicos.');