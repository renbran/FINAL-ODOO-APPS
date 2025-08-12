/** @odoo-module **/
// Approval State Field Widget - Placeholder
import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";

export class ApprovalStateField extends CharField {
    static template = "account_payment_approval.ApprovalStateField";
}

registry.category("fields").add("approval_state", ApprovalStateField);
