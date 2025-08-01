/** @odoo-module **/
/* This module is under copyright of 'OdooElevate' */

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * Field Mapping and Validation
 */
class FieldMapping {
    constructor() {
        this.fieldMapping = {
            // Date fields - prefer booking_date if available
            booking_date: 'booking_date',
            date_order: 'date_order',
            
            // Amount fields - prefer sale_value if available  
            sale_value: 'sale_value',
            amount_total: 'amount_total',
            amount_untaxed: 'amount_untaxed',
            
            // Commission fields
            agent1_partner_id: 'agent1_partner_id',
            agent1_amount: 'agent1_amount',
            broker_partner_id: 'broker_partner_id',
            broker_amount: 'broker_amount',
            
            // Sales type field
            sale_order_type_id: 'sale_order_type_id',
            
            // Track available fields
            _available: {}
        };
    }

    async initialize(orm) {
        if (!orm) {
            console.error('ORM service not available for field mapping');
            return;
        }
        
        try {
            const fieldsToCheck = [
                'booking_date', 'sale_value', 'date_order', 'amount_total', 
                'sale_order_type_id', 'agent1_partner_id', 'agent1_amount',
                'broker_partner_id', 'broker_amount'
            ];
            
            const fields = await orm.call('sale.order', 'fields_get', [fieldsToCheck]);
            
            // Update available fields
            fieldsToCheck.forEach(field => {
                this.fieldMapping._available[field] = !!fields[field];
            });
            
            console.log('Dashboard field availability:', this.fieldMapping._available);
            
            // Set fallbacks
            if (!this.fieldMapping._available.booking_date) {
                console.warn('booking_date not found, using date_order as fallback');
                this.fieldMapping.booking_date = 'date_order';
            }
            
            if (!this.fieldMapping._available.sale_value) {
                console.warn('sale_value not found, using amount_total as fallback');
                this.fieldMapping.sale_value = 'amount_total';
            }
            
        } catch (error) {
            console.error('Error initializing field mapping:', error);
        }
    }

    getFieldName(fieldName) {
        return this.fieldMapping[fieldName] || fieldName;
    }

    isFieldAvailable(fieldName) {
        return !!this.fieldMapping._available[fieldName];
    }

    buildDateDomain(startDate, endDate) {
        const dateField = this.getFieldName('booking_date');
        return [
            [dateField, '>=', startDate],
            [dateField, '<=', endDate]
        ];
    }
}

/**
 * Chart.js Fallback and Management
 */
class ChartManager {
    constructor() {
        this.charts = {};
        this.isChartJsReady = false;
    }

    async ensureChartJs() {
        if (typeof Chart !== 'undefined') {
            this.isChartJsReady = true;
            return true;
        }

        // Try fallback sources
        const fallbackSources = [
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.js',
            'https://unpkg.com/chart.js@4.4.0/dist/chart.umd.js'
        ];

        for (const source of fallbackSources) {
            try {
                await this.loadScript(source);
                if (typeof Chart !== 'undefined') {
                    this.isChartJsReady = true;
                    console.log(`Chart.js loaded from ${source}`);
                    return true;
                }
            } catch (error) {
                console.warn(`Failed to load Chart.js from ${source}`);
            }
        }

        console.error('Failed to load Chart.js from any source');
        return false;
    }

    loadScript(url) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = url;
            script.async = true;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    createChart(canvasId, config) {
        if (!this.isChartJsReady) {
            console.warn('Chart.js not available');
            return null;
        }

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.warn(`Canvas element ${canvasId} not found`);
            return null;
        }

        try {
            // Destroy existing chart if any
            if (this.charts[canvasId]) {
                this.charts[canvasId].destroy();
            }

            this.charts[canvasId] = new Chart(canvas, config);
            return this.charts[canvasId];
        } catch (error) {
            console.error(`Error creating chart ${canvasId}:`, error);
            return null;
        }
    }

    destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
            delete this.charts[canvasId];
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(canvasId => {
            this.destroyChart(canvasId);
        });
    }
}

