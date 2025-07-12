/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";  // Added missing import

export class PropertyFormController extends FormController {
    setup() {
        super.setup();
        this.action = useService("action");
        this.notification = useService("notification");
        this.orm = useService("orm");
    }
    async actionCreateSale() {
        try {
            const result = await this.orm.call(
                this.props.resModel,
                'action_create_sale',
                [this.props.resId]
            );
            
            if (result) {
                this.action.doAction({
                    type: 'ir.actions.act_window',
                    res_model: 'property.sale',
                    views: [[false, 'form']],
                    res_id: result,
                    target: 'current',
                });
            }
        } catch (error) {
            this.notification.add(this.env._t("Error creating sale"), {
                type: "danger",
                message: error.message
            });
        }
    }

    // Similar error handling for other actions
    // ...
}

registry.category("views").add("property_form", PropertyFormController);