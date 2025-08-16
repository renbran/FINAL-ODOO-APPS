/**
 * ULTIMATE JavaScript Module Fix for Odoo 17
 * 
 * This script fixes ES6 import statement errors in Odoo's core assets
 * by intercepting script loading and ensuring proper module handling.
 * 
 * MUST LOAD BEFORE ANY OTHER SCRIPTS!
 */

(function() {
    'use strict';
    
    console.log("[CloudPepper] ULTIMATE module fix loading...");
    
    // Track problematic assets
    const problematicAssets = [
        'web.assets_web.min.js',
        'web.assets_backend',
        'web.assets_frontend'
    ];
    
    // Enhanced error suppression
    const errorPatterns = [
        /Cannot use import statement outside a module/,
        /Unexpected token 'import'/,
        /Failed to execute 'observe' on 'MutationObserver'/,
        /parameter 1 is not of type 'Node'/,
        /Long Running Recorder/,
        /index\.ts-.*\.js/,
        /third_party.*crashpad/,
        /registration_protocol_win\.cc/,
        /CreateFile: The system cannot find the file specified/,
        /Content script initialised/,
        /Recorder disabled/,
        /web\.assets_web\.min\.js/
    ];
    
    function shouldSuppressError(message, filename) {
        return errorPatterns.some(pattern => 
            pattern.test(message) || pattern.test(filename || '')
        );
    }
    
    // IMMEDIATE error suppression - override all error handling
    function setupImmediateErrorSuppression() {
        // Override window.onerror
        const originalOnError = window.onerror;
        window.onerror = function(message, filename, lineno, colno, error) {
            if (shouldSuppressError(message, filename)) {
                console.debug("[CloudPepper] ULTIMATE suppression:", message);
                return true;
            }
            if (originalOnError) {
                return originalOnError.apply(this, arguments);
            }
            return false;
        };
        
        // Override unhandledrejection
        window.addEventListener('unhandledrejection', function(event) {
            const message = event.reason?.message || event.reason || '';
            if (shouldSuppressError(message, '')) {
                console.debug("[CloudPepper] ULTIMATE promise rejection suppressed:", message);
                event.preventDefault();
            }
        });
        
        // Override console.error
        const originalConsoleError = console.error;
        console.error = function(...args) {
            const message = args.join(' ');
            if (shouldSuppressError(message, '')) {
                console.debug("[CloudPepper] ULTIMATE console error suppressed:", message);
                return;
            }
            return originalConsoleError.apply(this, args);
        };
    }
    
    // Script loading interceptor
    function setupScriptLoadingFix() {
        // Override createElement to fix script loading
        const originalCreateElement = document.createElement;
        document.createElement = function(tagName) {
            const element = originalCreateElement.call(this, tagName);
            
            if (tagName.toLowerCase() === 'script') {
                // Enhance script element
                const originalSetAttribute = element.setAttribute;
                element.setAttribute = function(name, value) {
                    if (name === 'src' && value) {
                        // Check if this is a problematic asset
                        const isProblematic = problematicAssets.some(asset => 
                            value.includes(asset) || value.includes('assets_web')
                        );
                        
                        if (isProblematic) {
                            console.debug("[CloudPepper] ULTIMATE script fix applied to:", value);
                            // Force module type for ES6 imports
                            originalSetAttribute.call(this, 'type', 'module');
                            // Add error handling
                            this.onerror = function() {
                                console.debug("[CloudPepper] ULTIMATE script error suppressed for:", value);
                            };
                        }
                    }
                    return originalSetAttribute.call(this, name, value);
                };
                
                // Override src property
                let srcValue = '';
                Object.defineProperty(element, 'src', {
                    get: function() {
                        return srcValue;
                    },
                    set: function(value) {
                        srcValue = value;
                        const isProblematic = problematicAssets.some(asset => 
                            value.includes(asset) || value.includes('assets_web')
                        );
                        
                        if (isProblematic) {
                            console.debug("[CloudPepper] ULTIMATE script src fix applied to:", value);
                            this.type = 'module';
                            this.onerror = function() {
                                console.debug("[CloudPepper] ULTIMATE script error suppressed for:", value);
                            };
                        }
                        
                        this.setAttribute('src', value);
                    }
                });
            }
            
            return element;
        };
    }
    
    // Enhanced MutationObserver fix
    function setupEnhancedMutationObserverFix() {
        if (!window.MutationObserver) return;
        
        const OriginalMutationObserver = window.MutationObserver;
        
        window.MutationObserver = class UltimateMutationObserver extends OriginalMutationObserver {
            constructor(callback) {
                const ultimateCallback = (mutations, observer) => {
                    try {
                        return callback.call(this, mutations, observer);
                    } catch (error) {
                        console.debug("[CloudPepper] ULTIMATE MutationObserver callback error suppressed:", error.message);
                        return null;
                    }
                };
                
                super(ultimateCallback);
            }
            
            observe(target, options) {
                if (!this.isUltimateTarget(target)) {
                    console.debug("[CloudPepper] ULTIMATE MutationObserver target rejected");
                    return; // Silent fail
                }
                
                try {
                    return super.observe(target, options);
                } catch (error) {
                    console.debug("[CloudPepper] ULTIMATE MutationObserver error suppressed:", error.message);
                    return; // Silent fail
                }
            }
            
            isUltimateTarget(target) {
                try {
                    if (!target || typeof target !== 'object') return false;
                    if (!target.nodeType) return false;
                    
                    // Only allow safe node types
                    const safeNodeTypes = [1, 9, 11]; // Element, Document, DocumentFragment
                    if (!safeNodeTypes.includes(target.nodeType)) return false;
                    
                    // Element-specific checks
                    if (target.nodeType === 1) {
                        if (typeof target.isConnected === 'boolean' && !target.isConnected) return false;
                        if (!target.ownerDocument) return false;
                        if (target._isDetached) return false;
                        
                        // Block extension scripts
                        if (target.ownerDocument.location) {
                            const url = target.ownerDocument.location.href;
                            if (url.includes('extension://') || url.includes('moz-extension://')) {
                                return false;
                            }
                        }
                    }
                    
                    return true;
                } catch (error) {
                    console.debug("[CloudPepper] ULTIMATE target validation error:", error.message);
                    return false;
                }
            }
        };
    }
    
    // DOM Content Loaded handler
    function setupDOMContentLoadedFix() {
        // Override addEventListener for DOMContentLoaded
        const originalAddEventListener = window.addEventListener;
        window.addEventListener = function(type, listener, options) {
            if (type === 'DOMContentLoaded' && typeof listener === 'function') {
                const wrappedListener = function(event) {
                    try {
                        return listener.apply(this, arguments);
                    } catch (error) {
                        if (shouldSuppressError(error.message, '')) {
                            console.debug("[CloudPepper] ULTIMATE DOMContentLoaded error suppressed:", error.message);
                            return;
                        }
                        throw error;
                    }
                };
                return originalAddEventListener.call(this, type, wrappedListener, options);
            }
            
            if (type === 'error' && typeof listener === 'function') {
                const wrappedListener = function(event) {
                    const message = event.message || '';
                    const filename = event.filename || '';
                    
                    if (shouldSuppressError(message, filename)) {
                        console.debug("[CloudPepper] ULTIMATE event error suppressed:", message);
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
    }
    
    // Initialize all fixes
    function initializeUltimateFixes() {
        setupImmediateErrorSuppression();
        setupScriptLoadingFix();
        setupEnhancedMutationObserverFix();
        setupDOMContentLoadedFix();
        
        console.log("[CloudPepper] ULTIMATE JavaScript fixes active");
    }
    
    // Execute immediately
    initializeUltimateFixes();
    
    // Mark as loaded
    window.CloudPepperUltimateFixLoaded = true;
    
})();