/**
 * Main Dashboard Component
 */
class OeSaleDashboard extends Component {
    static template = "oe_sale_dashboard_17.yearly_sales_dashboard_template";
    
    setup() {
        super.setup();
        
        // Initialize services
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        // Initialize managers
        this.fieldMapping = new FieldMapping();
        this.chartManager = new ChartManager();
        
        // Color palette
        this.colorPalette = {
            primary: { background: 'rgba(139, 0, 0, 0.8)', border: 'rgba(139, 0, 0, 1)' },
            secondary: { background: 'rgba(114, 47, 55, 0.8)', border: 'rgba(114, 47, 55, 1)' },
            accent: { background: 'rgba(212, 175, 55, 0.8)', border: 'rgba(212, 175, 55, 1)' },
            success: { background: 'rgba(34, 197, 94, 0.8)', border: 'rgba(34, 197, 94, 1)' },
            warning: { background: 'rgba(251, 191, 36, 0.8)', border: 'rgba(251, 191, 36, 1)' },
            info: { background: 'rgba(59, 130, 246, 0.8)', border: 'rgba(59, 130, 246, 1)' }
        };
        
        // Initialize state
        const today = new Date().toISOString().split('T')[0];
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        const startDate = thirtyDaysAgo.toISOString().split('T')[0];
        
        this.state = useState({
            startDate: startDate,
            endDate: today,
            selectedSalesTypes: [],
            salesTypes: [],
            isLoading: true,
            hasError: false,
            errorMessage: '',
            // Dashboard data
            summaryData: {
                totalQuotations: { count: 0, amount: 0, formatted: '$0' },
                totalSalesOrders: { count: 0, amount: 0, formatted: '$0' },
                totalInvoiced: { count: 0, amount: 0, formatted: '$0' },
                conversionRate: '0%',
                avgDealSize: '$0',
                revenueGrowth: '0%',
                pipelineVelocity: '0 days',
                categories: {}
            },
            categoriesData: {},
            categoryNames: [],
            monthlyFluctuationData: { labels: [], quotations: [], sales_orders: [], invoiced_sales: [] },
            salesTypeDistribution: { count_distribution: {}, amount_distribution: {} },
            topAgentsData: [],
            topAgenciesData: [],
            recentOrders: [],
            // Additional arrays needed by template
            rankingData: [],
            quotationsData: [],
            salesOrdersData: [],
            invoicedSalesData: []
        });
        
        // Initialize dashboard on mount
        onMounted(async () => {
            await this._initializeDashboard();
        });
        
        // Cleanup on unmount
        onWillUnmount(() => {
            this.chartManager.destroyAllCharts();
        });
    }
    
    async _initializeDashboard() {
        try {
            this.state.isLoading = true;
            this.state.hasError = false;
            
            console.log('Initializing dashboard...');
            
            // Initialize field mapping
            await this.fieldMapping.initialize(this.orm);
            
            // Ensure Chart.js is available
            await this.chartManager.ensureChartJs();
            
            // Load sales types if available
            await this._loadSalesTypes();
            
            // Load dashboard data
            await this._loadDashboardData();
            
            // Load top performers data
            await this._loadTopPerformersData();
            
            // Create charts after a short delay to ensure DOM is ready
            setTimeout(() => this._createCharts(), 100);
            
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.state.hasError = true;
            this.state.errorMessage = 'Failed to initialize dashboard: ' + error.message;
            this.notification.add(_t("Failed to load dashboard"), { type: 'danger' });
        } finally {
            this.state.isLoading = false;
        }
    }
    
    async _loadSalesTypes() {
        try {
            if (this.fieldMapping.isFieldAvailable('sale_order_type_id')) {
                const salesTypes = await this.orm.searchRead(
                    'sale.order.type',
                    [],
                    ['id', 'name'],
                    { limit: 100 }
                );
                this.state.salesTypes = salesTypes;
                console.log('Loaded sales types:', salesTypes.length);
            } else {
                console.log('Sales types not available, using default functionality');
                this.state.salesTypes = [];
            }
        } catch (error) {
            console.warn('Could not load sales types:', error);
            this.state.salesTypes = [];
        }
    }
    
