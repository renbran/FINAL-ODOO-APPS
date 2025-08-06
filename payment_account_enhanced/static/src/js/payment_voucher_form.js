odoo.define('payment_account_enhanced.PaymentVoucherForm', function (require) {
"use strict";

var FormController = require('web.FormController');
var FormView = require('web.FormView');
var viewRegistry = require('web.view_registry');
var core = require('web.core');
var Dialog = require('web.Dialog');

var _t = core._t;

/**
 * Enhanced Payment Voucher Form Controller
 * Handles the simplified 2-state approval workflow
 */
var PaymentVoucherFormController = FormController.extend({
    events: _.extend({}, FormController.prototype.events, {
        'click .o_payment_submit_approval': '_onSubmitForApproval',
        'click .o_payment_approve_post': '_onApproveAndPost',
        'click .o_payment_reject': '_onRejectPayment',
    }),

    /**
     * Override to add custom logic for payment voucher workflow
     */
    init: function () {
        this._super.apply(this, arguments);
        this._isPaymentVoucher = this.modelName === 'account.payment';
    },

    /**
     * Update status bar and buttons when record changes
     */
    _updateButtons: function () {
        this._super.apply(this, arguments);
        if (this._isPaymentVoucher && this.renderer.state.data) {
            this._updatePaymentWorkflowButtons();
            this._updateStatusBarColors();
        }
    },

    /**
     * Update workflow buttons based on approval state
     */
    _updatePaymentWorkflowButtons: function () {
        var record = this.renderer.state.data;
        var approvalState = record.approval_state;
        
        // Update button visibility based on state
        this.$('.o_payment_submit_approval').toggle(approvalState === 'draft');
        this.$('.o_payment_approve_post').toggle(['waiting_approval', 'approved'].includes(approvalState));
        this.$('.o_payment_reject').toggle(approvalState === 'waiting_approval');
        
        // Update button text for context
        if (approvalState === 'waiting_approval') {
            this.$('.o_payment_approve_post').text(_t('Approve & Post'));
        } else if (approvalState === 'approved') {
            this.$('.o_payment_approve_post').text(_t('Post Payment'));
        }
    },

    /**
     * Update status bar colors and animations
     */
    _updateStatusBarColors: function () {
        var record = this.renderer.state.data;
        var approvalState = record.approval_state;
        var $statusbar = this.$('.o_payment_statusbar');
        
        // Remove all state classes
        $statusbar.removeClass('state-draft state-waiting state-approved state-posted state-cancelled');
        
        // Add current state class
        $statusbar.addClass('state-' + approvalState.replace('_', '-'));
        
        // Add voucher number to display
        if (record.voucher_number) {
            var $voucherDisplay = this.$('.o_voucher_number_display');
            if ($voucherDisplay.length === 0) {
                $statusbar.before('<div class="o_voucher_number_display">Voucher: <span class="o_voucher_number">' + record.voucher_number + '</span></div>');
            } else {
                $voucherDisplay.find('.o_voucher_number').text(record.voucher_number);
            }
        }
    },

    /**
     * Handle submit for approval action
     */
    _onSubmitForApproval: function (event) {
        event.preventDefault();
        var self = this;
        
        // Validate required fields
        if (!this._validatePaymentData()) {
            return;
        }
        
        // Show confirmation dialog
        Dialog.confirm(this, _t("Submit this payment for approval?"), {
            confirm_callback: function () {
                self._rpc({
                    model: 'account.payment',
                    method: 'action_submit_for_approval',
                    args: [self.renderer.state.res_id],
                }).then(function (result) {
                    if (result && result.type === 'ir.actions.client') {
                        self.displayNotification({
                            message: result.params.message,
                            type: result.params.type,
                        });
                    }
                    self.reload();
                });
            }
        });
    },

    /**
     * Handle approve and post action
     */
    _onApproveAndPost: function (event) {
        event.preventDefault();
        var self = this;
        
        Dialog.confirm(this, _t("Approve and post this payment?"), {
            confirm_callback: function () {
                self._rpc({
                    model: 'account.payment',
                    method: 'action_approve_and_post',
                    args: [self.renderer.state.res_id],
                }).then(function (result) {
                    if (result && result.type === 'ir.actions.client') {
                        self.displayNotification({
                            message: result.params.message,
                            type: result.params.type,
                        });
                    }
                    self.reload();
                });
            }
        });
    },

    /**
     * Handle reject payment action
     */
    _onRejectPayment: function (event) {
        event.preventDefault();
        var self = this;
        
        Dialog.confirm(this, _t("Reject this payment and return to draft?"), {
            confirm_callback: function () {
                self._rpc({
                    model: 'account.payment',
                    method: 'action_reject_payment',
                    args: [self.renderer.state.res_id],
                }).then(function (result) {
                    if (result && result.type === 'ir.actions.client') {
                        self.displayNotification({
                            message: result.params.message,
                            type: result.params.type,
                        });
                    }
                    self.reload();
                });
            }
        });
    },

    /**
     * Validate payment data before submission
     */
    _validatePaymentData: function () {
        var record = this.renderer.state.data;
        
        if (!record.partner_id) {
            this.displayNotification({
                message: _t('Please select a partner before submitting for approval.'),
                type: 'warning',
            });
            return false;
        }
        
        if (!record.amount || record.amount <= 0) {
            this.displayNotification({
                message: _t('Please enter a valid amount greater than zero.'),
                type: 'warning',
            });
            return false;
        }
        
        if (!record.journal_id) {
            this.displayNotification({
                message: _t('Please select a payment journal.'),
                type: 'warning',
            });
            return false;
        }
        
        return true;
    },

    /**
     * Override save to handle voucher number generation
     */
    saveRecord: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function (result) {
            // Reload to get updated voucher number
            if (self._isPaymentVoucher && result) {
                self.reload();
            }
            return result;
        });
    },
});

