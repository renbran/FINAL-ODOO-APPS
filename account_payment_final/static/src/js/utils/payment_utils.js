/** @odoo-module **/

/**
 * Payment Utility Functions
 * 
 * Collection of utility functions for payment-related operations
 * Modern ES6 module with performance optimizations
 */

/**
 * Format currency amount with proper locale support
 */
export function formatCurrency(amount, currency = null, locale = null) {
    if (amount === null || amount === undefined) return '';
    
    const options = {
        style: 'currency',
        currency: currency || 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    };
    
    try {
        return new Intl.NumberFormat(locale || 'en-US', options).format(amount);
    } catch (error) {
        console.warn('Currency formatting failed:', error);
        return `${currency || '$'} ${parseFloat(amount).toFixed(2)}`;
    }
}

/**
 * Format date with relative time support
 */
export function formatDate(date, options = {}) {
    if (!date) return '';
    
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    if (isNaN(dateObj.getTime())) return '';
    
    const defaults = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        ...options
    };
    
    try {
        if (options.relative) {
            const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
            const diffTime = dateObj.getTime() - Date.now();
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (Math.abs(diffDays) <= 7) {
                return rtf.format(diffDays, 'day');
            }
        }
        
        return dateObj.toLocaleDateString('en-US', defaults);
    } catch (error) {
        console.warn('Date formatting failed:', error);
        return dateObj.toLocaleDateString();
    }
}

/**
 * Debounce function for performance optimization
 */
export function debounce(func, wait, immediate = false) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(this, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(this, args);
    };
}

/**
 * Throttle function for performance optimization
 */
export function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Validate payment data
 */
export function validatePaymentData(paymentData) {
    const errors = [];
    
    if (!paymentData.partner_id) {
        errors.push('Partner is required');
        return { isValid: errors.length === 0, errors };
}
    
    if (!paymentData.amount || paymentData.amount <= 0) {
        errors.push('Amount must be greater than zero');
    }
    
    if (!paymentData.payment_method_id) {
        errors.push('Payment method is required');
    }
    
    if (!paymentData.journal_id) {
        errors.push('Journal is required');
    }
    
    return {
        isValid: errors.length === 0,
        errors
    };
}

/**
 * Generate QR code data string
 */
export function generateQRData(payment) {
    const data = {
        id: payment.id,
        name: payment.name,
        amount: payment.amount,
        partner: payment.partner_id?.[1],
        date: payment.date,
        verification_code: payment.verification_code
    };
    
    return btoa(JSON.stringify(data));
}

/**
 * Parse QR code data
 */
export function parseQRData(qrString) {
    try {
        const decoded = atob(qrString);
        return JSON.parse(decoded);
    } catch (error) {
        console.error('Failed to parse QR data:', error);
        return null;
    }
}

/**
 * Get payment status configuration
 */
export function getPaymentStatusConfig() {
    return {
        draft: {
            label: 'Draft',
            color: 'secondary',
            icon: 'fa-edit',
            description: 'Payment is being prepared'
        },
        under_review: {
            label: 'Under Review',
            color: 'info',
            icon: 'fa-search',
            description: 'Payment is under review'
        },
        for_approval: {
            label: 'For Approval',
            color: 'warning',
            icon: 'fa-clock',
            description: 'Waiting for approval'
        },
        for_authorization: {
            label: 'For Authorization',
            color: 'warning',
            icon: 'fa-key',
            description: 'Waiting for authorization'
        },
        approved: {
            label: 'Approved',
            color: 'success',
            icon: 'fa-check-circle',
            description: 'Payment approved'
        },
        posted: {
            label: 'Posted',
            color: 'success',
            icon: 'fa-check-double',
            description: 'Payment posted'
        },
        cancelled: {
            label: 'Cancelled',
            color: 'danger',
            icon: 'fa-times-circle',
            description: 'Payment cancelled'
        },
        rejected: {
            label: 'Rejected',
            color: 'danger',
            icon: 'fa-ban',
            description: 'Payment rejected'
        }
    };
}

/**
 * Get status configuration for a specific status
 */
export function getStatusConfig(status) {
    const configs = getPaymentStatusConfig();
    return configs[status] || configs.draft;
}

/**
 * Check if status allows editing
 */
export function isStatusEditable(status) {
    return ['draft', 'rejected'].includes(status);
}

/**
 * Check if status is final
 */
export function isStatusFinal(status) {
    return ['posted', 'cancelled'].includes(status);
}

/**
 * Generate unique ID for components
 */
export function generateUniqueId(prefix = 'component') {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Download file helper
 */
export function downloadFile(data, filename, type = 'application/octet-stream') {
    const blob = new Blob([data], { type });
    const url = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.URL.revokeObjectURL(url);
}

/**
 * Copy text to clipboard
 */
export async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            const result = document.execCommand('copy');
            document.body.removeChild(textArea);
            return result;
        } catch (fallbackError) {
            document.body.removeChild(textArea);
            console.error('Copy to clipboard failed:', fallbackError);
            return false;
        }
    }
}

/**
 * Format file size
 */
export function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Escape HTML to prevent XSS
 */
export function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Safe JSON parse with error handling
 */
export function safeJsonParse(jsonString, defaultValue = null) {
    try {
        return JSON.parse(jsonString);
    } catch (error) {
        console.warn('JSON parse failed:', error);
        return defaultValue;
    }
}
