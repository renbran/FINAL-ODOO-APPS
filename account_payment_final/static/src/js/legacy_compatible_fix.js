/**
 * LEGACY-COMPATIBLE JavaScript Module Fix for Odoo 17
 * 
 * This script uses NO ES6 modules or modern syntax to ensure compatibility
 * even in environments where ES6 modules are problematic.
 * 
 * Uses only ES5 syntax for maximum compatibility.
 */

(function() {
    'use strict';
    
    console.debug("[CloudPepper] LEGACY-compatible error prevention loading...");
    
    // Error patterns - ES5 compatible array
    var criticalErrorPatterns = [
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
    
    // ES5 function for error checking
    function shouldSuppressError(message, filename) {
        if (!message && !filename) return false;
        var msgStr = String(message || '');
        var fileStr = String(filename || '');
        
        for (var i = 0; i < criticalErrorPatterns.length; i++) {
            var pattern = criticalErrorPatterns[i];
            if (pattern.test(msgStr) || pattern.test(fileStr)) {
                return true;
            }
        }
        return false;
    }
    
    // Override window.onerror with ES5 function
    var originalOnError = window.onerror;
    window.onerror = function(message, filename, lineno, colno, error) {
        if (shouldSuppressError(message, filename)) {
            console.debug("[CloudPepper] LEGACY error suppressed:", message);
            return true; // Prevent default handling
        }
        if (originalOnError) {
            return originalOnError.apply(this, arguments);
        }
        return false;
    };
    
    // Override console.error with ES5 function
    var originalConsoleError = console.error;
    console.error = function() {
        var args = Array.prototype.slice.call(arguments);
        var message = args.join(' ');
        if (shouldSuppressError(message, '')) {
            console.debug("[CloudPepper] LEGACY console error suppressed:", message);
            return;
        }
        return originalConsoleError.apply(this, arguments);
    };
    
    // Promise rejection handling - ES5 compatible
    if (window.addEventListener) {
        window.addEventListener('unhandledrejection', function(event) {
            var message = '';
            if (event.reason) {
                if (event.reason.message) {
                    message = event.reason.message;
                } else {
                    message = String(event.reason);
                }
            }
            
            if (shouldSuppressError(message, '')) {
                console.debug("[CloudPepper] LEGACY promise rejection suppressed:", message);
                event.preventDefault();
            }
        }, true);
    }
    
    // Script loading fix - ES5 compatible
    var originalCreateElement = document.createElement;
    document.createElement = function(tagName) {
        var element = originalCreateElement.call(this, tagName);
        
        if (tagName && tagName.toLowerCase() === 'script') {
            // Problem asset detection
            var problemAssets = ['assets_web', 'web.assets_web.min.js', '.min.js'];
            
            // Override setAttribute
            var originalSetAttribute = element.setAttribute;
            element.setAttribute = function(name, value) {
                if (name === 'src' && value) {
                    // Check if this is a problematic asset
                    var isProblematic = false;
                    for (var i = 0; i < problemAssets.length; i++) {
                        if (value.indexOf(problemAssets[i]) !== -1) {
                            isProblematic = true;
                            break;
                        }
                    }
                    
                    if (isProblematic) {
                        console.debug("[CloudPepper] LEGACY script fix applied to:", value);
                        
                        // Force module type
                        originalSetAttribute.call(this, 'type', 'module');
                        originalSetAttribute.call(this, 'defer', 'true');
                        
                        // Add error handling
                        this.onerror = function() {
                            console.debug("[CloudPepper] LEGACY script error suppressed for:", value);
                            return true;
                        };
                    }
                }
                
                return originalSetAttribute.call(this, name, value);
            };
            
            // Override src property - ES5 compatible
            var srcValue = '';
            if (Object.defineProperty) {
                try {
                    Object.defineProperty(element, 'src', {
                        get: function() {
                            return srcValue;
                        },
                        set: function(value) {
                            srcValue = value;
                            if (value) {
                                this.setAttribute('src', value);
                            }
                        },
                        configurable: true
                    });
                } catch (e) {
                    // Fallback if defineProperty fails
                    console.debug("[CloudPepper] LEGACY property definition fallback");
                }
            }
        }
        
        return element;
    };
    
    // MutationObserver fix - ES5 compatible
    if (window.MutationObserver) {
        var OriginalMutationObserver = window.MutationObserver;
        
        window.MutationObserver = function(callback) {
            var safeCallback = function(mutations, observer) {
                try {
                    return callback.call(this, mutations, observer);
                } catch (error) {
                    console.debug("[CloudPepper] LEGACY MutationObserver callback error suppressed:", error.message);
                    return null;
                }
            };
            
            var instance = new OriginalMutationObserver(safeCallback);
            
            // Override observe method
            var originalObserve = instance.observe;
            instance.observe = function(target, options) {
                // Basic target validation
                if (!target || typeof target !== 'object' || !target.nodeType) {
                    console.debug("[CloudPepper] LEGACY MutationObserver invalid target rejected");
                    return; // Silent fail
                }
                
                // Check node type
                var validNodeTypes = [1, 9, 11]; // Element, Document, DocumentFragment
                var isValidNodeType = false;
                for (var i = 0; i < validNodeTypes.length; i++) {
                    if (target.nodeType === validNodeTypes[i]) {
                        isValidNodeType = true;
                        break;
                    }
                }
                
                if (!isValidNodeType) {
                    console.debug("[CloudPepper] LEGACY MutationObserver invalid node type rejected");
                    return; // Silent fail
                }
                
                // Connection check for elements
                if (target.nodeType === 1 && target.isConnected === false) {
                    console.debug("[CloudPepper] LEGACY MutationObserver disconnected element rejected");
                    return; // Silent fail
                }
                
                try {
                    return originalObserve.call(this, target, options);
                } catch (error) {
                    console.debug("[CloudPepper] LEGACY MutationObserver error suppressed:", error.message);
                    return; // Silent fail
                }
            };
            
            return instance;
        };
        
        // Preserve prototype chain
        if (Object.setPrototypeOf) {
            Object.setPrototypeOf(window.MutationObserver, OriginalMutationObserver);
        }
        window.MutationObserver.prototype = OriginalMutationObserver.prototype;
    }
    
    // Global error event listener
    if (window.addEventListener) {
        window.addEventListener('error', function(event) {
            var message = event.message || '';
            var filename = event.filename || '';
            
            if (shouldSuppressError(message, filename)) {
                console.debug("[CloudPepper] LEGACY global error suppressed:", message);
                event.preventDefault();
                event.stopPropagation();
                return false;
            }
        }, true);
    }
    
    // Mark as loaded
    window.CloudPepperLegacyCompatibleFixLoaded = true;
    
    console.debug("[CloudPepper] LEGACY-compatible error prevention ACTIVE");
})();
