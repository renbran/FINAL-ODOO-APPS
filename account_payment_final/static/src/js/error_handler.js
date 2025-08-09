/** @odoo-module **/

/**
 * Generic Error Handler for CloudPepper Deployment
 * Handles console errors, undefined actions, and third-party warnings
 */

import { registry } from "@web/core/registry";

const ErrorHandler = {
    name: "cloudpepper_error_handler",

    start() {
        this.setupGlobalErrorHandling();
        this.patchActionManager();
        this.setupConsoleFiltering();
        return {};
    },

    /**
     * Setup global error handling
     */
    setupGlobalErrorHandling() {
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            const error = event.reason;
            
            // Skip known non-critical errors
            if (this.isNonCriticalError(error)) {
                console.warn('[CloudPepper] Suppressed non-critical error:', error);
                event.preventDefault();
                return;
            }
            
            console.error('[CloudPepper] Unhandled promise rejection:', error);
        });

        // Handle general JavaScript errors
        window.addEventListener('error', (event) => {
            const error = event.error;
            
            if (this.isNonCriticalError(error)) {
                console.warn('[CloudPepper] Suppressed non-critical error:', error);
                event.preventDefault();
                return;
            }
        });
    },

    /**
     * Check if error is non-critical
     */
    isNonCriticalError(error) {
        if (!error) return false;
        
        const errorMessage = error.toString ? error.toString() : String(error);
        
        const nonCriticalPatterns = [
            'Unknown action: undefined',
            'Unknown action: is-mobile',
            'Page data capture skipped',
            'Fullstory: Skipped by sampling',
            'Check Redirect',
            'Font preload',
            'Analytics not available',
            'Tracking script not loaded'
        ];

        return nonCriticalPatterns.some(pattern => 
            errorMessage.includes(pattern)
        );
    },

    /**
     * Patch action manager to handle undefined actions
     */
    patchActionManager() {
        // Try to access the action manager from registry
        try {
            const actionManagerService = registry.category("services").get("action", null);
            
            if (actionManagerService) {
                const originalDoAction = actionManagerService.doAction;
                
                actionManagerService.doAction = function(action, options = {}) {
                    // Handle undefined or invalid actions
                    if (!action || action === 'undefined' || action === 'is-mobile') {
                        console.warn('[CloudPepper] Skipped undefined action:', action);
                        return Promise.resolve();
                    }
                    
                    // Ensure action has required properties
                    if (typeof action === 'string') {
                        action = {
                            type: 'ir.actions.client',
                            tag: action,
                            name: action
                        };
                    }
                    
                    return originalDoAction.call(this, action, options);
                };
            }
        } catch (error) {
            console.warn('[CloudPepper] Could not patch action manager:', error);
        }
    },

    /**
     * Setup console filtering for cleaner logs
     */
    setupConsoleFiltering() {
        // Store original console methods
        const originalConsole = {
            error: console.error,
            warn: console.warn,
            log: console.log
        };

        // Filter console.error
        console.error = (...args) => {
            const message = args.join(' ');
            
            if (this.shouldSuppressMessage(message, 'error')) {
                console.warn('[CloudPepper] Suppressed error:', message);
                return;
            }
            
            originalConsole.error.apply(console, args);
        };

        // Filter console.warn
        console.warn = (...args) => {
            const message = args.join(' ');
            
            if (this.shouldSuppressMessage(message, 'warn')) {
                return;
            }
            
            originalConsole.warn.apply(console, args);
        };
    },

    /**
     * Determine if a message should be suppressed
     */
    shouldSuppressMessage(message, level) {
        const suppressPatterns = {
            error: [
                'Unknown action: undefined',
                'Unknown action: is-mobile',
                'Action not found',
                'Invalid action type'
            ],
            warn: [
                'Page data capture skipped',
                'Fullstory: Skipped by sampling',
                'Check Redirect',
                'Font preload warning',
                'Third-party service warning'
            ]
        };

        const patterns = suppressPatterns[level] || [];
        
        return patterns.some(pattern => 
            message.toLowerCase().includes(pattern.toLowerCase())
        );
    }
};

// Register the error handler service
registry.category("services").add("cloudpepper_error_handler", ErrorHandler);

export default ErrorHandler;
