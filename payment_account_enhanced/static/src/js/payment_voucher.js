/** @odoo-module **/

import { registry } from "@web/core/registry";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";

/**
 * Enhanced Payment Voucher Form Controller
 */
export class PaymentVoucherFormController extends FormController {
    setup() {
        super.setup();
        this.notification = useService("notification");
        this.action = useService("action");
    }

    /**
     * Handle approval workflow actions
     */
    async onApprovalAction(action, record) {
        try {
            const result = await this.model.orm.call(
                "account.payment",
                action,
                [record.resId]
            );
            
            if (result && result.type === 'ir.actions.client') {
                this.notification.add(result.params.message, {
                    type: result.params.type,
                    sticky: result.params.sticky
                });
            }
            
            // Reload the form to show updated state
            await this.model.load();
        } catch (error) {
            this.notification.add("Action failed: " + error.message, {
                type: "danger"
            });
        }
    }

    /**
     * Validate payment data before submission
     */
    async validatePaymentData(record) {
        const data = record.data;
        const errors = [];

        if (!data.partner_id) {
            errors.push("Partner is required");
        }

        if (!data.amount || data.amount <= 0) {
            errors.push("Amount must be greater than zero");
        }

        if (!data.journal_id) {
            errors.push("Payment journal is required");
        }

        if (!data.date) {
            errors.push("Payment date is required");
        }

        if (errors.length > 0) {
            this.notification.add("Validation Error: " + errors.join(", "), {
                type: "danger"
            });
            return false;
        }

        return true;
    }

    /**
     * Enhanced save with validation
     */
    async onSave() {
        if (this.model.root.data.approval_state === 'draft') {
            const isValid = await this.validatePaymentData(this.model.root);
            if (!isValid) {
                return;
            }
        }
        
        return super.onSave();
    }
}

/**
 * Payment Voucher List Controller
 */
export class PaymentVoucherListController extends FormController {
    setup() {
        super.setup();
        this.notification = useService("notification");
    }

    /**
     * Handle bulk approval actions
     */
    async onBulkApprove(selectedRecords) {
        try {
            const recordIds = selectedRecords.map(r => r.resId);
            
            const result = await this.model.orm.call(
                "account.payment",
                "action_approve_payment",
                [recordIds]
            );
            
            this.notification.add("Payments approved successfully", {
                type: "success"
            });
            
            await this.model.load();
        } catch (error) {
            this.notification.add("Bulk approval failed: " + error.message, {
                type: "danger"
            });
        }
    }
}

/**
 * QR Code Widget for payment verification
 */
import { Component } from "@odoo/owl";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

export class QRCodeWidget extends Component {
    static template = "osus_payment_voucher.QRCodeWidget";
    static props = {
        ...standardWidgetProps,
    };

    get qrCodeUrl() {
        if (this.props.record.data.qr_code) {
            return `data:image/png;base64,${this.props.record.data.qr_code}`;
        }
        return null;
    }

    get isVisible() {
        return this.props.record.data.qr_in_report && this.qrCodeUrl;
    }

    onQRClick() {
        if (this.qrCodeUrl) {
            const baseUrl = window.location.origin;
            const verifyUrl = `${baseUrl}/payment/verify/${this.props.record.resId}`;
            window.open(verifyUrl, '_blank');
        }
    }
}

/**
 * Payment Status Badge Widget
 */
export class PaymentStatusBadge extends Component {
    static template = "osus_payment_voucher.PaymentStatusBadge";
    static props = {
        ...standardWidgetProps,
    };

    get statusClass() {
        const state = this.props.record.data.approval_state;
        const statusClasses = {
            draft: 'badge-secondary',
            submitted: 'badge-warning',
            approved: 'badge-success',
            posted: 'badge-primary',
            rejected: 'badge-danger',
            cancelled: 'badge-dark'
        };
        return statusClasses[state] || 'badge-secondary';
    }

    get statusIcon() {
        const state = this.props.record.data.approval_state;
        const statusIcons = {
            draft: 'fa-edit',
            submitted: 'fa-clock-o',
            approved: 'fa-check',
            posted: 'fa-check-circle',
            rejected: 'fa-times',
            cancelled: 'fa-ban'
        };
        return statusIcons[state] || 'fa-question';
    }

    get statusText() {
        const state = this.props.record.data.approval_state;
        const statusTexts = {
            draft: 'Draft',
            submitted: 'Submitted',
            approved: 'Approved',
            posted: 'Posted',
            rejected: 'Rejected',
            cancelled: 'Cancelled'
        };
        return statusTexts[state] || 'Unknown';
    }
}

/**
 * Register components
 */
registry.category("view_widgets").add("qr_code_widget", QRCodeWidget);
registry.category("view_widgets").add("payment_status_badge", PaymentStatusBadge);

/**
 * Payment Voucher Dashboard
 */
export class PaymentVoucherDashboard extends Component {
    static template = "osus_payment_voucher.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            stats: {
                submitted: 0,
                approved: 0,
                rejected: 0
            },
            loading: true
        });
        
        this.loadStats();
    }

    async loadStats() {
        try {
            const stats = await this.orm.call(
                "account.payment",
                "get_approval_statistics",
                []
            );
            
            this.state.stats = stats;
            this.state.loading = false;
        } catch (error) {
            console.error("Failed to load payment statistics:", error);
            this.state.loading = false;
        }
    }

    async openPayments(state) {
        const action = await this.orm.call(
            "ir.actions.act_window",
            "for_xml_id",
            ["osus_payment_voucher", "action_payment_voucher_all"]
        );
        
        action.domain = [['approval_state', '=', state]];
        action.context = {
            ...action.context,
            search_default_filter_state: 1
        };
        
        this.action.doAction(action);
    }
}

/**
 * Utility functions
 */
export const PaymentVoucherUtils = {
    /**
     * Format currency amount
     */
    formatCurrency(amount, currency) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency || 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    },

    /**
     * Get status color
     */
    getStatusColor(state) {
        const colors = {
            draft: '#6c757d',
            submitted: '#ffc107',
            approved: '#28a745',
            posted: '#007bff',
            rejected: '#dc3545',
            cancelled: '#343a40'
        };
        return colors[state] || '#6c757d';
    },

    /**
     * Validate QR code data
     */
    validateQRCode(qrData) {
        try {
            // Basic validation for QR code content
            return qrData && qrData.length > 0;
        } catch (error) {
            return false;
        }
    }
};

/**
 * Export for global use
 */
window.PaymentVoucherUtils = PaymentVoucherUtils;