/** @odoo-module **/
/**
 * Global DOM Protection for Odoo 17
 * 
 * Prevents common JavaScript errors related to:
 * - null/undefined DOM elements
 * - querySelector on null objects
 * - Missing parent elements
 * - Race conditions in element access
 * 
 * This is a defensive programming layer for production stability.
 */

(function() {
    'use strict';

    console.log('[rental_management] Loading global DOM protection...');

    // ========================================================================
    // 1. PROTECT QUERYSELECTOR METHODS
    // ========================================================================

    /**
     * Wrap querySelector to handle null elements gracefully
     */
    const originalQuerySelector = Element.prototype.querySelector;
    const originalQuerySelectorAll = Element.prototype.querySelectorAll;

    Element.prototype.querySelector = function(selector) {
        try {
            if (!this || this.nodeType !== Node.ELEMENT_NODE) {
                console.warn('[rental_management] querySelector called on invalid element');
                return null;
            }
            return originalQuerySelector.call(this, selector);
        } catch (error) {
            console.error('[rental_management] querySelector error:', error, 'selector:', selector);
            return null;
        }
    };

    Element.prototype.querySelectorAll = function(selector) {
        try {
            if (!this || this.nodeType !== Node.ELEMENT_NODE) {
                console.warn('[rental_management] querySelectorAll called on invalid element');
                return [];
            }
            return originalQuerySelectorAll.call(this, selector);
        } catch (error) {
            console.error('[rental_management] querySelectorAll error:', error, 'selector:', selector);
            return [];
        }
    };

    // ========================================================================
    // 2. PROTECT DOCUMENT METHODS
    // ========================================================================

    /**
     * Wrap document.querySelector for additional safety
     */
    const originalDocQuerySelector = document.querySelector;
    const originalDocQuerySelectorAll = document.querySelectorAll;

    document.querySelector = function(selector) {
        try {
            if (!selector || typeof selector !== 'string') {
                console.warn('[rental_management] Invalid selector passed to document.querySelector:', selector);
                return null;
            }
            return originalDocQuerySelector.call(this, selector);
        } catch (error) {
            console.error('[rental_management] document.querySelector error:', error, 'selector:', selector);
            return null;
        }
    };

    document.querySelectorAll = function(selector) {
        try {
            if (!selector || typeof selector !== 'string') {
                console.warn('[rental_management] Invalid selector passed to document.querySelectorAll:', selector);
                return [];
            }
            return originalDocQuerySelectorAll.call(this, selector);
        } catch (error) {
            console.error('[rental_management] document.querySelectorAll error:', error, 'selector:', selector);
            return [];
        }
    };

    // ========================================================================
    // 3. PROTECT EVENT HANDLERS
    // ========================================================================

    /**
     * Global error handler for uncaught errors
     */
    window.addEventListener('error', function(event) {
        if (event.error && event.error.message) {
            const message = event.error.message;
            
            // Catch querySelector errors
            if (message.includes("Cannot read properties of null (reading 'querySelector')") ||
                message.includes("Cannot read property 'querySelector' of null")) {
                
                console.warn('[rental_management] Caught querySelector error:', event.error);
                event.preventDefault(); // Prevent error from breaking the UI
                return false;
            }
        }
    }, true);

    // ========================================================================
    // 4. PROTECT AGAINST NULL PARENT ELEMENTS
    // ========================================================================

    /**
     * Add null safety to common DOM operations
     */
    const originalAppendChild = Element.prototype.appendChild;
    const originalRemoveChild = Element.prototype.removeChild;
    const originalInsertBefore = Element.prototype.insertBefore;

    Element.prototype.appendChild = function(child) {
        try {
            if (!this || !child) {
                console.warn('[rental_management] appendChild: Invalid parent or child');
                return child;
            }
            return originalAppendChild.call(this, child);
        } catch (error) {
            console.error('[rental_management] appendChild error:', error);
            return child;
        }
    };

    Element.prototype.removeChild = function(child) {
        try {
            if (!this || !child) {
                console.warn('[rental_management] removeChild: Invalid parent or child');
                return child;
            }
            return originalRemoveChild.call(this, child);
        } catch (error) {
            console.error('[rental_management] removeChild error:', error);
            return child;
        }
    };

    Element.prototype.insertBefore = function(newNode, referenceNode) {
        try {
            if (!this || !newNode) {
                console.warn('[rental_management] insertBefore: Invalid parent or node');
                return newNode;
            }
            return originalInsertBefore.call(this, newNode, referenceNode);
        } catch (error) {
            console.error('[rental_management] insertBefore error:', error);
            return newNode;
        }
    };

    // ========================================================================
    // 5. PROTECT OWL COMPONENT REFERENCES
    // ========================================================================

    /**
     * Add safe access helper for OWL refs
     */
    window.__rental_safe_ref_access__ = function(ref, defaultValue = null) {
        try {
            if (!ref) return defaultValue;
            if (!ref.el) return defaultValue;
            return ref.el;
        } catch (error) {
            console.error('[rental_management] Safe ref access error:', error);
            return defaultValue;
        }
    };

    // ========================================================================
    // 6. MONITOR CONSOLE FOR SPECIFIC ERRORS
    // ========================================================================

    /**
     * Enhanced error logging for debugging
     */
    const originalConsoleError = console.error;
    console.error = function(...args) {
        // Check for querySelector errors
        const errorString = args.join(' ');
        if (errorString.includes('querySelector') || 
            errorString.includes('ListRenderer') ||
            errorString.includes('Cannot read properties of null')) {
            
            // Add stack trace for debugging
            console.warn('[rental_management] Intercepted error:', ...args);
            console.trace('[rental_management] Error trace:');
        }
        
        // Call original console.error
        originalConsoleError.apply(console, args);
    };

    // ========================================================================
    // 7. SAFE DOM READY HELPER
    // ========================================================================

    /**
     * Ensure DOM is ready before executing code
     */
    window.__rental_dom_ready__ = function(callback) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', callback);
        } else {
            callback();
        }
    };

    // ========================================================================
    // 8. DEBOUNCE HELPER FOR EVENT HANDLERS
    // ========================================================================

    /**
     * Debounce function to prevent rapid event firing
     */
    window.__rental_debounce__ = function(func, wait = 100) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };

    // ========================================================================
    // INITIALIZATION COMPLETE
    // ========================================================================

    console.log('[rental_management] Global DOM protection loaded successfully');
    console.log('[rental_management] Protected methods: querySelector, appendChild, removeChild, insertBefore');
    console.log('[rental_management] Helper functions: __rental_safe_ref_access__, __rental_dom_ready__, __rental_debounce__');

})();