/**
 * Enhanced Payment Voucher Form View
 */
var PaymentVoucherFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Controller: PaymentVoucherFormController,
    }),
});

// Register the enhanced view for account.payment model
viewRegistry.add('payment_voucher_form', PaymentVoucherFormView);

/**
 * Auto-refresh functionality for approval status
 */
var PaymentVoucherAutoRefresh = {
    init: function () {
        this.setupAutoRefresh();
    },

    setupAutoRefresh: function () {
        // Refresh approval status every 30 seconds for pending approvals
        setInterval(function () {
            var $pendingElements = $('.o_payment_statusbar[data-approval-state="waiting_approval"]');
            if ($pendingElements.length > 0) {
                // Trigger a soft refresh of the current view
                if (window.location.hash.includes('model=account.payment')) {
                    // Only refresh if we're viewing payment records
                    var controller = $('.o_content .o_form_view').data('controller');
                    if (controller && controller.renderer && controller.renderer.state) {
                        controller.reload();
                    }
                }
            }
        }, 30000); // 30 seconds
    }
};

// Initialize auto-refresh when DOM is ready
$(document).ready(function () {
    PaymentVoucherAutoRefresh.init();
});

/**
 * Enhanced notification system for payment workflow
 */
var PaymentWorkflowNotifications = {
    showWorkflowHelp: function () {
        var $modal = $(
            '<div class="modal fade" tabindex="-1">' +
            '<div class="modal-dialog modal-lg">' +
            '<div class="modal-content">' +
            '<div class="modal-header">' +
            '<h5 class="modal-title">Payment Voucher Workflow Guide</h5>' +
            '<button type="button" class="close" data-dismiss="modal">&times;</button>' +
            '</div>' +
            '<div class="modal-body">' +
            '<div class="workflow-guide">' +
            '<h6>Simplified 2-State Approval Workflow:</h6>' +
            '<ol>' +
            '<li><strong>Draft:</strong> Create and edit payment details. Add remarks, select partner, amount, and journal.</li>' +
            '<li><strong>Waiting for Approval:</strong> Submit payment for approval. Only approved users can approve.</li>' +
            '<li><strong>Approved & Posted:</strong> Payment is approved and automatically posted to accounting.</li>' +
            '</ol>' +
            '<div class="alert alert-info mt-3">' +
            '<strong>Note:</strong> Voucher numbers are automatically generated when payments are created. ' +
            'QR codes are generated for verification purposes once the payment is submitted for approval.' +
            '</div>' +
            '</div>' +
            '</div>' +
            '<div class="modal-footer">' +
            '<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>' +
            '</div>' +
            '</div>' +
            '</div>' +
            '</div>'
        );
        
        $modal.modal('show');
        $modal.on('hidden.bs.modal', function () {
            $modal.remove();
        });
    }
};

// Export for global use
window.PaymentWorkflowNotifications = PaymentWorkflowNotifications;

return {
    PaymentVoucherFormController: PaymentVoucherFormController,
    PaymentVoucherFormView: PaymentVoucherFormView,
    PaymentVoucherAutoRefresh: PaymentVoucherAutoRefresh,
    PaymentWorkflowNotifications: PaymentWorkflowNotifications,
};

});
