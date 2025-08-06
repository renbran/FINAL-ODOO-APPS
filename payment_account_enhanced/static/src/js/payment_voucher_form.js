/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { FormView } from "@web/views/form/form_view";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { Component, onWillStart, useState } from "@odoo/owl";

const viewRegistry = registry.category("views");

/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { FormView } from "@web/views/form/form_view";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

/**
 * Enhanced Payment Voucher Form Controller for Odoo 17
 * Handles the simplified 2-state approval workflow
 */
export class PaymentVoucherFormController extends FormController {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this._isPaymentVoucher = this.props.resModel === 'account.payment';
    }

    /**
     * Update status bar and buttons when record changes
     */
    async _updateButtons() {
        await super._updateButtons();
        if (this._isPaymentVoucher && this.model.root.data) {
            this._updatePaymentWorkflowButtons();
            this._updateStatusBarColors();
        }
    }

    /**
     * Update workflow buttons based on approval state
     */
    _updatePaymentWorkflowButtons() {
        const record = this.model.root.data;
        const approvalState = record.approval_state;
        
        // Update button visibility based on state
        const $submitBtn = this.el.querySelector('.o_payment_submit_approval');
        const $approveBtn = this.el.querySelector('.o_payment_approve_post');
        const $rejectBtn = this.el.querySelector('.o_payment_reject');
        
        if ($submitBtn) $submitBtn.style.display = approvalState === 'draft' ? 'inline-block' : 'none';
        if ($approveBtn) $approveBtn.style.display = ['waiting_approval', 'approved'].includes(approvalState) ? 'inline-block' : 'none';
        if ($rejectBtn) $rejectBtn.style.display = approvalState === 'waiting_approval' ? 'inline-block' : 'none';
        
        // Update button text for context
        if ($approveBtn) {
            if (approvalState === 'waiting_approval') {
                $approveBtn.textContent = _t('Approve & Post');
            } else if (approvalState === 'approved') {
                $approveBtn.textContent = _t('Post Payment');
            }
        }
    }

    /**
     * Update status bar colors and animations
     */
    _updateStatusBarColors() {
        const record = this.model.root.data;
        const approvalState = record.approval_state;
        const $statusbar = this.el.querySelector('.o_payment_statusbar');
        
        if ($statusbar) {
            // Remove all state classes
            $statusbar.className = $statusbar.className.replace(/state-\w+/g, '');
            
            // Add current state class
            $statusbar.classList.add('state-' + approvalState.replace('_', '-'));
        }
        
        // Add voucher number to display
        if (record.voucher_number) {
            let $voucherDisplay = this.el.querySelector('.o_voucher_number_display');
            if (!$voucherDisplay && $statusbar) {
                const voucherDiv = document.createElement('div');
                voucherDiv.className = 'o_voucher_number_display';
                voucherDiv.innerHTML = `Voucher: <span class="o_voucher_number">${record.voucher_number}</span>`;
                $statusbar.parentNode.insertBefore(voucherDiv, $statusbar);
            } else if ($voucherDisplay) {
                const $voucherNumber = $voucherDisplay.querySelector('.o_voucher_number');
                if ($voucherNumber) {
                    $voucherNumber.textContent = record.voucher_number;
                }
            }
        }
    }

    /**
     * Handle submit for approval action
     */
    async onSubmitForApproval() {
        // Validate required fields
        if (!this._validatePaymentData()) {
            return;
        }
        
        // Show confirmation dialog
        this.dialog.add(ConfirmationDialog, {
            body: _t("Submit this payment for approval?"),
            confirm: async () => {
                try {
                    const result = await this.orm.call(
                        'account.payment',
                        'action_submit_for_approval',
                        [this.model.root.resId]
                    );
                    
                    if (result && result.type === 'ir.actions.client') {
                        this.notification.add(result.params.message, {
                            type: result.params.type
                        });
                    }
                    
                    await this.model.load();
                } catch (error) {
                    this.notification.add(_t("Failed to submit for approval"), {
                        type: "danger"
                    });
                }
            }
        });
    }

    /**
     * Handle approve and post action
     */
    async onApproveAndPost() {
        this.dialog.add(ConfirmationDialog, {
            body: _t("Approve and post this payment?"),
            confirm: async () => {
                try {
                    const result = await this.orm.call(
                        'account.payment',
                        'action_approve_and_post',
                        [this.model.root.resId]
                    );
                    
                    if (result && result.type === 'ir.actions.client') {
                        this.notification.add(result.params.message, {
                            type: result.params.type
                        });
                    }
                    
                    await this.model.load();
                } catch (error) {
                    this.notification.add(_t("Failed to approve and post"), {
                        type: "danger"
                    });
                }
            }
        });
    }

    /**
     * Handle reject payment action
     */
    async onRejectPayment() {
        this.dialog.add(ConfirmationDialog, {
            body: _t("Reject this payment and return to draft?"),
            confirm: async () => {
                try {
                    const result = await this.orm.call(
                        'account.payment',
                        'action_reject_payment',
                        [this.model.root.resId]
                    );
                    
                    if (result && result.type === 'ir.actions.client') {
                        this.notification.add(result.params.message, {
                            type: result.params.type
                        });
                    }
                    
                    await this.model.load();
                } catch (error) {
                    this.notification.add(_t("Failed to reject payment"), {
                        type: "danger"
                    });
                }
            }
        });
    }

    /**
     * Validate payment data before submission
     */
    _validatePaymentData() {
        const record = this.model.root.data;
        
        if (!record.partner_id) {
            this.notification.add(_t('Please select a partner before submitting for approval.'), {
                type: 'warning'
            });
            return false;
        }
        
        if (!record.amount || record.amount <= 0) {
            this.notification.add(_t('Please enter a valid amount greater than zero.'), {
                type: 'warning'
            });
            return false;
        }
        
        if (!record.journal_id) {
            this.notification.add(_t('Please select a payment journal.'), {
                type: 'warning'
            });
            return false;
        }
        
        return true;
    }
}

