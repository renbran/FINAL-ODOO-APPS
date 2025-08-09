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
        this.optimizeFontLoading();
        this.suppressThirdPartyWarnings();
        this.optimizeAssetLoading();
        return {};
    },

    /**
     * Optimize FontAwesome loading to prevent preload warnings
     */
    optimizeFontLoading() {
        // Check if FontAwesome is loaded
        const checkFontAwesome = () => {
            const testElement = document.createElement('i');
            testElement.className = 'fa fa-check';
            testElement.style.display = 'none';
            document.body.appendChild(testElement);
            
            const computedStyle = window.getComputedStyle(testElement);
            const fontFamily = computedStyle.getPropertyValue('font-family');
            
            document.body.removeChild(testElement);
            
            return fontFamily && fontFamily.toLowerCase().includes('fontawesome');
        };

        // Add font-display optimization
        const optimizeFontDisplay = () => {
            const style = document.createElement('style');
            style.textContent = `
                @font-face {
                    font-family: 'FontAwesome';
                    font-display: swap;
                }
                .fa, .fas, .far, .fal, .fab {
                    font-display: swap;
                }
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
            /fontawesome-webfont.*preload/i
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
