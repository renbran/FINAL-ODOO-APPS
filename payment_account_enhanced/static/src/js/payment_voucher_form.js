/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

/**
 * Patch the standard FormController for payment voucher functionality
 * This approach is more compatible and doesn't require extending undefined classes
 */
patch(registry.category("views").get("form").Controller.prototype, {
    
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");
        this._isPaymentVoucher = this.props.resModel === 'account.payment';
    },

    /**
     * Update status bar and buttons when record changes
     */
    async _updateButtons() {
        await super._updateButtons();
        if (this._isPaymentVoucher && this.model.root.data) {
            this._updatePaymentWorkflowButtons();
            this._updateStatusBarColors();
        }
    },

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
    },

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
    },

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
    },

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
    },

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
    },

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
});

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

/**
 * Payment Voucher Button Actions - Global handlers
 */
window.PaymentVoucherActions = {
    
    async submitForApproval(recordId) {
        const orm = useService("orm");
        const notification = useService("notification");
        
        try {
            const result = await orm.call(
                'account.payment',
                'action_submit_for_approval',
                [recordId]
            );
            
            if (result && result.type === 'ir.actions.client') {
                notification.add(result.params.message, {
                    type: result.params.type
                });
            }
            
            // Reload the page or trigger view refresh
            window.location.reload();
        } catch (error) {
            console.error("Submit for approval failed:", error);
            alert(_t("Failed to submit for approval"));
        }
    },
    
    async approveAndPost(recordId) {
        if (confirm(_t("Approve and post this payment?"))) {
            const orm = useService("orm");
            const notification = useService("notification");
            
            try {
                const result = await orm.call(
                    'account.payment',
                    'action_approve_and_post',
                    [recordId]
                );
                
                if (result && result.type === 'ir.actions.client') {
                    notification.add(result.params.message, {
                        type: result.params.type
                    });
                }
                
                window.location.reload();
            } catch (error) {
                console.error("Approve and post failed:", error);
                alert(_t("Failed to approve and post"));
            }
        }
    },
    
    async rejectPayment(recordId) {
        if (confirm(_t("Reject this payment and return to draft?"))) {
            const orm = useService("orm");
            const notification = useService("notification");
            
            try {
                const result = await orm.call(
                    'account.payment',
                    'action_reject_payment',
                    [recordId]
                );
                
                if (result && result.type === 'ir.actions.client') {
                    notification.add(result.params.message, {
                        type: result.params.type
                    });
                }
                
                window.location.reload();
            } catch (error) {
                console.error("Reject payment failed:", error);
                alert(_t("Failed to reject payment"));
            }
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

/**
 * Simple event-driven approach for button handling
 * This works when the patch approach might not be compatible
 */
document.addEventListener('DOMContentLoaded', function() {
    // Handle payment voucher buttons with event delegation
    document.body.addEventListener('click', function(e) {
        if (e.target.matches('.o_payment_submit_approval')) {
            e.preventDefault();
            const recordId = getRecordIdFromForm();
            if (recordId) {
                PaymentVoucherActions.submitForApproval(recordId);
            }
        } else if (e.target.matches('.o_payment_approve_post')) {
            e.preventDefault();
            const recordId = getRecordIdFromForm();
            if (recordId) {
                PaymentVoucherActions.approveAndPost(recordId);
            }
        } else if (e.target.matches('.o_payment_reject')) {
            e.preventDefault();
            const recordId = getRecordIdFromForm();
            if (recordId) {
                PaymentVoucherActions.rejectPayment(recordId);
            }
        }
    });
    
    // Helper function to get record ID from current form
    function getRecordIdFromForm() {
        // Try multiple ways to get the current record ID
        const urlMatch = window.location.href.match(/id=(\d+)/);
        if (urlMatch) {
            return parseInt(urlMatch[1]);
        }
        
        // Try from data attributes
        const formElement = document.querySelector('.o_form_view');
        if (formElement && formElement.dataset.recordId) {
            return parseInt(formElement.dataset.recordId);
        }
        
        // Try from breadcrumb or other sources
        const breadcrumbId = document.querySelector('.breadcrumb .active[data-id]');
        if (breadcrumbId) {
            return parseInt(breadcrumbId.dataset.id);
        }
        
        console.warn('Could not determine record ID');
        return null;
    }
});

/**
 * Enhanced status bar updates based on approval state changes
 */
const PaymentStatusBarUpdater = {
    init() {
        // Watch for changes in the approval state field
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' || mutation.type === 'attributes') {
                    PaymentStatusBarUpdater.updateStatusDisplay();
                }
            });
        });
        
        // Start observing
        const formView = document.querySelector('.o_form_view');
        if (formView) {
            observer.observe(formView, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['data-approval-state', 'class']
            });
        }
    },
    
    updateStatusDisplay() {
        const statusbar = document.querySelector('.o_payment_statusbar');
        if (!statusbar) return;
        
        // Get approval state from various possible sources
        let approvalState = null;
        
        // Check data attribute
        if (statusbar.dataset.approvalState) {
            approvalState = statusbar.dataset.approvalState;
        }
        
        // Check for state indicators in the form
        const stateField = document.querySelector('input[name="approval_state"], select[name="approval_state"]');
        if (stateField && stateField.value) {
            approvalState = stateField.value;
        }
        
        if (approvalState) {
            // Update status bar appearance
            statusbar.className = statusbar.className.replace(/state-\w+/g, '');
            statusbar.classList.add('state-' + approvalState.replace('_', '-'));
            
            // Update button visibility
            PaymentStatusBarUpdater.updateButtonVisibility(approvalState);
        }
    },
    
    updateButtonVisibility(approvalState) {
        const submitBtn = document.querySelector('.o_payment_submit_approval');
        const approveBtn = document.querySelector('.o_payment_approve_post');
        const rejectBtn = document.querySelector('.o_payment_reject');
        
        if (submitBtn) {
            submitBtn.style.display = approvalState === 'draft' ? 'inline-block' : 'none';
        }
        
        if (approveBtn) {
            approveBtn.style.display = ['waiting_approval', 'approved'].includes(approvalState) ? 'inline-block' : 'none';
            
            // Update button text
            if (approvalState === 'waiting_approval') {
                approveBtn.textContent = _t('Approve & Post');
            } else if (approvalState === 'approved') {
                approveBtn.textContent = _t('Post Payment');
            }
        }
        
        if (rejectBtn) {
            rejectBtn.style.display = approvalState === 'waiting_approval' ? 'inline-block' : 'none';
        }
    }
};

// Initialize status bar updater
document.addEventListener('DOMContentLoaded', function() {
    PaymentStatusBarUpdater.init();
});

// Also initialize when Odoo views change
if (typeof odoo !== 'undefined') {
    // Listen for Odoo's internal events
    document.addEventListener('DOMNodeInserted', function(e) {
        if (e.target.classList && e.target.classList.contains('o_form_view')) {
            setTimeout(function() {
                PaymentStatusBarUpdater.init();
            }, 500);
        }
    });
}