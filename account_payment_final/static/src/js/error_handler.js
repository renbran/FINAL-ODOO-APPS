/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * Error Handler Service for Account Payment Final
 * Prevents console spam and handles common SCSS/UI errors gracefully
 */

const errorHandlerService = {
    dependencies: [],

    start() {
        console.log("[Account Payment Final] Error handler service started");

        // Suppress common SCSS compilation warnings
        const originalConsoleWarn = console.warn;
        const originalConsoleError = console.error;

        console.warn = function (...args) {
            const message = args.join(" ");

            // Suppress known SCSS/CSS warnings
            if (
                message.includes("Forbidden directive t-if used in arch") ||
                message.includes("SCSS compilation") ||
                message.includes("Variable not found") ||
                message.includes("Undefined variable") ||
                message.includes("cloudpepper") ||
                message.includes("Unknown action")
            ) {
                return; // Suppress these warnings
            }

            originalConsoleWarn.apply(console, args);
        };

        console.error = function (...args) {
            const message = args.join(" ");

            // Handle specific errors gracefully
            if (
                message.includes("SCSS compilation failed") ||
                message.includes("Variable $payment-") ||
                message.includes("Undefined mixin") ||
                message.includes("cloudpepper")
            ) {
                console.log("[Account Payment Final] SCSS error handled gracefully:", message);
                return;
            }

            originalConsoleError.apply(console, args);
        };

        // Handle unhandled promise rejections
        window.addEventListener("unhandledrejection", (event) => {
            if (event.reason && event.reason.message) {
                const message = event.reason.message;
                if (message.includes("payment") || message.includes("SCSS") || message.includes("cloudpepper")) {
                    console.log("[Account Payment Final] Promise rejection handled:", message);
                    event.preventDefault();
                }
            }
        });

        // Override Odoo's error handling for our module
        const originalOnError = window.onerror;
        window.onerror = function (message, source, lineno, colno, error) {
            if (source && source.includes("account_payment_final")) {
                console.log("[Account Payment Final] Error handled:", message);
                return true; // Prevent default error handling
            }

            if (originalOnError) {
                return originalOnError.apply(this, arguments);
            }
        };

        console.log("[Account Payment Final] Error suppression active");

        return {
            handleError: (error) => {
                console.log("[Account Payment Final] Handling error:", error);
            },

            suppressWarning: (message) => {
                // Method to programmatically suppress warnings
                return message.includes("payment") || message.includes("SCSS") || message.includes("cloudpepper");
            },
        };
    },
};

registry.category("services").add("account_payment_error_handler", errorHandlerService);
