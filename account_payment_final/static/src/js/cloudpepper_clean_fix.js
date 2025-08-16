/*
 * Cloudpepper Clean Fix.Js
 * 
 * This file intentionally does NOT use /** @odoo-module **/
 * as it's a global error prevention utility loaded before
 * any Odoo modules to prevent import/loading errors.
 */

/**
 * CloudPepper Clean Fix for Odoo 17
 * 
 * Clean, production-ready error prevention specifically for CloudPepper
 * hosting environment. Focuses on Odoo 17 compatibility issues.
 * 
 * LOADS AFTER immediate_error_prevention.js
 */

(function() {
    'use strict';
    
    console.debug("[CloudPepper] Clean fix loading...");
    
    // CloudPepper specific error patterns
    const cloudPepperErrorPatterns = [
        /third_party.*crashpad/,
        /registration_protocol_win\.cc/,
        /CreateFile: The system cannot find the file specified/,
        /chrome-extension:/,
        /extensions\/.*\/content_scripts/,
        /Execution context was destroyed/,
        /Script error/
    ];
    
    // Enhanced error detection for CloudPepper
    function isCloudPepperError(message, filename, source) {
        const msgStr = String(message || '');
        const fileStr = String(filename || '');
        const srcStr = String(source || '');
        
        return cloudPepperErrorPatterns.some(pattern =>
            pattern.test(msgStr) || pattern.test(fileStr) || pattern.test(srcStr)
        );
    }
    
    // Clean error handler wrapper
    const originalErrorHandler = window.onerror;
    window.onerror = function(message, filename, lineno, colno, error) {
        // CloudPepper specific suppression
        if (isCloudPepperError(message, filename, error?.stack)) {
            console.debug("[CloudPepper] Clean suppression:", message);
            return true;
        }
        
        // Call previous handler if exists
        if (originalErrorHandler) {
            return originalErrorHandler.apply(this, arguments);
        }
        
        return false;
    };
    
    // Clean promise rejection handler
    window.addEventListener('unhandledrejection', function(event) {
        const reason = event.reason;
        const message = reason?.message || reason || '';
        
        if (isCloudPepperError(message, '', reason?.stack)) {
            console.debug("[CloudPepper] Clean promise rejection suppressed:", message);
            event.preventDefault();
        }
    });
    
    // DOM content loading safety
    function ensureDOMContentLoaded() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                console.debug("[CloudPepper] DOM content loaded safely");
            });
        } else {
            console.debug("[CloudPepper] DOM already ready");
        }
    }
    
    // Initialize clean fixes
    ensureDOMContentLoaded();
    
    // Mark as loaded
    window.CloudPepperCleanFixLoaded = true;
    
    console.debug("[CloudPepper] Clean fix loaded successfully");
    
})();