    async _loadDashboardData() {
        try {
            console.log('Loading dashboard data...');
            
            // Try to use backend methods first, fallback to direct queries
            let dashboardData;
            try {
                dashboardData = await this.orm.call(
                    'sale.order',
                    'get_dashboard_summary_data',
                    [this.state.startDate, this.state.endDate, this.state.selectedSalesTypes]
                );
            } catch (backendError) {
                console.warn('Backend method not available, using fallback:', backendError);
                dashboardData = await this._loadDashboardDataFallback();
            }
            
            if (dashboardData.error) {
                throw new Error(dashboardData.error);
            }
            
            // Process the data
            this._processDashboardData(dashboardData);
            
            // Load additional chart data
            await this._loadChartData();
            
            // Load ranking and detailed data arrays
            await this._loadRankingData();
            
            // Load separated data arrays for template
            this._populateDataArrays();
            
            // Load top performers data
            await this._loadTopPerformersData();
            
            // Load recent orders
            await this._loadRecentOrders();
            
            console.log('Dashboard data loaded successfully');
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            throw error;
        }
    }
    
    async _loadDashboardDataFallback() {
        // Fallback implementation using direct ORM queries
        const dateDomain = this.fieldMapping.buildDateDomain(this.state.startDate, this.state.endDate);
        
        // Load quotations (draft and sent states)
        const quotations = await this.orm.searchRead(
            'sale.order',
            [...dateDomain, ['state', 'in', ['draft', 'sent']]],
            ['id', 'amount_total', 'state'],
            { limit: false }
        );
        
        // Load sales orders (confirmed state)
        const salesOrders = await this.orm.searchRead(
            'sale.order',
            [...dateDomain, ['state', '=', 'sale']],
            ['id', 'amount_total', 'state', 'invoice_status'],
            { limit: false }
        );
        
        // Filter invoiced orders
        const invoicedOrders = salesOrders.filter(order => order.invoice_status === 'invoiced');
        
        // Calculate totals
        const quotationsTotal = quotations.reduce((sum, q) => sum + (q.amount_total || 0), 0);
        const salesOrdersTotal = salesOrders.reduce((sum, s) => sum + (s.amount_total || 0), 0);
        const invoicedTotal = invoicedOrders.reduce((sum, i) => sum + (i.amount_total || 0), 0);
        
        return {
            totals: {
                draft_count: quotations.length,
                draft_amount: quotationsTotal,
                sales_order_count: salesOrders.length,
                sales_order_amount: salesOrdersTotal,
                invoice_count: invoicedOrders.length,
                invoice_amount: invoicedTotal,
                conversion_rate: quotations.length > 0 ? (salesOrders.length / quotations.length) * 100 : 0,
                avg_deal_size: salesOrders.length > 0 ? salesOrdersTotal / salesOrders.length : 0,
                revenue_growth: 0, // Would need historical data
                pipeline_velocity: 0 // Would need date calculations
            },
            categories: {} // Would need additional queries for categories
        };
    }
    
