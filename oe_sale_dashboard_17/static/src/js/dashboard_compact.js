/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class OSUSExecutiveSalesDashboardCompact extends Component {
    static template = "oe_sale_dashboard_17.DashboardCompact";

    setup() {
        this.action = useService("action");
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        
        this.state = useState({
            loading: true,
            currentTab: 'overview',
            selectedSalesTypes: [],
            availableSalesTypes: [],
            dateRange: {
                start: this.getDefaultStartDate(),
                end: this.getDefaultEndDate()
            },
            data: {
                total_sales: 0,
                monthly_sales: 0,
                total_customers: 0,
                monthly_orders: 0,
                charts: {
                    monthly_sales: [],
                    sales_by_type: [],
                    project_analysis: [],
                    agent_ranking: [],
                    invoice_status: []
                }
            }
        });

        onMounted(this.loadDashboard);
    }

    getDefaultStartDate() {
        // Default to 12 months ago
        const date = new Date();
        date.setFullYear(date.getFullYear() - 1);
        return date.toISOString().split('T')[0];
    }

    getDefaultEndDate() {
        // Default to today
        return new Date().toISOString().split('T')[0];
    }

    onSalesTypeChange(event) {
        const salesTypeId = parseInt(event.target.value);
        const isChecked = event.target.checked;
        
        if (isChecked) {
            if (!this.state.selectedSalesTypes.includes(salesTypeId)) {
                this.state.selectedSalesTypes.push(salesTypeId);
            }
        } else {
            const index = this.state.selectedSalesTypes.indexOf(salesTypeId);
            if (index > -1) {
                this.state.selectedSalesTypes.splice(index, 1);
            }
        }
        
        this.loadDashboard();
    }

    clearSalesTypeFilter() {
        this.state.selectedSalesTypes = [];
        this.loadDashboard();
    }

    async loadDashboard() {
        try {
            this.state.loading = true;
            
            // Prepare parameters
            const params = {
                start_date: this.state.dateRange.start,
                end_date: this.state.dateRange.end,
                sales_type_ids: this.state.selectedSalesTypes.length > 0 ? this.state.selectedSalesTypes : null
            };
            
            const data = await this.rpc("/web/dataset/call_kw", {
                model: "sale.order",
                method: "get_dashboard_data_enhanced",
                args: [params],
                kwargs: {}
            });
            
            // Update state with enhanced data structure
            this.state.data = {
                total_sales: data.total_sales || 0,
                monthly_sales: data.monthly_sales || 0,
                total_customers: data.total_customers || 0,
                monthly_orders: data.monthly_orders || 0,
                charts: data.charts || {}
            };
            
            this.state.availableSalesTypes = data.sales_types || [];
            this.state.loading = false;
            
            // Load charts after DOM is ready
            setTimeout(() => {
                this.renderCharts();
            }, 100);
            
        } catch (error) {
            console.error("Dashboard loading error:", error);
            this.notification.add(_t("Failed to load dashboard data"), {
                type: "danger"
            });
            this.state.loading = false;
        }
    }

    setActiveTab(tab) {
        this.state.currentTab = tab;
        setTimeout(() => {
            this.renderCharts();
        }, 100);
    }

    renderCharts() {
        if (typeof Chart === 'undefined') {
            console.warn("Chart.js not loaded, using simple charts");
            this.renderSimpleCharts();
            return;
        }

        this.destroyExistingCharts();

        // Chart configurations with AED currency
        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            if (context.dataset.label && context.dataset.label.includes('Sales')) {
                                return `${context.dataset.label}: ${context.parsed.y} AED`;
                            }
                            return `${context.dataset.label}: ${context.parsed.y}`;
                        }
                    }
                }
            }
        };

        // Render charts based on current tab
        if (this.state.currentTab === 'overview') {
            this.renderOverviewCharts(chartOptions);
        } else if (this.state.currentTab === 'projects') {
            this.renderProjectCharts(chartOptions);
        } else if (this.state.currentTab === 'agents') {
            this.renderAgentCharts(chartOptions);
        } else if (this.state.currentTab === 'invoicing') {
            this.renderInvoiceCharts(chartOptions);
        }
    }

    renderOverviewCharts(options) {
        // Monthly Sales Chart
        const monthlyCtx = this.el?.querySelector('#monthlyChart');
        if (monthlyCtx) {
            this.monthlyChart = new Chart(monthlyCtx, {
                type: 'line',
                data: {
                    labels: this.state.data.charts.monthly_sales.map(item => item.month),
                    datasets: [{
                        label: 'Monthly Sales',
                        data: this.state.data.charts.monthly_sales.map(item => item.amount),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    }]
                },
                options: options
            });
        }

        // Sales by Type Chart
        const typeCtx = this.el?.querySelector('#salesTypeChart');
        if (typeCtx) {
            this.salesTypeChart = new Chart(typeCtx, {
                type: 'doughnut',
                data: {
                    labels: this.state.data.charts.sales_by_type.map(item => item.type),
                    datasets: [{
                        data: this.state.data.charts.sales_by_type.map(item => item.amount),
                        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
                    }]
                },
                options: options
            });
        }
    }

    renderProjectCharts(options) {
        const projectCtx = this.el?.querySelector('#projectChart');
        if (projectCtx) {
            this.projectChart = new Chart(projectCtx, {
                type: 'bar',
                data: {
                    labels: this.state.data.charts.project_analysis.map(item => item.project_name),
                    datasets: [{
                        label: 'Project Sales',
                        data: this.state.data.charts.project_analysis.map(item => item.amount),
                        backgroundColor: '#10b981'
                    }]
                },
                options: options
            });
        }
    }

    renderAgentCharts(options) {
        const agentCtx = this.el?.querySelector('#agentChart');
        if (agentCtx) {
            this.agentChart = new Chart(agentCtx, {
                type: 'horizontalBar',
                data: {
                    labels: this.state.data.charts.agent_ranking.map(item => item.agent_name),
                    datasets: [{
                        label: 'Agent Sales',
                        data: this.state.data.charts.agent_ranking.map(item => item.amount),
                        backgroundColor: '#8b5cf6'
                    }]
                },
                options: options
            });
        }
    }

    renderInvoiceCharts(options) {
        const invoiceCtx = this.el?.querySelector('#invoiceChart');
        if (invoiceCtx) {
            this.invoiceChart = new Chart(invoiceCtx, {
                type: 'pie',
                data: {
                    labels: this.state.data.charts.invoice_status.map(item => item.status),
                    datasets: [{
                        data: this.state.data.charts.invoice_status.map(item => item.count),
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#6b7280']
                    }]
                },
                options: options
            });
        }
    }

    renderSimpleCharts() {
        // Fallback rendering for when Chart.js is not available
        console.log("Rendering simple charts fallback");
        // Could implement basic SVG charts here if needed
    }

    destroyExistingCharts() {
        if (this.monthlyChart) this.monthlyChart.destroy();
        if (this.salesTypeChart) this.salesTypeChart.destroy();
        if (this.projectChart) this.projectChart.destroy();
        if (this.agentChart) this.agentChart.destroy();
        if (this.invoiceChart) this.invoiceChart.destroy();
    }

    formatCurrency(amount) {
        return `${amount.toLocaleString()} AED`;
    }
}

// Register the compact dashboard
registry.category("actions").add("osus_sales_dashboard_compact", OSUSExecutiveSalesDashboardCompact);
