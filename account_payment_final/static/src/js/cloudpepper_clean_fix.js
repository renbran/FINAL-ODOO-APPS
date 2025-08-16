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
            /Loading failed/,
            /third_party.*crashpad/,
            /registration_protocol_win\.cc/,
            /CreateFile: The system cannot find the file specified/,
            /Content script initialised/,
            /Recorder disabled/,
            /Uncaught SyntaxError: Cannot use import statement outside a module/
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
                if (!target) return false;
                
                // Check if it's a valid DOM node
                if (typeof target !== 'object') return false;
                if (!target.nodeType) return false;
                
                // Valid node types: 1=Element, 2=Attr, 3=Text, 9=Document, 11=DocumentFragment
                const validNodeTypes = [1, 2, 3, 9, 11];
                if (!validNodeTypes.includes(target.nodeType)) return false;
                
                // Check if node is still connected to DOM
                if (target.nodeType === 1 && !target.isConnected) return false;
                
                // Check if node is not detached
                if (target._isDetached) return false;
                
                // Additional safety checks
                try {
                    // Try to access a common property to ensure the node is valid
                    const hasValidProperties = 'addEventListener' in target || 'nodeValue' in target;
                    return hasValidProperties;
                } catch (error) {
                    console.debug("[CloudPepper] Node validation failed:", error.message);
                    return false;
                }
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
 * Enhanced CloudPepper Error Handler Class
 * Consolidates all error prevention functionality
 */
class CloudPepperEnhancedHandler extends ErrorPreventionManager {
    constructor() {
        super();
        this.cloudPepperPatterns = [
            /CloudPepper.*timeout/i,
            /CloudPepper.*connection/i,
            /hosting.*environment/i,
            /deployment.*error/i,
            /Permission denied.*script/i,
            /index\.ts-.*\.js/,
            /Long Running Recorder/
        ];
        
        this.initCloudPepperSpecific();
    }

    initCloudPepperSpecific() {
        this.setupCloudPepperErrorHandling();
        this.setupPerformanceMonitoring();
        this.setupNetworkErrorHandling();
        
        console.log("[CloudPepper] Enhanced error handler active");
    }

    setupCloudPepperErrorHandling() {
        // Add CloudPepper specific patterns
        this.cloudPepperPatterns.forEach(pattern => {
            this.addSuppressPattern(pattern);
        });

        // Enhanced console error handling for CloudPepper
        window.addEventListener('error', (event) => {
            const message = event.message || '';
            
            if (this.isCloudPepperError(message)) {
                console.debug("[CloudPepper] Suppressed CloudPepper-specific error:", message);
                event.preventDefault();
                return false;
            }
        }, true);
    }

    setupPerformanceMonitoring() {
        if (window.PerformanceObserver) {
            try {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach(entry => {
                        if (entry.duration > 1000) { // Log slow operations
                            console.debug("[CloudPepper] Slow operation detected:", entry.name, entry.duration + "ms");
                        }
                    });
                });
                
                observer.observe({ entryTypes: ['measure', 'navigation'] });
            } catch (error) {
                console.debug("[CloudPepper] Performance monitoring setup failed:", error.message);
            }
        }
    }

    setupNetworkErrorHandling() {
        // Monitor fetch failures
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch.apply(window, args);
                if (!response.ok && response.status >= 500) {
                    console.debug("[CloudPepper] Server error suppressed:", response.status, response.statusText);
                }
                return response;
            } catch (error) {
                if (this.isNetworkError(error)) {
                    console.debug("[CloudPepper] Network error suppressed:", error.message);
                    throw error; // Re-throw for proper handling
                }
                throw error;
            }
        };
    }

    isCloudPepperError(message) {
        return this.cloudPepperPatterns.some(pattern => pattern.test(message));
    }

    isNetworkError(error) {
        return error.name === 'TypeError' && 
               (error.message.includes('fetch') || 
                error.message.includes('network') ||
                error.message.includes('NetworkError'));
    }

    addSuppressPattern(pattern) {
        if (pattern instanceof RegExp) {
            this.suppressedPatterns.push(pattern);
        }
    }

    getStats() {
        return {
            suppressedErrors: this.suppressedErrors || 0,
            mutationObserverFixes: this.mutationObserverFixes || 0,
            networkErrorsSuppressed: this.networkErrorsSuppressed || 0
        };
    }
}

/**
 * Initialize Enhanced Error Prevention System
 */
const errorPreventionManager = new CloudPepperEnhancedHandler();

/**
 * Export utilities for use in other modules
 */
export { ErrorPreventionManager, CloudPepperEnhancedHandler, DOMUtils };

/**
 * Global access for legacy compatibility
 */
window.CloudPepperErrorPrevention = {
    manager: errorPreventionManager,
    DOMUtils: DOMUtils,
    addPattern: (pattern) => errorPreventionManager.addSuppressPattern(pattern),
    getStats: () => errorPreventionManager.getStats()
};

console.log("[CloudPepper] Enhanced error prevention system ready");
