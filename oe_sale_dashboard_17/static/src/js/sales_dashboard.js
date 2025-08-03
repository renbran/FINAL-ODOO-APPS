/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SalesDashboard extends Component {
    static template = "oe_sale_dashboard_17.SalesDashboard";

    // Brand color palette
    brandColors = {
        primary: '#800020',           // Deep Maroon/Burgundy
        gold: '#FFD700',             // Light Gold
        lightGold: '#FFF8DC',        // Light Gold Background
        darkGold: '#B8860B',         // Dark Gold
        white: '#FFFFFF',            // Pure White
        accent: '#A0522D',           // Sienna (complementary)
        success: '#228B22',          // Forest Green
        warning: '#FF8C00',          // Dark Orange
        danger: '#DC143C',           // Crimson
        
        // Chart color arrays
        chartColors: [
            '#800020',  // Primary
            '#FFD700',  // Gold
            '#A0522D',  // Accent
            '#228B22',  // Success
            '#FF8C00',  // Warning
            '#DC143C',  // Danger
            '#B8860B',  // Dark Gold
            '#8B4513'   // Saddle Brown
        ],
        
        chartBackgrounds: [
            'rgba(128, 0, 32, 0.2)',   // Primary transparent
            'rgba(255, 215, 0, 0.2)',  // Gold transparent
            'rgba(160, 82, 45, 0.2)',  // Accent transparent
            'rgba(34, 139, 34, 0.2)',  // Success transparent
            'rgba(255, 140, 0, 0.2)',  // Warning transparent
            'rgba(220, 20, 60, 0.2)',  // Danger transparent
            'rgba(184, 134, 11, 0.2)', // Dark Gold transparent
            'rgba(139, 69, 19, 0.2)'   // Saddle Brown transparent
        ]
    };

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
        // Wait for Chart.js to be available with timeout
        let chartReady = false;
        let attempts = 0;
        const maxAttempts = 50; // 5 seconds max wait
        
        while (!chartReady && attempts < maxAttempts) {
            if (typeof Chart !== 'undefined') {
                chartReady = true;
                console.log('[Sales Dashboard] Chart.js loaded successfully');
                break;
            }
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        if (!chartReady) {
            console.warn('[Sales Dashboard] Chart.js not available after timeout, using fallback');
            this.renderFallbackCharts();
            return;
        }
        
        try {
            this.renderMonthlyTrendChart();
            this.renderSalesStateChart();
            this.renderTopCustomersChart();
            this.renderSalesTeamChart();
            console.log('[Sales Dashboard] All charts rendered successfully');
        } catch (error) {
            console.error('[Sales Dashboard] Error rendering charts:', error);
            this.renderFallbackCharts();
        }
    }

    renderFallbackCharts() {
        console.log('[Sales Dashboard] Rendering fallback charts...');
        
        // Create simple HTML-based charts
        this.renderFallbackMonthlyTrend();
        this.renderFallbackSalesState();
        this.renderFallbackTopCustomers();
        this.renderFallbackSalesTeam();
    }

    renderFallbackMonthlyTrend() {
        const canvas = document.getElementById('monthly_trend_chart');
        if (!canvas || !this.state.data.charts.monthly_trend) return;
        
        const data = this.state.data.charts.monthly_trend;
        const maxValue = Math.max(...data.map(item => item.amount || 0));
        
        const chartHTML = `
            <div class="fallback-chart">
                <h4>Monthly Sales Trend</h4>
                <div class="chart-bars">
                    ${data.map(item => {
                        const height = maxValue ? ((item.amount || 0) / maxValue) * 100 : 0;
                        return `
                            <div class="chart-bar" style="height: ${height}%">
                                <div class="bar-value">${this.formatCurrency(item.amount || 0)}</div>
                                <div class="bar-label">${item.month}</div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
        
        canvas.parentElement.innerHTML = chartHTML;
    }

    renderFallbackSalesState() {
        const canvas = document.getElementById('sales_state_chart');
        if (!canvas || !this.state.data.charts.sales_state) return;
        
        const data = this.state.data.charts.sales_state;
        const total = data.reduce((sum, item) => sum + (item.count || 0), 0);
        
        const chartHTML = `
            <div class="fallback-chart">
                <h4>Sales by State</h4>
                <div class="chart-pie">
                    ${data.map((item, index) => {
                        const percentage = total ? ((item.count || 0) / total * 100).toFixed(1) : 0;
                        return `
                            <div class="pie-item" style="border-left-color: ${this.brandColors.chartColors[index % this.brandColors.chartColors.length]}">
                                <span class="pie-label">${item.state}</span>
                                <span class="pie-value">${item.count} (${percentage}%)</span>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
        
        canvas.parentElement.innerHTML = chartHTML;
    }

    renderFallbackTopCustomers() {
        const canvas = document.getElementById('top_customers_chart');
        if (!canvas || !this.state.data.charts.top_customers) return;
        
        const data = this.state.data.charts.top_customers;
        const maxValue = Math.max(...data.map(item => item.amount || 0));
        
        const chartHTML = `
            <div class="fallback-chart">
                <h4>Top Customers</h4>
                <div class="chart-horizontal-bars">
                    ${data.map((item, index) => {
                        const width = maxValue ? ((item.amount || 0) / maxValue) * 100 : 0;
                        return `
                            <div class="horizontal-bar-item">
                                <div class="bar-label">${item.customer}</div>
                                <div class="bar-container">
                                    <div class="bar-fill" style="width: ${width}%; background-color: ${this.brandColors.chartColors[index % this.brandColors.chartColors.length]}"></div>
                                    <span class="bar-value">${this.formatCurrency(item.amount || 0)}</span>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
        
        canvas.parentElement.innerHTML = chartHTML;
    }

    renderFallbackSalesTeam() {
        const canvas = document.getElementById('sales_team_chart');
        if (!canvas || !this.state.data.charts.sales_team) return;
        
        const data = this.state.data.charts.sales_team;
        const maxValue = Math.max(...data.map(item => item.amount || 0));
        
        const chartHTML = `
            <div class="fallback-chart">
                <h4>Sales Team Performance</h4>
                <div class="chart-bars">
                    ${data.map((item, index) => {
                        const height = maxValue ? ((item.amount || 0) / maxValue) * 100 : 0;
                        return `
                            <div class="chart-bar" style="height: ${height}%; background-color: ${this.brandColors.chartColors[index % this.brandColors.chartColors.length]}">
                                <div class="bar-value">${this.formatCurrency(item.amount || 0)}</div>
                                <div class="bar-label">${item.salesperson}</div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
        
        canvas.parentElement.innerHTML = chartHTML;
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
                        borderColor: this.brandColors.primary,
                        backgroundColor: this.brandColors.chartBackgrounds[0],
                        borderWidth: 3,
                        tension: 0.4
                    },
                    {
                        label: 'Sales Orders',
                        data: (data.sales_orders || []).map(s => s.amount || 0),
                        borderColor: this.brandColors.gold,
                        backgroundColor: this.brandColors.chartBackgrounds[1],
                        borderWidth: 3,
                        tension: 0.4
                    },
                    {
                        label: 'Invoiced Sales',
                        data: (data.invoiced_sales || []).map(i => i.amount || 0),
                        borderColor: this.brandColors.success,
                        backgroundColor: this.brandColors.chartBackgrounds[3],
                        borderWidth: 3,
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
                    backgroundColor: this.brandColors.chartColors,
                    borderColor: this.brandColors.white,
                    borderWidth: 2
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
                    backgroundColor: this.brandColors.chartColors,
                    borderColor: this.brandColors.primary,
                    borderWidth: 2
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
                    backgroundColor: this.brandColors.chartColors,
                    borderColor: this.brandColors.white,
                    borderWidth: 3
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

    formatCurrency(amount) {
        if (!amount && amount !== 0) return '0';
        
        // Convert to number if it's a string
        const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
        
        if (isNaN(numAmount)) return '0';
        
        // Format with currency symbol and commas
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(numAmount);
    }
}

// Register the component with the action registry
console.log('[Sales Dashboard] Registering sales_dashboard component...');
registry.category("actions").add("sales_dashboard", SalesDashboard);

// Also register with the action ID for direct access
console.log('[Sales Dashboard] Registering oe_sale_dashboard_17_action component...');
registry.category("actions").add("oe_sale_dashboard_17_action", SalesDashboard);

console.log('[Sales Dashboard] Component registration complete. Available actions:', 
    Object.keys(registry.category("actions").content));
