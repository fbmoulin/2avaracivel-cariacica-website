/**
 * Accessibility UI Module - Refined User Interface Components
 * 2ª Vara Cível de Cariacica - Advanced accessibility user interface
 */

/**
 * Visual Controls Module - Font size, contrast, and visual adjustments
 */
class VisualControlsModule extends AccessibilityModule {
    async setup() {
        this.fontSizeRange = {
            min: this.core.getSetting('fontSize.min'),
            max: this.core.getSetting('fontSize.max'),
            step: this.core.getSetting('fontSize.step')
        };
        
        this.contrastModes = ['normal', 'high', 'dark'];
        this.setupVisualEnhancements();
    }

    setupVisualEnhancements() {
        // Add CSS custom properties for dynamic control
        const root = document.documentElement;
        root.style.setProperty('--accessibility-font-size', `${this.core.getSetting('fontSize.current') || 16}px`);
        root.style.setProperty('--accessibility-contrast', this.core.getSetting('contrast.enabled') ? '150%' : '100%');
        
        // Listen for setting changes
        this.core.on('accessibility:settingChanged', this.handleSettingChange.bind(this));
    }

    handleSettingChange({ detail: { path, value } }) {
        const root = document.documentElement;
        
        switch (path) {
            case 'fontSize.current':
                root.style.setProperty('--accessibility-font-size', `${value}px`);
                root.style.fontSize = `${value}px`;
                break;
            case 'contrast.enabled':
                root.style.setProperty('--accessibility-contrast', value ? '150%' : '100%');
                document.body.classList.toggle('high-contrast', value);
                break;
            case 'motion.reduced':
                document.body.classList.toggle('reduced-motion', value);
                break;
        }
    }

    adjustFontSize(delta) {
        const current = this.core.getSetting('fontSize.current') || 16;
        const newSize = Math.max(
            this.fontSizeRange.min,
            Math.min(this.fontSizeRange.max, current + delta)
        );
        
        this.core.updateSetting('fontSize.current', newSize);
        return newSize;
    }

    setContrastMode(mode) {
        document.body.className = document.body.className.replace(/contrast-\w+/g, '');
        
        if (mode !== 'normal') {
            document.body.classList.add(`contrast-${mode}`);
        }
        
        this.core.updateSetting('contrast.mode', mode);
        this.core.updateSetting('contrast.enabled', mode !== 'normal');
    }

    toggleReducedMotion() {
        const enabled = !this.core.getSetting('motion.reduced');
        this.core.updateSetting('motion.reduced', enabled);
        return enabled;
    }

    async runDiagnostics() {
        const currentFontSize = this.core.getSetting('fontSize.current') || 16;
        const isInRange = currentFontSize >= this.fontSizeRange.min && currentFontSize <= this.fontSizeRange.max;
        
        return {
            ...await super.runDiagnostics(),
            currentFontSize,
            fontSizeInRange: isInRange,
            contrastEnabled: this.core.getSetting('contrast.enabled'),
            reducedMotion: this.core.getSetting('motion.reduced'),
            status: isInRange ? 'ok' : 'warning'
        };
    }
}

/**
 * Form Enhancer Module - Advanced form accessibility
 */
class FormEnhancerModule extends AccessibilityModule {
    async setup() {
        this.enhancedForms = new Set();
        this.validationMessages = new Map();
        
        this.enhanceExistingForms();
        this.setupFormMonitoring();
    }

