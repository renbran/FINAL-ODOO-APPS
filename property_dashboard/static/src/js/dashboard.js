odoo.define('property_dashboard_complete.dashboard', ['web.core', 'web.AbstractAction', 'web.view_registry'], function (core, AbstractAction, view_registry) {
    "use strict";
    
    const QWeb = core.qweb;
    const _t = core._t;
    
    const PropertyDashboard = AbstractAction.extend({
        template: 'property_dashboard_complete.PropertyDashboardMain',
        events: {
            'click .refresh_dashboard': '_onRefreshDashboard',
        },
        
        init: function(parent, action) {
            this._super.apply(this, arguments);
            this.actionManager = parent;
            this.action = action;
        },
        
        willStart: function() {
            return this._super.apply(this, arguments).then(() => {
                return this._fetchDashboardData();
            });
        },
        
        start: function() {
            return this._super.apply(this, arguments).then(() => {
                this._renderDashboard();
            });
        },
        
        _fetchDashboardData: function() {
            return this._rpc({
                model: 'property.property',
                method: 'get_dashboard_data',
                args: [],
            }).then((result) => {
                this.dashboardData = result;
            });
        },
        
        _renderDashboard: function() {
            this.$el.html(QWeb.render('property_dashboard_complete.PropertyDashboardMain', {
                widget: this,
                data: this.dashboardData,
            }));
        },
        
        _onRefreshDashboard: function() {
            this._fetchDashboardData().then(() => {
                this._renderDashboard();
            });
        },
    });
    
    view_registry.add('property_dashboard', PropertyDashboard);
    
    return PropertyDashboard;
});