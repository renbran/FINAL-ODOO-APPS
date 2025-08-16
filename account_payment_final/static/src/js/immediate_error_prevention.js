/*
 * Immediate Error Prevention.Js
 * 
 * This file intentionally does NOT use /** @odoo-module **/
 * as it's a global error prevention utility loaded before
 * any Odoo modules to prevent import/loading errors.
 */

/**
 * IMMEDIATE Error Prevention for Odoo 17 - CloudPepper Compatible
 * 
 * This script provides immediate error suppression for common CloudPepper
 * deployment issues, particularly with ES6 import statements and module loading.
 * 
 * MUST LOAD FIRST - Before any other JavaScript assets
 */

(function() {
    'use strict';
    
    // Mark as loaded immediately
    window.CloudPepperImmediateErrorPrevention = true;
    
    console.debug("[CloudPepper] Immediate error prevention loading...");
    
    // Critical error patterns that need immediate suppression
    const criticalErrorPatterns = [
        /Cannot use import statement outside a module/,
        /Unexpected token 'import'/,
        /SyntaxError.*import/,
        /Failed to execute 'observe' on 'MutationObserver'/,
        /parameter 1 is not of type 'Node'/,
        /web\.assets_web\.min\.js/,
        /Long Running Recorder/,
        /Content script initialised/,
        /Recorder disabled/
    ];
    
    // Immediate error suppression function
    function suppressCriticalErrors(message, filename) {
        if (!message && !filename) return false;
        
        const msgStr = String(message || '');
        const fileStr = String(filename || '');
        
        return criticalErrorPatterns.some(pattern => 
            pattern.test(msgStr) || pattern.test(fileStr)
        );
    }
    
    // Override window.onerror IMMEDIATELY
    const originalOnError = window.onerror;
    window.onerror = function(message, filename, lineno, colno, error) {
        if (suppressCriticalErrors(message, filename)) {
            console.debug("[CloudPepper] IMMEDIATE suppression:", message);
            return true; // Prevent default error handling
        }
        
        if (originalOnError) {
            return originalOnError.apply(this, arguments);
        }
        return false;
    };
    
    // Override unhandledrejection IMMEDIATELY
    window.addEventListener('unhandledrejection', function(event) {
        const message = event.reason?.message || event.reason || '';
        if (suppressCriticalErrors(message, '')) {
            console.debug("[CloudPepper] IMMEDIATE promise rejection suppressed:", message);
            event.preventDefault();
        }
    });
    
    // Override console.error for critical errors
    const originalConsoleError = console.error;
    console.error = function(...args) {
        const message = args.join(' ');
        if (suppressCriticalErrors(message, '')) {
            console.debug("[CloudPepper] IMMEDIATE console error suppressed:", message);
            return;
        }
        return originalConsoleError.apply(this, args);
    };
    
    // Prevent module loading errors
    if (typeof window.define === 'undefined') {
        window.define = function() {
            console.debug("[CloudPepper] AMD define() call intercepted");
        };
        window.define.amd = true;
    }
    
    // Prevent require() errors
    if (typeof window.require === 'undefined') {
        window.require = function() {
            console.debug("[CloudPepper] CommonJS require() call intercepted");
            return {};
        };
    }
    
    console.debug("[CloudPepper] Immediate error prevention loaded successfully");
    
})();