    _processDashboardData(dashboardData) {
        const totals = dashboardData.totals || {};
        
        // Update summary data
        this.state.summaryData = {
            totalQuotations: {
                count: totals.draft_count || 0,
                amount: totals.draft_amount || 0,
                formatted: this._formatCurrency(totals.draft_amount || 0)
            },
            totalSalesOrders: {
                count: totals.sales_order_count || 0,
                amount: totals.sales_order_amount || 0,
                formatted: this._formatCurrency(totals.sales_order_amount || 0)
            },
            totalInvoiced: {
                count: totals.invoice_count || 0,
                amount: totals.invoice_amount || 0,
                formatted: this._formatCurrency(totals.invoice_amount || 0)
            },
            conversionRate: totals.conversion_rate ? totals.conversion_rate.toFixed(1) + '%' : '0%',
            avgDealSize: this._formatCurrency(totals.avg_deal_size || 0),
            revenueGrowth: totals.revenue_growth ? totals.revenue_growth.toFixed(1) + '%' : '0%',
            pipelineVelocity: totals.pipeline_velocity ? totals.pipeline_velocity.toFixed(1) + ' days' : '0 days',
            categories: dashboardData.categories || {}
        };
        
        // Store categories data for charts
        this.state.categoriesData = dashboardData.categories || {};
        
        // Populate category names for safe template iteration
        this.state.categoryNames = Object.keys(dashboardData.categories || {});
        
        console.log('Processed dashboard data:', this.state.summaryData);
    }
    
    async _loadChartData() {
        try {
            // Try to load monthly fluctuation data
            try {
                const monthlyData = await this.orm.call(
                    'sale.order',
                    'get_monthly_fluctuation_data',
                    [this.state.startDate, this.state.endDate, this.state.selectedSalesTypes]
                );
                this.state.monthlyFluctuationData = monthlyData;
            } catch (error) {
                console.warn('Monthly fluctuation data not available:', error);
                this.state.monthlyFluctuationData = this._generateMockTrendData();
            }
            
            // Try to load sales type distribution
            try {
                const distributionData = await this.orm.call(
                    'sale.order',
                    'get_sales_type_distribution',
                    [this.state.startDate, this.state.endDate]
                );
                this.state.salesTypeDistribution = distributionData;
            } catch (error) {
                console.warn('Sales type distribution not available:', error);
                this.state.salesTypeDistribution = { count_distribution: {}, amount_distribution: {} };
            }
            
        } catch (error) {
            console.warn('Error loading chart data:', error);
        }
    }
    