/**
 * Enhanced Payment Voucher Form View
 */
export class PaymentVoucherFormView extends FormView {
    static components = {
        ...FormView.components,
    };
}

PaymentVoucherFormView.type = "payment_voucher_form";
PaymentVoucherFormView.Controller = PaymentVoucherFormController;

// Register the enhanced view for account.payment model
registry.category("views").add("payment_voucher_form", PaymentVoucherFormView);

/**
 * Auto-refresh functionality for approval status
 */
class PaymentVoucherAutoRefresh {
    constructor() {
        this.setupAutoRefresh();
    }

    setupAutoRefresh() {
        // Refresh approval status every 30 seconds for pending approvals
        setInterval(() => {
            const pendingElements = document.querySelectorAll('.o_payment_statusbar[data-approval-state="waiting_approval"]');
            if (pendingElements.length > 0) {
                // Only refresh if we're viewing payment records
                if (window.location.hash.includes('model=account.payment')) {
                    // Trigger a soft refresh of the current view
                    const formView = document.querySelector('.o_content .o_form_view');
                    if (formView && formView.__owl__) {
                        const controller = formView.__owl__.component;
                        if (controller && controller.model) {
                            controller.model.load();
                        }
                    }
                }
            }
        }, 30000); // 30 seconds
    }
}

/**
 * Enhanced notification system for payment workflow
 */
export const PaymentWorkflowNotifications = {
    showWorkflowHelp() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.tabIndex = -1;
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Payment Voucher Workflow Guide</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="workflow-guide">
                            <h6>Simplified 2-State Approval Workflow:</h6>
                            <ol>
                                <li><strong>Draft:</strong> Create and edit payment details. Add remarks, select partner, amount, and journal.</li>
                                <li><strong>Waiting for Approval:</strong> Submit payment for approval. Only approved users can approve.</li>
                                <li><strong>Approved & Posted:</strong> Payment is approved and automatically posted to accounting.</li>
                            </ol>
                            <div class="alert alert-info mt-3">
                                <strong>Note:</strong> Voucher numbers are automatically generated when payments are created. 
                                QR codes are generated for verification purposes once the payment is submitted for approval.
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Use Bootstrap 5 modal
        if (window.bootstrap && window.bootstrap.Modal) {
            const bsModal = new window.bootstrap.Modal(modal);
            bsModal.show();
            modal.addEventListener('hidden.bs.modal', () => {
                modal.remove();
            });
        }
    }
};

// Initialize auto-refresh when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new PaymentVoucherAutoRefresh();
    });
} else {
    new PaymentVoucherAutoRefresh();
}

// Export for global use
window.PaymentWorkflowNotifications = PaymentWorkflowNotifications;
