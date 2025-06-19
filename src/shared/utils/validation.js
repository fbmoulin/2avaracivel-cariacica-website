/**
 * Shared Validation Utilities
 * Common validation functions for frontend and backend
 */

export const ValidationUtils = {
    /**
     * Validate CPF format and checksum
     */
    validateCPF(cpf) {
        if (!cpf) return false;
        
        // Remove non-numeric characters
        cpf = cpf.replace(/[^\d]/g, '');
        
        // Check length and repeated digits
        if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) {
            return false;
        }
        
        // Calculate first check digit
        let sum = 0;
        for (let i = 0; i < 9; i++) {
            sum += parseInt(cpf[i]) * (10 - i);
        }
        let digit1 = (sum * 10) % 11;
        if (digit1 === 10) digit1 = 0;
        
        // Calculate second check digit
        sum = 0;
        for (let i = 0; i < 10; i++) {
            sum += parseInt(cpf[i]) * (11 - i);
        }
        let digit2 = (sum * 10) % 11;
        if (digit2 === 10) digit2 = 0;
        
        return parseInt(cpf[9]) === digit1 && parseInt(cpf[10]) === digit2;
    },

    /**
     * Validate email format
     */
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    /**
     * Validate phone number (Brazilian format)
     */
    validatePhone(phone) {
        if (!phone) return true; // Phone is optional
        const phoneRegex = /^\(?[1-9]{2}\)?\s?[0-9]{4,5}-?[0-9]{4}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
    },

    /**
     * Validate process number format
     */
    validateProcessNumber(processNumber) {
        // Basic format validation for Brazilian process numbers
        const processRegex = /^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$/;
        return processRegex.test(processNumber);
    },

    /**
     * Sanitize HTML input
     */
    sanitizeHtml(input) {
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    },

    /**
     * Validate required fields
     */
    validateRequired(value) {
        return value !== null && value !== undefined && value.toString().trim() !== '';
    },

    /**
     * Validate string length
     */
    validateLength(value, min = 0, max = Infinity) {
        if (!value) return min === 0;
        const length = value.toString().length;
        return length >= min && length <= max;
    }
};