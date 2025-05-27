/** @odoo-module **/

import { registry } from "@web/core/registry";
import { PaymentProgressField } from "./payment_progress";
import { PropertyFormController } from "./property_form_controller";
import { PropertyKanbanController } from "./property_kanban_controller";
import { PropertyListController } from "./property_list_controller";

// Register components
registry.category("fields").add("payment_progress", PaymentProgressField);

// Register view controllers
registry.category("views").add("property_form", { Controller: PropertyFormController });
registry.category("views").add("property_kanban", { Controller: PropertyKanbanController });
registry.category("views").add("property_list", { Controller: PropertyListController });