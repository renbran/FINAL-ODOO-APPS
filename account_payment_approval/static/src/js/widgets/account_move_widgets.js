/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * Approval Timeline Widget
 * Displays payment approval workflow progress with timeline visualization
 */
export class ApprovalTimelineWidget extends Component {
    static template = "account_payment_approval.ApprovalTimelineTemplate";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            timelineData: [],
            isLoading: true,
            selectedPayment: null,
        });

        onWillStart(this.loadTimelineData);
    }

    async loadTimelineData() {
        this.state.isLoading = true;
        try {
            const timelineData = this.props.record.data[this.props.name];
            this.state.timelineData = timelineData || [];
        } catch (error) {
            console.error("Error loading timeline data:", error);
            this.notification.add(_t("Failed to load approval timeline data"), { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Get CSS class for timeline step based on completion status
     */
    getStepClass(step) {
        if (step.completed) return "step-completed";
        if (step.current) return "step-current";
        return "step-pending";
    }

    /**
     * Get icon class for step state
     */
    getStepIcon(state) {
        const iconMap = {
            draft: "fa-edit",
            submitted: "fa-paper-plane",
            under_review: "fa-search",
            approved: "fa-check",
            authorized: "fa-key",
            posted: "fa-check-circle",
            rejected: "fa-times",
            cancelled: "fa-ban",
        };
        return iconMap[state] || "fa-circle";
    }

    /**
     * Get display name for state
     */
    getStateDisplayName(state) {
        const nameMap = {
            draft: "Draft",
            submitted: "Submitted",
            under_review: "Review",
            approved: "Approved",
            authorized: "Authorized",
            posted: "Posted",
            rejected: "Rejected",
            cancelled: "Cancelled",
        };
        return nameMap[state] || state;
    }

    /**
     * Handle viewing specific payment
     */
    async onViewPayment(paymentId) {
        try {
            await this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "account.payment",
                res_id: paymentId,
                views: [[false, "form"]],
                target: "current",
            });
        } catch (error) {
            this.notification.add(_t("Failed to open payment: %s", error.message), { type: "danger" });
        }
    }

    /**
     * Refresh timeline data
     */
    async onRefreshTimeline() {
        await this.loadTimelineData();
        this.notification.add(_t("Timeline refreshed successfully"), {
            type: "success",
        });
    }
    getStepClass(step) {
        if (step.completed) {
            return "o_timeline_step_completed";
        }
        return "o_timeline_step_pending";
    }

    /**
     * Get icon for timeline step based on state
     */
    getStepIcon(state) {
        const icons = {
            draft: "fa-file-o",
            submitted: "fa-paper-plane",
            under_review: "fa-search",
            approved: "fa-check",
            authorized: "fa-key",
            posted: "fa-check-circle",
            rejected: "fa-times-circle",
        };
        return icons[state] || "fa-circle-o";
    }

    /**
     * Get display name for approval state
     */
    getStateDisplayName(state) {
        const names = {
            draft: _t("Draft"),
            submitted: _t("Submitted"),
            under_review: _t("Under Review"),
            approved: _t("Approved"),
            authorized: _t("Authorized"),
            posted: _t("Posted"),
            rejected: _t("Rejected"),
        };
        return names[state] || state;
    }

    /**
     * Handle payment selection for detailed view
     */
    onPaymentSelect(payment) {
        this.state.selectedPayment = payment;
    }

    /**
     * Navigate to payment record
     */
    async onViewPayment(paymentId) {
        return this.env.services.action.doAction({
            type: "ir.actions.act_window",
            res_model: "account.payment",
            res_id: paymentId,
            view_mode: "form",
            target: "current",
        });
    }

    /**
     * Refresh timeline data
     */
    async onRefreshTimeline() {
        await this.loadTimelineData();
        this.notification.add(_t("Timeline refreshed"), { type: "success" });
    }
}

/**
 * Reconciliation Navigator Widget
 * Provides enhanced navigation for reconciled entries
 */
export class ReconciliationNavigatorWidget extends Component {
    static template = "account_payment_approval.ReconciliationNavigatorTemplate";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            reconciliationData: {},
            isLoading: true,
            expandedSections: new Set(),
        });

        onWillStart(this.loadReconciliationData);
    }

    async loadReconciliationData() {
        this.state.isLoading = true;
        try {
            const moveId = this.props.record.data.id;
            const data = await this.orm.call("account.move", "get_reconciliation_navigator_data", [moveId]);
            this.state.reconciliationData = data;
        } catch (error) {
            console.error("Error loading reconciliation data:", error);
            this.notification.add(_t("Failed to load reconciliation data"), { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Toggle expanded section
     */
    toggleSection(sectionKey) {
        if (this.state.expandedSections.has(sectionKey)) {
            this.state.expandedSections.delete(sectionKey);
        } else {
            this.state.expandedSections.add(sectionKey);
        }
    }

    /**
     * Check if section is expanded
     */
    isSectionExpanded(sectionKey) {
        return this.state.expandedSections.has(sectionKey);
    }

    /**
     * Navigate to invoice record
     */
    async onViewInvoice(invoiceId) {
        try {
            await this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "account.move",
                res_id: invoiceId,
                views: [[false, "form"]],
                target: "current",
            });
        } catch (error) {
            this.notification.add(_t("Failed to open invoice: %s", error.message), { type: "danger" });
        }
    }

    /**
     * Open reconciliation widget
     */
    async onOpenReconciliation(lineId) {
        try {
            await this.action.doAction({
                type: "ir.actions.client",
                tag: "manual_reconciliation_view",
                context: {
                    move_line_ids: [lineId],
                    default_partner_id: this.props.record.data.partner_id?.[0],
                },
            });
        } catch (error) {
            this.notification.add(_t("Failed to open reconciliation: %s", error.message), { type: "danger" });
        }
    }

    /**
     * Refresh reconciliation data
     */
    async onRefreshData() {
        await this.loadReconciliationData();
        this.notification.add(_t("Reconciliation data refreshed"), {
            type: "success",
        });
    }

    /**
     * Navigate to journal entry
     */
    async onViewJournalEntry(entryId) {
        return this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "account.move",
            res_id: entryId,
            view_mode: "form",
            target: "current",
        });
    }

    /**
     * Navigate to invoice
     */
    async onViewInvoice(invoiceId) {
        return this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "account.move",
            res_id: invoiceId,
            view_mode: "form",
            target: "current",
        });
    }

    /**
     * Open reconciliation wizard
     */
    async onOpenReconciliation(lineId) {
        return this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "account.reconcile.model",
            view_mode: "form",
            target: "new",
            context: {
                default_line_id: lineId,
            },
        });
    }

    /**
     * Refresh reconciliation data
     */
    async onRefreshData() {
        await this.loadReconciliationData();
        this.notification.add(_t("Data refreshed"), { type: "success" });
    }
}

