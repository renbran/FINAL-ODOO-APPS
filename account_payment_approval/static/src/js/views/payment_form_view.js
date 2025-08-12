/** @odoo-module **/
// Payment Form View Controller - Placeholder
import { FormController } from "@web/views/form/form_controller";
import { registry } from "@web/core/registry";

export class PaymentFormController extends FormController {
    // Custom payment form enhancements
}

registry.category("views").add("payment_form", {
    ...registry.category("views").get("form"),
    Controller: PaymentFormController,
});
