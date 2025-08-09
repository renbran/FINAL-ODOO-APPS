/** @odoo-module **/

/**
 * CloudPepper Console Optimizer
 * Suppresses non-critical console warnings and errors for cleaner debugging
 */

import { registry } from "@web/core/registry";

class CloudPepperConsoleOptimizer {
    constructor() {
        this.originalConsole = {};
        this.suppressedPatterns = [
            'Unknown action: is-mobile',
            'Check Redirect',
            'data-oe-',
            'tracking',
            'gtag',
            'analytics',
            'firebase',
            'google-analytics',
            'cloudpepper tracking',
            'third-party script',
            'advertisement',
            'social media'
        ];
        
        this.setupConsoleOptimization();
    }

    setupConsoleOptimization() {
        // Store original console methods
        this.originalConsole.log = console.log;
        this.originalConsole.warn = console.warn;
        this.originalConsole.error = console.error;
        this.originalConsole.info = console.info;
        
        // Override console methods with filtering
        console.log = this.createFilteredMethod('log');
        console.warn = this.createFilteredMethod('warn');
        console.error = this.createFilteredMethod('error');
        console.info = this.createFilteredMethod('info');
        
        console.debug('[CloudPepper] Console optimization enabled');
    }

    createFilteredMethod(level) {
        return (...args) => {
            const message = args.join(' ');
            
            // Check if message should be suppressed
            const shouldSuppress = this.suppressedPatterns.some(pattern => 
                message.toLowerCase().includes(pattern.toLowerCase())
            );
            
            if (!shouldSuppress) {
                // Call original console method
                this.originalConsole[level].apply(console, args);
            } else {
                // Log suppressed message in debug mode only
                if (window.location.search.includes('debug=1')) {
                    this.originalConsole.log(`[CloudPepper Suppressed ${level.toUpperCase()}]:`, ...args);
                }
            }
        };
    }

    restoreConsole() {
        // Restore original console methods
        Object.keys(this.originalConsole).forEach(method => {
            console[method] = this.originalConsole[method];
        });
        console.debug('[CloudPepper] Console optimization disabled');
    }
}

// Initialize console optimizer
const consoleOptimizer = new CloudPepperConsoleOptimizer();

// Register as a service
const consoleOptimizerService = {
    name: "console_optimizer_service",
    dependencies: [],
    
    start() {
        console.debug('[CloudPepper] Console optimizer service started');
        return consoleOptimizer;
    }
};

// Register service
try {
    registry.category("services").add("console_optimizer_service", consoleOptimizerService);
} catch (e) {
    console.debug('[CloudPepper] Could not register console optimizer service:', e.message);
}

// Handle action service errors
try {
    const actionService = registry.category("services").get("action");
    if (actionService) {
        const originalDoAction = actionService.doAction;
        actionService.doAction = function(action, options) {
            try {
                return originalDoAction.call(this, action, options);
            } catch (error) {
                if (error.message.includes('Unknown action')) {
                    console.debug('[CloudPepper] Suppressed unknown action error:', error.message);
                    return Promise.resolve();
                }
                throw error;
            }
        };
    }
} catch (e) {
    console.debug('[CloudPepper] Could not patch action service:', e.message);
}

export { CloudPepperConsoleOptimizer };
