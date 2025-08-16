/** @odoo-module **/

import { registry } from "@web/core/registry";
import { reactive } from "@odoo/owl";

/**
 * Payment Workflow Service
 * 
 * Centralized service for managing payment workflow operations
 * Provides reactive state management and API abstractions
 */
export const paymentWorkflowService = {
    dependencies: ["orm", "user", "notification"],
    
    start(env, { orm, user, notification }) {
        const state = reactive({
            currentPayment: null,
            workflowStages: [],
            userPermissions: {},
            isLoading: false,
        });

        /**
         * Get workflow stage configuration
         */
        const getStageConfig = () => ({
            draft: {
                name: "Draft",
                icon: "fa-edit",
                color: "secondary",
                description: "Payment is being prepared"
            },
            under_review: {
                name: "Under Review",
                icon: "fa-search",
                color: "info",
                description: "Payment is being reviewed"
            },
            for_approval: {
                name: "For Approval",
                icon: "fa-check",
                color: "warning",
                description: "Waiting for approval"
            },
            for_authorization: {
                name: "For Authorization",
                icon: "fa-key",
                color: "warning",
                description: "Waiting for final authorization"
            },
            approved: {
                name: "Approved",
                icon: "fa-check-circle",
                color: "success",
                description: "Payment has been approved"
            },
            posted: {
                name: "Posted",
                icon: "fa-check-circle",
                color: "success",
                description: "Payment has been posted"
            },
            cancelled: {
                name: "Cancelled",
                icon: "fa-times-circle",
                color: "danger",
                description: "Payment has been cancelled"
            }
        });

        /**
         * Load payment workflow data
         */
        const loadPaymentWorkflow = async (paymentId) => {
            if (!paymentId) return null;
            
            state.isLoading = true;
            try {
                const result = await orm.call(;
                    "account.payment",
                    "get_workflow_data",
                    [paymentId]
                );
                
                state.currentPayment = result.payment;
                state.workflowStages = result.stages;
                state.userPermissions = result.permissions;
                
                return result;
            } catch (error) {
                notification.add("Failed to load payment workflow", {
                    type: "danger"
                });
                throw error;
            } finally {
                state.isLoading = false;
            }
        };

        /**
         * Execute workflow action
         */
        const executeWorkflowAction = async (paymentId, action, data = {}) => {
            try {
                const result = await orm.call(;
                    "account.payment",
                    action,
                    [paymentId],
                    data
                );
                
                if (result.success) {
                    notification.add(result.message || "Action completed successfully", {
                        type: "success"
                    });
                    
                    // Reload workflow data
                    await loadPaymentWorkflow(paymentId);
                } else {
                    notification.add(result.message || "Action failed", {
                        type: "danger"
                    });
                }
                
                return result;
            } catch (error) {
                notification.add("Failed to execute action: " + error.message, {
                    type: "danger"
                });
                throw error;
            }
        };

        /**
         * Check user permissions for payment
         */
        const checkPermissions = async (paymentId) => {
            try {
                const result = await orm.call(;
                    "account.payment",
                    "check_user_permissions",
                    [paymentId]
                );
                
                state.userPermissions = result;
                return result;
            } catch (error) {
                console.error("Permission check failed:", error);
                return {};
            }
        };

        /**
         * Generate QR code for payment
         */
        const generateQRCode = async (paymentId) => {
            try {
                const result = await orm.call(;
                    "account.payment",
                    "generate_qr_code",
                    [paymentId]
                );
                
                if (result.success) {
                    return result.qr_code;
                } else {
                    notification.add(result.message || "Failed to generate QR code", {
                        type: "danger"
                    });
                    return null;
                }
            } catch (error) {
                notification.add("QR code generation failed", {
                    type: "danger"
                });
                throw error;
            }
        };

        /**
         * Get formatted stage data for UI display
         */
        const getFormattedStages = () => {
            const stageConfig = getStageConfig();
            return state.workflowStages.map(stage => ({
                ...stage,
                ...stageConfig[stage.state] || {},
                status: stage.is_completed ? 'completed' : 
                       stage.is_current ? 'current' : 'pending'
            }));
        };

        /**
         * Public API
         */
        return {
            state,
            getStageConfig,
            loadPaymentWorkflow,
            executeWorkflowAction,
            checkPermissions,
            generateQRCode,
            getFormattedStages,
            
            // Utility methods
            isUserAuthorized: (action) => state.userPermissions[action] || false,
            getCurrentStage: () => state.workflowStages.find(s => s.is_current),
            getNextStage: () => state.workflowStages.find(s => s.is_next),
        };
    },
};

registry.category("services").add("paymentWorkflow", paymentWorkflowService);
