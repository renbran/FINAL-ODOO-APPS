/** @odoo-module **/

import { registry } from "@web/core/registry";  // Ensure registry is imported
import { FloatField } from "@web/views/fields/float/float_field";
import { xml } from "@odoo/owl";

const paymentProgressTemplate = xml`
<div class="o_payment_progress">
    <div class="progress-bar" 
        role="progressbar" 
        t-att-style="{width: progressPercentage + '%'}"
        t-att-aria-valuenow="progressPercentage"
        t-att-aria-valuemin="0"
        t-att-aria-valuemax="max">
        <span t-esc="formattedValue"/>
    </div>
</div>`;

export class PaymentProgressField extends FloatField {
    static template = paymentProgressTemplate;
    static props = {
        ...FloatField.props,
        max: { type: Number, optional: true },
    };

    get max() {
        return this.props.max || 100;
    }

    get progressPercentage() {
        const value = this.props.value || 0;
        const percentage = (value / this.max) * 100;
        return Math.min(Math.max(percentage, 0), 100);
    }

    get formattedValue() {
        return `${this.progressPercentage.toFixed(1)}%`;
    }
}

registry.category("fields").add("payment_progress", PaymentProgressField);