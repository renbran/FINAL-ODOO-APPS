odoo.define('property_customization', [
    'web.FormController',
    'web.FormView',
    'web.view_registry',
    'web.core',
    'web.field_registry',
    'web.KanbanController',
    'web.KanbanView',
    'web.ListController',
    'web.ListView'
], function(
    FormController,
    FormView,
    viewRegistry,
    core,
    FieldRegistry,
    KanbanController,
    KanbanView,
    ListController,
    ListView
) {
    "use strict";

    var _t = core._t;

    var PropertyFormController = FormController.extend({
        renderButtons: function($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                // Your button rendering logic
            }
        },
        _onCustomAction: function() {
            return this.displayNotification({
                title: _t("Success"),
                message: _t("Action completed successfully"),
                type: 'success',
            });
        },
    });

    var PropertyFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: PropertyFormController,
        }),
    });

    var PropertyKanbanController = KanbanController.extend({
        custom_events: _.extend({}, KanbanController.prototype.custom_events, {
            'open_property_form': '_onOpenPropertyForm',
        }),
        _onOpenPropertyForm: function(ev) {
            ev.stopPropagation();
            return this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'property.property',
                views: [[false, 'form']],
                res_id: ev.data.res_id,
                target: 'new',
            });
        },
    });

    var PropertyKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: PropertyKanbanController,
        }),
    });

    var PropertyListController = ListController.extend({
        custom_events: _.extend({}, ListController.prototype.custom_events, {
            'open_property_sale': '_onOpenPropertySale',
        }),
        _onOpenPropertySale: function(ev) {
            ev.stopPropagation();
            return this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'property.sale',
                views: [[false, 'form']],
                res_id: ev.data.res_id,
                target: 'new',
            });
        },
    });

    var PropertyListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: PropertyListController,
        }),
    });

    var PaymentProgressWidget = FieldRegistry.get('float').extend({
        className: 'o_field_payment_progress',
        init: function() {
            this._super.apply(this, arguments);
            this.nodeOptions = this.nodeOptions || {};
        },
        _renderReadonly: function() {
            try {
                var value = this.value || 0;
                var max = this.nodeOptions.max || 100;
                var progress = Math.min(Math.max(0, value), max);
                this.$el.empty().append(
                    $('<div>').addClass('progress').append(
                        $('<div>')
                            .addClass('progress-bar')
                            .css('width', progress + '%')
                            .attr('aria-valuenow', progress)
                            .attr('aria-valuemin', 0)
                            .attr('aria-valuemax', max)
                            .text(progress + '%')
                    )
                );
            } catch (error) {
                console.error("Error rendering PaymentProgressWidget:", error);
                this.$el.text(_t("Error displaying progress"));
            }
        },
    });

    viewRegistry.add('property_form', PropertyFormView);
    viewRegistry.add('property_kanban', PropertyKanbanView);
    viewRegistry.add('property_list', PropertyListView);
    FieldRegistry.add('payment_progress', PaymentProgressWidget);

    return {
        PropertyFormController: PropertyFormController,
        PropertyFormView: PropertyFormView,
        PropertyKanbanController: PropertyKanbanController,
        PropertyKanbanView: PropertyKanbanView,
        PropertyListController: PropertyListController,
        PropertyListView: PropertyListView,
        PaymentProgressWidget: PaymentProgressWidget,
    };
});