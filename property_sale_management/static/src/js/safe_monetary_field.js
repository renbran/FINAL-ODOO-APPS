/** @odoo-module **/

import { registry } from "@web/core/registry";
import { MonetaryField } from "@web/views/fields/monetary/monetary_field";

/**
 * SafeMonetaryField - A MonetaryField that safely handles non-numeric values
 * 
 * This extension of the standard MonetaryField ensures that we never attempt to
 * call toFixed() on non-numeric values, which prevents the "value.toFixed is not a function"
 * error.
 */
export class SafeMonetaryField extends MonetaryField {
    setup() {
        super.setup();
    }
    
    /**
     * Override the formattedValue getter to ensure values are numeric
     */
    get formattedValue() {
        try {
            // Ensure we have a valid number before formatting
            const value = this.props.value;
            if (value === null || value === undefined || isNaN(parseFloat(value))) {
                // Return empty string or "0.00" depending on your preference
                return "";
            }
            
            // Let the parent class handle formatting if value is valid
            return super.formattedValue;
        } catch (error) {
            console.warn("Error formatting monetary value:", error);
            
            // Fallback formatting
            const currency = this.props.currencyId ? this.props.currencyId[1] || "€" : "€";
            const value = parseFloat(this.props.value || 0);
            return `${currency} ${value.toFixed(2)}`;
        }
    }
}

// Register the new field widget
registry.category("fields").add("safe_monetary", SafeMonetaryField);