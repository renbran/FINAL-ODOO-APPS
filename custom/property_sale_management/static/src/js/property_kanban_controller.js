/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { useService } from "@web/core/utils/hooks";

export class PropertyKanbanController extends KanbanController {
    setup() {
        super.setup();
        this.action = useService("action");
        this.notification = useService("notification");
    }

    async openRecord(record) {
        try {
            await this.action.doAction({
                type: 'ir.actions.act_window',
                res_model: record.resModel,
                views: [[false, 'form']],
                res_id: record.resId,
                target: 'current',
            });
        } catch (error) {
            this.notification.add(this.env._t("Error opening property"), {
                type: "danger",
                message: error.message
            });
        }
    }
}