/**
 * Payment Approval Badge Widget
 * Enhanced badge display for payment approval states
 */
export class PaymentApprovalBadgeWidget extends Component {
    static template = "account_payment_approval.PaymentApprovalBadgeTemplate";
    static props = {
        record: Object,
        name: String,
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        this.action = useService("action");
    }

    /**
     * Get badge class based on approval state
     */
    getBadgeClass() {
        const value = this.props.record.data[this.props.name];
        const classMap = {
            draft: "badge-secondary",
            submitted: "badge-info",
            under_review: "badge-warning",
            approved: "badge-success",
            authorized: "badge-primary",
            posted: "badge-success",
            rejected: "badge-danger",
            cancelled: "badge-dark",
        };
        return `badge ${classMap[value] || "badge-secondary"}`;
    }

    /**
     * Get display text for approval state
     */
    getDisplayText() {
        const value = this.props.record.data[this.props.name];
        const textMap = {
            draft: _t("Draft"),
            submitted: _t("Submitted"),
            under_review: _t("Under Review"),
            approved: _t("Approved"),
            authorized: _t("Authorized"),
            posted: _t("Posted"),
            rejected: _t("Rejected"),
            cancelled: _t("Cancelled"),
        };
        return textMap[value] || value;
    }

    /**
     * Handle badge click to show payment details
     */
    async onBadgeClick() {
        if (this.props.readonly) return;

        const paymentId = this.props.record.data.payment_id;
        if (paymentId) {
            return this.action.doAction({
                type: "ir.actions.act_window",
                res_model: "account.payment",
                res_id: paymentId[0],
                view_mode: "form",
                target: "current",
            });
        }
    }
}

// Register widgets
registry.category("fields").add("approval_timeline", ApprovalTimelineWidget);
registry.category("fields").add("reconciliation_navigator", ReconciliationNavigatorWidget);
registry.category("fields").add("payment_approval_badge", PaymentApprovalBadgeWidget);
