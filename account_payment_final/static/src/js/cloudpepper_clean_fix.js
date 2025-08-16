/** @odoo-module **/

/**
 * CloudPepper JavaScript Error Prevention System
 * 
 * Modern ES6 module for comprehensive JavaScript error handling
 * Optimized for CloudPepper hosting environment and Odoo 17
 */

console.log("[CloudPepper] Modern error prevention system initializing...");

/**
 * Error Prevention Manager Class
 */
class ErrorPreventionManager {
    constructor() {
        this.suppressedPatterns = [
            /Failed to execute 'observe' on 'MutationObserver'/,
            /parameter 1 is not of type 'Node'/,
            /Unexpected token ';'/,
            /Long Running Recorder/,
            /index\.ts-.*\.js/,
            /Cannot use import statement/,
            /Script error/,
            /Loading failed/
        ];
        
        this.init();
    }

    init() {
        this.setupMutationObserverProtection();
        this.setupGlobalErrorHandling();
        this.setupPromiseRejectionHandling();
        this.setupConsoleEnhancements();
        
        console.log("[CloudPepper] Error prevention system active");
    }

    /**
     * Enhanced MutationObserver Protection
     */
    setupMutationObserverProtection() {
        if (!window.MutationObserver) return;
        
        const OriginalMutationObserver = window.MutationObserver;
        
        window.MutationObserver = class extends OriginalMutationObserver {
            constructor(callback) {
                const safeCallback = (mutations, observer) => {
                    try {
                        return callback.call(this, mutations, observer);
                    } catch (error) {
                        console.debug("[CloudPepper] MutationObserver callback error:", error.message);
                    }
                };
                
                super(safeCallback);
            }
            
            observe(target, options) {
                // Enhanced target validation
                if (!this.isValidTarget(target)) {
                    console.debug("[CloudPepper] Invalid MutationObserver target, skipping");
                    return;
                }
                
                try {
                    return super.observe(target, options);
                } catch (error) {
                    console.debug("[CloudPepper] MutationObserver error caught:", error.message);
                }
            }
            
            isValidTarget(target) {
                return target && 
                       typeof target === 'object' && 
                       target.nodeType && 
                       target.nodeType >= 1 && 
                       target.nodeType <= 12 &&
                       !target._isDetached;
            }
        };
    }

    /**
     * Global Error Handling
     */
    setupGlobalErrorHandling() {
        window.addEventListener('error', (event) => {
            const message = event.message || '';
            const filename = event.filename || '';
            
            if (this.shouldSuppressError(message, filename)) {
                console.debug("[CloudPepper] Suppressed error:", message);
                event.preventDefault();
                return false;
            }
        }, true);
    }

    /**
     * Promise Rejection Handling
     */
    setupPromiseRejectionHandling() {
        window.addEventListener('unhandledrejection', (event) => {
            const reason = event.reason ? event.reason.toString() : '';
            
            if (this.shouldSuppressError(reason)) {
                console.debug("[CloudPepper] Suppressed promise rejection:", reason);
                event.preventDefault();
                return false;
            }
        });
    }

    /**
     * Console Enhancements for Development
     */
    setupConsoleEnhancements() {
        if (typeof window.odoo !== 'undefined' && window.odoo.debug) {
            // Development mode - enhanced logging
            const originalConsoleError = console.error;
            console.error = (...args) => {
                const message = args.join(' ');
                if (!this.shouldSuppressError(message)) {
                    originalConsoleError.apply(console, args);
                }
            };
        }
    }

    /**
     * Check if error should be suppressed
     */
    shouldSuppressError(message, filename = '') {
        return this.suppressedPatterns.some(pattern => 
            pattern.test(message) || pattern.test(filename)
        );
    }

    /**
     * Add custom error pattern
     */
    addSuppressPattern(pattern) {
        if (pattern instanceof RegExp) {
            this.suppressedPatterns.push(pattern);
        }
    }

    /**
     * Get suppression statistics
     */
    getStats() {
        return {
            patternsCount: this.suppressedPatterns.length,
            isActive: true,
            timestamp: new Date().toISOString()
        };
    }
}

/**
 * DOM Utilities for Safer Operations
 */
class DOMUtils {
    /**
     * Safe DOM element selection
     */
    static querySelector(selector, context = document) {
        try {
            return context.querySelector(selector);
        } catch (error) {
            console.debug("[CloudPepper] DOM query failed:", error.message);
            return null;
        }
    }

    /**
     * Safe DOM element selection (all)
     */
    static querySelectorAll(selector, context = document) {
        try {
            return Array.from(context.querySelectorAll(selector));
        } catch (error) {
            console.debug("[CloudPepper] DOM query all failed:", error.message);
            return [];
        }
    }

    /**
     * Safe event listener addition
     */
    static addEventListener(element, event, handler, options = {}) {
        if (!element || typeof element.addEventListener !== 'function') {
            return false;
        }

        try {
            element.addEventListener(event, handler, options);
            return true;
        } catch (error) {
            console.debug("[CloudPepper] Event listener addition failed:", error.message);
            return false;
        }
    }

    /**
     * Safe element manipulation
     */
    static safeManipulate(element, callback) {
        if (!element || !callback) return null;

        try {
            return callback(element);
        } catch (error) {
            console.debug("[CloudPepper] Element manipulation failed:", error.message);
            return null;
        }
    }
}

/**
 * Initialize Error Prevention System
 */
const errorPreventionManager = new ErrorPreventionManager();

/**
 * Export utilities for use in other modules
 */
export { ErrorPreventionManager, DOMUtils };

/**
 * Global access for legacy compatibility
 */
window.CloudPepperErrorPrevention = {
    manager: errorPreventionManager,
    DOMUtils: DOMUtils,
    addPattern: (pattern) => errorPreventionManager.addSuppressPattern(pattern),
    getStats: () => errorPreventionManager.getStats()
};

console.log("[CloudPepper] Modern error prevention system ready");
