/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class SalesDashboard extends Component {
    setup() {
        super.setup();
        
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            isLoading: true,
            hasError: false,
            errorMessage: '',
            startDate: this._getDefaultStartDate(),
            endDate: this._getDefaultEndDate(),
            selectedSalesType: '',
            salesTypes: [],
            kpis: {
                quotations: { value: 0, formatted: '0', count: 0 },
                sales: { value: 0, formatted: '0', count: 0 },
                invoiced: { value: 0, formatted: '0', count: 0 },
                conversionRate: '0%'
            },
            recentOrders: [],
            chartData: {
                monthly: null,
                distribution: null
            }
        });
        
        onMounted(async () => {
            await this._initializeDashboard();
        });
        
        onWillUnmount(() => {
            this._destroyCharts();
        });
    }
    
    _getDefaultStartDate() {
        const date = new Date();
        date.setMonth(date.getMonth() - 6);
        return date.toISOString().split('T')[0];
    }
    
    _getDefaultEndDate() {
        return new Date().toISOString().split('T')[0];
    }
    
    async _initializeDashboard() {
        try {
            this.state.isLoading = true;
            this.state.hasError = false;
            
            // Wait for Chart.js to be available
            await this._ensureChartJsAvailable();
            
            // Load initial data
            await Promise.all([
                this._loadSalesTypes(),
                this._loadDashboardData()
            ]);
            
            // Initialize charts after a small delay to ensure DOM is ready
            setTimeout(() => {
                this._initializeCharts();
            }, 100);
            
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this._handleError('Failed to initialize dashboard', error);
        } finally {
            this.state.isLoading = false;
        }
    }
    
    async _ensureChartJsAvailable() {
        return new Promise((resolve, reject) => {
            const maxAttempts = 30;
            let attempts = 0;
            
            const checkChartJs = () => {
                attempts++;
                
                // Check for Chart.js or our SimpleChart fallback
                if (typeof Chart !== 'undefined' || typeof SimpleChart !== 'undefined') {
                    console.log('Chart library successfully loaded');
                    resolve(true);
                    return;
                }
                
                if (attempts >= maxAttempts) {
                    console.warn('Chart.js not available, using fallback rendering');
                    resolve(false);
                    return;
                }
                
                setTimeout(checkChartJs, 200);
            };
            
            checkChartJs();
        });
    }
    
    async _loadSalesTypes() {
        try {
            // Try to load sales types if available
            const salesTypes = await this.orm.searchRead(
                'sale.order.type',
                [],
                ['id', 'name'],
                { limit: 100 }
            );
            this.state.salesTypes = salesTypes;
        } catch (error) {
            console.log('Sales types not available, using default functionality');
            this.state.salesTypes = [];
        }
    }
    
    async _loadDashboardData() {
        try {
            // Load KPI data
            await this._loadKPIData();
            
            // Load chart data
            await this._loadChartData();
            
            // Load recent orders
            await this._loadRecentOrders();
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            throw error;
        }
    }
    
    async _loadKPIData() {
        try {
            const domain = this._buildDateDomain();
            
            // Get quotations
            const quotations = await this.orm.searchRead(
                'sale.order',
                [...domain, ['state', 'in', ['draft', 'sent']]],
                ['amount_total'],
                { limit: false }
            );
            
            // Get sales orders
            const salesOrders = await this.orm.searchRead(
                'sale.order',
                [...domain, ['state', '=', 'sale']],
                ['amount_total'],
                { limit: false }
            );
            
            // Get invoiced orders
            const invoicedOrders = await this.orm.searchRead(
                'sale.order',
                [...domain, ['state', '=', 'sale'], ['invoice_status', '=', 'invoiced']],
                ['amount_total'],
                { limit: false }
            );
            
            // Calculate KPIs
            const quotationsSum = quotations.reduce((sum, q) => sum + (q.amount_total || 0), 0);
            const salesSum = salesOrders.reduce((sum, s) => sum + (s.amount_total || 0), 0);
            const invoicedSum = invoicedOrders.reduce((sum, i) => sum + (i.amount_total || 0), 0);
            
            const conversionRate = quotations.length > 0 
                ? ((salesOrders.length / quotations.length) * 100).toFixed(1) + '%'
                : '0%';
            
            this.state.kpis = {
                quotations: {
                    value: quotationsSum,
                    formatted: this._formatCurrency(quotationsSum),
                    count: quotations.length
                },
                sales: {
                    value: salesSum,
                    formatted: this._formatCurrency(salesSum),
                    count: salesOrders.length
                },
                invoiced: {
                    value: invoicedSum,
                    formatted: this._formatCurrency(invoicedSum),
                    count: invoicedOrders.length
                },
                conversionRate: conversionRate
            };
            
        } catch (error) {
            console.error('Error loading KPI data:', error);
            // Set default values on error
            this.state.kpis = {
                quotations: { value: 0, formatted: '$0', count: 0 },
                sales: { value: 0, formatted: '$0', count: 0 },
                invoiced: { value: 0, formatted: '$0', count: 0 },
                conversionRate: '0%'
            };
        }
    }
    
    async _loadChartData() {
        try {
            // Call the backend method for monthly data
            const monthlyData = await this.orm.call(
                'sale.order',
                'get_monthly_fluctuation_data',
                [this.state.startDate, this.state.endDate, this.state.selectedSalesType ? [parseInt(this.state.selectedSalesType)] : null]
            );
            
            this.state.chartData.monthly = monthlyData;
            
            // Get distribution data
            const distributionData = await this.orm.call(
                'sale.order',
                'get_sales_type_distribution',
                [this.state.startDate, this.state.endDate]
            );
            
            this.state.chartData.distribution = distributionData;
            
        } catch (error) {
            console.error('Error loading chart data:', error);
            // Set fallback data
            this.state.chartData = {
                monthly: {
                    labels: ['Current Period'],
                    quotations: [0],
                    sales_orders: [0],
                    invoiced_sales: [0]
                },
                distribution: {
                    labels: ['No Data'],
                    amounts: [1]
                }
            };
        }
    }
    
    async _loadRecentOrders() {
        try {
            const domain = this._buildDateDomain();
            const recentOrders = await this.orm.searchRead(
                'sale.order',
                domain,
                ['name', 'partner_id', 'date_order', 'amount_total', 'state'],
                { limit: 10, order: 'date_order desc' }
            );
            
            this.state.recentOrders = recentOrders.map(order => ({
                id: order.id,
                name: order.name,
                partner_name: order.partner_id[1],
                date: new Date(order.date_order).toLocaleDateString(),
                amount_formatted: this._formatCurrency(order.amount_total),
                status_text: this._getStatusText(order.state),
                status_class: this._getStatusClass(order.state)
            }));
            
        } catch (error) {
            console.error('Error loading recent orders:', error);
            this.state.recentOrders = [];
        }
    }
    
    _buildDateDomain() {
        const dateField = 'date_order'; // Fallback to standard field
        return [
            [dateField, '>=', this.state.startDate],
            [dateField, '<=', this.state.endDate],
            ['state', '!=', 'cancel']
        ];
    }
    
    _initializeCharts() {
        try {
            this._createMonthlyTrendChart();
            this._createDistributionChart();
        } catch (error) {
            console.error('Error initializing charts:', error);
            this._renderFallbackCharts();
        }
    }
    
    _createMonthlyTrendChart() {
        const canvas = document.getElementById('monthlyTrendChart');
        if (!canvas) {
            console.warn('Monthly trend chart canvas not found');
            return;
        }
        
        const ctx = canvas.getContext('2d');
        const data = this.state.chartData.monthly;
        
        if (typeof Chart !== 'undefined') {
            // Use Chart.js
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Quotations',
                            data: data.quotations,
                            borderColor: '#17a2b8',
                            backgroundColor: 'rgba(23, 162, 184, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Sales Orders',
                            data: data.sales_orders,
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Invoiced',
                            data: data.invoiced_sales,
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
                            position: 'top',
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        } else if (typeof SimpleChart !== 'undefined') {
            // Use fallback SimpleChart
            new SimpleChart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Sales Trend',
                            data: data.sales_orders,
                            borderColor: '#28a745',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)'
                        }
                    ]
                }
            });
        }
    }
    
    _createDistributionChart() {
        const canvas = document.getElementById('revenueDistributionChart');
        if (!canvas) {
            console.warn('Distribution chart canvas not found');
            return;
        }
        
        const ctx = canvas.getContext('2d');
        const data = this.state.chartData.distribution;
        
        if (typeof Chart !== 'undefined') {
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels || ['Total Revenue'],
                    datasets: [{
                        data: data.amounts || [100],
                        backgroundColor: [
                            '#FF6384',
                            '#36A2EB',
                            '#FFCE56',
                            '#4BC0C0',
                            '#9966FF',
                            '#FF9F40'
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
        } else if (typeof SimpleChart !== 'undefined') {
            new SimpleChart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels || ['Revenue'],
                    datasets: [{
                        data: data.amounts || [100],
                        backgroundColor: ['#36A2EB', '#FF6384', '#FFCE56']
                    }]
                }
            });
        }
    }
    
    _renderFallbackCharts() {
        console.log('Rendering fallback charts with basic HTML');
        
        // Simple fallback for when no chart library is available
        const trendCanvas = document.getElementById('monthlyTrendChart');
        const distCanvas = document.getElementById('revenueDistributionChart');
        
        if (trendCanvas) {
            const ctx = trendCanvas.getContext('2d');
            ctx.fillStyle = '#f8f9fa';
            ctx.fillRect(0, 0, trendCanvas.width, trendCanvas.height);
            ctx.fillStyle = '#6c757d';
            ctx.font = '16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Chart Data Available', trendCanvas.width/2, trendCanvas.height/2);
            ctx.fillText('Install Chart.js for visualization', trendCanvas.width/2, trendCanvas.height/2 + 25);
        }
        
        if (distCanvas) {
            const ctx = distCanvas.getContext('2d');
            ctx.fillStyle = '#f8f9fa';
            ctx.fillRect(0, 0, distCanvas.width, distCanvas.height);
            ctx.fillStyle = '#6c757d';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Distribution Chart', distCanvas.width/2, distCanvas.height/2);
        }
    }
    
    _destroyCharts() {
        // Cleanup charts if needed
        try {
            const canvases = ['monthlyTrendChart', 'revenueDistributionChart'];
            canvases.forEach(id => {
                const canvas = document.getElementById(id);
                if (canvas) {
                    const chart = Chart.getChart(canvas);
                    if (chart) {
                        chart.destroy();
                    }
                }
            });
        } catch (error) {
            console.log('Chart cleanup completed');
        }
    }
    
    async _onDateRangeChange() {
        await this._reloadDashboard();
    }
    
    async _onSalesTypeChange() {
        await this._reloadDashboard();
    }
    
    async _reloadDashboard() {
        try {
            this.state.isLoading = true;
            this._destroyCharts();
            await this._loadDashboardData();
            setTimeout(() => {
                this._initializeCharts();
                this.state.isLoading = false;
            }, 100);
        } catch (error) {
            this._handleError('Failed to reload dashboard', error);
        }
    }
    
    _handleError(message, error) {
        console.error(message, error);
        this.state.hasError = true;
        this.state.errorMessage = message + ': ' + (error.message || 'Unknown error');
        this.state.isLoading = false;
        
        if (this.notification) {
            this.notification.add(message, { type: 'danger' });
        }
    }
    
    _formatCurrency(value) {
        if (!value && value !== 0) return '$0';
        
        const absValue = Math.abs(value);
        if (absValue >= 1000000000) {
            return '$' + (value / 1000000000).toFixed(1) + 'B';
        } else if (absValue >= 1000000) {
            return '$' + (value / 1000000).toFixed(1) + 'M';
        } else if (absValue >= 1000) {
            return '$' + (value / 1000).toFixed(0) + 'K';
        } else {
            return '$' + value.toFixed(0);
        }
    }
    
    _getStatusText(state) {
        const statusMap = {
            'draft': 'Draft',
            'sent': 'Quotation Sent',
            'sale': 'Sales Order',
            'done': 'Locked',
            'cancel': 'Cancelled'
        };
        return statusMap[state] || state;
    }
    
    _getStatusClass(state) {
        const classMap = {
            'draft': 'secondary',
            'sent': 'info',
            'sale': 'success',
            'done': 'primary',
            'cancel': 'danger'
        };
        return classMap[state] || 'secondary';
    }
}

SalesDashboard.template = "oe_sale_dashboard_17.yearly_sales_dashboard_template";

// Register the component
registry.category("actions").add("sales_dashboard_action", SalesDashboard);

export default SalesDashboard;
