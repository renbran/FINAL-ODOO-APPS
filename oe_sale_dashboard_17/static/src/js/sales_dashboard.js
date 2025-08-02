/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SalesDashboard extends Component {
    static template = "oe_sale_dashboard_17.SalesDashboard";

    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        
        this.state = useState({
            loading: true,
            dateRange: {
                start: this.getDefaultStartDate(),
                end: this.getDefaultEndDate()
            },
            data: {
                performance: {},
                monthly: {},
                byState: {},
                topCustomers: {},
                salesTeam: {}
            }
        });

        onMounted(() => {
            this.initializeDashboard();
        });
    }

    async initializeDashboard() {
        try {
            await this.loadDashboardData();
            this.setupEventListeners();
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            this.notification.add('Error initializing dashboard', {
                type: 'danger'
            });
        }
    }
    }

    getDefaultStartDate() {
        const date = new Date();
        date.setMonth(date.getMonth() - 3); // Last 3 months
        return date.toISOString().split('T')[0];
    }

    getDefaultEndDate() {
        return new Date().toISOString().split('T')[0];
    }

    setupEventListeners() {
        const refreshBtn = document.getElementById('refresh_dashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        const startDateInput = document.getElementById('start_date');
        const endDateInput = document.getElementById('end_date');
        
        if (startDateInput && endDateInput) {
            startDateInput.value = this.state.dateRange.start;
            endDateInput.value = this.state.dateRange.end;
            
            startDateInput.addEventListener('change', (e) => {
                this.state.dateRange.start = e.target.value;
            });
            
            endDateInput.addEventListener('change', (e) => {
                this.state.dateRange.end = e.target.value;
            });
        }
    }

    async loadDashboardData() {
        try {
            this.state.loading = true;
            
            const promises = [
                this.loadPerformanceData(),
                this.loadMonthlyData(),
                this.loadStateData(),
                this.loadCustomersData(),
                this.loadTeamData()
            ];

            await Promise.all(promises);
            
            this.updateKPIs();
            this.renderCharts();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.notification.add('Error loading dashboard data', {
                type: 'danger'
            });
        } finally {
            this.state.loading = false;
        }
    }

    async loadPerformanceData() {
        try {
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_sales_performance_data", {
                model: 'sale.order',
                method: 'get_sales_performance_data',
                args: [this.state.dateRange.start, this.state.dateRange.end],
                kwargs: {}
            });
            this.state.data.performance = result;
        } catch (error) {
            console.error('Error loading performance data:', error);
            this.state.data.performance = {};
        }
    }

    async loadMonthlyData() {
        try {
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_monthly_fluctuation_data", {
                model: 'sale.order',
                method: 'get_monthly_fluctuation_data',
                args: [this.state.dateRange.start, this.state.dateRange.end, null],
                kwargs: {}
            });
            this.state.data.monthly = result;
        } catch (error) {
            console.error('Error loading monthly data:', error);
            this.state.data.monthly = {};
        }
    }

    async loadStateData() {
        try {
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_sales_by_state_data", {
                model: 'sale.order',
                method: 'get_sales_by_state_data',
                args: [this.state.dateRange.start, this.state.dateRange.end],
                kwargs: {}
            });
            this.state.data.byState = result;
        } catch (error) {
            console.error('Error loading state data:', error);
            this.state.data.byState = {};
        }
    }

    async loadCustomersData() {
        try {
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_top_customers_data", {
                model: 'sale.order',
                method: 'get_top_customers_data',
                args: [this.state.dateRange.start, this.state.dateRange.end, 10],
                kwargs: {}
            });
            this.state.data.topCustomers = result;
        } catch (error) {
            console.error('Error loading customers data:', error);
            this.state.data.topCustomers = {};
        }
    }

    async loadTeamData() {
        try {
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_sales_team_performance", {
                model: 'sale.order',
                method: 'get_sales_team_performance',
                args: [this.state.dateRange.start, this.state.dateRange.end],
                kwargs: {}
            });
            this.state.data.salesTeam = result;
        } catch (error) {
            console.error('Error loading team data:', error);
            this.state.data.salesTeam = {};
        }
    }

    updateKPIs() {
        const performance = this.state.data.performance;
        
        const elements = {
            'total_quotations': performance.total_quotations || 0,
            'total_orders': performance.total_orders || 0,
            'total_invoiced': performance.total_invoiced || 0,
            'total_amount': performance.total_amount || '0'
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    async renderCharts() {
        // Ensure Chart.js is available before rendering
        if (typeof Chart === 'undefined') {
            if (window.ensureChartJsAvailable) {
                try {
                    await window.ensureChartJsAvailable();
                } catch (error) {
                    console.error('Chart.js not available, using fallback charts');
                    this.renderFallbackCharts();
                    return;
                }
            } else {
                console.error('Chart.js not available and no fallback mechanism found');
                return;
            }
        }
        
        this.renderMonthlyTrendChart();
        this.renderSalesStateChart();
        this.renderTopCustomersChart();
        this.renderSalesTeamChart();
    }

    renderFallbackCharts() {
        // Use SimpleChart as fallback
        if (window.SimpleChart) {
            this.renderSimpleCharts();
        } else {
            // Show message about charts not being available
            const chartContainers = [
                'monthly_trend_chart',
                'sales_state_chart', 
                'top_customers_chart',
                'sales_team_chart'
            ];
            
            chartContainers.forEach(id => {
                const canvas = document.getElementById(id);
                if (canvas) {
                    const parent = canvas.parentElement;
                    parent.innerHTML = '<div class="alert alert-info">Chart visualization not available</div>';
                }
            });
        }
    }

    renderSimpleCharts() {
        // Implement simple chart rendering using SimpleChart
        try {
            this.renderSimpleMonthlyTrendChart();
            this.renderSimpleSalesStateChart();
            this.renderSimpleTopCustomersChart();
            this.renderSimpleSalesTeamChart();
        } catch (error) {
            console.error('Error rendering simple charts:', error);
        }
    }

    renderSimpleMonthlyTrendChart() {
        const canvas = document.getElementById('monthly_trend_chart');
        if (!canvas || !this.state.data.monthly.labels) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.data.monthly;
        
        new SimpleChart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: 'Quotations',
                        data: (data.quotations || []).map(q => q.amount || 0),
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)'
                    }
                ]
            }
        });
    }

    renderSimpleSalesStateChart() {
        const canvas = document.getElementById('sales_state_chart');
        if (!canvas || !this.state.data.byState.labels) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.data.byState;
        
        new SimpleChart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.counts || [],
                    backgroundColor: [
                        '#007bff', '#28a745', '#ffc107', '#dc3545', '#6c757d'
                    ]
                }]
            }
        });
    }

    renderSimpleTopCustomersChart() {
        const canvas = document.getElementById('top_customers_chart');
        if (!canvas || !this.state.data.topCustomers.labels) return;

        const ctx = canvas.getContext('2d');
        // Create a simple bar chart representation
        ctx.fillStyle = '#007bff';
        const data = this.state.data.topCustomers;
        const maxValue = Math.max(...(data.amounts || [1]));
        
        (data.amounts || []).forEach((amount, index) => {
            const barHeight = (amount / maxValue) * (canvas.height - 40);
            const barWidth = (canvas.width - 40) / data.amounts.length - 10;
            const x = 20 + index * (barWidth + 10);
            const y = canvas.height - 20 - barHeight;
            
            ctx.fillRect(x, y, barWidth, barHeight);
        });
    }

    renderSimpleSalesTeamChart() {
        const canvas = document.getElementById('sales_team_chart');
        if (!canvas || !this.state.data.salesTeam.labels) return;

        const ctx = canvas.getContext('2d');
        const data = this.state.data.salesTeam;
        
        new SimpleChart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.amounts || [],
                    backgroundColor: [
                        '#007bff', '#28a745', '#ffc107', '#dc3545', '#6c757d', '#17a2b8'
                    ]
                }]
            }
        });
    }

    renderMonthlyTrendChart() {
        const canvas = document.getElementById('monthly_trend_chart');
        if (!canvas || !this.state.data.monthly.labels) return;

        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.monthlyChart) {
            this.monthlyChart.destroy();
        }

        const data = this.state.data.monthly;
        
        this.monthlyChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: 'Quotations',
                        data: (data.quotations || []).map(q => q.amount || 0),
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Sales Orders',
                        data: (data.sales_orders || []).map(s => s.amount || 0),
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Invoiced Sales',
                        data: (data.invoiced_sales || []).map(i => i.amount || 0),
                        borderColor: '#ffc107',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
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
    }

    renderSalesStateChart() {
        const canvas = document.getElementById('sales_state_chart');
        if (!canvas || !this.state.data.byState.labels) return;

        const ctx = canvas.getContext('2d');
        
        if (this.stateChart) {
            this.stateChart.destroy();
        }

        const data = this.state.data.byState;
        
        this.stateChart = new Chart(ctx, {
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
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    renderTopCustomersChart() {
        const canvas = document.getElementById('top_customers_chart');
        if (!canvas || !this.state.data.topCustomers.labels) return;

        const ctx = canvas.getContext('2d');
        
        if (this.customersChart) {
            this.customersChart.destroy();
        }

        const data = this.state.data.topCustomers;
        
        this.customersChart = new Chart(ctx, {
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
    }

    renderSalesTeamChart() {
        const canvas = document.getElementById('sales_team_chart');
        if (!canvas || !this.state.data.salesTeam.labels) return;

        const ctx = canvas.getContext('2d');
        
        if (this.teamChart) {
            this.teamChart.destroy();
        }

        const data = this.state.data.salesTeam;
        
        this.teamChart = new Chart(ctx, {
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
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    async refreshData() {
        await this.loadDashboardData();
        this.notification.add('Dashboard refreshed successfully', {
            type: 'success'
        });
    }
}

// Register the component with the action registry
registry.category("actions").add("sales_dashboard", SalesDashboard);
