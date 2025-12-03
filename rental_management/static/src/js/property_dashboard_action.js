/** @odoo-module **/

import { registry } from "@web/core/registry";
import { RentalPropertyDashboard } from "@rental_management/components/rental_property_dashboard";

/**
 * Property Dashboard Client Action
 * Registers the property dashboard as a client action for Odoo 17
 */

console.log('[rental_management] property_dashboard_action.js loading...');
console.log('[rental_management] RentalPropertyDashboard class:', RentalPropertyDashboard);
console.log('[rental_management] registry:', registry);

try {
    registry.category("actions").add("property_dashboard", RentalPropertyDashboard);
    console.log('[rental_management] ✓ Successfully registered property_dashboard action');
} catch (error) {
    console.error('[rental_management] ✗ Failed to register property_dashboard:', error);
}
