/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, onWillStart } from "@odoo/owl";
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

        onWillStart(async () => {
            console.log('[Sales Dashboard] Component starting...');
            await this.loadDashboardData();
        });

        onMounted(() => {
            console.log('[Sales Dashboard] Component mounted, setting up...');
            this.initializeDashboard();
        });
    }

    async initializeDashboard() {
        try {
            console.log('[Sales Dashboard] Initializing dashboard...');
            
            // Wait for DOM to be ready
            await this.waitForDOM();
            
            this.setupEventListeners();
            await this.loadDashboardData();
            
            console.log('[Sales Dashboard] Dashboard initialization complete');
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            this.notification.add('Error initializing dashboard: ' + error.message, {
                type: 'danger'
            });
        }
    }

    async waitForDOM() {
        return new Promise((resolve) => {
            const checkDOM = () => {
                const elements = [
                    'monthly_trend_chart',
                    'sales_state_chart', 
                    'top_customers_chart',
                    'sales_team_chart',
                    'total_quotations',
                    'total_orders',
                    'total_invoiced',
                    'total_amount'
                ];
                
                const allExist = elements.every(id => document.getElementById(id));
                
                if (allExist) {
                    console.log('[Sales Dashboard] All DOM elements found');
                    resolve();
                } else {
                    console.log('[Sales Dashboard] Waiting for DOM elements...');
                    setTimeout(checkDOM, 100);
                }
            };
            checkDOM();
        });
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
            console.log('[Sales Dashboard] Loading all dashboard data...');
            this.state.loading = true;
            
            const promises = [
                this.loadPerformanceData(),
                this.loadMonthlyData(),
                this.loadStateData(),
                this.loadCustomersData(),
                this.loadTeamData()
            ];

            await Promise.all(promises);
            
            console.log('[Sales Dashboard] All data loaded:', this.state.data);
            
            // Validate data structure
            this.validateDataStructure();
            
            // Update UI
            this.updateKPIs();
            await this.renderCharts();
            
            console.log('[Sales Dashboard] Dashboard data loading complete');
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.notification.add('Error loading dashboard data: ' + error.message, {
                type: 'danger'
            });
            
            // Try to render with fallback data anyway
            await this.renderCharts();
        } finally {
            this.state.loading = false;
        }
    }

    validateDataStructure() {
        console.log('[Sales Dashboard] Validating data structure...');
        
        // Ensure monthly data has required structure
        if (!this.state.data.monthly.labels) {
            console.warn('[Sales Dashboard] Missing monthly labels, using defaults');
            this.state.data.monthly = {
                labels: ['Jan', 'Feb', 'Mar'],
                quotations: [{amount: 0}, {amount: 0}, {amount: 0}],
                sales_orders: [{amount: 0}, {amount: 0}, {amount: 0}],
                invoiced_sales: [{amount: 0}, {amount: 0}, {amount: 0}]
            };
        }
        
        // Ensure state data has required structure
        if (!this.state.data.byState.labels) {
            console.warn('[Sales Dashboard] Missing state labels, using defaults');
            this.state.data.byState = {
                labels: ['Draft', 'Sale', 'Done'],
                counts: [0, 0, 0]
            };
        }
        
        // Ensure customers data has required structure
        if (!this.state.data.topCustomers.labels) {
            console.warn('[Sales Dashboard] Missing customer labels, using defaults');
            this.state.data.topCustomers = {
                labels: ['No customers found'],
                amounts: [0]
            };
        }
        
        // Ensure team data has required structure
        if (!this.state.data.salesTeam.labels) {
            console.warn('[Sales Dashboard] Missing team labels, using defaults');
            this.state.data.salesTeam = {
                labels: ['Unassigned'],
                amounts: [0]
            };
        }
        
        console.log('[Sales Dashboard] Data structure validation complete');
    }

    async loadPerformanceData() {
        try {
            console.log('[Sales Dashboard] Loading performance data...');
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_sales_performance_data", {
                model: 'sale.order',
                method: 'get_sales_performance_data',
                args: [this.state.dateRange.start, this.state.dateRange.end],
                kwargs: {}
            });
            console.log('[Sales Dashboard] Performance data received:', result);
            this.state.data.performance = result;
        } catch (error) {
            console.error('Error loading performance data:', error);
            this.state.data.performance = {
                total_quotations: 0,
                total_orders: 0,
                total_invoiced: 0,
                total_amount: 0
            };
        }
    }

    async loadMonthlyData() {
        try {
            console.log('[Sales Dashboard] Loading monthly data...');
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_monthly_fluctuation_data", {
                model: 'sale.order',
                method: 'get_monthly_fluctuation_data',
                args: [this.state.dateRange.start, this.state.dateRange.end, null],
                kwargs: {}
            });
            console.log('[Sales Dashboard] Monthly data received:', result);
            this.state.data.monthly = result;
        } catch (error) {
            console.error('Error loading monthly data:', error);
            this.state.data.monthly = {
                labels: [],
                quotations: [],
                sales_orders: [],
                invoiced_sales: []
            };
        }
    }

    async loadStateData() {
        try {
            console.log('[Sales Dashboard] Loading state data...');
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_sales_by_state_data", {
                model: 'sale.order',
                method: 'get_sales_by_state_data',
                args: [this.state.dateRange.start, this.state.dateRange.end],
                kwargs: {}
            });
            console.log('[Sales Dashboard] State data received:', result);
            this.state.data.byState = result;
        } catch (error) {
            console.error('Error loading state data:', error);
            this.state.data.byState = {
                labels: ['Draft', 'Sale', 'Done'],
                counts: [0, 0, 0]
            };
        }
    }

    async loadCustomersData() {
        try {
            console.log('[Sales Dashboard] Loading customers data...');
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_top_customers_data", {
                model: 'sale.order',
                method: 'get_top_customers_data',
                args: [this.state.dateRange.start, this.state.dateRange.end, 10],
                kwargs: {}
            });
            console.log('[Sales Dashboard] Customers data received:', result);
            this.state.data.topCustomers = result;
        } catch (error) {
            console.error('Error loading customers data:', error);
            this.state.data.topCustomers = {
                labels: ['Customer 1', 'Customer 2'],
                amounts: [0, 0]
            };
        }
    }

    async loadTeamData() {
        try {
            console.log('[Sales Dashboard] Loading team data...');
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_sales_team_performance", {
                model: 'sale.order',
                method: 'get_sales_team_performance',
                args: [this.state.dateRange.start, this.state.dateRange.end],
                kwargs: {}
            });
            console.log('[Sales Dashboard] Team data received:', result);
            this.state.data.salesTeam = result;
        } catch (error) {
            console.error('Error loading team data:', error);
            this.state.data.salesTeam = {
                labels: ['Sales Team'],
                amounts: [0]
            };
        }
    }

    updateKPIs() {
        console.log('[Sales Dashboard] Updating KPIs with data:', this.state.data.performance);
        
        const performance = this.state.data.performance || {};
        
        const elements = {
            'total_quotations': performance.total_quotations || performance.draft_count || 0,
            'total_orders': performance.total_orders || performance.sales_order_count || 0,
            'total_invoiced': performance.total_invoiced || performance.invoice_count || 0,
            'total_amount': this.formatCurrency(performance.total_amount || 0)
        };

        console.log('[Sales Dashboard] KPI elements to update:', elements);

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                console.log(`[Sales Dashboard] Updated ${id} with value:`, value);
            } else {
                console.warn(`[Sales Dashboard] Element ${id} not found in DOM`);
            }
        });
    }

    async renderCharts() {
        console.log('[Sales Dashboard] Starting chart rendering...');
        
        // Always try fallback charts first to ensure something renders
        console.log('[Sales Dashboard] Rendering fallback charts as primary method...');
        this.renderFallbackCharts();
        
        // Then try Chart.js if available
        let chartReady = false;
        let attempts = 0;
        const maxAttempts = 30; // 3 seconds max wait
        
        while (!chartReady && attempts < maxAttempts) {
            if (typeof Chart !== 'undefined') {
                chartReady = true;
                console.log('[Sales Dashboard] Chart.js loaded, attempting Chart.js rendering...');
                break;
            }
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        if (chartReady) {
            try {
                this.renderMonthlyTrendChart();
                this.renderSalesStateChart();
                this.renderTopCustomersChart();
                this.renderSalesTeamChart();
                console.log('[Sales Dashboard] Chart.js charts rendered successfully');
            } catch (error) {
                console.error('[Sales Dashboard] Error rendering Chart.js charts:', error);
                console.log('[Sales Dashboard] Fallback charts remain active');
            }
        } else {
            console.warn('[Sales Dashboard] Chart.js not available, using fallback charts only');
        }
        
        console.log('[Sales Dashboard] Chart rendering complete');
    }

    renderFallbackCharts() {
        console.log('[Sales Dashboard] Rendering fallback charts with data:', {
            monthly: this.state.data.monthly,
            byState: this.state.data.byState,
            topCustomers: this.state.data.topCustomers,
            salesTeam: this.state.data.salesTeam
        });
        
        // Create simple HTML-based charts
        this.renderFallbackMonthlyTrend();
        this.renderFallbackSalesState();
        this.renderFallbackTopCustomers();
        this.renderFallbackSalesTeam();
        
        console.log('[Sales Dashboard] Fallback charts rendering complete');
    }

    renderFallbackMonthlyTrend() {
        const canvas = document.getElementById('monthly_trend_chart');
        if (!canvas || !this.state.data.monthly || !this.state.data.monthly.labels) return;
        
        const data = this.state.data.monthly;
        const quotationAmounts = (data.quotations || []).map(q => q.amount || 0);
        const salesAmounts = (data.sales_orders || []).map(s => s.amount || 0);
        const invoicedAmounts = (data.invoiced_sales || []).map(i => i.amount || 0);
        
        const allAmounts = [...quotationAmounts, ...salesAmounts, ...invoicedAmounts];
        const maxValue = Math.max(...allAmounts, 1);
        
        const chartHTML = `
            <div class="fallback-chart">
                <h4>Monthly Sales Trend</h4>
                <div class="chart-lines">
                    <div class="trend-legend">
                        <span style="color: ${this.brandColors.primary}">● Quotations</span>
                        <span style="color: ${this.brandColors.gold}">● Sales Orders</span>
                        <span style="color: ${this.brandColors.success}">● Invoiced Sales</span>
                    </div>
                    <div class="chart-bars">
                        ${(data.labels || []).map((label, index) => {
                            const quotationAmount = quotationAmounts[index] || 0;
                            const salesAmount = salesAmounts[index] || 0;
                            const invoicedAmount = invoicedAmounts[index] || 0;
                            const quotationHeight = maxValue ? (quotationAmount / maxValue) * 100 : 0;
                            const salesHeight = maxValue ? (salesAmount / maxValue) * 100 : 0;
                            const invoicedHeight = maxValue ? (invoicedAmount / maxValue) * 100 : 0;
                            
                            return `
                                <div class="chart-group">
                                    <div class="bar-group">
                                        <div class="chart-bar" style="height: ${quotationHeight}%; background-color: ${this.brandColors.primary};" title="Quotations: ${this.formatCurrency(quotationAmount)}"></div>
                                        <div class="chart-bar" style="height: ${salesHeight}%; background-color: ${this.brandColors.gold};" title="Sales Orders: ${this.formatCurrency(salesAmount)}"></div>
                                        <div class="chart-bar" style="height: ${invoicedHeight}%; background-color: ${this.brandColors.success};" title="Invoiced: ${this.formatCurrency(invoicedAmount)}"></div>
                                    </div>
                                    <div class="bar-label">${label}</div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
        
        canvas.parentElement.innerHTML = chartHTML;
    }

    renderFallbackSalesState() {
        const canvas = document.getElementById('sales_state_chart');
        if (!canvas || !this.state.data.byState || !this.state.data.byState.labels) return;
        
        const data = this.state.data.byState;
        const counts = data.counts || [];
        const labels = data.labels || [];
        const total = counts.reduce((sum, count) => sum + (count || 0), 0);
        
        const chartHTML = `
            <div class="fallback-chart">
                <h4>Sales by State</h4>
                <div class="chart-pie">
                    ${labels.map((label, index) => {
                        const count = counts[index] || 0;
                        const percentage = total ? ((count / total) * 100).toFixed(1) : 0;
                        return `
                            <div class="pie-item" style="border-left-color: ${this.brandColors.chartColors[index % this.brandColors.chartColors.length]}">
                                <span class="pie-label">${label}</span>
                                <span class="pie-value">${count} (${percentage}%)</span>
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
        if (!canvas || !this.state.data.topCustomers || !this.state.data.topCustomers.labels) return;
        
        const data = this.state.data.topCustomers;
        const amounts = data.amounts || [];
        const labels = data.labels || [];
        const maxValue = Math.max(...amounts, 1);
        
        const chartHTML = `
            <div class="fallback-chart">
                <h4>Top Customers</h4>
                <div class="chart-horizontal-bars">
                    ${labels.map((customer, index) => {
                        const amount = amounts[index] || 0;
                        const width = maxValue ? ((amount / maxValue) * 100) : 0;
                        return `
                            <div class="horizontal-bar-item">
                                <div class="bar-label">${customer}</div>
                                <div class="bar-container">
                                    <div class="bar-fill" style="width: ${width}%; background-color: ${this.brandColors.chartColors[index % this.brandColors.chartColors.length]}"></div>
                                    <span class="bar-value">${this.formatCurrency(amount)}</span>
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
        if (!canvas || !this.state.data.salesTeam || !this.state.data.salesTeam.labels) return;
        
        const data = this.state.data.salesTeam;
        const amounts = data.amounts || [];
        const labels = data.labels || [];
        const maxValue = Math.max(...amounts, 1);
        
        const chartHTML = `
            <div class="fallback-chart">
                <h4>Sales Team Performance</h4>
                <div class="chart-bars">
                    ${labels.map((salesperson, index) => {
                        const amount = amounts[index] || 0;
                        const height = maxValue ? ((amount / maxValue) * 100) : 0;
                        return `
                            <div class="chart-bar" style="height: ${height}%; background-color: ${this.brandColors.chartColors[index % this.brandColors.chartColors.length]}">
                                <div class="bar-value">${this.formatCurrency(amount)}</div>
                                <div class="bar-label">${salesperson}</div>
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
        console.log('[Sales Dashboard] Refreshing data with filters:', {
            startDate: this.state.dateRange.start,
            endDate: this.state.dateRange.end
        });
        
        // Update date range from inputs if they exist
        const startDateInput = document.getElementById('start_date');
        const endDateInput = document.getElementById('end_date');
        
        if (startDateInput && startDateInput.value) {
            this.state.dateRange.start = startDateInput.value;
        }
        if (endDateInput && endDateInput.value) {
            this.state.dateRange.end = endDateInput.value;
        }
        
        console.log('[Sales Dashboard] Updated date range:', this.state.dateRange);
        
        // Test backend connectivity first
        await this.testBackendConnectivity();
        
        await this.loadDashboardData();
        this.notification.add('Dashboard refreshed successfully', {
            type: 'success'
        });
    }

    async testBackendConnectivity() {
        try {
            console.log('[Sales Dashboard] Testing backend connectivity...');
            const result = await this.rpc("/web/dataset/call_kw/sale.order/search_count", {
                model: 'sale.order',
                method: 'search_count',
                args: [[]],
                kwargs: {}
            });
            console.log('[Sales Dashboard] Backend connectivity test passed. Total sale orders:', result);
            return true;
        } catch (error) {
            console.error('[Sales Dashboard] Backend connectivity test failed:', error);
            this.notification.add('Backend connection failed: ' + error.message, {
                type: 'danger'
            });
            return false;
        }
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
