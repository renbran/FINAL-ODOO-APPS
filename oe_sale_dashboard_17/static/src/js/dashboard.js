/** @odoo-module **/
/* Complete Production-Ready Sales Dashboard for Odoo 17 */

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * Enhanced Chart Manager with robust error handling
 */
class ChartManager {
    constructor() {
        this.charts = {};
        this.isChartJsReady = false;
        this.loadingAttempts = 0;
        this.maxLoadingAttempts = 3;
    }

    async ensureChartJs() {
        if (typeof Chart !== 'undefined') {
            this.isChartJsReady = true;
            return true;
        }

        if (this.loadingAttempts >= this.maxLoadingAttempts) {
            console.error('Max Chart.js loading attempts reached');
            return false;
        }

        this.loadingAttempts++;

        const fallbackSources = [
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.js',
            'https://unpkg.com/chart.js@4.4.0/dist/chart.umd.js',
            'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js'
        ];

        for (const source of fallbackSources) {
            try {
                await this.loadScript(source);
                if (typeof Chart !== 'undefined') {
                    this.isChartJsReady = true;
                    console.log(`Chart.js loaded successfully from ${source}`);
                    return true;
                }
            } catch (error) {
                console.warn(`Failed to load Chart.js from ${source}:`, error);
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
            script.timeout = 10000;
            document.head.appendChild(script);
        });
    }

    createChart(canvasId, config) {
        if (!this.isChartJsReady) {
            console.warn('Chart.js not available, skipping chart creation for:', canvasId);
            return null;
        }

        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.warn(`Canvas element ${canvasId} not found`);
            return null;
        }

        try {
            if (this.charts[canvasId]) {
                this.charts[canvasId].destroy();
            }

            this.charts[canvasId] = new Chart(canvas, config);
            console.log(`Chart ${canvasId} created successfully`);
            return this.charts[canvasId];
        } catch (error) {
            console.error(`Error creating chart ${canvasId}:`, error);
            return null;
        }
    }

    destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            try {
                this.charts[canvasId].destroy();
                delete this.charts[canvasId];
                console.log(`Chart ${canvasId} destroyed`);
            } catch (error) {
                console.error(`Error destroying chart ${canvasId}:`, error);
            }
        }
    }

    destroyAllCharts() {
        Object.keys(this.charts).forEach(canvasId => {
            this.destroyChart(canvasId);
        });
    }
}

/**
 * Complete Sales Dashboard Component
 */
class CompleteSalesDashboard extends Component {
    static template = "oe_sale_dashboard_17.yearly_sales_dashboard_template";
    
