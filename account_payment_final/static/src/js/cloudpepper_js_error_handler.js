/** @odoo-module **/

/**
 * CloudPepper Enhanced JavaScript Error Handler
 * 
 * Specialized error handling for CloudPepper hosting environment
 * Extends the main error prevention system with specific handlers
 */

import { ErrorPreventionManager } from "./cloudpepper_clean_fix";

console.log("[CloudPepper] Enhanced error handler loading...");

/**
 * Enhanced Error Handler for CloudPepper Specific Issues
 */
class CloudPepperEnhancedHandler extends ErrorPreventionManager {
    constructor() {
        super();
        this.cloudPepperPatterns = [
            /CloudPepper.*timeout/i,
            /CloudPepper.*connection/i,
            /hosting.*environment/i,
            /deployment.*error/i,
            /Permission denied.*script/i
        ];
        
        this.initCloudPepperSpecific();
    }

    initCloudPepperSpecific() {
        this.setupCloudPepperErrorHandling();
        this.setupPerformanceMonitoring();
        this.setupNetworkErrorHandling();
        
        console.log("[CloudPepper] Enhanced error handler active");
    }

    /**
     * CloudPepper specific error handling
     */
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

    /**
     * Performance monitoring for CloudPepper
     */
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

    /**
     * Network error handling
     */
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

    /**
     * Check if error is CloudPepper specific
     */
    isCloudPepperError(message) {
        return this.cloudPepperPatterns.some(pattern => pattern.test(message));
    }

    /**
     * Check if error is network related
     */
    isNetworkError(error) {
        const networkPatterns = [
            /NetworkError/i,
            /Failed to fetch/i,
            /Connection.*failed/i,
            /timeout/i
        ];
        
        return networkPatterns.some(pattern => pattern.test(error.message));
    }

    /**
     * Get CloudPepper specific statistics
     */
    getCloudPepperStats() {
        return {
            ...this.getStats(),
            cloudPepperPatterns: this.cloudPepperPatterns.length,
            environment: "CloudPepper",
            enhancedFeatures: ["performance", "network", "cloudpepper-specific"]
        };
    }
}

/**
 * Initialize Enhanced Handler
 */
const enhancedHandler = new CloudPepperEnhancedHandler();

/**
 * Export for use in other modules
 */
export { CloudPepperEnhancedHandler };

/**
 * Global access for legacy compatibility
 */
window.CloudPepperEnhancedErrorHandler = enhancedHandler;

console.log("[CloudPepper] Enhanced error handler ready");
        const OriginalMutationObserver = window.MutationObserver;

        // Create safe wrapper
        window.MutationObserver = class SafeMutationObserver extends OriginalMutationObserver {
            observe(target, options) {
                try {
                    // Validate target parameter
                    if (!target) {
                        console.warn("[CloudPepper] MutationObserver.observe called with null/undefined target");
                        return;
                    }

                    if (typeof target !== "object" || !target.nodeType) {
                        console.warn("[CloudPepper] MutationObserver.observe called with invalid target:", target);
                        return;
                    }

                    // Ensure target is a proper DOM node
                    if (
                        target.nodeType !== Node.ELEMENT_NODE &&

                        target.nodeType !== Node.DOCUMENT_NODE &&

                        target.nodeType !== Node.DOCUMENT_FRAGMENT_NODE

                    ) {
                        console.warn(
                            "[CloudPepper] MutationObserver.observe called with invalid node type:",
                            target.nodeType

                        );
                        return;
                    }

                    // Call original observe method
                    return super.observe(target, options);
                } catch (error) {
                    console.warn("[CloudPepper] MutationObserver.observe error caught:", error.message);
                    // Don't re-throw, just log and continue
                }
            }
        };

        console.debug("[CloudPepper] MutationObserver patched for safety");
    }

    setupDOMObservation() {
        // Provide safe DOM observation utility
        window.CloudPepperDOM = {
            safeObserve: (selector, callback, options = {}) => {
                const element = typeof selector === "string" ? document.querySelector(selector) : selector;

                if (!element) {
                    console.warn(`[CloudPepper] Element not found for observation: ${selector}`);
                    return null;
                }

                try {
                    const observer = new MutationObserver(callback);
                    observer.observe(element, {
                        childList: true,
                        subtree: true,
                        attributes: true,
                        ...options
                    });
                    return observer;
                } catch (error) {
                    console.warn("[CloudPepper] Failed to create safe observer:", error.message);
                    return null;
                }
            },

            waitForElement: (selector, timeout = 5000) => {
                return new Promise((resolve, reject) => {
                    const element = document.querySelector(selector);
                    if (element) {
                        resolve(element);
                        return;
                    }

                    const observer = new MutationObserver((mutations) => {
                        const element = document.querySelector(selector);
                        if (element) {
                            observer.disconnect();
                            resolve(element);
                        }
                    });

                    try {
                        observer.observe(document.body, {
                            childList: true,
                            subtree: true;
});

                        setTimeout(() => {
                            observer.disconnect();
                            reject(new Error(`Element ${selector} not found within ${timeout}ms`));
                        }, timeout);
                    } catch (error) {
                        reject(error);
                    }
                });
            }
};
    }
}

// Initialize error handler immediately
const errorHandler = new CloudPepperJSErrorHandler();

// Make available globally for debugging
window.CloudPepperJSErrorHandler = CloudPepperJSErrorHandler;
window.cloudPepperErrorHandler = errorHandler;

console.log("[CloudPepper] JavaScript error handler initialized successfully");

})(); // End IIFE
