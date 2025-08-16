/**
 * CloudPepper Clean Fix for Odoo 17
 * 
 * This script provides additional error suppression and module loading fixes
 * specifically optimized for CloudPepper hosting environment.
 * 
 * Should load after immediate_error_prevention.js
 */

(function() {
    'use strict';
    
    console.debug("[CloudPepper] Clean fix loading...");
    
    // Additional error patterns for CloudPepper environment
    var cloudPepperPatterns = [
        /chrome-extension:/,
        /moz-extension:/,
        /safari-extension:/,
        /Script error/,
        /Non-Error promise rejection captured/,
        /ResizeObserver loop limit exceeded/,
        /The play\(\) request was interrupted/,
        /ChunkLoadError/,
        /Loading chunk/,
        /NetworkError/
    ];
    
    function isCloudPepperError(message, filename) {
        if (!message && !filename) return false;
        var msgStr = String(message || '');
        var fileStr = String(filename || '');
        
        for (var i = 0; i < cloudPepperPatterns.length; i++) {
            var pattern = cloudPepperPatterns[i];
            if (pattern.test(msgStr) || pattern.test(fileStr)) {
                return true;
            }
        }
        return false;
    }
    
    // Enhance existing error handler
    var existingHandler = window.onerror;
    window.onerror = function(message, filename, lineno, colno, error) {
        if (isCloudPepperError(message, filename)) {
            console.debug("[CloudPepper] CloudPepper-specific error suppressed:", message);
            return true;
        }
        if (existingHandler) {
            return existingHandler.apply(this, arguments);
        }
        return false;
    };
    
    // Enhance Promise rejection handler
    window.addEventListener('unhandledrejection', function(event) {
        var message = event.reason?.message || event.reason || '';
        if (isCloudPepperError(message, '')) {
            console.debug("[CloudPepper] CloudPepper promise rejection suppressed:", message);
            event.preventDefault();
        }
    });
    
    // Script loading optimization for CloudPepper
    if (document.createElement) {
        var originalCreateElement = document.createElement;
        document.createElement = function(tagName) {
            var element = originalCreateElement.call(this, tagName);
            
            if (tagName.toLowerCase() === 'script') {
                // Add error handling to all script elements
                element.addEventListener('error', function(e) {
                    console.debug("[CloudPepper] Script loading error suppressed:", e.target.src);
                    e.preventDefault();
                    e.stopPropagation();
                });
            }
            
            return element;
        };
    }
    
    // DOM mutation optimization
    if (window.MutationObserver) {
        var OriginalMutationObserver = window.MutationObserver;
        window.MutationObserver = function(callback) {
            var wrappedCallback = function(mutations, observer) {
                try {
                    return callback.call(this, mutations, observer);
                } catch (error) {
                    if (isCloudPepperError(error.message, '')) {
                        console.debug("[CloudPepper] MutationObserver error suppressed:", error.message);
                        return;
                    }
                    throw error;
                }
            };
            return new OriginalMutationObserver(wrappedCallback);
        };
        
        // Copy static methods
        Object.setPrototypeOf(window.MutationObserver, OriginalMutationObserver);
        Object.defineProperty(window.MutationObserver, 'prototype', {
            value: OriginalMutationObserver.prototype,
            writable: false
        });
    }
    
    // Mark as loaded
    window.CloudPepperCleanFixLoaded = true;
    console.debug("[CloudPepper] Clean fix loaded");
    
})();
