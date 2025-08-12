/** @odoo-module **/
// Voucher State Field Widget (formerly approval_state)
import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";

export class VoucherStateField extends CharField {
    static template = "account_payment_approval.VoucherStateField";
}

// Register under both names for backward compatibility
registry.category("fields").add("voucher_state", VoucherStateField);
registry.category("fields").add("approval_state", VoucherStateField);
