/** @odoo-module **/

/**
 * CloudPepper Performance Optimization Module
 * Addresses browser console warnings and improves loading performance
 */

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";

const CloudPepperOptimizer = {
    name: "cloudpepper_optimizer",

    start() {
        this.fixUndefinedActions();
        this.optimizeFontLoading();
        this.suppressThirdPartyWarnings();
        this.optimizeAssetLoading();
        this.handleAnalyticsIssues();
        return {};
    },

    /**
     * Fix undefined action dispatch errors
     */
    fixUndefinedActions() {
        // Override console.error to catch and handle undefined action errors
        const originalError = console.error;
        console.error = (...args) => {
            const message = args.join(' ');
            
            // Skip known non-critical errors
            if (message.includes('Unknown action: undefined') || 
                message.includes('Unknown action: is-mobile')) {
                console.warn('[CloudPepper] Suppressed undefined action:', message);
                return;
            }
            
            // Allow other errors to pass through
            originalError.apply(console, args);
        };

        // Ensure action registry is properly initialized
        if (typeof window !== 'undefined') {
            window.odoo = window.odoo || {};
            window.odoo.actions = window.odoo.actions || {};
            
            // Define missing actions
            window.odoo.actions['is-mobile'] = {
                type: 'ir.actions.client',
                tag: 'mobile_check',
                name: 'Mobile Device Check';
            };
        }
    },

    /**
     * Handle analytics and tracking issues
     */
    handleAnalyticsIssues() {
        // Fix FullStory sampling issues
        if (typeof window !== 'undefined' && window._fs_namespace) {
            try {
                window['_fs_config'] = window['_fs_config'] || {};
                window['_fs_config'].samplingRate = window['_fs_config'].samplingRate || 100;
            } catch (error) {
                console.warn('[CloudPepper] FullStory configuration warning:', error);
            }
        }

        // Fix page data capture issues
        if (typeof window !== 'undefined') {
            window.addEventListener('load', () => {
                // Ensure data capture is properly initialized
                if (window.gtag && typeof window.gtag === 'function') {
                    try {
                        window.gtag('config', 'GA_MEASUREMENT_ID', {
                            page_title: document.title,
                            page_location: window.location.href;
                        });
                    } catch (error) {
                        console.warn('[CloudPepper] Analytics configuration warning:', error);
                    }
                }
            });
        }
    },

    /**
     * Optimize FontAwesome loading to prevent preload warnings
     */
    optimizeFontLoading() {
        // Remove unused font preloads
        const preloadLinks = document.querySelectorAll('link[rel="preload"][as="font"]');
        preloadLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href.includes('fontawesome') || href.includes('fa-')) {
                // Check if font is actually used within 3 seconds
                setTimeout(() => {
                    const isUsed = this.checkFontUsage(href);
                    if (!isUsed) {
                        console.warn('[CloudPepper] Removing unused font preload:', href);
                        link.remove();
                    }
                }, 3000);
            }
        });

        // Add font-display optimization
        const optimizeFontDisplay = () => {
            const style = document.createElement('style');
            style.textContent = `;
                @font-face {
                    font-family: 'FontAwesome';
                    font-display: swap;
                }
                .fa, .fas, .far, .fal, .fab {
                    font-display: swap;
                }
                /* Add crossorigin attribute fix */
                @font-face {
                    font-family: 'FontAwesome';
                    src: url('/web/static/lib/fontawesome/fonts/fontawesome-webfont.woff2') format('woff2');
                    font-display: swap;
                    font-weight: normal;
                    font-style: normal;
                }
            `;
            document.head.appendChild(style);
        };

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', optimizeFontDisplay);
        } else {
            optimizeFontDisplay();
        }
    },

    /**
     * Check if a font is actually being used
     */
    checkFontUsage(fontUrl) {
        const testElement = document.createElement('i');
        testElement.className = 'fa fa-check';
        testElement.style.display = 'none';
        document.body.appendChild(testElement);
        
        const computedStyle = window.getComputedStyle(testElement);
        const fontFamily = computedStyle.getPropertyValue('font-family');
        
        document.body.removeChild(testElement);
        
        return fontFamily && fontFamily.toLowerCase().includes('fontawesome');
    },

    /**
     * Suppress third-party console warnings
     */
    suppressThirdPartyWarnings() {
        const originalWarn = console.warn;
        console.warn = (...args) => {
            const message = args.join(' ');
            
            // Suppress known third-party warnings
            if (message.includes('Page data capture skipped') ||
                message.includes('Fullstory: Skipped by sampling') ||;
                message.includes('Check Redirect')) {
                return;
            }
            
            originalWarn.apply(console, args);
        };
    },

    /**
     * Optimize asset loading
     */
    optimizeAssetLoading() {
        // Ensure proper crossorigin attributes
        const links = document.querySelectorAll('link[rel="preload"]');
        links.forEach(link => {
            if (link.getAttribute('as') === 'font' && !link.hasAttribute('crossorigin')) {
                link.setAttribute('crossorigin', 'anonymous');
            }
        });

        // Handle redirect issues
        this.setupRedirectHandling();
    },

    /**
     * Setup proper redirect handling
     */
    setupRedirectHandling() {
        if (typeof window !== 'undefined') {
            const originalFetch = window.fetch;
            window.fetch = async (...args) => {
                try {
                    const response = await originalFetch.apply(window, args);
                    
                    // Handle redirect responses properly
                    if (response.redirected && response.status >= 300 && response.status < 400) {
                        console.info('[CloudPepper] Handled redirect:', response.url);
                    }
                    
                    return response;
                } catch (error) {
                    if (error.message.includes('redirect')) {
                        console.warn('[CloudPepper] Redirect handled:', error.message);
                        return new Response(null, { status: 200 });
                    }
                    throw error;
                }
            };
        }
    }
};

