/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUpdateProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * Modernized Payment Approval Widget Component
 * 
 * Enhanced OWL Component using service-based architecture
 * Improved performance, error handling, and accessibility
 */
export class PaymentApprovalWidgetModern extends Component {
    static template = "account_payment_final.PaymentApprovalWidgetModern";
    static props = {
        readonly: { type: Boolean, optional: true },
        record: Object,
        update: Function,
    };

    setup() {
        // Modern service injection
        this.paymentWorkflow = useService("paymentWorkflow");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this.action = useService("action");
        
        // Reactive state
        this.state = useState({
            isLoading: false,
            hasError: false,
            errorMessage: '',
            showActions: !this.props.readonly,
        });

        // Lifecycle hooks
        onWillStart(async () => {
            await this.loadWorkflowData();
        });

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.record.resId !== this.props.record.resId) {
                await this.loadWorkflowData(nextProps.record.resId);
            }
        });

        onMounted(() => {
            this.setupAccessibility();
        });
    }

    /**
     * Load workflow data using the service
     */
    async loadWorkflowData(paymentId = null) {
        const id = paymentId || this.props.record.resId;
        if (!id) return;

        this.state.isLoading = true;
        this.state.hasError = false;

        try {
            await this.paymentWorkflow.loadPaymentWorkflow(id);
        } catch (error) {
            this.state.hasError = true;
            this.state.errorMessage = error.message || "Failed to load workflow data";
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Get formatted stages for display
     */
    get formattedStages() {
        return this.paymentWorkflow.getFormattedStages();
    }

    /**
     * Get current stage information
     */
    get currentStage() {
        return this.paymentWorkflow.getCurrentStage();
    }

    /**
     * Check if user can perform specific action
     */
    canPerformAction(action) {
        return this.paymentWorkflow.isUserAuthorized(action);
    }

    /**
     * Handle approval action
     */
    async onApprove() {
        if (!this.canPerformAction('approve')) {
            this.notification.add(_t("You don't have permission to approve this payment"), {
                type: "warning"
            });
            return;
        }

        try {
            await this.paymentWorkflow.executeWorkflowAction(
                this.props.record.resId,
                'action_approve_payment'
            );
            
            // Update parent record
            if (this.props.update) {
                await this.props.update();
            }
        } catch (error) {
            console.error("Approval failed:", error);
        }
    }

    /**
     * Handle rejection action
     */
    async onReject() {
        if (!this.canPerformAction('reject')) {
            this.notification.add(_t("You don't have permission to reject this payment"), {
                type: "warning"
            });
            return;
        }

        // Show rejection reason dialog
        this.dialog.add(RejectReasonDialog, {
            title: _t("Reject Payment"),
            onConfirm: async (reason) => {
                try {
                    await this.paymentWorkflow.executeWorkflowAction(
                        this.props.record.resId,
                        'action_reject_payment',
                        { rejection_reason: reason }
                    );
                    
                    if (this.props.update) {
                        await this.props.update();
                    }
                } catch (error) {
                    console.error("Rejection failed:", error);
                }
            }
        });
    }

    /**
     * Handle submit for review action
     */
    async onSubmitForReview() {
        if (!this.canPerformAction('submit')) {
            this.notification.add(_t("You don't have permission to submit this payment"), {
                type: "warning"
            });
            return;
        }

        try {
            await this.paymentWorkflow.executeWorkflowAction(
                this.props.record.resId,
                'action_submit_for_review'
            );
            
            if (this.props.update) {
                await this.props.update();
            }
        } catch (error) {
            console.error("Submission failed:", error);
        }
    }

    /**
     * Handle authorization action
     */
    async onAuthorize() {
        if (!this.canPerformAction('authorize')) {
            this.notification.add(_t("You don't have permission to authorize this payment"), {
                type: "warning"
            });
            return;
        }

        try {
            await this.paymentWorkflow.executeWorkflowAction(
                this.props.record.resId,
                'action_authorize_payment'
            );
            
            if (this.props.update) {
                await this.props.update();
            }
        } catch (error) {
            console.error("Authorization failed:", error);
        }
    }

    /**
     * Setup accessibility features
     */
    setupAccessibility() {
        const container = this.el;
        if (!container) return;

        // Add ARIA labels
        container.setAttribute('role', 'region');
        container.setAttribute('aria-label', 'Payment Approval Workflow');

        // Add keyboard navigation
        const buttons = container.querySelectorAll('button');
        buttons.forEach((button, index) => {
            button.setAttribute('tabindex', index === 0 ? '0' : '-1');
            button.addEventListener('keydown', this.handleKeyboardNavigation.bind(this));
        });
    }

    /**
     * Handle keyboard navigation
     */
    handleKeyboardNavigation(event) {
        const buttons = Array.from(this.el.querySelectorAll('button'));
        const currentIndex = buttons.indexOf(event.target);

        switch (event.key) {
            case 'ArrowRight':
            case 'ArrowDown':
                event.preventDefault();
                const nextIndex = (currentIndex + 1) % buttons.length;
                buttons[nextIndex].focus();
                break;
            case 'ArrowLeft':
            case 'ArrowUp':
                event.preventDefault();
                const prevIndex = currentIndex === 0 ? buttons.length - 1 : currentIndex - 1;
                buttons[prevIndex].focus();
                break;
            case 'Home':
                event.preventDefault();
                buttons[0].focus();
                break;
            case 'End':
                event.preventDefault();
                buttons[buttons.length - 1].focus();
                break;
        }
    }

    /**
     * Get stage CSS classes
     */
    getStageClasses(stage) {
        const baseClasses = ['workflow-stage', 'd-flex', 'align-items-center', 'mb-2'];
        
        if (stage.status === 'completed') {
            baseClasses.push('stage-completed');
        } else if (stage.status === 'current') {
            baseClasses.push('stage-current');
        } else {
            baseClasses.push('stage-pending');
        }
        
        return baseClasses.join(' ');
    }

    /**
     * Get stage icon classes
     */
    getStageIconClasses(stage) {
        const baseClasses = ['stage-icon', 'me-3'];
        baseClasses.push(`text-${stage.color || 'secondary'}`);
        
        if (stage.status === 'completed') {
            baseClasses.push('completed');
        } else if (stage.status === 'current') {
            baseClasses.push('current', 'pulse');
        }
        
        return baseClasses.join(' ');
    }
}

/**
 * Rejection Reason Dialog Component
 */
class RejectReasonDialog extends Component {
    static template = "account_payment_final.RejectReasonDialog";
    static props = {
        title: String,
        onConfirm: Function,
        close: Function,
    };

    setup() {
        this.state = useState({
            reason: '',
            isValid: false,
        });
    }

    onReasonChange(event) {
        this.state.reason = event.target.value;
        this.state.isValid = this.state.reason.trim().length >= 10;
    }

    onConfirm() {
        if (!this.state.isValid) {
            return;
        }
        
        this.props.onConfirm(this.state.reason);
        this.props.close();
    }

    onCancel() {
        this.props.close();
    }
}

// Register the modernized component
registry.category("fields").add("payment_approval_widget_modern", PaymentApprovalWidgetModern);
