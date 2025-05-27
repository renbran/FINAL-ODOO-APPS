/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";

export class PropertyStatusWidget extends CharField {
    static template = "property_management.PropertyStatusWidget";
    
    setup() {
        super.setup();
    }

    get statusClass() {
        if (!this.props.value) return "";
        const status = this.props.value.toLowerCase();
        const classes = {
            "available": "text-success",
            "reserved": "text-warning",
            "sold": "text-danger"
        };
        return classes[status] || "";
    }
}

registry.category("fields").add("property_status", PropertyStatusWidget);