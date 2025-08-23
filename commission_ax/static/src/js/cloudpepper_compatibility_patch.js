/** @odoo-module **/

/**
 * CloudPepper Compatibility Patch for Commission AX Module
 * Provides global error handling and OWL lifecycle protection
 * 
 * @module commission_ax.cloudpepper_compatibility_patch
 * @author OSUS Properties
 * @version 17.0.2.0.0
 */

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

console.log("🛡️ Commission AX CloudPepper Compatibility Patch Loading...");

// Global error handler for CloudPepper environment
window.addEventListener('error', function(event) {
    console.error('🚨 Commission AX Global Error Handler:', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error,
        timestamp: new Date().toISOString()
    });
    
    // Prevent error propagation in CloudPepper
    if (event.message && event.message.includes('commission')) {
        event.preventDefault();
        return true;
    }
});

// Promise rejection handler for async operations
window.addEventListener('unhandledrejection', function(event) {
    console.error('🚨 Commission AX Unhandled Promise Rejection:', {
        reason: event.reason,
        promise: event.promise,
        timestamp: new Date().toISOString()
    });
    
    // Handle commission-related promise rejections
    if (event.reason && event.reason.toString().toLowerCase().includes('commission')) {
        event.preventDefault();
        return true;
    }
});

// OWL Component error boundary
const originalSetup = Component.prototype.setup;
Component.prototype.setup = function() {
    try {
        if (originalSetup) {
            originalSetup.call(this);
        }
    } catch (error) {
        console.error('🚨 Commission AX OWL Setup Error:', {
            component: this.constructor.name,
            error: error.message,
            stack: error.stack,
            timestamp: new Date().toISOString()
        });
        
        // Fallback setup for commission components
        if (this.constructor.name.toLowerCase().includes('commission')) {
            this.env = this.env || {};
            this.props = this.props || {};
        }
    }
};

// RPC error handling for commission operations
const originalRPCCall = odoo.define ? odoo.define : function() {};
if (typeof odoo !== 'undefined' && odoo.define) {
    odoo.define('commission_ax.rpc_handler', function(require) {
        'use strict';
        
        const rpc = require('web.rpc');
        const originalQuery = rpc.query;
        
        rpc.query = function(params) {
            return originalQuery.call(this, params).catch(function(error) {
                if (params.model && params.model.includes('commission')) {
                    console.error('🚨 Commission AX RPC Error:', {
                        model: params.model,
                        method: params.method,
                        error: error.message,
                        timestamp: new Date().toISOString()
                    });
                    
                    // Return empty result for commission queries to prevent UI freeze
                    return { result: [] };
                }
                throw error;
            });
        };
    });
}

// Form view error protection
if (typeof odoo !== 'undefined' && odoo.define) {
    odoo.define('commission_ax.form_protection', function(require) {
        'use strict';
        
        const FormView = require('web.FormView');
        const originalWillStart = FormView.prototype.willStart;
        
        FormView.prototype.willStart = function() {
            try {
                return originalWillStart.call(this);
            } catch (error) {
                if (this.modelName && this.modelName.includes('commission')) {
                    console.error('🚨 Commission AX Form View Error:', {
                        model: this.modelName,
                        error: error.message,
                        timestamp: new Date().toISOString()
                    });
                    
                    // Return resolved promise to continue loading
                    return Promise.resolve();
                }
                throw error;
            }
        };
    });
}

// Field widget error protection
if (typeof odoo !== 'undefined' && odoo.define) {
    odoo.define('commission_ax.field_protection', function(require) {
        'use strict';
        
        const AbstractField = require('web.AbstractField');
        const originalInit = AbstractField.prototype._init;
        
        AbstractField.prototype._init = function() {
            try {
                return originalInit.call(this);
            } catch (error) {
                if (this.name && this.name.includes('commission')) {
                    console.error('🚨 Commission AX Field Widget Error:', {
                        field: this.name,
                        error: error.message,
                        timestamp: new Date().toISOString()
                    });
                    
                    // Initialize with safe defaults
                    this.value = this.value || '';
                    return;
                }
                throw error;
            }
        };
    });
}

// Commission-specific error recovery functions
window.CommissionAXErrorHandler = {
    
    /**
     * Safely execute commission operations with error handling
     */
    safeExecute: function(operation, fallback) {
        try {
            return operation();
        } catch (error) {
            console.error('🚨 Commission AX Safe Execute Error:', error);
            return fallback ? fallback() : null;
        }
    },
    
    /**
     * Recover from commission form errors
     */
    recoverCommissionForm: function(formView) {
        try {
            if (formView && formView.renderer) {
                formView.renderer.$el.find('.o_form_button_save').prop('disabled', false);
                formView.renderer.$el.find('.o_form_button_cancel').prop('disabled', false);
            }
        } catch (error) {
            console.error('🚨 Commission Form Recovery Error:', error);
        }
    },
    
    /**
     * Reset commission UI state
     */
    resetCommissionUI: function() {
        try {
            // Remove any stuck loading states
            $('.o_commission_loading').removeClass('o_commission_loading');
            $('button[disabled]').filter('[data-commission]').prop('disabled', false);
            
            // Clear any error messages
            $('.o_commission_error').remove();
            
        } catch (error) {
            console.error('🚨 Commission UI Reset Error:', error);
        }
    }
};

// Initialize CloudPepper protection on DOM ready
$(document).ready(function() {
    console.log("✅ Commission AX CloudPepper Compatibility Patch Initialized");
    
    // Set up periodic error recovery
    setInterval(function() {
        if (window.CommissionAXErrorHandler) {
            window.CommissionAXErrorHandler.resetCommissionUI();
        }
    }, 30000); // Every 30 seconds
});

console.log("🛡️ Commission AX CloudPepper Compatibility Patch Loaded Successfully");
