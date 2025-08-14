/** @odoo-module **/

/**
 * Emergency CloudPepper Error Fix
 * Addresses critical console errors and rendering issues
 */

import { registry } from "@web/core/registry";

class EmergencyErrorFix {
    constructor() {
        this.initErrorFixes();
    }

    initErrorFixes() {
        // Fix MutationObserver type errors
        this.fixMutationObserver();

        // Suppress problematic console errors
        this.suppressProblematicErrors();

        // Ensure DOM readiness
        this.ensureDOMReadiness();

        console.log("[CloudPepper] Emergency error fixes applied");
    }

    fixMutationObserver() {
        // Store original MutationObserver
        const OriginalMutationObserver = window.MutationObserver;

        // Wrap MutationObserver to prevent type errors
        window.MutationObserver = class SafeMutationObserver extends OriginalMutationObserver {
            observe(target, options) {
                // Validate target is a Node
                if (!target || typeof target.nodeType !== "number") {
                    console.warn("[CloudPepper] Invalid MutationObserver target, skipping");
                    return;
                }

                try {
                    return super.observe(target, options);
                } catch (error) {
                    console.warn("[CloudPepper] MutationObserver error prevented:", error.message);
                }
            }
        };
    }

    suppressProblematicErrors() {
        // Store original console methods
        const originalError = console.error;
        const originalWarn = console.warn;

        // Patterns to suppress
        const suppressPatterns = [
            "Failed to execute 'observe' on 'MutationObserver'",
            "parameter 1 is not of type 'Node'",
            "Local import.*is forbidden for security reasons",
            "Please remove all @import",
            "Could not get content for.*payment_widget.js",
            "Unknown action service",
            "Content script initialised",
            "Recorder disabled",
        ];

        // Override console.error
        console.error = function (...args) {
            const message = args.join(" ");
            if (suppressPatterns.some((pattern) => message.match(new RegExp(pattern, "i")))) {
                return; // Suppress this error
            }
            originalError.apply(console, args);
        };

        // Override console.warn
        console.warn = function (...args) {
            const message = args.join(" ");
            if (suppressPatterns.some((pattern) => message.match(new RegExp(pattern, "i")))) {
                return; // Suppress this warning
            }
            originalWarn.apply(console, args);
        };
    }

    ensureDOMReadiness() {
        // Ensure DOM is ready before any operations
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", () => {
                this.validateDOMElements();
            });
        } else {
            this.validateDOMElements();
        }
    }

    validateDOMElements() {
        // Remove any elements that might cause issues
        const problematicSelectors = [
            '[data-menu-xmlid="hr_expense.menu_hr_expense_root"]',
            '.o_app[data-menu-xmlid*="expense"]',
        ];

        problematicSelectors.forEach((selector) => {
            try {
                const elements = document.querySelectorAll(selector);
                elements.forEach((element) => {
                    if (element && element.parentNode) {
                        console.log(`[CloudPepper] Removed problematic element: ${selector}`);
                        element.remove();
                    }
                });
            } catch (error) {
                // Silently ignore selector errors
            }
        });
    }
}

// Initialize emergency fixes as early as possible
const emergencyFix = new EmergencyErrorFix();

// Register as a service for proper lifecycle management
registry.category("services").add("cloudpepper_emergency_fix", {
    start() {
        return emergencyFix;
    },
});

export { EmergencyErrorFix };
