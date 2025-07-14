/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";

export class PaymentApprovalListController extends ListController {
    
    /**
     * Override the action execution to handle bulk operations with better UX
     */
    async executeActionButton(action, resIds) {
        if (action.name === 'bulk_approve_payments') {
            return this._handleBulkApprove(action, resIds);
        } else if (action.name === 'bulk_reject_payments') {
            return this._handleBulkReject(action, resIds);
        } else if (action.name === 'bulk_draft_payments') {
            return this._handleBulkDraft(action, resIds);
        }
        
        return super.executeActionButton(action, resIds);
    }

    /**
     * Handle bulk approve with filtering and user feedback
     */
    async _handleBulkApprove(action, resIds) {
        // Filter to only payments that are waiting for approval
        const waitingApprovalIds = [];
        for (const record of this.model.root.records) {
            if (resIds.includes(record.resId) && record.data.state === 'waiting_approval') {
                waitingApprovalIds.push(record.resId);
            }
        }
        
        if (waitingApprovalIds.length === 0) {
            this.notification.add("No selected payments are waiting for approval.", {
                type: "warning",
            });
            return;
        }
        
        if (waitingApprovalIds.length !== resIds.length) {
            const message = `${waitingApprovalIds.length} out of ${resIds.length} selected payments are waiting for approval. Only these will be processed.`;
            this.notification.add(message, {
                type: "info",
            });
        }
        
        return super.executeActionButton(action, waitingApprovalIds);
    }

    /**
     * Handle bulk reject with filtering and user feedback
     */
    async _handleBulkReject(action, resIds) {
        // Filter to only payments that are waiting for approval
        const waitingApprovalIds = [];
        for (const record of this.model.root.records) {
            if (resIds.includes(record.resId) && record.data.state === 'waiting_approval') {
                waitingApprovalIds.push(record.resId);
            }
        }
        
        if (waitingApprovalIds.length === 0) {
            this.notification.add("No selected payments are waiting for approval to reject.", {
                type: "warning",
            });
            return;
        }
        
        if (waitingApprovalIds.length !== resIds.length) {
            const message = `${waitingApprovalIds.length} out of ${resIds.length} selected payments are waiting for approval. Only these will be rejected.`;
            this.notification.add(message, {
                type: "info",
            });
        }
        
        return super.executeActionButton(action, waitingApprovalIds);
    }

    /**
     * Handle bulk draft with filtering and user feedback
     */
    async _handleBulkDraft(action, resIds) {
        // Filter to only payments that can be set to draft (rejected or cancelled)
        const draftableIds = [];
        for (const record of this.model.root.records) {
            if (resIds.includes(record.resId) && ['rejected', 'cancel'].includes(record.data.state)) {
                draftableIds.push(record.resId);
            }
        }
        
        if (draftableIds.length === 0) {
            this.notification.add("No selected payments can be set to draft. Only rejected or cancelled payments can be reset to draft.", {
                type: "warning",
            });
            return;
        }
        
        if (draftableIds.length !== resIds.length) {
            const message = `${draftableIds.length} out of ${resIds.length} selected payments can be set to draft. Only these will be processed.`;
            this.notification.add(message, {
                type: "info",
            });
        }
        
        return super.executeActionButton(action, draftableIds);
    }
}

export const paymentApprovalListView = {
    ...listView,
    Controller: PaymentApprovalListController,
};

registry.category("views").add("payment_approval_list", paymentApprovalListView);