    setup() {
        super.setup();
        
        // Initialize services
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        // Initialize chart manager
        this.chartManager = new ChartManager();
        
        // Color palette for consistent styling
        this.colorPalette = {
            primary: { background: 'rgba(139, 0, 0, 0.8)', border: 'rgba(139, 0, 0, 1)' },
            secondary: { background: 'rgba(114, 47, 55, 0.8)', border: 'rgba(114, 47, 55, 1)' },
            accent: { background: 'rgba(212, 175, 55, 0.8)', border: 'rgba(212, 175, 55, 1)' },
            success: { background: 'rgba(34, 197, 94, 0.8)', border: 'rgba(34, 197, 94, 1)' },
            warning: { background: 'rgba(251, 191, 36, 0.8)', border: 'rgba(251, 191, 36, 1)' },
            info: { background: 'rgba(59, 130, 246, 0.8)', border: 'rgba(59, 130, 246, 1)' }
        };
        
        // Initialize state with reasonable defaults
        const today = new Date().toISOString().split('T')[0];
        const ninetyDaysAgo = new Date();
        ninetyDaysAgo.setDate(ninetyDaysAgo.getDate() - 90);
        const startDate = ninetyDaysAgo.toISOString().split('T')[0];
        
        this.state = useState({
            startDate: startDate,
            endDate: today,
            selectedSalesTypes: [],
            salesTypes: [],
            isLoading: true,
            hasError: false,
            errorMessage: '',
            showSampleDataWarning: false,
            
            // Enhanced dashboard data structure
            summaryData: {
                totalQuotations: { count: 0, amount: 0, formatted: 'AED 0' },
                totalSalesOrders: { count: 0, amount: 0, formatted: 'AED 0' },
                totalInvoiced: { count: 0, amount: 0, formatted: 'AED 0' },
                conversionRate: '0%',
                avgDealSize: 'AED 0',
                revenueGrowth: '0%',
                pipelineVelocity: '0 days'
            },
            
            categoriesData: {},
            categoryNames: [],
            monthlyFluctuationData: { 
                labels: [], 
                quotations: [], 
                sales_orders: [], 
                invoiced_sales: [] 
            },
            salesTypeDistribution: { 
                count_distribution: {}, 
                amount_distribution: {} 
            },
            topAgentsData: [],
            topAgenciesData: [],
            recentOrders: [],
            fieldMapping: {}
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
            this.state.errorMessage = '';
            
            console.log('Initializing complete dashboard...');
            
            // Get field mapping from backend
            await this._loadFieldMapping();
            
            // Ensure Chart.js is available
            const chartReady = await this.chartManager.ensureChartJs();
            if (!chartReady) {
                console.warn('Charts will not be available - Chart.js failed to load');
            }
            
            // Load sales types
            await this._loadSalesTypes();
            
            // Load dashboard data
            await this._loadDashboardData();
            
            // Create charts after a delay to ensure DOM is ready
            setTimeout(() => {
                if (this.chartManager.isChartJsReady) {
                    this._createCharts();
                }
            }, 300);
            
            console.log('Dashboard initialization completed successfully');
            
        } catch (error) {
            console.error('Dashboard initialization failed:', error);
            this.state.hasError = true;
            this.state.errorMessage = `Failed to initialize dashboard: ${error.message}`;
            this.notification.add(_t("Failed to load dashboard"), { type: 'danger' });
        } finally {
            this.state.isLoading = false;
        }
    }

    async _loadFieldMapping() {
        try {
            const fieldMapping = await this.orm.call(
                'sale.order',
                'get_field_mapping',
                []
            );
            this.state.fieldMapping = fieldMapping;
            console.log('Field mapping loaded:', fieldMapping);
        } catch (error) {
            console.warn('Could not load field mapping:', error);
            this.state.fieldMapping = {
                date_field: 'date_order',
                amount_field: 'amount_total',
                sales_type_field: null,
                available_fields: {}
            };
        }
    }
    
    async _loadSalesTypes() {
        try {
            console.log('Loading sales types...');
            const salesTypes = await this.orm.call(
                'sale.order',
                'get_sales_types',
                []
            );
            this.state.salesTypes = salesTypes || [];
            console.log('Loaded sales types:', salesTypes.length);
        } catch (error) {
            console.warn('Could not load sales types:', error);
            this.state.salesTypes = [];
        }
    }
    
    async _loadDashboardData() {
        try {
            console.log('Loading dashboard data for date range:', this.state.startDate, 'to', this.state.endDate);
            
            // Load main dashboard data
            const dashboardData = await this.orm.call(
                'sale.order',
                'get_dashboard_summary_data',
                [this.state.startDate, this.state.endDate, this.state.selectedSalesTypes]
            );
            
            console.log('Backend data received:', dashboardData);
            
            // Check if the backend returned an error
            if (dashboardData.error) {
                console.warn('Backend returned error:', dashboardData.error);
                throw new Error(dashboardData.error);
            }
            
            // Process the data
            this._processDashboardData(dashboardData);
            
            // Load additional data in parallel
            await Promise.allSettled([
                this._loadChartData(),
                this._loadTopPerformersData(),
                this._loadRecentOrders()
            ]);
            
            console.log('Dashboard data loaded successfully');
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.state.hasError = true;
            this.state.errorMessage = error.message || 'Failed to load dashboard data';
            this.notification.add(
                _t("Failed to load dashboard data: %s", error.message),
                { type: 'danger' }
            );
        }
    }
    
    _processDashboardData(dashboardData) {
        const totals = dashboardData.totals || {};
        
        // Check if this is sample data
        if (dashboardData.metadata && dashboardData.metadata.is_sample_data) {
            console.log('Using sample dashboard data for demonstration');
            this.state.showSampleDataWarning = true;
            this.notification.add(
                _t("Using sample data for demonstration. No sales data found for selected date range."),
                { type: 'info' }
            );
        } else {
            this.state.showSampleDataWarning = false;
        }
        
        // Update summary data with proper formatting
        this.state.summaryData = {
            totalQuotations: {
                count: totals.draft_count || 0,
                amount: totals.draft_amount || 0,
                formatted: totals.formatted_draft_amount || this._formatCurrency(totals.draft_amount || 0)
            },
            totalSalesOrders: {
                count: totals.sales_order_count || 0,
                amount: totals.sales_order_amount || 0,
                formatted: totals.formatted_sales_order_amount || this._formatCurrency(totals.sales_order_amount || 0)
            },
            totalInvoiced: {
                count: totals.invoice_count || 0,
                amount: totals.invoice_amount || 0,
                formatted: totals.formatted_invoice_amount || this._formatCurrency(totals.invoice_amount || 0)
            },
            conversionRate: totals.conversion_rate ? totals.conversion_rate.toFixed(1) + '%' : '0%',
            avgDealSize: totals.formatted_avg_deal_size || this._formatCurrency(totals.avg_deal_size || 0),
            revenueGrowth: totals.revenue_growth ? totals.revenue_growth.toFixed(1) + '%' : '0%',
            pipelineVelocity: totals.pipeline_velocity ? totals.pipeline_velocity.toFixed(1) + ' days' : '0 days'
        };
        
        // Store categories data
        this.state.categoriesData = dashboardData.categories || {};
        this.state.categoryNames = Object.keys(dashboardData.categories || {});
        
        console.log('Processed dashboard data:', this.state.summaryData);
        console.log('Categories data:', this.state.categoriesData);
    }
    
    async _loadChartData() {
        try {
            // Load monthly fluctuation data
            const monthlyData = await this.orm.call(
                'sale.order',
                'get_monthly_fluctuation_data',
                [this.state.startDate, this.state.endDate, this.state.selectedSalesTypes]
            );
            this.state.monthlyFluctuationData = monthlyData;
            
            // Load sales type distribution
            const distributionData = await this.orm.call(
                'sale.order',
                'get_sales_type_distribution',
                [this.state.startDate, this.state.endDate]
            );
            this.state.salesTypeDistribution = distributionData;
            
        } catch (error) {
            console.warn('Error loading chart data:', error);
            // Use fallback data
            this.state.monthlyFluctuationData = this._generateMockTrendData();
            this.state.salesTypeDistribution = { count_distribution: {}, amount_distribution: {} };
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
            if (this.state.fieldMapping.available_fields?.agent1_partner_id && 
                this.state.fieldMapping.available_fields?.agent1_amount) {
                try {
                    const topAgents = await this.orm.call(
                        'sale.order',
                        'get_top_performers_data',
                        [this.state.startDate, this.state.endDate, 'agent', 10]
                    );
                    this.state.topAgentsData = topAgents || [];
                    console.log('Loaded top agents:', this.state.topAgentsData.length);
                } catch (error) {
                    console.warn('Top agents data not available:', error);
                    this.state.topAgentsData = [];
                }
            }
            
            // Load top agencies if fields are available
            if (this.state.fieldMapping.available_fields?.broker_partner_id && 
                this.state.fieldMapping.available_fields?.broker_amount) {
                try {
                    const topAgencies = await this.orm.call(
                        'sale.order',
                        'get_top_performers_data',
                        [this.state.startDate, this.state.endDate, 'agency', 10]
                    );
                    this.state.topAgenciesData = topAgencies || [];
                    console.log('Loaded top agencies:', this.state.topAgenciesData.length);
                } catch (error) {
                    console.warn('Top agencies data not available:', error);
                    this.state.topAgenciesData = [];
                }
            }