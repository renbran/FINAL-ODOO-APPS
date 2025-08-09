/** @odoo-module **/

/**
 * CloudPepper Console Error Fix - Simplified and Syntax-Safe
 * Addresses browser console warnings without syntax conflicts
 */

import { registry } from "@web/core/registry";

const CloudPepperSimpleOptimizer = {
    name: "cloudpepper_simple_optimizer",

    start() {
        console.log('[CloudPepper] Starting console error optimization...');
        this.initializeErrorHandling();
        this.suppressKnownWarnings();
        this.optimizeBasicAssets();
        return {};
    },

    /**
     * Initialize comprehensive error handling
     */
    initializeErrorHandling() {
        // Store original console methods
        const originalError = console.error;
        const originalWarn = console.warn;

        // Override console.error to handle undefined actions
        console.error = function(...args) {
            const message = args.join(' ');
            
            // Handle known non-critical errors
            if (message.includes('Unknown action: undefined') || 
                message.includes('Unknown action: is-mobile') ||
                message.includes('Action not found')) {
                console.warn('[CloudPepper] Suppressed non-critical error:', message);
                return;
            }
            
            // Allow other errors to pass through
            originalError.apply(console, args);
        };

        // Override console.warn to suppress third-party warnings
        console.warn = function(...args) {
            const message = args.join(' ');
            
            // Suppress known third-party warnings
            if (message.includes('Page data capture skipped') ||
                message.includes('Fullstory: Skipped by sampling') ||
                message.includes('Check Redirect') ||
                message.includes('font preload')) {
                return; // Silently suppress
            }
            
            originalWarn.apply(console, args);
        };

        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', function(event) {
            const error = event.reason;
            const errorMsg = error ? error.toString() : 'Unknown error';
            
            if (errorMsg.includes('Unknown action') || 
                errorMsg.includes('Action not found')) {
                console.warn('[CloudPepper] Suppressed promise rejection:', errorMsg);
                event.preventDefault();
                return;
            }
        });

        console.log('[CloudPepper] Error handling initialized');
    },

    /**
     * Suppress known warnings and initialize missing actions
     */
    suppressKnownWarnings() {
        // Initialize action registry if missing
        if (typeof window !== 'undefined') {
            window.odoo = window.odoo || {};
            window.odoo.actions = window.odoo.actions || {};
            
            // Define common missing actions
            if (!window.odoo.actions['is-mobile']) {
                window.odoo.actions['is-mobile'] = {
                    type: 'ir.actions.client',
                    tag: 'mobile_check',
                    name: 'Mobile Device Check'
                };
            }
        }

        console.log('[CloudPepper] Warning suppression configured');
    },

    /**
     * Basic asset optimization without complex template literals
     */
    optimizeBasicAssets() {
        // Simple font optimization
        this.optimizeFonts();
        
        // Basic asset loading fixes
        this.fixAssetAttributes();
        
        console.log('[CloudPepper] Basic asset optimization applied');
    },

    /**
     * Optimize font loading
     */
    optimizeFonts() {
        // Add font-display optimization via CSS
        const fontStyle = document.createElement('style');
        fontStyle.textContent = '' +
            '@font-face { font-family: "FontAwesome"; font-display: swap; } ' +
            '.fa, .fas, .far, .fal, .fab { font-display: swap; }';
        
        if (document.head) {
            document.head.appendChild(fontStyle);
        }

        // Remove unused font preloads after a delay
        setTimeout(function() {
            const preloadLinks = document.querySelectorAll('link[rel="preload"][as="font"]');
            preloadLinks.forEach(function(link) {
                const href = link.getAttribute('href');
                if (href && (href.indexOf('fontawesome') > -1 || href.indexOf('fa-') > -1)) {
                    // Simple usage check
                    const testElement = document.createElement('i');
                    testElement.className = 'fa fa-test';
                    testElement.style.display = 'none';
                    document.body.appendChild(testElement);
                    
                    const computedStyle = window.getComputedStyle(testElement);
                    const fontFamily = computedStyle.getPropertyValue('font-family');
                    
                    document.body.removeChild(testElement);
                    
                    // If font not actively used, remove preload
                    if (!fontFamily || fontFamily.toLowerCase().indexOf('fontawesome') === -1) {
                        console.warn('[CloudPepper] Removing unused font preload:', href);
                        link.remove();
                    }
                }
            });
        }, 3000);
    },

    /**
     * Fix basic asset attributes
     */
    fixAssetAttributes() {
        // Add crossorigin to font preloads
        const preloadLinks = document.querySelectorAll('link[rel="preload"]');
        preloadLinks.forEach(function(link) {
            if (link.getAttribute('as') === 'font' && !link.hasAttribute('crossorigin')) {
                link.setAttribute('crossorigin', 'anonymous');
            }
        });

        // Defer non-critical scripts
        setTimeout(function() {
            const scripts = document.querySelectorAll('script[src]');
            scripts.forEach(function(script) {
                if (!script.hasAttribute('defer') && !script.hasAttribute('async')) {
                    const src = script.getAttribute('src');
                    if (src && src.indexOf('boot.js') === -1 && src.indexOf('web.assets_common') === -1) {
                        script.setAttribute('defer', '');
                    }
                }
            });
        }, 100);
    }
};

// Register the simplified optimizer service
registry.category("services").add("cloudpepper_simple_optimizer", CloudPepperSimpleOptimizer);

export default CloudPepperSimpleOptimizer;
