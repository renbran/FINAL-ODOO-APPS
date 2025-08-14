/** @odoo-module **/

/**
 * Action Handler for Unknown Actions
 * Handles 'is-mobile' and other undefined actions gracefully
 */

import { registry } from "@web/core/registry";

export class UnknownActionHandler {
    setup() {
        // Register handlers for problematic actions
        this.setupMobileActionHandler();
        this.setupUndefinedActionHandler();
    }

    setupMobileActionHandler() {
        // Handle 'is-mobile' action
        const mobileHandler = {
            type: 'ir.actions.client',
            tag: 'mobile_check',
            
            action: function() {
                // Simple mobile detection
                const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
                console.log('[CloudPepper] Mobile check result:', isMobile);
                return { is_mobile: isMobile };
            }
        };

        // Try to register the action if registry is available
        try {
            if (registry && registry.category) {
                registry.category("actions").add("is-mobile", mobileHandler);
            }
        } catch (e) {
            console.debug('[CloudPepper] Could not register mobile action:', e.message);
        }
    }

    setupUndefinedActionHandler() {
        // Create a default handler for undefined actions
        const undefinedHandler = {
            type: 'ir.actions.client',
            tag: 'undefined_action',
            
            action: function() {
                console.warn('[CloudPepper] Undefined action called, returning empty result');
                return {};
            }
        };

        // Try to register the action if registry is available
        try {
            if (registry && registry.category) {
                registry.category("actions").add("undefined", undefinedHandler);
            }
        } catch (e) {
            console.debug('[CloudPepper] Could not register undefined action handler:', e.message);
        }
    }
}

// Initialize the action handler
const actionHandler = new UnknownActionHandler();
actionHandler.setup();

// Also register as a service
const unknownActionService = {
    name: "unknown_action_service",
    dependencies: [],
    
    start() {
        console.log('[CloudPepper] Unknown action service started');
        return actionHandler;
    }
};

registry.category("services").add("unknown_action_service", unknownActionService);
