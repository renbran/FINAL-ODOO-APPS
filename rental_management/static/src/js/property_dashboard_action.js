/** @odoo-module **/

import { registry } from "@web/core/registry";
import { RentalPropertyDashboard } from "@rental_management/components/rental_property_dashboard";

/**
 * Property Dashboard Client Action
 * Registers the property dashboard as a client action for Odoo 17
 */
registry.category("actions").add("property_dashboard", RentalPropertyDashboard);
