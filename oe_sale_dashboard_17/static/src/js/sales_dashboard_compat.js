odoo.define('oe_sale_dashboard_17.SalesDashboard', function (require) {
'use strict';

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var rpc = require('web.rpc');
var QWeb = core.qweb;

var SalesDashboard = AbstractAction.extend({
    template: 'SalesDashboardMain',
    
    init: function(parent, action) {
        this._super.apply(this, arguments);
        this.action_manager = parent;
        this.dashboardData = {};
        this.charts = {};
    },

    start: function() {
        var self = this;
        return this._super().then(function() {
            self.setupDateRange();
            self.bindEvents();
            return self.loadDashboardData();
        });
    },

    setupDateRange: function() {
        var today = new Date();
        var threeMonthsAgo = new Date();
        threeMonthsAgo.setMonth(today.getMonth() - 3);
        
        this.$('#start_date').val(this.formatDate(threeMonthsAgo));
        this.$('#end_date').val(this.formatDate(today));
    },

    formatDate: function(date) {
        return date.toISOString().split('T')[0];
    },

    bindEvents: function() {
        var self = this;
        this.$('#refresh_dashboard').on('click', function() {
            self.refreshDashboard();
        });
    },

    loadDashboardData: function() {
        var self = this;
        var startDate = this.$('#start_date').val() || this.formatDate(new Date(Date.now() - 90*24*60*60*1000));
        var endDate = this.$('#end_date').val() || this.formatDate(new Date());

        this.showLoading();

        return Promise.all([
            this.loadPerformanceData(startDate, endDate),
            this.loadMonthlyData(startDate, endDate),
            this.loadStateData(startDate, endDate),
            this.loadCustomersData(startDate, endDate),
            this.loadTeamData(startDate, endDate)
        ]).then(function() {
            self.hideLoading();
            self.updateKPIs();
            self.renderCharts();
        }).catch(function(error) {
            console.error('Error loading dashboard data:', error);
            self.hideLoading();
            self.displayError('Failed to load dashboard data');
        });
    },

    showLoading: function() {
        this.$('.dashboard_content').hide();
        this.$('.loading_indicator').show();
    },

    hideLoading: function() {
        this.$('.loading_indicator').hide();
        this.$('.dashboard_content').show();
    },

    loadPerformanceData: function(startDate, endDate) {
        var self = this;
        return rpc.query({
            model: 'sale.order',
            method: 'get_sales_performance_data',
            args: [startDate, endDate]
        }).then(function(result) {
            self.dashboardData.performance = result;
        });
    },

    loadMonthlyData: function(startDate, endDate) {
        var self = this;
        return rpc.query({
            model: 'sale.order',
            method: 'get_monthly_fluctuation_data',
            args: [startDate, endDate, null]
        }).then(function(result) {
            self.dashboardData.monthly = result;
        });
    },

    loadStateData: function(startDate, endDate) {
        var self = this;
        return rpc.query({
            model: 'sale.order',
            method: 'get_sales_by_state_data',
            args: [startDate, endDate]
        }).then(function(result) {
            self.dashboardData.byState = result;
        });
    },

    loadCustomersData: function(startDate, endDate) {
        var self = this;
        return rpc.query({
            model: 'sale.order',
            method: 'get_top_customers_data',
            args: [startDate, endDate, 10]
        }).then(function(result) {
            self.dashboardData.topCustomers = result;
        });
    },

    loadTeamData: function(startDate, endDate) {
        var self = this;
        return rpc.query({
            model: 'sale.order',
            method: 'get_sales_team_performance',
            args: [startDate, endDate]
        }).then(function(result) {
            self.dashboardData.salesTeam = result;
        });
    },

    updateKPIs: function() {
        var performance = this.dashboardData.performance || {};
        
        this.$('#total_quotations').text(performance.total_quotations || 0);
        this.$('#total_orders').text(performance.total_orders || 0);
        this.$('#total_invoiced').text(performance.total_invoiced || 0);
        this.$('#total_amount').text(performance.total_amount || '0');
        this.$('#conversion_rate').text((performance.conversion_rate || 0) + '%');
        this.$('#invoiced_amount').text(performance.invoiced_amount || '0');
    },

    renderCharts: function() {
        this.renderMonthlyChart();
        this.renderStateChart();
        this.renderCustomersChart();
        this.renderTeamChart();
    },

    renderMonthlyChart: function() {
        var canvas = this.$('#monthly_trend_chart')[0];
        if (!canvas || !this.dashboardData.monthly) return;

        var ctx = canvas.getContext('2d');
        
        if (this.charts.monthly) {
            this.charts.monthly.destroy();
        }

        var data = this.dashboardData.monthly;
        
        this.charts.monthly = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: 'Quotations',
                        data: (data.quotations || []).map(function(q) { return q.amount || 0; }),
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Sales Orders',
                        data: (data.sales_orders || []).map(function(s) { return s.amount || 0; }),
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Invoiced Sales',
                        data: (data.invoiced_sales || []).map(function(i) { return i.amount || 0; }),
                        borderColor: '#ffc107',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    },

    renderStateChart: function() {
        var canvas = this.$('#sales_state_chart')[0];
        if (!canvas || !this.dashboardData.byState) return;

        var ctx = canvas.getContext('2d');
        
        if (this.charts.state) {
            this.charts.state.destroy();
        }

        var data = this.dashboardData.byState;
        
        this.charts.state = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.counts || [],
                    backgroundColor: [
                        '#007bff',
                        '#28a745',
                        '#ffc107',
                        '#dc3545',
                        '#6c757d'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    },

    renderCustomersChart: function() {
        var canvas = this.$('#top_customers_chart')[0];
        if (!canvas || !this.dashboardData.topCustomers) return;

        var ctx = canvas.getContext('2d');
        
        if (this.charts.customers) {
            this.charts.customers.destroy();
        }

        var data = this.dashboardData.topCustomers;
        
        this.charts.customers = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Sales Amount',
                    data: data.amounts || [],
                    backgroundColor: '#007bff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    },

    renderTeamChart: function() {
        var canvas = this.$('#sales_team_chart')[0];
        if (!canvas || !this.dashboardData.salesTeam) return;

        var ctx = canvas.getContext('2d');
        
        if (this.charts.team) {
            this.charts.team.destroy();
        }

        var data = this.dashboardData.salesTeam;
        
        this.charts.team = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.amounts || [],
                    backgroundColor: [
                        '#007bff',
                        '#28a745',
                        '#ffc107',
                        '#dc3545',
                        '#6c757d',
                        '#17a2b8'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    },

    refreshDashboard: function() {
        var self = this;
        this.loadDashboardData().then(function() {
            self.displayNotification('Dashboard refreshed successfully', 'success');
        });
    },

    displayNotification: function(message, type) {
        this.do_notify(false, message);
    },

    displayError: function(message) {
        this.do_warn(false, message);
    }
});

core.action_registry.add('sales_dashboard', SalesDashboard);

return SalesDashboard;

});
