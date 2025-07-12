/** @odoo-module **/

import { FormController, FormView } from "@web/views/form/form_view";
import { KanbanController, KanbanView, KanbanRecord } from "@web/views/kanban/kanban_view";
import { ListController, ListView } from "@web/views/list/list_view";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

// Property Form Controller
class PropertyFormController extends FormController {
    setup() {
        super.setup();
        this.notification = useService("notification");
    }

    onCustomAction() {
        this.notification.add(this.env._t("Success"), {
            message: this.env._t("Action completed successfully"),
            type: 'success',
        });
    }
}

registry.category("views").add("property_form", {
    Controller: PropertyFormController,
    View: FormView,
});

// Property Kanban Components
class PropertyKanbanRecord extends KanbanRecord {
    static template = "web.KanbanRecord";
    
    onClick(ev) {
        if (this.props.record.resModel === 'property.property') {
            this.trigger('open-property-form', { resId: this.props.record.resId });
        } else {
            super.onClick(ev);
        }
    }
}

class PropertyKanbanController extends KanbanController {
    setup() {
        super.setup();
        this.action = useService("action");
        this.env.bus.addEventListener('open-property-form', this.onOpenPropertyForm);
    }

    onOpenPropertyForm = (ev) => {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'property.property',
            views: [[false, 'form']],
            res_id: ev.detail.resId,
            target: 'current',
        });
    }
}

registry.category("views").add("property_kanban", {
    Controller: PropertyKanbanController,
    View: KanbanView,
    Record: PropertyKanbanRecord,
});

// Property List Components
class PropertyListController extends ListController {
    setup() {
        super.setup();
        this.action = useService("action");
        this.env.bus.addEventListener('open-property-sale', this.onOpenPropertySale);
    }

    onOpenPropertySale = (ev) => {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'property.sale',
            views: [[false, 'form']],
            res_id: ev.detail.resId,
            target: 'current',
        });
    }
}

registry.category("views").add("property_list", {
    Controller: PropertyListController,
    View: ListView,
});