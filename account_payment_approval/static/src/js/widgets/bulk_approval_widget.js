/** @odoo-module **/
// Bulk Approval Widget - Placeholder
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class BulkApprovalWidget extends Component {
    static template = "account_payment_approval.BulkApprovalWidget";
}

registry.category("fields").add("bulk_approval", BulkApprovalWidget);
