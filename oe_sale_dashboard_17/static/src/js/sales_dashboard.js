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
            // Use setTimeout to ensure DOM is fully rendered
            setTimeout(() => {
                this.initializeDashboard();
            }, 100);
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
                
                const foundElements = elements.filter(id => document.getElementById(id));
                const allExist = foundElements.length === elements.length;
                
                console.log(`[Sales Dashboard] DOM Check - Found ${foundElements.length}/${elements.length} elements:`, foundElements);
                
                if (allExist) {
                    console.log('[Sales Dashboard] All DOM elements found');
                    resolve();
                } else {
                    console.log('[Sales Dashboard] Still waiting for DOM elements...');
                    setTimeout(checkDOM, 200);
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
            console.log('[Sales Dashboard] Loading all dashboard data with date range:', {
                start: this.state.dateRange.start,
                end: this.state.dateRange.end
            });
            this.state.loading = true;
            
            // Ensure we have valid date range
            if (!this.state.dateRange.start || !this.state.dateRange.end) {
                console.warn('[Sales Dashboard] Invalid date range, using defaults');
                this.state.dateRange.start = this.getDefaultStartDate();
                this.state.dateRange.end = this.getDefaultEndDate();
            }
            
            const promises = [
                this.loadPerformanceData(),
                this.loadMonthlyData(),
                this.loadStateData(),
                this.loadCustomersData(),
                this.loadTeamData()
            ];

            const results = await Promise.allSettled(promises);
            
            // Log any failed promises
            results.forEach((result, index) => {
                const methodNames = ['Performance', 'Monthly', 'State', 'Customers', 'Team'];
                if (result.status === 'rejected') {
                    console.error(`[Sales Dashboard] ${methodNames[index]} data loading failed:`, result.reason);
                }
            });
            
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
        console.log('[Sales Dashboard] Validating and enhancing data structure...');
        
        // Initialize data structure if missing
        if (!this.state.data) {
            this.state.data = {};
        }
        
        // Validate performance data
        if (!this.state.data.performance || typeof this.state.data.performance !== 'object') {
            console.warn('[Sales Dashboard] Invalid performance data structure, initializing defaults');
            this.state.data.performance = {
                total_quotations: 0,
                total_orders: 0,
                total_invoiced: 0,
                total_amount: 0
            };
        }
        
        // Ensure all performance values are numbers
        ['total_quotations', 'total_orders', 'total_invoiced', 'total_amount'].forEach(key => {
            if (this.state.data.performance[key] === undefined || 
                this.state.data.performance[key] === null ||
                isNaN(Number(this.state.data.performance[key]))) {
                console.warn(`[Sales Dashboard] Invalid ${key} value, setting to 0`);
                this.state.data.performance[key] = 0;
            } else {
                this.state.data.performance[key] = Number(this.state.data.performance[key]);
            }
        });
        
        // Validate monthly data
        if (!Array.isArray(this.state.data.monthly)) {
            console.warn('[Sales Dashboard] Invalid monthly data, initializing as empty array');
            this.state.data.monthly = [];
        }
        
        // Validate chart data structures
        const chartDataDefaults = {
            byState: { labels: ['Draft', 'Sale', 'Done'], counts: [0, 0, 0] },
            topCustomers: { labels: [], amounts: [] },
            salesTeam: { labels: ['Sales Team'], amounts: [0] }
        };
        
        Object.entries(chartDataDefaults).forEach(([chartKey, defaultData]) => {
            if (!this.state.data[chartKey] || typeof this.state.data[chartKey] !== 'object') {
                console.warn(`[Sales Dashboard] Invalid ${chartKey} data, using defaults`);
                this.state.data[chartKey] = { ...defaultData };
                return;
            }
            
            // Validate arrays within chart data
            Object.entries(defaultData).forEach(([arrayKey, defaultArray]) => {
                if (!Array.isArray(this.state.data[chartKey][arrayKey])) {
                    console.warn(`[Sales Dashboard] Invalid ${chartKey}.${arrayKey}, using default`);
                    this.state.data[chartKey][arrayKey] = [...defaultArray];
                }
            });
            
            // Ensure arrays are same length for paired data
            if (chartKey !== 'monthly') {
                const keys = Object.keys(this.state.data[chartKey]);
                if (keys.length === 2) {
                    const [key1, key2] = keys;
                    const len1 = this.state.data[chartKey][key1].length;
                    const len2 = this.state.data[chartKey][key2].length;
                    
                    if (len1 !== len2) {
                        console.warn(`[Sales Dashboard] Array length mismatch in ${chartKey}: ${key1}(${len1}) vs ${key2}(${len2})`);
                        const minLength = Math.min(len1, len2);
                        this.state.data[chartKey][key1] = this.state.data[chartKey][key1].slice(0, minLength);
                        this.state.data[chartKey][key2] = this.state.data[chartKey][key2].slice(0, minLength);
                    }
                }
            }
        });
        
        console.log('[Sales Dashboard] Data structure validation complete:', {
            performanceKeys: Object.keys(this.state.data.performance).length,
            monthlyEntries: this.state.data.monthly.length,
            stateLabels: this.state.data.byState?.labels?.length || 0,
            customerLabels: this.state.data.topCustomers?.labels?.length || 0,
            teamLabels: this.state.data.salesTeam?.labels?.length || 0
        });
    }

    async loadPerformanceData() {
        try {
            console.log('[Sales Dashboard] Loading performance data with date range:', {
                start: this.state.dateRange.start,
                end: this.state.dateRange.end
            });
            
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_sales_performance_data", {
                model: 'sale.order',
                method: 'get_sales_performance_data',
                args: [this.state.dateRange.start, this.state.dateRange.end],
                kwargs: {}
            });
            console.log('[Sales Dashboard] Performance data received:', result);
            
            // Ensure we have valid data structure
            this.state.data.performance = {
                total_quotations: result.total_quotations || 0,
                total_orders: result.total_orders || 0,
                total_invoiced: result.total_invoiced || 0,
                total_amount: result.total_amount || 0,
                performance_indicator: result.performance_indicator || 'neutral'
            };
            
        } catch (error) {
            console.error('Error loading performance data:', error);
            this.notification.add('Failed to load performance data: ' + error.message, {
                type: 'warning'
            });
            this.state.data.performance = {
                total_quotations: 0,
                total_orders: 0,
                total_invoiced: 0,
                total_amount: 0,
                performance_indicator: 'neutral'
            };
        }
    }

    async loadMonthlyData() {
        try {
            console.log('[Sales Dashboard] Loading monthly data with date range:', {
                start: this.state.dateRange.start,
                end: this.state.dateRange.end
            });
            
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_monthly_fluctuation_data", {
                model: 'sale.order',
                method: 'get_monthly_fluctuation_data',
                args: [this.state.dateRange.start, this.state.dateRange.end, null],
                kwargs: {}
            });
            console.log('[Sales Dashboard] Monthly data received:', result);
            
            // Ensure proper data structure
            this.state.data.monthly = {
                labels: result.labels || [],
                quotations: result.quotations || [],
                sales_orders: result.sales_orders || [],
                invoiced_sales: result.invoiced_sales || []
            };
            
            // Log data validation
            console.log('[Sales Dashboard] Monthly data validation:', {
                labelsCount: this.state.data.monthly.labels.length,
                quotationsCount: this.state.data.monthly.quotations.length,
                salesOrdersCount: this.state.data.monthly.sales_orders.length,
                invoicedSalesCount: this.state.data.monthly.invoiced_sales.length
            });
            
        } catch (error) {
            console.error('Error loading monthly data:', error);
            this.notification.add('Failed to load monthly trends: ' + error.message, {
                type: 'warning'
            });
            this.state.data.monthly = {
                labels: [],
                quotations: [],
                sales_orders: [],
                invoiced_sales: []
            };
        }
    }

    async loadStateData() {
        console.log('[Sales Dashboard] Loading state/regional data...');
        
        try {
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_sales_by_state_data", {
                model: 'sale.order',
                method: 'get_sales_by_state_data',
                args: [this.state.dateRange.start, this.state.dateRange.end],
                kwargs: {}
            });
            
            console.log('[Sales Dashboard] State data received:', result);
            
            // Validate data structure
            if (!result || typeof result !== 'object') {
                console.warn('[Sales Dashboard] Invalid state data structure, using defaults');
                this.state.data.byState = {
                    labels: ['Draft', 'Sale', 'Done'],
                    counts: [0, 0, 0]
                };
                return;
            }
            
            // Ensure required properties exist
            if (!result.labels || !Array.isArray(result.labels)) {
                console.warn('[Sales Dashboard] Missing or invalid labels in state data');
                result.labels = ['Draft', 'Sale', 'Done'];
            }
            
            if (!result.counts || !Array.isArray(result.counts)) {
                console.warn('[Sales Dashboard] Missing or invalid counts in state data');
                result.counts = new Array(result.labels.length).fill(0);
            }
            
            // Ensure arrays are same length
            if (result.labels.length !== result.counts.length) {
                console.warn('[Sales Dashboard] Label/count array length mismatch, padding with zeros');
                const maxLength = Math.max(result.labels.length, result.counts.length);
                while (result.labels.length < maxLength) result.labels.push('Unknown');
                while (result.counts.length < maxLength) result.counts.push(0);
            }
            
            // Validate numeric values
            result.counts = result.counts.map((count, index) => {
                const numCount = Number(count) || 0;
                if (isNaN(numCount)) {
                    console.warn(`[Sales Dashboard] Invalid count at index ${index}:`, count);
                    return 0;
                }
                return numCount;
            });
            
            this.state.data.byState = result;
            console.log('[Sales Dashboard] Processed state data:', this.state.data.byState);
            
        } catch (error) {
            console.error('[Sales Dashboard] Error loading state data:', error);
            this.notification.add(`Failed to load regional data: ${error.message}`, {
                type: 'danger'
            });
            // Set safe default data
            this.state.data.byState = {
                labels: ['Draft', 'Sale', 'Done'],
                counts: [0, 0, 0]
            };
        }
    }

    async loadCustomersData() {
        console.log('[Sales Dashboard] Loading top customers data...');
        
        try {
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_top_customers_data", {
                model: 'sale.order',
                method: 'get_top_customers_data',
                args: [this.state.dateRange.start, this.state.dateRange.end, 10],
                kwargs: {}
            });
            
            console.log('[Sales Dashboard] Customers data received:', result);
            
            // Validate data structure
            if (!result || typeof result !== 'object') {
                console.warn('[Sales Dashboard] Invalid customers data structure, using defaults');
                this.state.data.topCustomers = {
                    labels: ['Customer 1', 'Customer 2'],
                    amounts: [0, 0]
                };
                return;
            }
            
            // Ensure required properties exist
            if (!result.labels || !Array.isArray(result.labels)) {
                console.warn('[Sales Dashboard] Missing or invalid labels in customers data');
                result.labels = ['Customer 1', 'Customer 2'];
            }
            
            if (!result.amounts || !Array.isArray(result.amounts)) {
                console.warn('[Sales Dashboard] Missing or invalid amounts in customers data');
                result.amounts = [0, 0];
            }
            
            // Ensure arrays are same length
            if (result.labels.length !== result.amounts.length) {
                console.warn('[Sales Dashboard] Customer label/amount array length mismatch');
                const minLength = Math.min(result.labels.length, result.amounts.length);
                result.labels = result.labels.slice(0, minLength);
                result.amounts = result.amounts.slice(0, minLength);
            }
            
            // Validate and convert amounts to numbers
            result.amounts = result.amounts.map((amount, index) => {
                const numAmount = Number(amount) || 0;
                if (isNaN(numAmount)) {
                    console.warn(`[Sales Dashboard] Invalid amount at index ${index}:`, amount);
                    return 0;
                }
                return numAmount;
            });
            
            // Ensure customer names are strings
            result.labels = result.labels.map((label, index) => {
                if (typeof label !== 'string') {
                    console.warn(`[Sales Dashboard] Invalid customer name at index ${index}:`, label);
                    return `Customer ${index + 1}`;
                }
                return label.trim() || `Customer ${index + 1}`;
            });
            
            this.state.data.topCustomers = result;
            console.log('[Sales Dashboard] Processed customers data:', this.state.data.topCustomers.labels.length, 'customers');
            
        } catch (error) {
            console.error('[Sales Dashboard] Error loading customers data:', error);
            this.notification.add(`Failed to load customer data: ${error.message}`, {
                type: 'danger'
            });
            // Set safe default data
            this.state.data.topCustomers = {
                labels: ['Customer 1', 'Customer 2'],
                amounts: [0, 0]
            };
        }
    }

    async loadTeamData() {
        console.log('[Sales Dashboard] Loading sales team performance data...');
        
        try {
            const result = await this.rpc("/web/dataset/call_kw/sale.order/get_sales_team_performance", {
                model: 'sale.order',
                method: 'get_sales_team_performance',
                args: [this.state.dateRange.start, this.state.dateRange.end],
                kwargs: {}
            });
            
            console.log('[Sales Dashboard] Team data received:', result);
            
            // Validate data structure
            if (!result || typeof result !== 'object') {
                console.warn('[Sales Dashboard] Invalid team data structure, using defaults');
                this.state.data.salesTeam = {
                    labels: ['Sales Team'],
                    amounts: [0]
                };
                return;
            }
            
            // Ensure required properties exist
            if (!result.labels || !Array.isArray(result.labels)) {
                console.warn('[Sales Dashboard] Missing or invalid labels in team data');
                result.labels = ['Sales Team'];
            }
            
            if (!result.amounts || !Array.isArray(result.amounts)) {
                console.warn('[Sales Dashboard] Missing or invalid amounts in team data');
                result.amounts = [0];
            }
            
            // Ensure arrays are same length
            if (result.labels.length !== result.amounts.length) {
                console.warn('[Sales Dashboard] Team label/amount array length mismatch');
                const minLength = Math.min(result.labels.length, result.amounts.length);
                result.labels = result.labels.slice(0, minLength);
                result.amounts = result.amounts.slice(0, minLength);
            }
            
            // Validate and convert amounts to numbers
            result.amounts = result.amounts.map((amount, index) => {
                const numAmount = Number(amount) || 0;
                if (isNaN(numAmount)) {
                    console.warn(`[Sales Dashboard] Invalid team amount at index ${index}:`, amount);
                    return 0;
                }
                return numAmount;
            });
            
            // Ensure team names are strings
            result.labels = result.labels.map((label, index) => {
                if (typeof label !== 'string') {
                    console.warn(`[Sales Dashboard] Invalid team name at index ${index}:`, label);
                    return `Team ${index + 1}`;
                }
                return label.trim() || `Team ${index + 1}`;
            });
            
            this.state.data.salesTeam = result;
            console.log('[Sales Dashboard] Processed team data:', this.state.data.salesTeam.labels.length, 'teams');
            
        } catch (error) {
            console.error('[Sales Dashboard] Error loading team data:', error);
            this.notification.add(`Failed to load team performance data: ${error.message}`, {
                type: 'danger'
            });
            // Set safe default data
            this.state.data.salesTeam = {
                labels: ['Sales Team'],
                amounts: [0]
            };
        }
    }

    // Handle category-based filtering for dashboard data
    async applyFiltersByCategory(category = null) {
        console.log('[Sales Dashboard] Applying category filters:', category);
        
        if (!category) {
            // No specific category, load all data
            console.log('[Sales Dashboard] No category filter, loading all data');
            await this.loadDashboardData();
            return;
        }
        
        try {
            // Apply category-specific filters to data loading
            const categoryFilters = {
                'quotations': 'draft',
                'orders': 'sale',
                'invoiced': 'done',
                'all': null
            };
            
            const stateFilter = categoryFilters[category.toLowerCase()] || null;
            console.log('[Sales Dashboard] Category state filter:', stateFilter);
            
            // Load data with category filter
            const dateRange = this.validateDateRange();
            
            // Load performance data with category filter
            const performanceResult = await this.orm.call(
                'sale.order',
                'get_sales_performance_data',
                [dateRange.start, dateRange.end],
                { state_filter: stateFilter }
            );
            
            console.log('[Sales Dashboard] Category-filtered performance data:', performanceResult);
            this.state.data.performance = performanceResult || {};
            
            // Update KPIs and charts based on filtered data
            this.updateKPIs();
            await this.renderCharts();
            
            this.notification.add(`Dashboard filtered by category: ${category}`, {
                type: 'info'
            });
            
        } catch (error) {
            console.error('[Sales Dashboard] Error applying category filters:', error);
            this.notification.add(`Failed to apply ${category} filter: ${error.message}`, {
                type: 'warning'
            });
            // Fallback to loading all data
            await this.loadDashboardData();
        }
    }

    // Validate date range inputs
    validateDateRange() {
        const today = new Date().toISOString().split('T')[0];
        const oneYearAgo = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        
        // Validate start date
        if (!this.state.dateRange.start || this.state.dateRange.start === '') {
            console.warn('[Sales Dashboard] Invalid start date, using default');
            this.state.dateRange.start = oneYearAgo;
        }
        
        // Validate end date
        if (!this.state.dateRange.end || this.state.dateRange.end === '') {
            console.warn('[Sales Dashboard] Invalid end date, using default');
            this.state.dateRange.end = today;
        }
        
        // Ensure start date is not after end date
        if (new Date(this.state.dateRange.start) > new Date(this.state.dateRange.end)) {
            console.warn('[Sales Dashboard] Start date after end date, swapping');
            const temp = this.state.dateRange.start;
            this.state.dateRange.start = this.state.dateRange.end;
            this.state.dateRange.end = temp;
        }
        
        // Ensure dates are not in the future
        if (new Date(this.state.dateRange.start) > new Date(today)) {
            console.warn('[Sales Dashboard] Start date in future, using today');
            this.state.dateRange.start = today;
        }
        
        if (new Date(this.state.dateRange.end) > new Date(today)) {
            console.warn('[Sales Dashboard] End date in future, using today');
            this.state.dateRange.end = today;
        }
        
        console.log('[Sales Dashboard] Validated date range:', this.state.dateRange);
        
        return {
            isValid: true,
            start: this.state.dateRange.start,
            end: this.state.dateRange.end
        };
    }

    // Enhanced data validation method
    validateAndSanitizeData() {
        console.log('[Sales Dashboard] Validating and sanitizing all data...');
        
        // Validate performance data
        if (!this.state.data.performance) {
            this.state.data.performance = {};
        }
        
        // Ensure all KPI values are numbers
        const performanceDefaults = {
            total_quotations: 0,
            total_orders: 0,
            total_invoiced: 0,
            total_amount: 0,
            quotation_count: 0,
            sales_order_count: 0,
            invoice_count: 0
        };
        
        for (const [key, defaultValue] of Object.entries(performanceDefaults)) {
            if (this.state.data.performance[key] === undefined || 
                this.state.data.performance[key] === null ||
                isNaN(Number(this.state.data.performance[key]))) {
                this.state.data.performance[key] = defaultValue;
            } else {
                this.state.data.performance[key] = Number(this.state.data.performance[key]);
            }
        }
        
        // Validate monthly data
        if (!this.state.data.monthly || !Array.isArray(this.state.data.monthly)) {
            this.state.data.monthly = [];
        }
        
        // Validate chart data structures
        const chartDefaults = {
            byState: { labels: ['Draft', 'Sale', 'Done'], counts: [0, 0, 0] },
            topCustomers: { labels: [], amounts: [] },
            salesTeam: { labels: ['Sales Team'], amounts: [0] }
        };
        
        for (const [chartKey, defaultData] of Object.entries(chartDefaults)) {
            if (!this.state.data[chartKey] || typeof this.state.data[chartKey] !== 'object') {
                this.state.data[chartKey] = { ...defaultData };
                continue;
            }
            
            // Validate labels and amounts/counts arrays
            const dataKeys = Object.keys(defaultData);
            for (const dataKey of dataKeys) {
                if (!Array.isArray(this.state.data[chartKey][dataKey])) {
                    this.state.data[chartKey][dataKey] = [...defaultData[dataKey]];
                }
            }
        }
        
        console.log('[Sales Dashboard] Data validation complete:', {
            performance: Object.keys(this.state.data.performance).length,
            monthly: this.state.data.monthly.length,
            stateLabels: this.state.data.byState.labels.length,
            customerLabels: this.state.data.topCustomers.labels.length,
            teamLabels: this.state.data.salesTeam.labels.length
        });
    }

    updateKPIs() {
        console.log('[Sales Dashboard] Updating KPIs with data:', this.state.data.performance);
        
        // Ensure data is validated first
        this.validateAndSanitizeData();
        
        // Since we're using QWeb templates with reactive state, 
        // we just need to ensure the state data is properly formatted
        const performance = this.state.data.performance || {};
        
        // Update state data to trigger reactive updates
        this.state.data.performance = {
            total_quotations: performance.total_quotations || performance.draft_count || 0,
            total_orders: performance.total_orders || performance.sales_order_count || 0,
            total_invoiced: performance.total_invoiced || performance.invoice_count || 0,
            total_amount: performance.total_amount || 0
        };

        console.log('[Sales Dashboard] Updated KPI state data:', this.state.data.performance);
        
        // Also update DOM elements for backward compatibility with fallback charts
        const elements = {
            'total_quotations': this.formatNumber(this.state.data.performance.total_quotations),
            'total_orders': this.formatNumber(this.state.data.performance.total_orders),
            'total_invoiced': this.formatNumber(this.state.data.performance.total_invoiced),
            'total_amount': this.formatCurrency(this.state.data.performance.total_amount)
        };

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
        if (!canvas || !this.state.data.monthly || !this.state.data.monthly.labels) {
            console.warn('[Sales Dashboard] Monthly trend chart canvas not found or no data');
            return;
        }
        
        const data = this.state.data.monthly;
        const quotationAmounts = (data.quotations || []).map(q => q.amount || 0);
        const salesAmounts = (data.sales_orders || []).map(s => s.amount || 0);
        const invoicedAmounts = (data.invoiced_sales || []).map(i => i.amount || 0);
        
        const allAmounts = [...quotationAmounts, ...salesAmounts, ...invoicedAmounts];
        const maxValue = Math.max(...allAmounts, 1);
        
        const chartHTML = `
            <div class="fallback-chart">
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
        
        // Find the chart container and replace its content
        const chartContainer = canvas.closest('.chart_container, .chart_body') || canvas.parentElement;
        if (chartContainer) {
            chartContainer.innerHTML = chartHTML;
            console.log('[Sales Dashboard] Rendered fallback monthly trend chart');
        } else {
            console.warn('[Sales Dashboard] Could not find chart container for monthly trend');
        }
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
        console.log('[Sales Dashboard] Refreshing data with current filters...');
        
        // Update date range from inputs if they exist
        const startDateInput = document.getElementById('start_date');
        const endDateInput = document.getElementById('end_date');
        
        let dateChanged = false;
        
        if (startDateInput && startDateInput.value) {
            if (this.state.dateRange.start !== startDateInput.value) {
                this.state.dateRange.start = startDateInput.value;
                dateChanged = true;
            }
        }
        if (endDateInput && endDateInput.value) {
            if (this.state.dateRange.end !== endDateInput.value) {
                this.state.dateRange.end = endDateInput.value;
                dateChanged = true;
            }
        }
        
        console.log('[Sales Dashboard] Date range for refresh:', {
            start: this.state.dateRange.start,
            end: this.state.dateRange.end,
            dateChanged: dateChanged
        });
        
        // Validate date range
        if (this.state.dateRange.start > this.state.dateRange.end) {
            this.notification.add('Start date cannot be after end date', {
                type: 'warning'
            });
            return;
        }
        
        // Test backend connectivity first
        const isConnected = await this.testBackendConnectivity();
        if (!isConnected) {
            console.error('[Sales Dashboard] Cannot refresh - backend not available');
            return;
        }
        
        // Reload all data with new filters
        await this.loadDashboardData();
        
        this.notification.add('Dashboard refreshed successfully with filtered data', {
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
        if (!amount && amount !== 0) return '$0';
        
        // Convert to number if it's a string
        const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
        
        if (isNaN(numAmount)) return '$0';
        
        // Format with currency symbol and commas
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(numAmount);
    }

    formatNumber(value) {
        if (!value && value !== 0) return '0';
        
        // Convert to number if it's a string
        const numValue = typeof value === 'string' ? parseFloat(value) : value;
        
        if (isNaN(numValue)) return '0';
        
        // Format with commas for thousands
        return new Intl.NumberFormat('en-US').format(numValue);
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
