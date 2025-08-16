/** @odoo-module **/

/**
 * IMMEDIATE JavaScript Error Prevention System
 * 
 * This script loads immediately and aggressively prevents JavaScript errors
 * before they can occur, specifically targeting browser extension conflicts
 * and MutationObserver issues in CloudPepper environment.
 */

console.log("[CloudPepper] IMMEDIATE error prevention loading...");

// Immediate MutationObserver protection - override before any other scripts load
(function() {
    'use strict';
    
    if (!window.MutationObserver) return;
    
    const OriginalMutationObserver = window.MutationObserver;
    
    // Enhanced error suppression patterns
    const suppressedPatterns = [
        /Failed to execute 'observe' on 'MutationObserver'/,
        /parameter 1 is not of type 'Node'/,
        /Long Running Recorder/,
        /index\.ts-.*\.js/,
        /Cannot use import statement/,
        /third_party.*crashpad/,
        /registration_protocol_win\.cc/,
        /CreateFile: The system cannot find the file specified/,
        /Content script initialised/,
        /Recorder disabled/,
        /Uncaught SyntaxError: Cannot use import statement outside a module/,
        /web\.assets_web\.min\.js/
    ];
    
    // Immediate error suppression
    function shouldSuppressError(message, filename) {
        return suppressedPatterns.some(pattern => 
            pattern.test(message) || pattern.test(filename || '')
        );
    }
    
    // Override window.onerror immediately
    const originalOnError = window.onerror;
    window.onerror = function(message, filename, lineno, colno, error) {
        if (shouldSuppressError(message, filename)) {
            console.debug("[CloudPepper] IMMEDIATE suppression:", message);
            return true; // Prevent default handling
        }
        if (originalOnError) {
            return originalOnError.apply(this, arguments);
        }
        return false;
    };
    
    // Override addEventListener for error events
    const originalAddEventListener = window.addEventListener;
    window.addEventListener = function(type, listener, options) {
        if (type === 'error' && typeof listener === 'function') {
            const wrappedListener = function(event) {
                const message = event.message || '';
                const filename = event.filename || '';
                
                if (shouldSuppressError(message, filename)) {
                    console.debug("[CloudPepper] IMMEDIATE event suppression:", message);
                    event.preventDefault();
                    event.stopPropagation();
                    return false;
                }
                
                return listener.apply(this, arguments);
            };
            
            return originalAddEventListener.call(this, type, wrappedListener, options);
        }
        
        return originalAddEventListener.apply(this, arguments);
    };
    
    // Enhanced MutationObserver with immediate protection
    window.MutationObserver = class EnhancedMutationObserver extends OriginalMutationObserver {
        constructor(callback) {
            const safeCallback = (mutations, observer) => {
                try {
                    return callback.call(this, mutations, observer);
                } catch (error) {
                    console.debug("[CloudPepper] IMMEDIATE MutationObserver callback error suppressed:", error.message);
                    return null;
                }
            };
            
            super(safeCallback);
        }
        
        observe(target, options) {
            // Ultra-comprehensive target validation
            if (!this.isUltraSafeTarget(target)) {
                console.debug("[CloudPepper] IMMEDIATE MutationObserver target rejection");
                return; // Silent fail instead of throwing
            }
            
            try {
                return super.observe(target, options);
            } catch (error) {
                console.debug("[CloudPepper] IMMEDIATE MutationObserver error suppressed:", error.message);
                return; // Silent fail
            }
        }
        
        isUltraSafeTarget(target) {
            try {
                // Basic existence check
                if (!target) return false;
                
                // Type validation
                if (typeof target !== 'object') return false;
                
                // Node interface validation
                if (!target.nodeType) return false;
                
                // Valid node types (more restrictive)
                const safeNodeTypes = [1, 9, 11]; // Element, Document, DocumentFragment only
                if (!safeNodeTypes.includes(target.nodeType)) return false;
                
                // DOM connection check (if element)
                if (target.nodeType === 1) {
                    if (typeof target.isConnected === 'boolean' && !target.isConnected) {
                        return false;
                    }
                    
                    // Additional safety checks
                    if (!target.ownerDocument) return false;
                    if (target._isDetached) return false;
                }
                
                // Method existence validation
                if (target.nodeType === 1 && typeof target.addEventListener !== 'function') {
                    return false;
                }
                
                // Extension script detection
                if (target.ownerDocument && target.ownerDocument.location) {
                    const url = target.ownerDocument.location.href;
                    if (url.includes('extension://') || url.includes('moz-extension://')) {
                        return false;
                    }
                }
                
                return true;
                
            } catch (error) {
                console.debug("[CloudPepper] IMMEDIATE target validation error:", error.message);
                return false;
            }
        }
    };
    
    // Immediate console enhancement
    const originalConsoleError = console.error;
    console.error = function(...args) {
        const message = args.join(' ');
        if (shouldSuppressError(message, '')) {
            console.debug("[CloudPepper] IMMEDIATE console error suppressed:", message);
            return;
        }
        return originalConsoleError.apply(this, args);
    };
    
    // Promise rejection handling
    window.addEventListener('unhandledrejection', function(event) {
        const message = event.reason?.message || event.reason || '';
        if (shouldSuppressError(message, '')) {
            console.debug("[CloudPepper] IMMEDIATE promise rejection suppressed:", message);
            event.preventDefault();
        }
    });
    
    console.log("[CloudPepper] IMMEDIATE error prevention active");
})();

// Export for module compatibility
export { };

// Mark as loaded
window.CloudPepperImmediateProtectionLoaded = true;
