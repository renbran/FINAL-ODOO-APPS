/** @odoo-module **/

import { Component, useRef, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class CRMDashboardView extends Component {
    static template = "crm_dashboard.Dashboard";
    
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
        
        this.state = useState({
            isLoading: true,
            currentPeriod: 'today',
            crmData: null
        });
        
        // Chart references
        this.chartRefs = {
            overdue_chart: useRef("overdue_chart"),
            pipeline_chart: useRef("pipeline_chart"),
            lead_chart: useRef("lead_chart"),
            won_chart: useRef("won_chart"),
            yearly_chart: useRef("yearly_chart"),
            won_chart_year: useRef("won_chart_year"),
            expected_chart: useRef("expected_chart")
        };
        
        onMounted(() => {
            this.willStart();
        });
        
        onWillUnmount(() => {
            // Cleanup charts if needed
            Object.values(this.chartInstances || {}).forEach(chart => {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            });
        });
        
        this.chartInstances = {};
    }

    async willStart() {
        try {
            this.state.isLoading = true;
            await this.get_details();
            await this.render_dashboards();
            await this.render_graphs();
        } catch (error) {
            console.error("Error initializing CRM Dashboard:", error);
            this.notification.add(
                _t("Failed to load dashboard data"),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    // Convert get_data to modern async/await pattern
    async get_data() {
        try {
            const result = await this.orm.call('crm.dashboard', 'get_crm_info', []);
            this.state.crmData = result[0];
            this.crm_data = result[0]; // Keep for backward compatibility
            return result;
        } catch (error) {
            console.error("Error fetching CRM data:", error);
            this.notification.add(_t("Failed to load CRM data"), { type: "danger" });
            throw error;
        }
    }
    
    // Modernize reload function
    async reload() {
        try {
            await this.get_data();
            await this.render_dashboards();
            await this.render_graphs();
        } catch (error) {
            console.error("Error reloading dashboard:", error);
        }
    }

    // Modernize period filter functions
    async onDayClicked() {
        try {
            this.state.currentPeriod = 'today';
            await this.reload();
        } catch (error) {
            console.error("Error setting day filter:", error);
        }
    }

    async onWeekClicked() {
        try {
            this.state.currentPeriod = 'week';
            await this.reload();
        } catch (error) {
            console.error("Error setting week filter:", error);
        }
    }

    async onMonthClicked() {
        try {
            this.state.currentPeriod = 'month';
            await this.reload();
        } catch (error) {
            console.error("Error setting month filter:", error);
        }
    }

    async onYearClicked() {
        try {
            this.state.currentPeriod = 'year';
            await this.reload();
        } catch (error) {
            console.error("Error setting year filter:", error);
        }
    }

    async onLastYearClicked() {
        try {
            this.state.currentPeriod = 'last_year';
            await this.reload();
        } catch (error) {
            console.error("Error setting last year filter:", error);
        }
    }

    async onQuarterClicked() {
        try {
            this.state.currentPeriod = 'quarter';
            await this.reload();
        } catch (error) {
            console.error("Error setting quarter filter:", error);
        }
    }

    async onLastQuarterClicked() {
        try {
            this.state.currentPeriod = 'last_quarter';
            await this.reload();
        } catch (error) {
            console.error("Error setting last quarter filter:", error);
        }
    }

    // Modernize render functions
    async render_dashboards() {
        console.log("Rendering dashboards...");
        // Add dashboard rendering logic here
    }

    async render_graphs() {
        this.graph();
    }

    async get_details() {
        await this.get_data();
    }

    // Modernized action methods
    async action_overdue_opportunities(event) {
        event.stopPropagation();
        event.preventDefault();
        try {
            await this.actionService.doAction({
                name: _t("Overdue Opportunities"),
                type: 'ir.actions.act_window',
                res_model: 'crm.lead',
                view_mode: 'kanban,tree,form',
                view_type: 'form',
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                context: {                        
                    'search_default_ep_overdue': true,                   
                },
                search_view_id: this.crm_data?.crm_search_view_id,
                target: 'current'
            }, {
                onClose: () => this.willStart()
            });
        } catch (error) {
            this.notification.add(_t("Error opening overdue opportunities"), { type: "danger" });
        }
    }

    async action_my_pipeline(event) {
        event.stopPropagation();
        event.preventDefault();
        try {
            await this.actionService.doAction({
                name: _t("My Pipeline"),
                type: 'ir.actions.act_window',
                res_model: 'crm.lead',
                view_mode: 'kanban,tree,form',
                view_type: 'form',
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                context: {                        
                    'search_default_ep_my_pipeline': true,                   
                },
                search_view_id: this.crm_data?.crm_search_view_id,
                target: 'current'
            }, {
                onClose: () => this.willStart()
            });
        } catch (error) {
            this.notification.add(_t("Error opening my pipeline"), { type: "danger" });
        }
    }

    async action_open_opportunities(event) {
        event.stopPropagation();
        event.preventDefault();
        try {
            await this.actionService.doAction({
                name: _t("Open Opportunities"),
                type: 'ir.actions.act_window',
                res_model: 'crm.lead',
                view_mode: 'kanban,tree,form',
                view_type: 'form',
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                context: {                        
                    'search_default_ep_open_opportunities': true,                   
                },
                search_view_id: this.crm_data?.crm_search_view_id,
                target: 'current'
            }, {
                onClose: () => this.willStart()
            });
        } catch (error) {
            this.notification.add(_t("Error opening opportunities"), { type: "danger" });
        }
    }

    async action_won_count(event) {
        event.stopPropagation();
        event.preventDefault();
        try {
            await this.actionService.doAction({
                name: _t("Won"),
                type: 'ir.actions.act_window',
                res_model: 'crm.lead',
                view_mode: 'kanban,tree,form',
                view_type: 'form',
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
                context: {                        
                    'search_default_ep_won': true,                   
                },
                search_view_id: this.crm_data?.crm_search_view_id,
                target: 'current'
            }, {
                onClose: () => this.willStart()
            });
        } catch (error) {
            this.notification.add(_t("Error opening won opportunities"), { type: "danger" });
        }
    }

    async action_loss_count(event) {
        event.stopPropagation();
        event.preventDefault();
        try {
            await this.actionService.doAction({
                name: _t("Loss"),
                type: 'ir.actions.act_window',
                res_model: 'crm.lead',
                view_mode: 'kanban,tree,form',
                view_type: 'form',
                views: [[false, 'list'],[false, 'form']],
                context: {                        
                    'search_default_ep_lost': true,                   
                },
                search_view_id: this.crm_data?.crm_search_view_id,
                target: 'current'
            }, {
                onClose: () => this.willStart()
            });
        } catch (error) {
            this.notification.add(_t("Error opening lost opportunities"), { type: "danger" });
        }
    }

    async action_tot_exp_revenue(event) {
        event.stopPropagation();
        event.preventDefault();
        try {
            await this.actionService.doAction({
                name: _t("Expected Revenue"),
                type: 'ir.actions.act_window',
                res_model: 'crm.lead',
                view_mode: 'kanban,tree,form',
                view_type: 'form',
                views: [[false, 'kanban'],[false, 'list'],[false, 'form']],                
                search_view_id: this.crm_data?.crm_search_view_id,
                target: 'current'
            }, {
                onClose: () => this.willStart()
            });
        } catch (error) {
            this.notification.add(_t("Error opening expected revenue"), { type: "danger" });
        }
    }

    // Function which gives random color for charts.
    getRandomColor() {
        const letters = '0123456789ABCDEF'.split('');
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    // Here we are plotting bar,pie chart
    graph() {
        const ctx = this.env.root.el.querySelector('#Chart');
        if (!ctx) {
            console.warn("Chart canvas not found");
            return;
        }
        
        // Fills the canvas with white background
        Chart.plugins.register({
            beforeDraw: function(chartInstance) {
                const ctx = chartInstance.chart.ctx;
                ctx.fillStyle = "white";
                ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
            }
        });
        
        const bg_color_list = [];
        for (let i = 0; i <= 12; i++) {
            bg_color_list.push(this.getRandomColor());
        }
        
        const myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.crm_data?.graph_exp_revenue_label || [],
                datasets: [{
                    label: 'Expected Revenue',
                    data: this.crm_data?.graph_exp_revenue_dataset || [],
                    backgroundColor: bg_color_list,
                    borderColor: bg_color_list,
                    borderWidth: 1,
                    pointBorderColor: 'white',
                    pointBackgroundColor: 'red',
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    pointHitRadius: 30,
                    pointBorderWidth: 2,
                    pointStyle: 'rectRounded'
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0,
                            max: Math.max.apply(null, this.crm_data?.graph_exp_revenue_dataset || [0]),
                            stepSize: (this.crm_data?.graph_exp_revenue_dataset || [])
                                .reduce((pv, cv) => pv + (parseFloat(cv) || 0), 0) / 
                                (this.crm_data?.graph_exp_revenue_dataset?.length || 1)
                        }
                    }]
                },
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 100, // general animation time
                },
                hover: {
                    animationDuration: 500, // duration of animations when hovering an item
                },
                responsiveAnimationDuration: 500, // animation duration after a resize
                legend: {
                    display: true,
                    labels: {
                        fontColor: 'black'
                    }
                },
            },
        });
        
        // Store chart instance for cleanup
        this.chartInstances = this.chartInstances || {};
        this.chartInstances.mainChart = myChart;
    }
}

registry.category("actions").add("crm_dashboard.dashboard", CRMDashboardView);