    _generateMockTrendData() {
        // Generate mock trend data based on current summary
        const labels = [];
        const quotations = [];
        const sales_orders = [];
        const invoiced_sales = [];
        
        const startDate = new Date(this.state.startDate);
        const endDate = new Date(this.state.endDate);
        const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
        
        // Generate weekly data points
        const weeks = Math.min(Math.ceil(daysDiff / 7), 12);
        const baseQuotations = this.state.summaryData.totalQuotations.amount / weeks;
        const baseSalesOrders = this.state.summaryData.totalSalesOrders.amount / weeks;
        const baseInvoiced = this.state.summaryData.totalInvoiced.amount / weeks;
        
        for (let i = 0; i < weeks; i++) {
            const weekDate = new Date(startDate);
            weekDate.setDate(weekDate.getDate() + i * 7);
            labels.push(weekDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            
            // Add some variation
            const variation = 0.7 + Math.random() * 0.6;
            quotations.push(Math.round(baseQuotations * variation));
            sales_orders.push(Math.round(baseSalesOrders * variation));
            invoiced_sales.push(Math.round(baseInvoiced * variation));
        }
        
        return { labels, quotations, sales_orders, invoiced_sales };
    }
    
    async _loadTopPerformersData() {
        try {
            // Load top agents if fields are available
            if (this.fieldMapping.isFieldAvailable('agent1_partner_id') && 
                this.fieldMapping.isFieldAvailable('agent1_amount')) {
                try {
                    const topAgents = await this.orm.call(
                        'sale.order',
                        'get_top_performers_data',
                        [this.state.startDate, this.state.endDate, 'agent', 10]
                    );
                    this.state.topAgentsData = topAgents || [];
                } catch (error) {
                    console.warn('Top agents data not available:', error);
                    this.state.topAgentsData = [];
                }
            }
            
            // Load top agencies if fields are available
            if (this.fieldMapping.isFieldAvailable('broker_partner_id') && 
                this.fieldMapping.isFieldAvailable('broker_amount')) {
                try {
                    const topAgencies = await this.orm.call(
                        'sale.order',
                        'get_top_performers_data',
                        [this.state.startDate, this.state.endDate, 'agency', 10]
                    );
                    this.state.topAgenciesData = topAgencies || [];
                } catch (error) {
                    console.warn('Top agencies data not available:', error);
                    this.state.topAgenciesData = [];
                }
            }
            
        } catch (error) {
            console.warn('Error loading top performers:', error);
            this.state.topAgentsData = [];
            this.state.topAgenciesData = [];
        }
    }
    
    async _loadRecentOrders() {
        try {
            const dateDomain = this.fieldMapping.buildDateDomain(this.state.startDate, this.state.endDate);
            const dateField = this.fieldMapping.getFieldName('booking_date');
            const amountField = this.fieldMapping.isFieldAvailable('sale_value') ? 'sale_value' : 'amount_total';
            
            const recentOrders = await this.orm.searchRead(
                'sale.order',
                dateDomain,
                ['name', 'partner_id', dateField, amountField, 'state'],
                { 
                    limit: 10, 
                    order: `${dateField} desc` 
                }
            );
            
            this.state.recentOrders = recentOrders.map(order => ({
                id: order.id,
                name: order.name,
                partner_name: order.partner_id ? order.partner_id[1] : 'Unknown Customer',
                date: this._formatDate(order[dateField]),
                amount_formatted: this._formatCurrency(order[amountField] || 0),
                status_text: this._getStatusText(order.state),
                status_class: this._getStatusClass(order.state)
            }));
            
        } catch (error) {
            console.warn('Could not load recent orders:', error);
            this.state.recentOrders = [];
        }
    }
    
    async _loadRankingData() {
        try {
            // Load sales type ranking data if available
            const rankingData = await this.orm.call(
                'sale.order',
                'get_sales_type_ranking_data',
                [this.state.startDate, this.state.endDate, this.state.selectedSalesTypes]
            );
            this.state.rankingData = rankingData || [];
        } catch (error) {
            console.warn('Ranking data not available:', error);
            this.state.rankingData = [];
        }
    }
    
    _populateDataArrays() {
        // Populate arrays from categoriesData for template
        this.state.quotationsData = [];
        this.state.salesOrdersData = [];
        this.state.invoicedSalesData = [];
        
        if (this.state.categoriesData && typeof this.state.categoriesData === 'object') {
            for (const [categoryName, categoryData] of Object.entries(this.state.categoriesData)) {
                // Add quotations data
                if (categoryData.draft_count > 0) {
                    this.state.quotationsData.push({
                        sales_type_name: categoryName,
                        count: categoryData.draft_count,
                        amount: categoryData.draft_amount,
                        formatted_amount: this._formatCurrency(categoryData.draft_amount)
                    });
                }
                
                // Add sales orders data
                if (categoryData.sales_order_count > 0) {
                    this.state.salesOrdersData.push({
                        sales_type_name: categoryName,
                        count: categoryData.sales_order_count,
                        amount: categoryData.sales_order_amount,
                        formatted_amount: this._formatCurrency(categoryData.sales_order_amount)
                    });
                }
                
                // Add invoiced sales data
                if (categoryData.invoice_count > 0) {
                    this.state.invoicedSalesData.push({
                        sales_type_name: categoryName,
                        count: categoryData.invoice_count,
                        amount: categoryData.invoice_amount,
                        formatted_amount: this._formatCurrency(categoryData.invoice_amount)
                    });
                }
            }
        }
    }
    
    _createCharts() {
        if (!this.chartManager.isChartJsReady) {
            console.warn('Chart.js not ready, skipping chart creation');
            return;
        }
        
        this._createTrendChart();
        this._createCategoryChart();
        this._createStatusChart();
    }
    
    _createTrendChart() {
        const config = {
            type: 'line',
            data: {
                labels: this.state.monthlyFluctuationData.labels || [],
                datasets: [
                    {
                        label: 'Quotations',
                        data: this.state.monthlyFluctuationData.quotations || [],
                        borderColor: this.colorPalette.primary.border,
                        backgroundColor: this.colorPalette.primary.background,
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: 'Sales Orders',
                        data: this.state.monthlyFluctuationData.sales_orders || [],
                        borderColor: this.colorPalette.secondary.border,
                        backgroundColor: this.colorPalette.secondary.background,
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: 'Invoiced Sales',
                        data: this.state.monthlyFluctuationData.invoiced_sales || [],
                        borderColor: this.colorPalette.success.border,
                        backgroundColor: this.colorPalette.success.background,
                        tension: 0.4,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Sales Trends Over Time'
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (value) => this._formatCurrency(value)
                        }
                    }
                }
            }
        };
        
        this.chartManager.createChart('trendsLineChart', config);
    }
    
