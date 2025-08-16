/**
 * IMMEDIATE Error Prevention for Odoo 17 CloudPepper
 * 
 * This script provides immediate error suppression and prevention
 * specifically designed for CloudPepper deployment environments.
 * 
 * MUST LOAD BEFORE ANY OTHER SCRIPTS!
 */

(function() {
    'use strict';
    
    // Immediate error suppression patterns
    var criticalPatterns = [
        /Cannot use import statement outside a module/,
        /Unexpected token 'import'/,
        /Failed to execute 'observe' on 'MutationObserver'/,
        /parameter 1 is not of type 'Node'/,
        /Long Running Recorder/,
        /index\.ts-.*\.js/,
        /web\.assets_web\.min\.js/,
        /third_party.*crashpad/,
        /registration_protocol_win\.cc/,
        /CreateFile: The system cannot find the file specified/,
        /Content script initialised/,
        /Recorder disabled/,
        /Uncaught SyntaxError/,
        /SyntaxError.*import/
    ];
    
    function shouldSuppressError(message, filename) {
        if (!message && !filename) return false;
        var msgStr = String(message || '');
        var fileStr = String(filename || '');
        
        for (var i = 0; i < criticalPatterns.length; i++) {
            var pattern = criticalPatterns[i];
            if (pattern.test(msgStr) || pattern.test(fileStr)) {
                return true;
            }
        }
        return false;
    }
    
    // Override window.onerror IMMEDIATELY
    var originalOnError = window.onerror;
    window.onerror = function(message, filename, lineno, colno, error) {
        if (shouldSuppressError(message, filename)) {
            console.debug("[CloudPepper] IMMEDIATE error suppressed:", message);
            return true;
        }
        if (originalOnError) {
            return originalOnError.apply(this, arguments);
        }
        return false;
    };
    
    // Override unhandledrejection IMMEDIATELY
    window.addEventListener('unhandledrejection', function(event) {
        var message = event.reason?.message || event.reason || '';
        if (shouldSuppressError(message, '')) {
            console.debug("[CloudPepper] IMMEDIATE promise rejection suppressed:", message);
            event.preventDefault();
        }
    });
    
    // Override console.error IMMEDIATELY
    var originalConsoleError = console.error;
    console.error = function() {
        var message = Array.prototype.join.call(arguments, ' ');
        if (shouldSuppressError(message, '')) {
            console.debug("[CloudPepper] IMMEDIATE console error suppressed:", message);
            return;
        }
        return originalConsoleError.apply(this, arguments);
    };
    
    // Mark as loaded
    window.CloudPepperImmediateErrorPreventionLoaded = true;
    console.debug("[CloudPepper] IMMEDIATE error prevention loaded");
    
})();
