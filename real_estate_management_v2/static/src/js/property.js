odoo.define('real_estate_management_v2.PropertyKanban', function (require) {
    "use strict";

    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');
    var viewRegistry = require('web.view_registry');

    var PropertyKanbanController = KanbanController.extend({
        custom_events: _.extend({}, KanbanController.prototype.custom_events, {
            'open_property_action': '_onOpenPropertyAction',
        }),

        _onOpenPropertyAction: function (ev) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'property.property',
                views: [[false, 'form']],
                res_id: ev.data.resId,
                target: 'current'
            });
        },
    });

    var PropertyKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: PropertyKanbanController,
        }),
    });

    viewRegistry.add('property_kanban', PropertyKanbanView);
});