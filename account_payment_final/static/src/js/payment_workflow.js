/** @odoo-module **/

/**
 * Payment Workflow Helper Module
 * 
 * Utility functions for payment workflow management
 * Compatible with Odoo 17 OWL framework
 */

import { registry } from "@web/core/registry";

export const PaymentWorkflowHelper = {
    /**
     * Get workflow stage configuration
     */
    getStageConfig() {
        return {
            draft: {
                name: "Draft",
                icon: "fa-edit",
                color: "secondary"
            },
            under_review: {
                name: "Under Review", 
                icon: "fa-search",
                color: "info"
            },
            for_approval: {
                name: "For Approval",
                icon: "fa-check",
                color: "warning"
            },
            for_authorization: {
                name: "For Authorization",
                icon: "fa-key",
                color: "warning"
            },
            approved: {
                name: "Approved",
                icon: "fa-check-circle",
                color: "success"
            },
            posted: {
                name: "Posted",
                icon: "fa-check-circle",
                color: "success"
            },
            rejected: {
                name: "Rejected",
                icon: "fa-times",
                color: "danger"
            }
        };
    },

    /**
     * Format currency amount for display
     */
    formatCurrency(amount, currency) {
        if (!amount || !currency) return "0.00";
        
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency.name || 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    },

    /**
     * Get next stage in workflow
     */
    getNextStage(currentStage, paymentType) {
        const workflows = {
            outbound: ['draft', 'under_review', 'for_approval', 'for_authorization', 'approved', 'posted'],
            inbound: ['draft', 'under_review', 'for_approval', 'approved', 'posted']
        };
        
        const workflow = workflows[paymentType] || workflows.outbound;
        const currentIndex = workflow.indexOf(currentStage);
        
        return currentIndex < workflow.length - 1 ? workflow[currentIndex + 1] : null;
    }
};

// Register the helper for use in other components
registry.category("services").add("payment_workflow_helper", {
    start() {
        return PaymentWorkflowHelper;
    }
});