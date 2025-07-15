/** @odoo-module **/

import { Component, onWillStart, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

const actionRegistry = registry.category("actions");

export class EnterpriseDashboard extends Component {
    static template = "enterprise_dynamic_reports.DashboardTemplate";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.user = useService("user");
        this.router = useService("router");

        this.state = useState({
            isLoading: true,
            dashboardData: null,
            selectedPeriod: 'month',
            themeMode: 'light',
            showFilters: false,
            widgets: [],
            kpis: {},
            error: null,
            refreshing: false,
        });

        this.dashboardRef = useRef("dashboard");
        this.filterPanelRef = useRef("filterPanel");

        onWillStart(async () => {
            await this.loadDashboardData();
        });

        onMounted(() => {
            this.initializeTheme();
            this.setupEventListeners();
        });
    }

    async loadDashboardData() {
        try {
            this.state.isLoading = true;
            this.state.error = null;

            const dashboardData = await this.orm.call(
                "enterprise.dashboard",
                "get_dashboard_data",
                []
            );

            this.state.dashboardData = dashboardData;
            this.state.widgets = dashboardData.widgets || [];
            this.state.kpis = dashboardData.kpis || {};
            this.state.themeMode = dashboardData.dashboard_info?.theme_mode || 'light';

            // Initialize widgets
            await this.initializeWidgets();

        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.state.error = _t("Failed to load dashboard data. Please try again.");
            this.notification.add(_t("Error loading dashboard"), {
                type: "danger",
            });
        } finally {
            this.state.isLoading = false;
        }
    }

    async initializeWidgets() {
        // Initialize chart widgets and other interactive components
        for (const widget of this.state.widgets) {
            if (widget.type.includes('chart')) {
                await this.renderChart(widget);
            }
        }
    }

    async renderChart(widget) {
        const chartContainer = document.querySelector(`#widget-${widget.id} .o_enterprise_chart_container`);
        if (!chartContainer) return;

        try {
            const chartType = widget.config.chart_type || 'line';
            const chartData = widget.data;

            if (chartType === 'line' || chartType === 'bar') {
                await this.renderLineBarChart(chartContainer, chartData, chartType);
            } else if (chartType === 'pie' || chartType === 'doughnut') {
                await this.renderPieChart(chartContainer, chartData, chartType);
            }
        } catch (error) {
            console.error(`Error rendering chart for widget ${widget.id}:`, error);
        }
    }

    async renderLineBarChart(container, data, type) {
        if (!window.Chart) {
            console.error("Chart.js not loaded");
            return;
        }

        const canvas = document.createElement('canvas');
        container.appendChild(canvas);

        const chart = new Chart(canvas, {
            type: type,
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                        },
                        ticks: {
                            callback: function(value) {
                                return new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0,
                                }).format(value);
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false,
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });

        // Store chart instance for later cleanup
        container.chartInstance = chart;
    }

    async renderPieChart(container, data, type) {
        if (!window.Chart) {
            console.error("Chart.js not loaded");
            return;
        }

        const canvas = document.createElement('canvas');
        container.appendChild(canvas);

        const chart = new Chart(canvas, {
            type: type === 'pie' ? 'pie' : 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD',
                                }).format(context.raw);
                                
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.raw / total) * 100).toFixed(1);
                                
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });

        container.chartInstance = chart;
    }

    initializeTheme() {
        document.documentElement.setAttribute('data-theme', this.state.themeMode);
    }

    setupEventListeners() {
        // Add any global event listeners here
        window.addEventListener('resize', this.handleResize.bind(this));
    }

    handleResize() {
        // Handle responsive chart resizing
        this.state.widgets.forEach(widget => {
            if (widget.type.includes('chart')) {
                const container = document.querySelector(`#widget-${widget.id} .o_enterprise_chart_container`);
                if (container && container.chartInstance) {
                    container.chartInstance.resize();
                }
            }
        });
    }

    // Event handlers
    async onPeriodChange(period) {
        this.state.selectedPeriod = period;
        await this.refreshDashboard();
    }

    async onToggleTheme() {
        this.state.themeMode = this.state.themeMode === 'light' ? 'dark' : 'light';
        this.initializeTheme();
        
        // Save theme preference
        try {
            await this.orm.call("enterprise.dashboard", "update_theme", [
                this.state.dashboardData.dashboard_info.id,
                this.state.themeMode
            ]);
        } catch (error) {
            console.error("Error saving theme preference:", error);
        }
    }

    onToggleFilters() {
        this.state.showFilters = !this.state.showFilters;
    }

    async onRefreshDashboard() {
        this.state.refreshing = true;
        await this.loadDashboardData();
        this.state.refreshing = false;
        
        this.notification.add(_t("Dashboard refreshed"), {
            type: "success",
        });
    }

    async refreshDashboard() {
        try {
            this.state.refreshing = true;
            
            const dashboardData = await this.orm.call(
                "enterprise.dashboard",
                "get_dashboard_data",
                [this.state.dashboardData.dashboard_info.id]
            );

            this.state.widgets = dashboardData.widgets || [];
            this.state.kpis = dashboardData.kpis || {};
            
            // Re-initialize widgets
            setTimeout(() => {
                this.initializeWidgets();
            }, 100);

        } catch (error) {
            console.error("Error refreshing dashboard:", error);
            this.notification.add(_t("Error refreshing dashboard"), {
                type: "danger",
            });
        } finally {
            this.state.refreshing = false;
        }
    }

    // Navigation methods
    onNavigateToReport(reportType) {
        const reportActions = {
            'balance_sheet': 'enterprise_dynamic_reports.action_balance_sheet_report',
            'profit_loss': 'enterprise_dynamic_reports.action_profit_loss_report',
            'trial_balance': 'enterprise_dynamic_reports.action_trial_balance_report',
            'general_ledger': 'enterprise_dynamic_reports.action_general_ledger_report',
            'cash_flow': 'enterprise_dynamic_reports.action_cash_flow_report',
            'aged_receivables': 'enterprise_dynamic_reports.action_aged_receivables_report',
            'aged_payables': 'enterprise_dynamic_reports.action_aged_payables_report',
        };

        const actionName = reportActions[reportType];
        if (actionName) {
            this.env.services.action.doAction(actionName);
        }
    }

    async onExportDashboard(format) {
        try {
            const exportData = {
                dashboard_id: this.state.dashboardData.dashboard_info.id,
                format: format,
                include_charts: true,
            };

            const result = await this.orm.call(
                "enterprise.dashboard",
                "export_dashboard",
                [exportData]
            );

            if (result.url) {
                window.open(result.url, '_blank');
            }

            this.notification.add(_t("Dashboard exported successfully"), {
                type: "success",
            });

        } catch (error) {
            console.error("Error exporting dashboard:", error);
            this.notification.add(_t("Error exporting dashboard"), {
                type: "danger",
            });
        }
    }

    // Utility methods
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    }

    formatPercentage(value) {
        return `${value.toFixed(1)}%`;
    }

    getKpiTrendIcon(trend) {
        return trend === 'up' ? 'fa-arrow-up' : 'fa-arrow-down';
    }

    getKpiTrendClass(trend) {
        return trend === 'up' ? 'positive' : 'negative';
    }

    getWidgetSizeClass(widget) {
        const width = widget.position?.width || 4;
        const height = widget.position?.height || 2;
        
        let sizeClass = 'o_enterprise_widget_md';
        if (width <= 3) sizeClass = 'o_enterprise_widget_sm';
        else if (width >= 6) sizeClass = 'o_enterprise_widget_lg';
        else if (width >= 8) sizeClass = 'o_enterprise_widget_xl';
        else if (width >= 12) sizeClass = 'o_enterprise_widget_full';

        let heightClass = 'o_enterprise_widget_h_md';
        if (height <= 1) heightClass = 'o_enterprise_widget_h_sm';
        else if (height >= 3) heightClass = 'o_enterprise_widget_h_lg';

        return `${sizeClass} ${heightClass}`;
    }

    // Cleanup
    willUnmount() {
        window.removeEventListener('resize', this.handleResize.bind(this));
        
        // Cleanup chart instances
        this.state.widgets.forEach(widget => {
            if (widget.type.includes('chart')) {
                const container = document.querySelector(`#widget-${widget.id} .o_enterprise_chart_container`);
                if (container && container.chartInstance) {
                    container.chartInstance.destroy();
                }
            }
        });
    }
}

// Register the dashboard component
actionRegistry.add("enterprise_dashboard_main", EnterpriseDashboard);
