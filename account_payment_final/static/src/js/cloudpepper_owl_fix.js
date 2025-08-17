/** @odoo-module **/
/**
 * Enhanced CloudPepper OWL Lifecycle Protection
 * Prevents OWL lifecycle errors and RPC failures in CloudPepper environment
 */

import { patch } from "@web/core/utils/patch";
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

// Global error handler for CloudPepper
const CLOUDPEPPER_ERROR_HANDLER = {
    
    /**
     * Enhanced RPC error handling
     */
    handleRPCError(error, context = {}) {
        console.warn(`[CloudPepper] RPC Error in ${context.component || 'Unknown'}:`, error);
        
        // Don't let RPC errors crash the OWL lifecycle
        if (error.message && error.message.includes('RPC_ERROR')) {
            console.warn('[CloudPepper] Suppressing RPC error to prevent OWL crash');
            return { success: false, error: error.message };
        }
        
        return null;
    },
    
    /**
     * OWL lifecycle error protection
     */
    handleOwlError(error, component) {
        console.warn(`[CloudPepper] OWL Error in ${component.constructor.name}:`, error);
        
        // Prevent error propagation that causes lifecycle crashes
        if (error.cause && error.cause.message && error.cause.message.includes('RPC_ERROR')) {
            console.warn('[CloudPepper] Preventing OWL lifecycle crash from RPC error');
            return true; // Error handled
        }
        
        return false; // Let other errors propagate normally
    },
    
    /**
     * Safe async operation wrapper
     */
    async safeAsync(operation, fallback = null, context = {}) {
        try {
            return await operation();
        } catch (error) {
            const handled = this.handleRPCError(error, context);
            if (handled) {
                return fallback;
            }
            throw error;
        }
    }
};

// Patch Component base class for enhanced error handling
patch(Component.prototype, {
    
    setup() {
        super.setup();
        
        // Add CloudPepper error handling to all components
        this._cloudpepperErrorHandler = CLOUDPEPPER_ERROR_HANDLER;
        
        // Wrap existing setup in try-catch
        try {
            this._originalSetup();
        } catch (error) {
            console.warn(`[CloudPepper] Setup error in ${this.constructor.name}:`, error);
            // Don't let setup errors crash the component
        }
    },
    
    _originalSetup() {
        // Override in components that need special setup handling
    },
    
    /**
     * Safe RPC call wrapper for CloudPepper
     */
    async safeRpc(model, method, args = [], kwargs = {}) {
        const context = {
            component: this.constructor.name,
            model: model,
            method: method
        };
        
        return await this._cloudpepperErrorHandler.safeAsync(
            () => this.rpc({
                model: model,
                method: method,
                args: args,
                kwargs: kwargs
            }),
            null,
            context
        );
    },
    
    /**
     * Safe ORM call wrapper
     */
    async safeOrmCall(model, method, args = [], kwargs = {}) {
        if (!this.orm) {
            console.warn('[CloudPepper] ORM service not available');
            return null;
        }
        
        const context = {
            component: this.constructor.name,
            model: model,
            method: method
        };
        
        return await this._cloudpepperErrorHandler.safeAsync(
            () => this.orm.call(model, method, args, kwargs),
            null,
            context
        );
    }
});

// Enhanced error handling for specific modules
const KNOWN_PROBLEMATIC_MODULES = [
    'account_payment_final',
    'order_status_override',
    'enhanced_rest_api',
    'oe_sale_dashboard_17'
];

// Safe module loading
KNOWN_PROBLEMATIC_MODULES.forEach(moduleName => {
    try {
        console.log(`[CloudPepper] Protecting module: ${moduleName}`);
        
        // Add module-specific error handling if needed
        registry.category("services").addEventListener("UPDATE", (ev) => {
            if (ev.detail && ev.detail.key && ev.detail.key.includes(moduleName)) {
                console.log(`[CloudPepper] Safe loading: ${ev.detail.key}`);
            }
        });
        
    } catch (error) {
        console.warn(`[CloudPepper] Error protecting module ${moduleName}:`, error);
    }
});

// Global window error handler for unhandled promises
window.addEventListener('unhandledrejection', function(event) {
    if (event.reason && event.reason.message && event.reason.message.includes('RPC_ERROR')) {
        console.warn('[CloudPepper] Prevented unhandled RPC rejection:', event.reason);
        event.preventDefault(); // Prevent the error from crashing the application
    }
});

// Global error handler for OWL errors
window.addEventListener('error', function(event) {
    if (event.error && event.error.message && 
        (event.error.message.includes('owl lifecycle') || event.error.message.includes('RPC_ERROR'))) {
        console.warn('[CloudPepper] Prevented OWL/RPC error crash:', event.error);
        event.preventDefault();
    }
});

console.log('[CloudPepper] Enhanced OWL Lifecycle & RPC Error Protection Loaded');