    enhanceExistingForms() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => this.enhanceForm(form));
    }

    enhanceForm(form) {
        if (this.enhancedForms.has(form)) return;
        
        // Add form role and labels
        if (!form.getAttribute('role')) {
            form.setAttribute('role', 'form');
        }
        
        // Enhance form inputs
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => this.enhanceInput(input));
        
        // Add form validation
        this.setupFormValidation(form);
        
        // Mark as enhanced
        this.enhancedForms.add(form);
    }

    enhanceInput(input) {
        // Ensure proper labeling
        if (!this.hasProperLabel(input)) {
            this.addImplicitLabel(input);
        }
        
        // Add required field indicators
        if (input.hasAttribute('required')) {
            this.addRequiredIndicator(input);
        }
        
        // Add input description if needed
        this.addInputDescription(input);
        
        // Setup real-time validation
        this.setupInputValidation(input);
    }

    hasProperLabel(input) {
        return input.getAttribute('aria-label') ||
               input.getAttribute('aria-labelledby') ||
               document.querySelector(`label[for="${input.id}"]`) ||
               input.closest('label');
    }

    addImplicitLabel(input) {
        const labelText = this.inferLabelText(input);
        if (labelText) {
            input.setAttribute('aria-label', labelText);
        }
    }

    inferLabelText(input) {
        // Check previous elements for label text
        let element = input.previousElementSibling;
        while (element) {
            if (element.tagName === 'LABEL' || 
                (element.textContent && element.textContent.trim().length < 50)) {
                return element.textContent.trim();
            }
            element = element.previousElementSibling;
        }
        
        // Check parent container
        const parent = input.parentElement;
        if (parent && parent.textContent) {
            const text = parent.textContent.replace(input.value || '', '').trim();
            if (text.length < 50) return text;
        }
        
        // Use placeholder or name as fallback
        return input.getAttribute('placeholder') || 
               input.getAttribute('name') || 
               `Campo ${input.type || 'text'}`;
    }

    addRequiredIndicator(input) {
        const currentLabel = this.getInputLabel(input);
        if (currentLabel && !currentLabel.includes('obrigatório') && !currentLabel.includes('*')) {
            const enhancedLabel = `${currentLabel} (obrigatório)`;
            
            if (input.getAttribute('aria-label')) {
                input.setAttribute('aria-label', enhancedLabel);
            }
            
            // Visual indicator
            this.addVisualRequiredIndicator(input);
        }
    }

    addVisualRequiredIndicator(input) {
        const existing = input.parentElement.querySelector('.required-indicator');
        if (existing) return;
        
        const indicator = document.createElement('span');
        indicator.className = 'required-indicator';
        indicator.textContent = ' *';
        indicator.style.color = '#dc2626';
        indicator.style.fontWeight = 'bold';
        indicator.setAttribute('aria-hidden', 'true');
        
        const label = document.querySelector(`label[for="${input.id}"]`) || input.closest('label');
        if (label) {
            label.appendChild(indicator);
        } else {
            input.parentElement.insertBefore(indicator, input);
        }
    }

    addInputDescription(input) {
        const type = input.type;
        let description = '';
        
        switch (type) {
            case 'email':
                description = 'Digite um endereço de email válido';
                break;
            case 'tel':
                description = 'Digite um número de telefone';
                break;
            case 'password':
                description = 'Digite sua senha';
                break;
            case 'date':
                description = 'Selecione uma data';
                break;
        }
        
        if (description && !input.getAttribute('aria-describedby')) {
            const descId = `desc-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
            const descElement = document.createElement('div');
            descElement.id = descId;
            descElement.className = 'input-description sr-only';
            descElement.textContent = description;
            
            input.parentElement.appendChild(descElement);
            input.setAttribute('aria-describedby', descId);
        }
    }

    setupFormValidation(form) {
        form.addEventListener('submit', this.handleFormSubmit.bind(this));
    }

    setupInputValidation(input) {
        input.addEventListener('blur', () => this.validateInput(input));
        input.addEventListener('input', () => this.clearValidationMessage(input));
    }

    handleFormSubmit(event) {
        const form = event.target;
        const invalidInputs = Array.from(form.querySelectorAll(':invalid'));
        
        if (invalidInputs.length > 0) {
            event.preventDefault();
            
            // Focus first invalid input
            invalidInputs[0].focus();
            
            // Announce validation errors
            this.core.announce(
                `Formulário contém ${invalidInputs.length} erro(s). Por favor, corrija os campos destacados.`,
                'assertive'
            );
            
            // Show individual error messages
            invalidInputs.forEach(input => this.validateInput(input));
        }
    }

    validateInput(input) {
        const isValid = input.checkValidity();
        
        if (!isValid) {
            this.showValidationMessage(input, input.validationMessage);
        } else {
            this.clearValidationMessage(input);
        }
        
        return isValid;
    }

    showValidationMessage(input, message) {
        const messageId = `error-${input.id || Date.now()}`;
        let messageElement = document.getElementById(messageId);
        
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.id = messageId;
            messageElement.className = 'validation-message error-message';
            messageElement.setAttribute('role', 'alert');
            input.parentElement.appendChild(messageElement);
            
            input.setAttribute('aria-describedby', 
                (input.getAttribute('aria-describedby') || '') + ' ' + messageId
            );
        }
        
        messageElement.textContent = message;
        messageElement.style.cssText = `
            color: #dc2626;
            font-size: 0.875rem;
            margin-top: 0.25rem;
            display: block;
        `;
        
        input.setAttribute('aria-invalid', 'true');
        this.validationMessages.set(input, messageElement);
    }

    clearValidationMessage(input) {
        const messageElement = this.validationMessages.get(input);
        if (messageElement) {
            messageElement.remove();
            this.validationMessages.delete(input);
            input.removeAttribute('aria-invalid');
        }
    }

    getInputLabel(input) {
        return input.getAttribute('aria-label') ||
               input.getAttribute('title') ||
               (document.querySelector(`label[for="${input.id}"]`)?.textContent) ||
               input.getAttribute('placeholder') ||
               input.getAttribute('name');
    }

    setupFormMonitoring() {
        // Monitor for dynamically added forms
        this.core.on('accessibility:contentChanged', () => {
            const newForms = document.querySelectorAll('form');
            newForms.forEach(form => {
                if (!this.enhancedForms.has(form)) {
                    this.enhanceForm(form);
                }
            });
        });
    }

    onContentChange() {
        setTimeout(() => this.enhanceExistingForms(), 100);
    }

    async runDiagnostics() {
        const allForms = document.querySelectorAll('form');
        const enhancedCount = this.enhancedForms.size;
        const unlabeledInputs = document.querySelectorAll('input:not([aria-label]):not([aria-labelledby])');
        const requiredFields = document.querySelectorAll('input[required], textarea[required], select[required]');
        
        return {
            ...await super.runDiagnostics(),
            totalForms: allForms.length,
            enhancedForms: enhancedCount,
            unlabeledInputs: unlabeledInputs.length,
            requiredFields: requiredFields.length,
            validationMessages: this.validationMessages.size,
            status: enhancedCount === allForms.length && unlabeledInputs.length === 0 ? 'ok' : 'warning'
        };
    }
}

/**
 * Color Contrast Module - Advanced contrast management
 */
class ColorContrastModule extends AccessibilityModule {
    async setup() {
        this.contrastRatios = new Map();
        this.problemElements = new Set();
        
        this.analyzeContrast();
        this.setupContrastMonitoring();
    }

    analyzeContrast() {
        const textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, a, button, span, div');
        let checkedCount = 0;
        
        textElements.forEach(element => {
            if (checkedCount >= 50) return; // Limit for performance
            
            const text = element.textContent.trim();
            if (text.length > 0) {
                const ratio = this.calculateContrastRatio(element);
                this.contrastRatios.set(element, ratio);
                
                if (ratio < 4.5) {
                    this.problemElements.add(element);
                }
                checkedCount++;
            }
        });
    }

    calculateContrastRatio(element) {
        const styles = window.getComputedStyle(element);
        const textColor = this.parseColor(styles.color);
        const bgColor = this.getBackgroundColor(element);
        
        if (!textColor || !bgColor) return 21; // Assume good if can't calculate
        
        return this.getContrastRatio(textColor, bgColor);
    }

    parseColor(colorString) {
        const rgb = colorString.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
        if (rgb) {
            return [parseInt(rgb[1]), parseInt(rgb[2]), parseInt(rgb[3])];
        }
        return null;
    }

    getBackgroundColor(element) {
        let el = element;
        while (el && el !== document.body) {
            const styles = window.getComputedStyle(el);
            const bgColor = styles.backgroundColor;
            
            if (bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent') {
                return this.parseColor(bgColor);
            }
            el = el.parentElement;
        }
        return [255, 255, 255]; // Default to white
    }

    getContrastRatio(color1, color2) {
        const l1 = this.getLuminance(color1);
        const l2 = this.getLuminance(color2);
        const lighter = Math.max(l1, l2);
        const darker = Math.min(l1, l2);
        return (lighter + 0.05) / (darker + 0.05);
    }

    getLuminance([r, g, b]) {
        const [rs, gs, bs] = [r, g, b].map(c => {
            c = c / 255;
            return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    }

    highlightContrastIssues() {
        this.problemElements.forEach(element => {
            element.style.outline = '2px solid #ef4444';
            element.style.outlineOffset = '2px';
            element.title = `Contraste baixo: ${this.contrastRatios.get(element).toFixed(2)}:1`;
        });
        
        this.core.announce(`${this.problemElements.size} elementos com problemas de contraste destacados`);
        
        // Auto-remove highlights after 5 seconds
        setTimeout(() => {
            this.problemElements.forEach(element => {
                element.style.outline = '';
                element.style.outlineOffset = '';
                element.removeAttribute('title');
            });
        }, 5000);
    }

    setupContrastMonitoring() {
        // Re-analyze when contrast settings change
        this.core.on('accessibility:settingChanged', ({ detail: { path } }) => {
            if (path.includes('contrast')) {
                setTimeout(() => this.analyzeContrast(), 100);
            }
        });
    }

    onContentChange() {
        setTimeout(() => this.analyzeContrast(), 200);
    }

    async runDiagnostics() {
        const totalElements = this.contrastRatios.size;
        const problemElements = this.problemElements.size;
        const passRate = totalElements > 0 ? ((totalElements - problemElements) / totalElements) * 100 : 100;
        
        return {
            ...await super.runDiagnostics(),
            elementsAnalyzed: totalElements,
            contrastIssues: problemElements,
            passRate: Math.round(passRate),
            averageRatio: this.getAverageRatio(),
            status: passRate >= 90 ? 'ok' : passRate >= 70 ? 'warning' : 'error'
        };
    }

    getAverageRatio() {
        if (this.contrastRatios.size === 0) return 0;
        const sum = Array.from(this.contrastRatios.values()).reduce((a, b) => a + b, 0);
        return Math.round((sum / this.contrastRatios.size) * 100) / 100;
    }
}

/**
 * Media Accessibility Module - Images, videos, and audio accessibility
 */
class MediaAccessibilityModule extends AccessibilityModule {
    async setup() {
        this.mediaElements = new Map();
        
        this.enhanceImages();
        this.enhanceVideos();
        this.enhanceAudio();
        this.setupMediaMonitoring();
    }

    enhanceImages() {
        const images = document.querySelectorAll('img');
        
        images.forEach(img => {
            if (!img.getAttribute('alt')) {
                const altText = this.generateAltText(img);
                img.setAttribute('alt', altText);
            }
            
            // Add loading states
            this.addImageLoadingStates(img);
            
            this.mediaElements.set(img, { type: 'image', enhanced: true });
        });
    }

    generateAltText(img) {
        const src = img.src || img.getAttribute('data-src') || '';
        const className = img.className || '';
        
        // Decorative images
        if (className.includes('decoration') || className.includes('background')) {
            return '';
        }
        
        // Infer from filename
        const filename = src.split('/').pop().split('.')[0];
        if (filename) {
            if (filename.includes('logo')) return 'Logo';
            if (filename.includes('avatar')) return 'Avatar do usuário';
            if (filename.includes('icon')) return 'Ícone';
            if (filename.includes('banner')) return 'Banner';
            
            // Clean filename
            return filename.replace(/[-_]/g, ' ').replace(/\d+/g, '').trim() || 'Imagem';
        }
        
        return 'Imagem';
    }

    addImageLoadingStates(img) {
        img.addEventListener('load', () => {
            img.setAttribute('aria-label', `${img.alt} (carregada)`);
        });
        
        img.addEventListener('error', () => {
            img.setAttribute('aria-label', `${img.alt} (erro no carregamento)`);
        });
    }

    enhanceVideos() {
        const videos = document.querySelectorAll('video');
        
        videos.forEach(video => {
            if (!video.hasAttribute('controls')) {
                video.setAttribute('controls', '');
            }
            
            if (!video.getAttribute('aria-label')) {
                video.setAttribute('aria-label', 'Vídeo');
            }
            
            this.addVideoAccessibilityFeatures(video);
            this.mediaElements.set(video, { type: 'video', enhanced: true });
        });
    }

    addVideoAccessibilityFeatures(video) {
        // Add keyboard controls
        video.addEventListener('keydown', (e) => {
            switch (e.key) {
                case ' ':
                    e.preventDefault();
                    video.paused ? video.play() : video.pause();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    video.currentTime = Math.max(0, video.currentTime - 10);
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    video.currentTime = Math.min(video.duration, video.currentTime + 10);
                    break;
            }
        });
        
        // Announce state changes
        video.addEventListener('play', () => {
            this.core.announce('Vídeo reproduzindo', 'polite');
        });
        
        video.addEventListener('pause', () => {
            this.core.announce('Vídeo pausado', 'polite');
        });
    }

    enhanceAudio() {
        const audioElements = document.querySelectorAll('audio');
        
        audioElements.forEach(audio => {
            if (!audio.hasAttribute('controls')) {
                audio.setAttribute('controls', '');
            }
            
            if (!audio.getAttribute('aria-label')) {
                audio.setAttribute('aria-label', 'Áudio');
            }
            
            this.mediaElements.set(audio, { type: 'audio', enhanced: true });
        });
    }

    setupMediaMonitoring() {
        this.core.on('accessibility:contentChanged', () => {
            this.enhanceImages();
            this.enhanceVideos();
            this.enhanceAudio();
        });
    }

    onContentChange() {
        setTimeout(() => {
            this.enhanceImages();
            this.enhanceVideos();
            this.enhanceAudio();
        }, 100);
    }

    async runDiagnostics() {
        const images = document.querySelectorAll('img');
        const videos = document.querySelectorAll('video');
        const audioElements = document.querySelectorAll('audio');
        
        const imagesWithAlt = Array.from(images).filter(img => img.getAttribute('alt') !== null);
        const videosWithControls = Array.from(videos).filter(video => video.hasAttribute('controls'));
        const audioWithControls = Array.from(audioElements).filter(audio => audio.hasAttribute('controls'));
        
        return {
            ...await super.runDiagnostics(),
            totalImages: images.length,
            imagesWithAlt: imagesWithAlt.length,
            totalVideos: videos.length,
            videosWithControls: videosWithControls.length,
            totalAudio: audioElements.length,
            audioWithControls: audioWithControls.length,
            enhancedElements: this.mediaElements.size,
            status: imagesWithAlt.length === images.length && 
                   videosWithControls.length === videos.length ? 'ok' : 'warning'
        };
    }
}

// Export modules
window.VisualControlsModule = VisualControlsModule;
window.FormEnhancerModule = FormEnhancerModule;
window.ColorContrastModule = ColorContrastModule;
window.MediaAccessibilityModule = MediaAccessibilityModule;