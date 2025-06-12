/**
 * Form Micro-Interactions System for 2ª Vara Cível de Cariacica
 * Real-time validation with smooth animations and user feedback
 */

window.FormMicroInteractions = window.FormMicroInteractions || class FormMicroInteractions {
    constructor() {
        this.forms = new Map();
        this.validationRules = new Map();
        this.currentFocus = null;
        this.debounceTimers = new Map();
        
        // Animation durations
        this.animationSpeed = {
            fast: 150,
            normal: 300,
            slow: 500
        };
        
        // Validation patterns
        this.patterns = {
            email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
            phone: /^(\(?[0-9]{2}\)?[-.\s]?)?[0-9]{4,5}[-.\s]?[0-9]{4}$/,
            cpf: /^[0-9]{3}\.?[0-9]{3}\.?[0-9]{3}-?[0-9]{2}$/,
            cnpj: /^[0-9]{2}\.?[0-9]{3}\.?[0-9]{3}\/?[0-9]{4}-?[0-9]{2}$/,
            cep: /^[0-9]{5}-?[0-9]{3}$/
        };
        
        this.init();
    }
    
    init() {
        this.setupStyles();
        this.initializeForms();
        console.log('Form micro-interactions initialized');
    }
    
    setupStyles() {
        const styles = `
            .form-field {
                position: relative;
                margin-bottom: 1.5rem;
                transition: all 0.3s ease;
            }
            
            .form-field input,
            .form-field textarea,
            .form-field select {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 16px;
                width: 100%;
                background: #fff;
                position: relative;
            }
            
            .form-field input:focus,
            .form-field textarea:focus,
            .form-field select:focus {
                outline: none;
                border-color: #0d6efd;
                box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
                transform: translateY(-2px);
            }
            
            .form-field.valid input,
            .form-field.valid textarea,
            .form-field.valid select {
                border-color: #198754;
                background-color: #f8fff8;
            }
            
            .form-field.invalid input,
            .form-field.invalid textarea,
            .form-field.invalid select {
                border-color: #dc3545;
                background-color: #fff8f8;
                animation: shake 0.5s ease-in-out;
            }
            
            .form-field.loading input,
            .form-field.loading textarea,
            .form-field.loading select {
                border-color: #ffc107;
                background-image: linear-gradient(45deg, transparent 25%, rgba(255, 255, 255, 0.5) 25%, rgba(255, 255, 255, 0.5) 50%, transparent 50%, transparent 75%, rgba(255, 255, 255, 0.5) 75%, rgba(255, 255, 255, 0.5));
                background-size: 20px 20px;
                animation: loading-stripes 1s linear infinite;
            }
            
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-5px); }
                75% { transform: translateX(5px); }
            }
            
            @keyframes loading-stripes {
                0% { background-position: 0 0; }
                100% { background-position: 20px 0; }
            }
            
            @keyframes bounce-in {
                0% { transform: scale(0.3) translateY(-20px); opacity: 0; }
                50% { transform: scale(1.05) translateY(-5px); }
                70% { transform: scale(0.95) translateY(0); }
                100% { transform: scale(1) translateY(0); opacity: 1; }
            }
            
            @keyframes slide-down {
                0% { transform: translateY(-10px); opacity: 0; }
                100% { transform: translateY(0); opacity: 1; }
            }
            
            @keyframes fade-in {
                0% { opacity: 0; }
                100% { opacity: 1; }
            }
            
            .validation-message {
                position: absolute;
                bottom: -25px;
                left: 0;
                right: 0;
                font-size: 0.875rem;
                padding: 4px 8px;
                border-radius: 4px;
                transition: all 0.3s ease;
                animation: slide-down 0.3s ease;
            }
            
            .validation-message.success {
                color: #198754;
                background-color: rgba(25, 135, 84, 0.1);
                border: 1px solid rgba(25, 135, 84, 0.3);
            }
            
            .validation-message.error {
                color: #dc3545;
                background-color: rgba(220, 53, 69, 0.1);
                border: 1px solid rgba(220, 53, 69, 0.3);
            }
            
            .validation-message.warning {
                color: #ffc107;
                background-color: rgba(255, 193, 7, 0.1);
                border: 1px solid rgba(255, 193, 7, 0.3);
            }
            
            .field-icon {
                position: absolute;
                right: 12px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 18px;
                transition: all 0.3s ease;
                pointer-events: none;
            }
            
            .field-icon.valid {
                color: #198754;
                animation: bounce-in 0.5s ease;
            }
            
            .field-icon.invalid {
                color: #dc3545;
                animation: shake 0.5s ease;
            }
            
            .field-icon.loading {
                color: #ffc107;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: translateY(-50%) rotate(0deg); }
                100% { transform: translateY(-50%) rotate(360deg); }
            }
            
            .form-progress {
                height: 4px;
                background: #e1e5e9;
                border-radius: 2px;
                margin-bottom: 20px;
                overflow: hidden;
            }
            
            .form-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #0d6efd, #0dcaf0);
                border-radius: 2px;
                transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
            }
            
            .form-progress-bar::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
                animation: progress-shine 2s infinite;
            }
            
            @keyframes progress-shine {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
            
            .submit-button {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
                min-width: 200px;
                height: 50px;
            }
            
            .submit-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: scale(0.98);
            }
            
            .submit-button:not(:disabled):hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(13, 110, 253, 0.3);
            }
            
            .submit-button:not(:disabled):active {
                transform: translateY(0);
                box-shadow: 0 4px 15px rgba(13, 110, 253, 0.2);
            }
            
            .button-text,
            .button-loading {
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
            }
            
            .button-loading {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
            }
            
            .form-check-enhanced {
                position: relative;
                padding-left: 2rem;
                margin-bottom: 1rem;
            }
            
            .form-check-enhanced .form-check-input {
                position: absolute;
                left: 0;
                top: 0.25rem;
                transform: scale(1.2);
                transition: all 0.3s ease;
            }
            
            .form-check-enhanced .form-check-input:checked {
                background-color: #198754;
                border-color: #198754;
                animation: check-bounce 0.3s ease;
            }
            
            @keyframes check-bounce {
                0% { transform: scale(1.2); }
                50% { transform: scale(1.4); }
                100% { transform: scale(1.2); }
            }
            
            .strength-meter {
                height: 6px;
                background: #e1e5e9;
                border-radius: 3px;
                margin-top: 8px;
                overflow: hidden;
            }
            
            .strength-meter-bar {
                height: 100%;
                border-radius: 3px;
                transition: all 0.3s ease;
            }
            
            .strength-weak { background: #dc3545; width: 25%; }
            .strength-fair { background: #ffc107; width: 50%; }
            .strength-good { background: #fd7e14; width: 75%; }
            .strength-strong { background: #198754; width: 100%; }
            
            .floating-label {
                position: absolute;
                left: 16px;
                top: 50%;
                transform: translateY(-50%);
                background: #fff;
                padding: 0 4px;
                color: #6c757d;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                pointer-events: none;
                font-size: 16px;
            }
            
            .floating-label.active {
                top: 0;
                transform: translateY(-50%);
                font-size: 12px;
                color: #0d6efd;
                font-weight: 500;
            }
            
            .form-field.valid .floating-label.active {
                color: #198754;
            }
            
            .form-field.invalid .floating-label.active {
                color: #dc3545;
            }
            
            @media (prefers-reduced-motion: reduce) {
                * {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    initializeForms() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            const formId = form.id || this.generateId();
            form.id = formId;
            
            this.forms.set(formId, {
                element: form,
                fields: new Map(),
                progress: 0,
                isValid: false
            });
            
            this.setupForm(form);
        });
    }
    
    setupForm(form) {
        // Add progress bar
        this.addProgressBar(form);
        
        // Setup fields
        const fields = form.querySelectorAll('input, textarea, select');
        fields.forEach(field => this.setupField(field, form.id));
        
        // Form submission handling
        form.addEventListener('submit', (e) => this.handleSubmit(e));
    }
    
    setupField(field, formId) {
        const fieldContainer = this.wrapField(field);
        const fieldId = field.id || this.generateId();
        field.id = fieldId;
        
        const formData = this.forms.get(formId);
        formData.fields.set(fieldId, {
            element: field,
            container: fieldContainer,
            isValid: false,
            rules: this.getValidationRules(field)
        });
        
        // Add floating label
        this.addFloatingLabel(field, fieldContainer);
        
        // Add field icon
        this.addFieldIcon(fieldContainer);
        
        // Setup event listeners
        this.setupFieldListeners(field, formId);
    }
    
    wrapField(field) {
        if (field.closest('.form-field')) {
            return field.closest('.form-field');
        }
        
        const wrapper = document.createElement('div');
        wrapper.className = 'form-field';
        
        field.parentNode.insertBefore(wrapper, field);
        wrapper.appendChild(field);
        
        return wrapper;
    }
    
    addFloatingLabel(field, container) {
        const existingLabel = container.querySelector('label');
        if (existingLabel && !existingLabel.classList.contains('floating-label')) {
            existingLabel.classList.add('floating-label');
            
            // Check if field has value or is focused
            const updateLabel = () => {
                if (field.value || field === document.activeElement) {
                    existingLabel.classList.add('active');
                } else {
                    existingLabel.classList.remove('active');
                }
            };
            
            updateLabel();
            field.addEventListener('focus', updateLabel);
            field.addEventListener('blur', updateLabel);
            field.addEventListener('input', updateLabel);
        }
    }
    
    addFieldIcon(container) {
        const icon = document.createElement('span');
        icon.className = 'field-icon';
        container.appendChild(icon);
    }
    
    addProgressBar(form) {
        const existingProgress = form.querySelector('.form-progress');
        if (existingProgress) return;
        
        const progressContainer = document.createElement('div');
        progressContainer.className = 'form-progress';
        
        const progressBar = document.createElement('div');
        progressBar.className = 'form-progress-bar';
        progressBar.style.width = '0%';
        
        progressContainer.appendChild(progressBar);
        form.insertBefore(progressContainer, form.firstChild);
    }
    
    setupFieldListeners(field, formId) {
        // Real-time validation on input
        field.addEventListener('input', (e) => {
            this.debounce(field.id, () => {
                this.validateField(field, formId);
                this.updateFormProgress(formId);
            }, 300);
        });
        
        // Immediate validation on blur
        field.addEventListener('blur', () => {
            this.validateField(field, formId);
            this.updateFormProgress(formId);
        });
        
        // Focus effects
        field.addEventListener('focus', () => {
            this.currentFocus = field;
            this.clearFieldState(field);
        });
        
        // Special handling for password fields
        if (field.type === 'password') {
            this.setupPasswordStrength(field);
        }
        
        // Special handling for file inputs
        if (field.type === 'file') {
            this.setupFileValidation(field);
        }
    }
    
    getValidationRules(field) {
        const rules = [];
        
        // Required validation
        if (field.required) {
            rules.push({
                type: 'required',
                message: 'Este campo é obrigatório'
            });
        }
        
        // Type-based validation
        if (field.type === 'email') {
            rules.push({
                type: 'email',
                pattern: this.patterns.email,
                message: 'Digite um email válido'
            });
        }
        
        // Custom validations based on field attributes
        if (field.dataset.validation) {
            const customRules = JSON.parse(field.dataset.validation);
            rules.push(...customRules);
        }
        
        // Pattern validation
        if (field.pattern) {
            rules.push({
                type: 'pattern',
                pattern: new RegExp(field.pattern),
                message: field.title || 'Formato inválido'
            });
        }
        
        // Length validation
        if (field.minLength) {
            rules.push({
                type: 'minLength',
                value: field.minLength,
                message: `Mínimo de ${field.minLength} caracteres`
            });
        }
        
        if (field.maxLength) {
            rules.push({
                type: 'maxLength',
                value: field.maxLength,
                message: `Máximo de ${field.maxLength} caracteres`
            });
        }
        
        return rules;
    }
    
    async validateField(field, formId) {
        const formData = this.forms.get(formId);
        const fieldData = formData.fields.get(field.id);
        const container = fieldData.container;
        
        // Clear previous state
        this.clearFieldState(field);
        
        // Show loading state
        this.setFieldState(field, 'loading');
        
        // Simulate async validation delay for better UX
        await this.delay(150);
        
        const value = field.value.trim();
        const rules = fieldData.rules;
        
        let isValid = true;
        let message = '';
        
        // Run validation rules
        for (const rule of rules) {
            const result = this.runValidationRule(value, rule, field);
            if (!result.valid) {
                isValid = false;
                message = result.message;
                break;
            }
        }
        
        // Custom validation for specific field types
        if (isValid && value) {
            const customResult = await this.runCustomValidation(field, value);
            if (!customResult.valid) {
                isValid = false;
                message = customResult.message;
            }
        }
        
        // Update field state
        fieldData.isValid = isValid;
        this.setFieldState(field, isValid ? 'valid' : 'invalid', message);
        
        return isValid;
    }
    
    runValidationRule(value, rule, field) {
        switch (rule.type) {
            case 'required':
                return {
                    valid: value.length > 0,
                    message: rule.message
                };
                
            case 'email':
                return {
                    valid: !value || rule.pattern.test(value),
                    message: rule.message
                };
                
            case 'pattern':
                return {
                    valid: !value || rule.pattern.test(value),
                    message: rule.message
                };
                
            case 'minLength':
                return {
                    valid: value.length >= rule.value,
                    message: rule.message
                };
                
            case 'maxLength':
                return {
                    valid: value.length <= rule.value,
                    message: rule.message
                };
                
            case 'cpf':
                return {
                    valid: !value || this.validateCPF(value),
                    message: rule.message || 'CPF inválido'
                };
                
            case 'cnpj':
                return {
                    valid: !value || this.validateCNPJ(value),
                    message: rule.message || 'CNPJ inválido'
                };
                
            default:
                return { valid: true, message: '' };
        }
    }
    
    async runCustomValidation(field, value) {
        // Email domain validation
        if (field.type === 'email' && value) {
            const domain = value.split('@')[1];
            if (domain) {
                // You could add domain validation here
                return { valid: true, message: '' };
            }
        }
        
        // Phone number formatting and validation
        if (field.type === 'tel' && value) {
            const cleanPhone = value.replace(/\D/g, '');
            if (cleanPhone.length === 10 || cleanPhone.length === 11) {
                // Format phone number
                field.value = this.formatPhone(cleanPhone);
                return { valid: true, message: '' };
            }
            return { valid: false, message: 'Número de telefone inválido' };
        }
        
        return { valid: true, message: '' };
    }
    
    setFieldState(field, state, message = '') {
        const container = field.closest('.form-field');
        const icon = container.querySelector('.field-icon');
        
        // Clear previous states
        container.classList.remove('valid', 'invalid', 'loading');
        
        // Set new state
        container.classList.add(state);
        
        // Update icon
        if (icon) {
            icon.innerHTML = '';
            switch (state) {
                case 'valid':
                    icon.innerHTML = '✓';
                    break;
                case 'invalid':
                    icon.innerHTML = '✗';
                    break;
                case 'loading':
                    icon.innerHTML = '⟳';
                    break;
            }
        }
        
        // Show/update message
        this.showValidationMessage(container, message, state);
    }
    
    clearFieldState(field) {
        const container = field.closest('.form-field');
        container.classList.remove('valid', 'invalid', 'loading');
        
        const icon = container.querySelector('.field-icon');
        if (icon) icon.innerHTML = '';
        
        this.hideValidationMessage(container);
    }
    
    showValidationMessage(container, message, type) {
        this.hideValidationMessage(container);
        
        if (!message) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = `validation-message ${type}`;
        messageElement.textContent = message;
        
        container.appendChild(messageElement);
    }
    
    hideValidationMessage(container) {
        const existingMessage = container.querySelector('.validation-message');
        if (existingMessage) {
            existingMessage.remove();
        }
    }
    
    updateFormProgress(formId) {
        const formData = this.forms.get(formId);
        const fields = Array.from(formData.fields.values());
        const validFields = fields.filter(field => field.isValid);
        
        const progress = fields.length > 0 ? (validFields.length / fields.length) * 100 : 0;
        formData.progress = progress;
        
        const progressBar = formData.element.querySelector('.form-progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        // Update form validity
        formData.isValid = progress === 100;
        
        // Update submit button state
        this.updateSubmitButton(formData.element, formData.isValid);
    }
    
    updateSubmitButton(form, isValid) {
        const submitButton = form.querySelector('button[type="submit"], .submit-button');
        if (submitButton) {
            submitButton.disabled = !isValid;
            
            if (isValid) {
                submitButton.classList.add('btn-success');
                submitButton.classList.remove('btn-primary');
                const buttonText = submitButton.querySelector('.button-text');
                if (buttonText) {
                    buttonText.innerHTML = '<i class="fas fa-check me-2"></i>Pronto para Enviar';
                }
            } else {
                submitButton.classList.add('btn-primary');
                submitButton.classList.remove('btn-success');
                const buttonText = submitButton.querySelector('.button-text');
                if (buttonText) {
                    buttonText.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar Mensagem';
                }
            }
        }
    }
    
    setupPasswordStrength(passwordField) {
        const container = passwordField.closest('.form-field');
        
        // Add strength meter
        const strengthMeter = document.createElement('div');
        strengthMeter.className = 'strength-meter';
        
        const strengthBar = document.createElement('div');
        strengthBar.className = 'strength-meter-bar';
        
        strengthMeter.appendChild(strengthBar);
        container.appendChild(strengthMeter);
        
        passwordField.addEventListener('input', () => {
            const strength = this.calculatePasswordStrength(passwordField.value);
            strengthBar.className = `strength-meter-bar strength-${strength.level}`;
        });
    }
    
    calculatePasswordStrength(password) {
        let score = 0;
        
        if (password.length >= 8) score++;
        if (/[a-z]/.test(password)) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;
        
        const levels = ['weak', 'weak', 'fair', 'good', 'strong'];
        return {
            score,
            level: levels[score] || 'weak'
        };
    }
    
    setupFileValidation(fileField) {
        fileField.addEventListener('change', () => {
            const files = Array.from(fileField.files);
            const maxSize = parseInt(fileField.dataset.maxSize) || 5 * 1024 * 1024; // 5MB default
            const allowedTypes = fileField.dataset.allowedTypes?.split(',') || [];
            
            let isValid = true;
            let message = '';
            
            for (const file of files) {
                if (file.size > maxSize) {
                    isValid = false;
                    message = 'Arquivo muito grande';
                    break;
                }
                
                if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
                    isValid = false;
                    message = 'Tipo de arquivo não permitido';
                    break;
                }
            }
            
            this.setFieldState(fileField, isValid ? 'valid' : 'invalid', message);
        });
    }
    
    handleSubmit(e) {
        const form = e.target;
        const formData = this.forms.get(form.id);
        
        if (!formData.isValid) {
            e.preventDefault();
            
            // Find first invalid field and focus it
            const firstInvalidField = Array.from(formData.fields.values())
                .find(field => !field.isValid);
            
            if (firstInvalidField) {
                firstInvalidField.element.focus();
                firstInvalidField.element.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
            }
            
            // Shake the submit button
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.style.animation = 'shake 0.5s ease-in-out';
                setTimeout(() => {
                    submitButton.style.animation = '';
                }, 500);
            }
        } else {
            // Show loading state
            this.showSubmitLoading(form);
        }
    }
    
    showSubmitLoading(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            const buttonText = submitButton.querySelector('.button-text');
            const buttonLoading = submitButton.querySelector('.button-loading');
            
            if (buttonText && buttonLoading) {
                buttonText.style.display = 'none';
                buttonLoading.style.display = 'flex';
                submitButton.disabled = true;
            }
        }
    }
    
    // Utility methods
    validateCPF(cpf) {
        cpf = cpf.replace(/\D/g, '');
        if (cpf.length !== 11 || /^(.)\1*$/.test(cpf)) return false;
        
        let sum = 0;
        for (let i = 0; i < 9; i++) {
            sum += parseInt(cpf.charAt(i)) * (10 - i);
        }
        let remainder = (sum * 10) % 11;
        if (remainder === 10 || remainder === 11) remainder = 0;
        if (remainder !== parseInt(cpf.charAt(9))) return false;
        
        sum = 0;
        for (let i = 0; i < 10; i++) {
            sum += parseInt(cpf.charAt(i)) * (11 - i);
        }
        remainder = (sum * 10) % 11;
        if (remainder === 10 || remainder === 11) remainder = 0;
        return remainder === parseInt(cpf.charAt(10));
    }
    
    validateCNPJ(cnpj) {
        cnpj = cnpj.replace(/\D/g, '');
        if (cnpj.length !== 14 || /^(.)\1*$/.test(cnpj)) return false;
        
        const weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
        const weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
        
        let sum = 0;
        for (let i = 0; i < 12; i++) {
            sum += parseInt(cnpj.charAt(i)) * weights1[i];
        }
        let remainder = sum % 11;
        const digit1 = remainder < 2 ? 0 : 11 - remainder;
        
        if (digit1 !== parseInt(cnpj.charAt(12))) return false;
        
        sum = 0;
        for (let i = 0; i < 13; i++) {
            sum += parseInt(cnpj.charAt(i)) * weights2[i];
        }
        remainder = sum % 11;
        const digit2 = remainder < 2 ? 0 : 11 - remainder;
        
        return digit2 === parseInt(cnpj.charAt(13));
    }
    
    formatPhone(phone) {
        if (phone.length === 10) {
            return phone.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
        } else if (phone.length === 11) {
            return phone.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        }
        return phone;
    }
    
    debounce(key, func, delay) {
        if (this.debounceTimers.has(key)) {
            clearTimeout(this.debounceTimers.get(key));
        }
        
        const timer = setTimeout(func, delay);
        this.debounceTimers.set(key, timer);
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    generateId() {
        return 'field_' + Math.random().toString(36).substr(2, 9);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (!window.formMicroInteractions) {
        window.formMicroInteractions = new FormMicroInteractions();
    }
});

// Voice accessibility integration
if (window.voiceAccessibilityManager) {
    window.voiceAccessibilityManager.registerComponent('formValidation', {
        describe: () => 'Sistema de validação de formulário com feedback em tempo real',
        getStatus: () => {
            const forms = document.querySelectorAll('form');
            const validForms = Array.from(forms).filter(form => {
                const instance = window.formMicroInteractions;
                const formData = instance?.forms.get(form.id);
                return formData?.isValid;
            });
            
            return `${validForms.length} de ${forms.length} formulários válidos`;
        }
    });
}