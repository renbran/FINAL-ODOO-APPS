/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Payment Approval Widget Component
 * 
 * OWL Component for displaying and managing payment approval workflow
 * Compatible with Odoo 17 OWL framework patterns
 */
export class PaymentApprovalWidget extends Component {
    static template = "account_payment_final.PaymentApprovalWidget";
    static props = {
        readonly: { type: Boolean, optional: true },
        record: Object,
        update: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.user = useService("user");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        
        this.state = useState({
            currentStage: null,
            approvalStages: [],
            canApprove: false,
            canReject: false,
            isLoading: false,
        });

        onWillStart(async () => {
            await this.loadApprovalData();
        });
    }

    /**
     * Load approval workflow data from the backend
     */
    async loadApprovalData() {
        if (!this.props.record.resId) return;

        try {
            const result = await this.orm.call(
                "account.payment",
                "get_approval_workflow_data",
                [this.props.record.resId]
            );

            this.state.approvalStages = result.stages || [];
            this.state.currentStage = result.current_stage;
            this.state.canApprove = result.can_approve || false;
            this.state.canReject = result.can_reject || false;
        } catch (error) {
            console.error("Failed to load approval data:", error);
            this.notification.add("Failed to load approval workflow data", {
                type: "danger",
            });
        }
    }

    /**
     * Get CSS class for current payment state
     */
    getStateClass() {
        const state = this.props.record.data.state;
        return `badge-${state}`;
    }

    /**
     * Get human-readable label for current state
     */
    getStateLabel() {
        const stateLabels = {
            draft: "Draft",
            review: "Under Review",
            approve: "Approved",
            authorize: "Authorized",
            post: "Posted",
            cancel: "Cancelled",
            reject: "Rejected",
        };
        
        const state = this.props.record.data.state;
        return stateLabels[state] || state.charAt(0).toUpperCase() + state.slice(1);
    }

    /**
     * Get approval stages for display
     */
    getApprovalStages() {
        return this.state.approvalStages;
    }

    /**
     * Get CSS class for approval stage
     */
    getStageClass(stage) {
        let classes = ["o_stage"];
        
        if (stage.is_current) {
            classes.push("o_stage_current");
        } else if (stage.is_completed) {
            classes.push("o_stage_completed");
        } else {
            classes.push("o_stage_pending");
        }
        
        return classes.join(" ");
    }

    /**
     * Check if current user can approve
     */
    canApprove() {
        return this.state.canApprove && !this.props.readonly;
    }

    /**
     * Check if current user can reject
     */
    canReject() {
        return this.state.canReject && !this.props.readonly;
    }

    /**
     * Handle approval action
     */
    async onApprove() {
        if (this.state.isLoading) return;

        this.state.isLoading = true;
        
        try {
            const result = await this.orm.call(
                "account.payment",
                "approve_payment",
                [this.props.record.resId]
            );

            if (result.success) {
                this.notification.add(result.message || "Payment approved successfully", {
                    type: "success",
                });
                
                // Refresh the record
                await this.props.update();
                await this.loadApprovalData();
            } else {
                this.notification.add(result.message || "Failed to approve payment", {
                    type: "danger",
                });
            }
        } catch (error) {
            console.error("Approval failed:", error);
            this.notification.add("An error occurred while approving the payment", {
                type: "danger",
            });
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Handle rejection action
     */
    async onReject() {
        if (this.state.isLoading) return;

        // Show confirmation dialog
        this.dialog.add("web.ConfirmationDialog", {
            title: "Reject Payment",
            body: "Are you sure you want to reject this payment? This action cannot be undone.",
            confirmLabel: "Reject",
            cancelLabel: "Cancel",
            confirm: async () => {
                await this._performReject();
            },
        });
    }

    /**
     * Perform the actual rejection
     */
    async _performReject() {
        this.state.isLoading = true;
        
        try {
            const result = await this.orm.call(
                "account.payment",
                "reject_payment",
                [this.props.record.resId]
            );

            if (result.success) {
                this.notification.add(result.message || "Payment rejected successfully", {
                    type: "warning",
                });
                
                // Refresh the record
                await this.props.update();
                await this.loadApprovalData();
            } else {
                this.notification.add(result.message || "Failed to reject payment", {
                    type: "danger",
                });
            }
        } catch (error) {
            console.error("Rejection failed:", error);
            this.notification.add("An error occurred while rejecting the payment", {
                type: "danger",
            });
        } finally {
            this.state.isLoading = false;
        }
    }
}

// Register the component for use in form views
registry.category("fields").add("payment_approval_widget", PaymentApprovalWidget);