    _createCategoryChart() {
        const categories = this.state.categoriesData;
        const labels = Object.keys(categories);
        const data = labels.map(label => categories[label]?.total_amount || 0);
        
        if (labels.length === 0) return;
        
        const config = {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        this.colorPalette.primary.background,
                        this.colorPalette.secondary.background,
                        this.colorPalette.accent.background,
                        this.colorPalette.success.background,
                        this.colorPalette.warning.background,
                        this.colorPalette.info.background
                    ],
                    borderColor: [
                        this.colorPalette.primary.border,
                        this.colorPalette.secondary.border,
                        this.colorPalette.accent.border,
                        this.colorPalette.success.border,
                        this.colorPalette.warning.border,
                        this.colorPalette.info.border
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Revenue by Category'
                    },
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${context.label}: ${this._formatCurrency(value)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        };
        
        this.chartManager.createChart('enhancedPieChart', config);
    }
    
    _createStatusChart() {
        const totals = this.state.summaryData;
        
        const config = {
            type: 'bar',
            data: {
                labels: ['Quotations', 'Sales Orders', 'Invoiced'],
                datasets: [{
                    label: 'Count',
                    data: [
                        totals.totalQuotations.count,
                        totals.totalSalesOrders.count,
                        totals.totalInvoiced.count
                    ],
                    backgroundColor: [
                        this.colorPalette.warning.background,
                        this.colorPalette.info.background,
                        this.colorPalette.success.background
                    ],
                    borderColor: [
                        this.colorPalette.warning.border,
                        this.colorPalette.info.border,
                        this.colorPalette.success.border
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Orders by Status'
                    },
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
        };
        
        this.chartManager.createChart('comparisonBarChart', config);
    }
    
    // Utility methods
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
    
    formatDashboardValue(value) {
        return this._formatCurrency(value);
    }
    
    _formatDate(dateValue) {
        if (!dateValue) return '';
        const date = new Date(dateValue);
        return date.toLocaleDateString();
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
    
    // Event handlers
    async onStartDateChange(event) {
        this.state.startDate = event.target.value;
        await this._reloadDashboard();
    }
    
    async onEndDateChange(event) {
        this.state.endDate = event.target.value;
        await this._reloadDashboard();
    }
    
    async onSalesTypeFilterChange(event) {
        const selectedOptions = Array.from(event.target.selectedOptions);
        this.state.selectedSalesTypes = selectedOptions.map(option => parseInt(option.value));
        await this._reloadDashboard();
    }
    
    async _reloadDashboard() {
        try {
            this.state.isLoading = true;
            await this._loadDashboardData();
            await this._loadTopPerformersData();
            this._createCharts(); // Recreate charts with new data
            this.notification.add(_t("Dashboard updated successfully"), { type: 'success' });
        } catch (error) {
            console.error('Error reloading dashboard:', error);
            this.notification.add(_t("Failed to update dashboard"), { type: 'danger' });
        } finally {
            this.state.isLoading = false;
        }
    }
}

// Register the component
registry.category("actions").add("oe_sale_dashboard_17_action", OeSaleDashboard);

export default OeSaleDashboard;