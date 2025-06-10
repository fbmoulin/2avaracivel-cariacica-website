/**
 * Form handling and validation for 2ª Vara Cível de Cariacica
 * Enhanced form functionality with better UX and accessibility
 */

class FormHandler {
    constructor() {
        this.init();
    }

    init() {
        this.setupFormValidation();
        this.setupInputFormatting();
        this.setupDynamicFields();
        this.setupFileUploads();
        this.setupFormSubmission();
        this.setupAutoSave();
    }

    setupFormValidation() {
        // Enhanced validation for all forms
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            // Add custom validation rules
            this.addCustomValidationRules(form);
            
            // Real-time validation
            this.addRealTimeValidation(form);
            
            // Accessibility improvements
            this.improveFormAccessibility(form);
        });
    }

    addCustomValidationRules(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // CPF validation
            if (input.name === 'cpf' || input.id === 'cpf') {
                input.addEventListener('blur', () => {
                    if (input.value && !this.validateCPF(input.value)) {
                        this.setCustomValidity(input, 'CPF inválido');
                    } else {
                        this.setCustomValidity(input, '');
                    }
                });
            }

            // Email validation enhancement
            if (input.type === 'email') {
                input.addEventListener('blur', () => {
                    if (input.value && !this.validateEmail(input.value)) {
                        this.setCustomValidity(input, 'Email inválido');
                    } else {
                        this.setCustomValidity(input, '');
                    }
                });
            }

            // Phone validation
            if (input.type === 'tel' || input.name.includes('telefone') || input.name.includes('phone')) {
                input.addEventListener('blur', () => {
                    if (input.value && !this.validatePhone(input.value)) {
                        this.setCustomValidity(input, 'Telefone inválido');
                    } else {
                        this.setCustomValidity(input, '');
                    }
                });
            }

            // Process number validation
            if (input.name.includes('process') || input.name.includes('processo')) {
                input.addEventListener('blur', () => {
                    if (input.value && !this.validateProcessNumber(input.value)) {
                        this.setCustomValidity(input, 'Número do processo inválido (deve ter 20 dígitos)');
                    } else {
                        this.setCustomValidity(input, '');
                    }
                });
            }
        });
    }

    addRealTimeValidation(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // Show validation feedback as user types
            input.addEventListener('input', () => {
                if (input.validity.valid) {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                    this.hideFieldError(input);
                } else if (input.value.length > 0) {
                    input.classList.remove('is-valid');
                    input.classList.add('is-invalid');
                    this.showFieldError(input, input.validationMessage);
                }
            });

            // Validate on blur for better UX
            input.addEventListener('blur', () => {
                if (input.value.length > 0) {
                    if (input.validity.valid) {
                        input.classList.remove('is-invalid');
                        input.classList.add('is-valid');
                        this.hideFieldError(input);
                    } else {
                        input.classList.remove('is-valid');
                        input.classList.add('is-invalid');
                        this.showFieldError(input, input.validationMessage);
                    }
                }
            });
        });
    }

    improveFormAccessibility(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            const label = form.querySelector(`label[for="${input.id}"]`);
            
            // Ensure proper label association
            if (!label && input.id) {
                const parentLabel = input.closest('label');
                if (parentLabel) {
                    parentLabel.setAttribute('for', input.id);
                }
            }

            // Add required indicator to labels
            if (input.required && label) {
                if (!label.querySelector('.required-indicator')) {
                    const requiredSpan = document.createElement('span');
                    requiredSpan.className = 'required-indicator text-danger';
                    requiredSpan.innerHTML = ' *';
                    requiredSpan.setAttribute('aria-label', 'campo obrigatório');
                    label.appendChild(requiredSpan);
                }
            }

            // Add ARIA attributes
            if (input.required) {
                input.setAttribute('aria-required', 'true');
            }

            // Associate help text with input
            const helpText = input.parentNode.querySelector('.form-text');
            if (helpText) {
                const helpId = `${input.id}-help`;
                helpText.id = helpId;
                input.setAttribute('aria-describedby', helpId);
            }
        });
    }

    setupInputFormatting() {
        // CPF formatting
        this.setupCPFFormatting();
        
        // Phone formatting
        this.setupPhoneFormatting();
        
        // Process number formatting
        this.setupProcessNumberFormatting();
        
        // Currency formatting
        this.setupCurrencyFormatting();
        
        // Date formatting
        this.setupDateFormatting();
    }

    setupCPFFormatting() {
        const cpfInputs = document.querySelectorAll('input[name="cpf"], input[id="cpf"]');
        
        cpfInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length <= 11) {
                    value = value.replace(/(\d{3})(\d)/, '$1.$2');
                    value = value.replace(/(\d{3})(\d)/, '$1.$2');
                    value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
                }
                
                e.target.value = value;
            });

            input.addEventListener('keydown', (e) => {
                // Allow only numbers and control keys
                if (!/[\d\b]/.test(e.key) && !['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                    e.preventDefault();
                }
            });
        });
    }

    setupPhoneFormatting() {
        const phoneInputs = document.querySelectorAll('input[type="tel"], input[name*="telefone"], input[name*="phone"]');
        
        phoneInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length <= 11) {
                    if (value.length >= 11) {
                        value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
                    } else if (value.length >= 10) {
                        value = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
                    } else if (value.length >= 6) {
                        value = value.replace(/(\d{2})(\d{4})(\d)/, '($1) $2-$3');
                    } else if (value.length >= 2) {
                        value = value.replace(/(\d{2})(\d)/, '($1) $2');
                    }
                }
                
                e.target.value = value;
            });
        });
    }

    setupProcessNumberFormatting() {
        const processInputs = document.querySelectorAll('input[name*="process"], input[name*="processo"]');
        
        processInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                
                if (value.length <= 20) {
                    if (value.length >= 7) {
                        value = value.replace(/(\d{7})(\d)/, '$1-$2');
                    }
                    if (value.length >= 10) {
                        value = value.replace(/(\d{7}-\d{2})(\d)/, '$1.$2');
                    }
                    if (value.length >= 15) {
                        value = value.replace(/(\d{7}-\d{2}\.\d{4})(\d)/, '$1.$2');
                    }
                    if (value.length >= 17) {
                        value = value.replace(/(\d{7}-\d{2}\.\d{4}\.\d{1})(\d)/, '$1.$2');
                    }
                    if (value.length >= 20) {
                        value = value.replace(/(\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2})(\d)/, '$1.$2');
                    }
                }
                
                e.target.value = value;
            });
        });
    }

    setupCurrencyFormatting() {
        const currencyInputs = document.querySelectorAll('input[name*="valor"], input[name*="price"], input[data-type="currency"]');
        
        currencyInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                let value = e.target.value.replace(/\D/g, '');
                value = (parseInt(value) / 100).toLocaleString('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                });
                e.target.value = value;
            });
        });
    }

    setupDateFormatting() {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        
        dateInputs.forEach(input => {
            // Add date validation
            input.addEventListener('blur', () => {
                if (input.value) {
                    const selectedDate = new Date(input.value);
                    const today = new Date();
                    
                    // Validate future dates for appointments
                    if (input.name.includes('agendamento') || input.name.includes('data_preferencia')) {
                        if (selectedDate <= today) {
                            this.setCustomValidity(input, 'Data deve ser futura');
                        } else {
                            this.setCustomValidity(input, '');
                        }
                    }
                }
            });
        });
    }

    setupDynamicFields() {
        // Show/hide fields based on selections
        const conditionalSelects = document.querySelectorAll('select[data-conditional]');
        
        conditionalSelects.forEach(select => {
            select.addEventListener('change', () => {
                this.handleConditionalFields(select);
            });
            
            // Initialize on page load
            this.handleConditionalFields(select);
        });

        // Handle dynamic field additions
        this.setupDynamicFieldAddition();
    }

    handleConditionalFields(select) {
        const targetField = select.dataset.conditional;
        const targetElement = document.getElementById(targetField);
        
        if (!targetElement) return;

        const showValues = select.dataset.showWhen ? select.dataset.showWhen.split(',') : [];
        
        if (showValues.includes(select.value)) {
            targetElement.style.display = 'block';
            const inputs = targetElement.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.required = input.dataset.required === 'true';
            });
        } else {
            targetElement.style.display = 'none';
            const inputs = targetElement.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.required = false;
                input.value = '';
            });
        }
    }

    setupDynamicFieldAddition() {
        const addButtons = document.querySelectorAll('[data-add-field]');
        
        addButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.addDynamicField(button);
            });
        });
    }

    addDynamicField(button) {
        const templateId = button.dataset.addField;
        const template = document.getElementById(templateId);
        const container = button.dataset.container ? 
            document.getElementById(button.dataset.container) : 
            button.parentNode;
        
        if (template && container) {
            const clone = template.content.cloneNode(true);
            const fieldCount = container.querySelectorAll('.dynamic-field').length;
            
            // Update field names and IDs
            clone.querySelectorAll('input, select, textarea').forEach(input => {
                if (input.name) {
                    input.name = input.name.replace(/\[\d+\]/, `[${fieldCount}]`);
                }
                if (input.id) {
                    input.id = input.id.replace(/\d+/, fieldCount);
                }
            });
            
            container.appendChild(clone);
        }
    }

    setupFileUploads() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        
        fileInputs.forEach(input => {
            // Add drag and drop functionality
            this.addDragAndDrop(input);
            
            // Add file validation
            input.addEventListener('change', () => {
                this.validateFile(input);
            });
            
            // Show file preview
            input.addEventListener('change', () => {
                this.showFilePreview(input);
            });
        });
    }

    addDragAndDrop(input) {
        const wrapper = input.parentNode;
        
        wrapper.addEventListener('dragover', (e) => {
            e.preventDefault();
            wrapper.classList.add('drag-over');
        });
        
        wrapper.addEventListener('dragleave', () => {
            wrapper.classList.remove('drag-over');
        });
        
        wrapper.addEventListener('drop', (e) => {
            e.preventDefault();
            wrapper.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                this.validateFile(input);
                this.showFilePreview(input);
            }
        });
    }

    validateFile(input) {
        const file = input.files[0];
        if (!file) return;

        const maxSize = input.dataset.maxSize ? parseInt(input.dataset.maxSize) : 5 * 1024 * 1024; // 5MB default
        const allowedTypes = input.dataset.allowedTypes ? input.dataset.allowedTypes.split(',') : [];

        if (file.size > maxSize) {
            this.setCustomValidity(input, `Arquivo muito grande. Tamanho máximo: ${this.formatFileSize(maxSize)}`);
            return false;
        }

        if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
            this.setCustomValidity(input, `Tipo de arquivo não permitido. Tipos aceitos: ${allowedTypes.join(', ')}`);
            return false;
        }

        this.setCustomValidity(input, '');
        return true;
    }

    showFilePreview(input) {
        const file = input.files[0];
        if (!file) return;

        const previewContainer = document.getElementById(`${input.id}-preview`);
        if (!previewContainer) return;

        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => {
                previewContainer.innerHTML = `
                    <img src="${e.target.result}" alt="Preview" style="max-width: 200px; max-height: 200px;">
                    <p>${file.name} (${this.formatFileSize(file.size)})</p>
                `;
            };
            reader.readAsDataURL(file);
        } else {
            previewContainer.innerHTML = `
                <i class="fas fa-file fa-3x"></i>
                <p>${file.name} (${this.formatFileSize(file.size)})</p>
            `;
        }
    }

    setupFormSubmission() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmission(e, form);
            });
        });
    }

    handleFormSubmission(event, form) {
        // Prevent double submission
        const submitButton = form.querySelector('[type="submit"]');
        if (submitButton && submitButton.disabled) {
            event.preventDefault();
            return;
        }

        // Show loading state
        if (submitButton) {
            submitButton.disabled = true;
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
            
            // Reset button after timeout
            setTimeout(() => {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }, 30000); // 30 seconds timeout
        }

        // Clear auto-saved data on successful submission
        if (!event.defaultPrevented) {
            this.clearAutoSavedData(form);
        }
    }

    setupAutoSave() {
        const forms = document.querySelectorAll('form[data-autosave]');
        
        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {
                input.addEventListener('input', window.Court.debounce(() => {
                    this.autoSaveForm(form);
                }, 1000));
            });
            
            // Load auto-saved data on page load
            this.loadAutoSavedData(form);
        });
    }

    autoSaveForm(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        const formId = form.id || form.action || 'default';
        localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
    }

    loadAutoSavedData(form) {
        const formId = form.id || form.action || 'default';
        const savedData = localStorage.getItem(`autosave_${formId}`);
        
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                
                Object.keys(data).forEach(key => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input && !input.value) {
                        input.value = data[key];
                    }
                });
                
                // Show notification about auto-saved data
                this.showAutoSaveNotification(form);
            } catch (error) {
                console.warn('Could not load auto-saved data:', error);
            }
        }
    }

    clearAutoSavedData(form) {
        const formId = form.id || form.action || 'default';
        localStorage.removeItem(`autosave_${formId}`);
    }

    showAutoSaveNotification(form) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show';
        notification.innerHTML = `
            <i class="fas fa-info-circle me-2"></i>
            Dados salvos automaticamente foram restaurados.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        form.insertBefore(notification, form.firstChild);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    // Validation helper methods
    validateCPF(cpf) {
        cpf = cpf.replace(/\D/g, '');
        
        if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) {
            return false;
        }
        
        let sum = 0;
        for (let i = 0; i < 9; i++) {
            sum += parseInt(cpf.charAt(i)) * (10 - i);
        }
        
        let remainder = 11 - (sum % 11);
        if (remainder === 10 || remainder === 11) remainder = 0;
        if (remainder !== parseInt(cpf.charAt(9))) return false;
        
        sum = 0;
        for (let i = 0; i < 10; i++) {
            sum += parseInt(cpf.charAt(i)) * (11 - i);
        }
        
        remainder = 11 - (sum % 11);
        if (remainder === 10 || remainder === 11) remainder = 0;
        
        return remainder === parseInt(cpf.charAt(10));
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    validatePhone(phone) {
        const phoneRegex = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
        return phoneRegex.test(phone);
    }

    validateProcessNumber(processNumber) {
        const cleanNumber = processNumber.replace(/\D/g, '');
        return cleanNumber.length === 20;
    }

    // Helper methods
    setCustomValidity(input, message) {
        input.setCustomValidity(message);
        
        if (message) {
            this.showFieldError(input, message);
        } else {
            this.hideFieldError(input);
        }
    }

    showFieldError(input, message) {
        let errorElement = input.parentNode.querySelector('.field-error');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'field-error invalid-feedback';
            input.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }

    hideFieldError(input) {
        const errorElement = input.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize form handler when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.formHandler = new FormHandler();
});

// Export for global access
window.FormHandler = FormHandler;