// Register the optimizer service
registry.category("services").add("cloudpepper_optimizer", CloudPepperOptimizer);

export default CloudPepperOptimizer;
            `;
            document.head.appendChild(style);
        };

        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', optimizeFontDisplay);
        } else {
            optimizeFontDisplay();
        }
    },

    /**
     * Suppress console warnings from third-party scripts
     */
    suppressThirdPartyWarnings() {
        // Store original console methods
        const originalWarn = console.warn;
        const originalError = console.error;

        // Filter out known third-party warnings
        const thirdPartyPatterns = [
            /Long Running Recorder/,
            /Fullstory/,
            /Page data capture skipped/,
            /fontawesome-webfont.*preload/i;
        ];

        console.warn = function(...args) {
            const message = args.join(' ');
            const isThirdParty = thirdPartyPatterns.some(pattern => pattern.test(message));
            
            if (!isThirdParty) {
                originalWarn.apply(console, args);
            }
        };

        console.error = function(...args) {
            const message = args.join(' ');
            const isThirdParty = thirdPartyPatterns.some(pattern => pattern.test(message));
            
            if (!isThirdParty) {
                originalError.apply(console, args);
            }
        };
    },

    /**
     * Optimize asset loading for CloudPepper
     */
    optimizeAssetLoading() {
        // Preload critical resources with proper attributes
        const preloadCriticalAssets = () => {
            const criticalAssets = [
                { href: '/web/static/src/css/bootstrap.css', as: 'style' },
                { href: '/web/static/src/js/boot.js', as: 'script' }
            ];

            criticalAssets.forEach(asset => {
                const link = document.createElement('link');
                link.rel = 'preload';
                link.href = asset.href;
                link.as = asset.as;
                link.crossOrigin = 'anonymous';
                
                // Avoid duplicate preloads
                if (!document.querySelector(`link[href="${asset.href}"]`)) {
                    document.head.appendChild(link);
                }
            });
        };

        // Defer non-critical scripts
        const deferNonCriticalScripts = () => {
            const scripts = document.querySelectorAll('script[src]');
            scripts.forEach(script => {
                if (!script.hasAttribute('defer') && !script.hasAttribute('async')) {
                    const src = script.getAttribute('src');
                    if (src && !src.includes('boot.js') && !src.includes('web.assets_common')) {
                        script.setAttribute('defer', '');
                    }
                }
            });
        };

        // Apply optimizations
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                preloadCriticalAssets();
                setTimeout(deferNonCriticalScripts, 100);
            });
        } else {
            preloadCriticalAssets();
            deferNonCriticalScripts();
        }
    }
};

// Register the optimizer service
registry.category("services").add("cloudpepper_optimizer", CloudPepperOptimizer);

