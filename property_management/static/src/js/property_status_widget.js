odoo.define('property_sale_management.PropertyManagement', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var viewRegistry = require('web.view_registry');
    var core = require('web.core');
    var _t = core._t;
    var FieldRegistry = require('web.field_registry');

    // Property Form Controller
    var PropertyFormController = FormController.extend({
        /**
         * @override
         */
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                // Add custom buttons or modify existing ones here
            }
        },

        /**
         * Custom method to handle property actions
         */
        _onCustomAction: function () {
            return this.displayNotification({
                title: _t("Success"),
                message: _t("Action completed successfully"),
                type: 'success',
            });
        },
    });

    // Property Form View
    var PropertyFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: PropertyFormController,
        }),
    });

    // Property Kanban Controller
    var PropertyKanbanController = require('web.KanbanController').extend({
        custom_events: _.extend({}, require('web.KanbanController').prototype.custom_events, {
            'open_property_form': '_onOpenPropertyForm',
        }),

        _onOpenPropertyForm: function (ev) {
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

    // Property Kanban View
    var PropertyKanbanView = require('web.KanbanView').extend({
        config: _.extend({}, require('web.KanbanView').prototype.config, {
            Controller: PropertyKanbanController,
        }),
    });

    // Property List Controller
    var PropertyListController = require('web.ListController').extend({
        custom_events: _.extend({}, require('web.ListController').prototype.custom_events, {
            'open_property_sale': '_onOpenPropertySale',
        }),

        _onOpenPropertySale: function (ev) {
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

    // Property List View
    var PropertyListView = require('web.ListView').extend({
        config: _.extend({}, require('web.ListView').prototype.config, {
            Controller: PropertyListController,
        }),
    });

    // Payment Progress Widget with safety checks
    var PaymentProgressWidget = FieldRegistry.get('float').extend({
        className: 'o_field_payment_progress',
        
        init: function () {
            this._super.apply(this, arguments);
            // Set defaults if nodeOptions is undefined
            this.nodeOptions = this.nodeOptions || {};
        },
        
        _renderReadonly: function () {
            try {
                var value = this.value || 0;
                var max = this.nodeOptions.max || 100;
                var progress = Math.min(Math.max(0, value), max);
                
                this.$el.empty().append(
                    $('<div>').addClass('progress')
                        .append($('<div>').addClass('progress-bar')
                            .css('width', progress + '%')
                            .attr('aria-valuenow', progress)
                            .attr('aria-valuemin', 0)
                            .attr('aria-valuemax', max)
                            .text(progress + '%'))
                );
            } catch (error) {
                console.error("Error rendering PaymentProgressWidget:", error);
                this.$el.text(_t("Error displaying progress"));
            }
        },
    });

    // Register all components
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