/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";

export class PropertyListController extends ListController {
    setup() {
        super.setup();
        this.action = useService("action");
        this.notification = useService("notification");
    }

    async openRecord(record) {
        try {
            await this.action.doAction({
                type: 'ir.actions.act_window',
                res_model: this.props.resModel,
                views: [[false, 'form']],
                res_id: record.resId,
                target: 'current',
            });
        } catch (error) {
            this.notification.add("Error opening property", {
                type: "danger",
                message: error.message
            });
        }
    }
}