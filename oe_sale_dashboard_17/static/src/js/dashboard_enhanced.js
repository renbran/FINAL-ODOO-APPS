/** @odoo-m        this.state = useState({
            loading: true,
            currentTab: 'overview',
            selectedSalesTypes: [],
            availableSalesTypes: [],
            dateRange: {
                start: this.getDefaultStartDate(),
                end: this.getDefaultEndDate()
            },
            data: {
                kpis: {},
                monthly: {},
                projects: {},
                agents: {},
                invoiceStatus: {},
                byState: {},
                topCustomers: {}
            }
        });rt { registry } from "@web/core/registry";
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class OSUSExecutiveSalesDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        
        this.state = useState({
            loading: true,
            activeTab: 'overview',
            dateRange: {
                start: this.getDefaultStartDate(),
                end: this.getDefaultEndDate()
            },
            data: {
                kpis: {},
                monthly: {},
                projects: {},
                agents: {},
                invoiceStatus: {},
                byState: {},
                topCustomers: {}
            }
        });

        onMounted(() => {
            this.loadAllDashboardData();
            this.setupEventListeners();
        });
    }

    getDefaultStartDate() {
        const date = new Date();
        date.setMonth(date.getMonth() - 6); // Last 6 months for better analysis
        return date.toISOString().split('T')[0];
    }

    getDefaultEndDate() {
        return new Date().toISOString().split('T')[0];
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh_dashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshAllData());
        }

        // Date inputs
        const startDateInput = document.getElementById('start_date');
        const endDateInput = document.getElementById('end_date');
        
        if (startDateInput) {
            startDateInput.addEventListener('change', (e) => {
                this.state.dateRange.start = e.target.value;
                this.loadAllDashboardData();
            });
        }
        
        if (endDateInput) {
            endDateInput.addEventListener('change', (e) => {
                this.state.dateRange.end = e.target.value;
                this.loadAllDashboardData();
            });
        }

        // Tab navigation
        document.querySelectorAll('.dashboard-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        this.state.activeTab = tabName;
        
        // Update tab UI
        document.querySelectorAll('.dashboard-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');
        
        // Show/hide content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });
        document.getElementById(`${tabName}-content`)?.style.display = 'block';
        
        // Render charts for the active tab
        setTimeout(() => this.renderChartsForTab(tabName), 100);
    }

    // Filter management methods
    async loadSalesTypes() {
        try {
            const salesTypes = await this.rpc("/web/dataset/call_kw", {
                model: "sale.order",
                method: "get_sales_order_types",
                args: [[]],
                kwargs: {}
            });
            
            this.state.availableSalesTypes = salesTypes;
            return salesTypes;
        } catch (error) {
            console.error("Error loading sales types:", error);
            return [];
        }
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
        
        // Reload data with new filter
        this.loadAllDashboardData();
    }

    clearSalesTypeFilter() {
        this.state.selectedSalesTypes = [];
        this.loadAllDashboardData();
    }

    onDateChange() {
        // Reload data when date range changes
        this.loadAllDashboardData();
    }

    async loadAllDashboardData() {
        try {
            this.state.loading = true;
            
            // Load sales types if not already loaded
            if (this.state.availableSalesTypes.length === 0) {
                await this.loadSalesTypes();
            }
            
            const promises = [
                this.loadKPIData(),
                this.loadMonthlyData(),
                this.loadProjectAnalysis(),
                this.loadAgentRanking(),
                this.loadInvoiceStatusAnalysis(),
                this.loadStateData(),
                this.loadTopCustomersData()
            ];

            await Promise.all(promises);
            
            this.updateKPICards();
            this.renderChartsForTab(this.state.activeTab);
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.notification.add('Error loading dashboard data', {
                type: 'danger'
            });
        } finally {
            this.state.loading = false;
        }
    }

    async loadKPIData() {
        try {
            const args = [this.state.dateRange.start, this.state.dateRange.end];
            // Add sales type filter if selected
            if (this.state.selectedSalesTypes.length > 0) {
                args.push(this.state.selectedSalesTypes);
            }
            
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_dashboard_kpis", {
                model: 'sale.order',
                method: 'get_dashboard_kpis',
                args: args,
                kwargs: {}
            });
            this.state.data.kpis = result;
        } catch (error) {
            console.error('Error loading KPI data:', error);
            this.state.data.kpis = {};
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

    async loadProjectAnalysis() {
        try {
            const args = [this.state.dateRange.start, this.state.dateRange.end];
            // Add sales type filter if selected
            if (this.state.selectedSalesTypes.length > 0) {
                args.push(this.state.selectedSalesTypes);
            }
            
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_project_analysis", {
                model: 'sale.order',
                method: 'get_project_analysis',
                args: args,
                kwargs: {}
            });
            this.state.data.projects = result;
        } catch (error) {
            console.error('Error loading project analysis:', error);
            this.state.data.projects = {};
        }
    }

    async loadAgentRanking() {
        try {
            const args = [this.state.dateRange.start, this.state.dateRange.end, 10];
            // Add sales type filter if selected
            if (this.state.selectedSalesTypes.length > 0) {
                args.push(this.state.selectedSalesTypes);
            }
            
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_agent_ranking", {
                model: 'sale.order',
                method: 'get_agent_ranking',
                args: args,
                kwargs: {}
            });
            this.state.data.agents = result;
        } catch (error) {
            console.error('Error loading agent ranking:', error);
            this.state.data.agents = {};
        }
    }

    async loadInvoiceStatusAnalysis() {
        try {
            const args = [this.state.dateRange.start, this.state.dateRange.end];
            // Add sales type filter if selected
            if (this.state.selectedSalesTypes.length > 0) {
                args.push(this.state.selectedSalesTypes);
            }
            
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_invoice_status_analysis", {
                model: 'sale.order',
                method: 'get_invoice_status_analysis',
                args: args,
                kwargs: {}
            });
            this.state.data.invoiceStatus = result;
        } catch (error) {
            console.error('Error loading invoice status analysis:', error);
            this.state.data.invoiceStatus = {};
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

    async loadTopCustomersData() {
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

    updateKPICards() {
        const kpis = this.state.data.kpis;
        
        const elements = {
            'total_quotations': kpis.total_quotations || 0,
            'total_orders': kpis.total_orders || 0,
            'total_invoiced': kpis.total_invoiced || 0,
            'total_amount': kpis.total_amount || '0 AED',
            'invoiced_amount': kpis.invoiced_amount || '0 AED',
            'conversion_rate': (kpis.conversion_rate || 0) + '%'
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    renderChartsForTab(tabName) {
        switch (tabName) {
            case 'overview':
                this.renderOverviewCharts();
                break;
            case 'projects':
                this.renderProjectCharts();
                break;
            case 'agents':
                this.renderAgentCharts();
                break;
            case 'invoicing':
                this.renderInvoiceCharts();
                break;
        }
    }

    renderOverviewCharts() {
        this.renderMonthlyTrendChart();
        this.renderSalesStateChart();
        this.renderTopCustomersChart();
    }

    renderProjectCharts() {
        this.renderProjectAnalysisChart();
    }

    renderAgentCharts() {
        this.renderAgentRankingChart();
        this.renderAgentPerformanceChart();
    }

    renderInvoiceCharts() {
        this.renderInvoiceStatusChart();
        this.renderInvoiceMetricsChart();
    }

    // Chart rendering methods with AED currency formatting
    renderMonthlyTrendChart() {
        const canvas = document.getElementById('monthly_trend_chart');
        if (!canvas || !this.state.data.monthly.labels) return;

        const ctx = canvas.getContext('2d');
        
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
                        label: 'Quotations (AED)',
                        data: data.quotations || [],
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Sales Orders (AED)',
                        data: data.sales_orders || [],
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Invoiced Sales (AED)',
                        data: data.invoiced_sales || [],
                        borderColor: '#f39c12',
                        backgroundColor: 'rgba(243, 156, 18, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Sales Trend (AED)'
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return new Intl.NumberFormat('en-AE', {
                                    style: 'currency',
                                    currency: 'AED',
                                    minimumFractionDigits: 0
                                }).format(value);
                            }
                        }
                    }
                }
            }
        });
    }

    renderProjectAnalysisChart() {
        const canvas = document.getElementById('project_analysis_chart');
        if (!canvas || !this.state.data.projects.labels) return;

        const ctx = canvas.getContext('2d');
        
        if (this.projectChart) {
            this.projectChart.destroy();
        }

        const data = this.state.data.projects;
        
        this.projectChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Project Sales (AED)',
                    data: data.raw_amounts || [],
                    backgroundColor: [
                        '#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6',
                        '#1abc9c', '#34495e', '#f1c40f', '#e67e22', '#95a5a6'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Sales by Project (AED)'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return new Intl.NumberFormat('en-AE', {
                                    style: 'currency',
                                    currency: 'AED',
                                    minimumFractionDigits: 0
                                }).format(value);
                            }
                        }
                    }
                }
            }
        });
    }

    renderAgentRankingChart() {
        const canvas = document.getElementById('agent_ranking_chart');
        if (!canvas || !this.state.data.agents.labels) return;

        const ctx = canvas.getContext('2d');
        
        if (this.agentChart) {
            this.agentChart.destroy();
        }

        const data = this.state.data.agents;
        
        this.agentChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Total Sales (AED)',
                    data: data.raw_sales || [],
                    backgroundColor: '#2ecc71',
                    yAxisID: 'y'
                }, {
                    label: 'Performance Score',
                    data: data.performance_scores || [],
                    backgroundColor: '#3498db',
                    type: 'line',
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Agent Performance Ranking'
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return new Intl.NumberFormat('en-AE', {
                                    style: 'currency',
                                    currency: 'AED',
                                    minimumFractionDigits: 0
                                }).format(value);
                            }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            drawOnChartArea: false,
                        },
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    renderInvoiceStatusChart() {
        const canvas = document.getElementById('invoice_status_chart');
        if (!canvas || !this.state.data.invoiceStatus.labels) return;

        const ctx = canvas.getContext('2d');
        
        if (this.invoiceChart) {
            this.invoiceChart.destroy();
        }

        const data = this.state.data.invoiceStatus;
        
        this.invoiceChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.amounts || [],
                    backgroundColor: [
                        '#2ecc71', // Invoiced - Green
                        '#f39c12', // To Invoice - Orange
                        '#3498db', // Upselling - Blue
                        '#95a5a6'  // Nothing to Invoice - Gray
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Invoice Status Distribution (AED)'
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = new Intl.NumberFormat('en-AE', {
                                    style: 'currency',
                                    currency: 'AED',
                                    minimumFractionDigits: 0
                                }).format(context.raw);
                                const percentage = data.percentages[context.dataIndex];
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Additional chart methods...
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
                        '#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Sales by State'
                    },
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
                    label: 'Sales Amount (AED)',
                    data: data.amounts || [],
                    backgroundColor: '#3498db'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Top Customers by Sales (AED)'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return new Intl.NumberFormat('en-AE', {
                                    style: 'currency',
                                    currency: 'AED',
                                    minimumFractionDigits: 0
                                }).format(value);
                            }
                        }
                    }
                }
            }
        });
    }

    async refreshAllData() {
        await this.loadAllDashboardData();
        this.notification.add('Dashboard refreshed successfully', {
            type: 'success'
        });
    }
}

OSUSExecutiveSalesDashboard.template = "oe_sale_dashboard_17.ExecutiveDashboard";

// Register the component
registry.category("actions").add("osus_executive_sales_dashboard", OSUSExecutiveSalesDashboard);
