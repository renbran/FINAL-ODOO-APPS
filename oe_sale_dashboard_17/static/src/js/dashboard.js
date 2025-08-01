/** @odoo-module **/
/* This module is under copyright of 'OdooElevate' */

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { initFieldMapping, getFieldName, buildDateDomain, getAmountFields, isFieldAvailable } from "./field_mapping";

class OeSaleDashboard extends Component {
    static template = "oe_sale_dashboard_17.yearly_sales_dashboard_template";
    
    setup() {
        super.setup();
        
        // Initialize services
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        // Initialize state with default date range (last 30 days)
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
                categories: {} // Initialize categories to prevent template errors
            },
            categoriesData: {},
            monthlyFluctuationData: { labels: [], quotations: [], sales_orders: [], invoiced_sales: [] },
            salesTypeDistribution: { count_distribution: {}, amount_distribution: {} },
            topAgentsData: [],
            topAgenciesData: [],
            recentOrders: [],
            // Additional data arrays expected by template
            quotationsData: [],
            salesOrdersData: [],
            invoicesData: [],
            rankingData: []
        });
        
        // Initialize dashboard on mount
        onMounted(async () => {
            await this._initializeDashboard();
        });
    }
    
    async _initializeDashboard() {
        try {
            this.state.isLoading = true;
            this.state.hasError = false;
            
            console.log('Initializing dashboard...');
            
            // Initialize field mapping
            await initFieldMapping(this.orm);
            
            // Load sales types if available
            await this._loadSalesTypes();
            
            // Load dashboard data
            await this._loadDashboardData();
            
            // Load top performers data
            await this._loadTopPerformersData();
            
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
            if (isFieldAvailable('sale_order_type_id')) {
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
            
            // Use the Python backend methods instead of direct ORM calls
            const dashboardData = await this.orm.call(
                'sale.order',
                'get_dashboard_summary_data',
                [this.state.startDate, this.state.endDate, this.state.selectedSalesTypes]
            );
            
            console.log('Dashboard data from backend:', dashboardData);
            
            if (dashboardData.error) {
                throw new Error(dashboardData.error);
            }
            
            // Process the backend data
            this._processDashboardData(dashboardData);
            
            // Load additional chart data
            await this._loadChartData();
            
            // Load recent orders
            await this._loadRecentOrdersFromBackend();
            
            console.log('Dashboard data loaded successfully');
            console.log('Summary data:', this.state.summaryData);
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            throw error;
        }
    }
    
    _processDashboardData(dashboardData) {
        const totals = dashboardData.totals || {};
        
        // Update summary data using backend calculations
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
            pipelineVelocity: totals.pipeline_velocity ? totals.pipeline_velocity.toFixed(1) + ' days' : '0 days'
        };
        
        // Store categories data for charts and template
        this.state.categoriesData = dashboardData.categories || {};
        
        // Also store categories in summaryData for template compatibility
        if (!this.state.summaryData.categories) {
            this.state.summaryData.categories = {};
        }
        this.state.summaryData.categories = dashboardData.categories || {};
        
        console.log('Processed dashboard data:', this.state.summaryData);
    }
    
    async _loadChartData() {
        try {
            // Load monthly fluctuation data for line charts
            const monthlyData = await this.orm.call(
                'sale.order',
                'get_monthly_fluctuation_data',
                [this.state.startDate, this.state.endDate, this.state.selectedSalesTypes]
            );
            
            this.state.monthlyFluctuationData = monthlyData;
            
            // Load sales type distribution for pie charts
            const distributionData = await this.orm.call(
                'sale.order',
                'get_sales_type_distribution',
                [this.state.startDate, this.state.endDate]
            );
            
            this.state.salesTypeDistribution = distributionData;
            
            console.log('Chart data loaded:', { monthlyData, distributionData });
            
        } catch (error) {
            console.warn('Error loading chart data:', error);
            this.state.monthlyFluctuationData = { labels: [], quotations: [], sales_orders: [], invoiced_sales: [] };
            this.state.salesTypeDistribution = { count_distribution: {}, amount_distribution: {} };
        }
    }
    
    async _loadRecentOrdersFromBackend() {
        try {
            // Load recent orders using proper field mapping
            const dateField = getFieldName('booking_date');
            const amountField = isFieldAvailable('sale_value') ? 'sale_value' : 'amount_total';
            
            const dateDomain = buildDateDomain(this.state.startDate, this.state.endDate);
            
            const recentOrdersFields = ['name', 'partner_id', dateField, amountField, 'state'];
            
            console.log('Loading recent orders with fields:', recentOrdersFields);
            
            const recentOrders = await this.orm.searchRead(
                'sale.order',
                dateDomain,
                recentOrdersFields,
                { 
                    limit: 10, 
                    order: `${dateField} desc` 
                }
            );
            
            // Format the recent orders data
            this.state.recentOrders = recentOrders.map(order => ({
                id: order.id,
                name: order.name,
                partner_name: order.partner_id ? order.partner_id[1] : 'Unknown Customer',
                date: this._formatDate(order[dateField]),
                amount_formatted: this._formatCurrency(order[amountField] || 0),
                status_text: this._getStatusText(order.state),
                status_class: this._getStatusClass(order.state)
            }));
            
            console.log('Loaded recent orders:', this.state.recentOrders.length);
            
        } catch (error) {
            console.warn('Could not load recent orders:', error);
            this.state.recentOrders = [];
        }
    }
    
    async _loadTopPerformersData() {
        try {
            // Check if commission fields are available before loading
            const hasAgentFields = isFieldAvailable('agent1_partner_id') && isFieldAvailable('agent1_amount');
            const hasBrokerFields = isFieldAvailable('broker_partner_id') && isFieldAvailable('broker_amount');
            
            console.log('Commission fields availability:', { 
                agent1_partner_id: isFieldAvailable('agent1_partner_id'),
                agent1_amount: isFieldAvailable('agent1_amount'),
                broker_partner_id: isFieldAvailable('broker_partner_id'), 
                broker_amount: isFieldAvailable('broker_amount')
            });
            
            let topAgents = [];
            let topAgencies = [];
            
            // Load top agents if fields are available
            if (hasAgentFields) {
                topAgents = await this.orm.call(
                    'sale.order',
                    'get_top_performers_data',
                    [this.state.startDate, this.state.endDate, 'agent', 10]
                );
                console.log('Agent data loaded using agent1_partner_id field');
            } else {
                console.warn('Agent fields not available - skipping agent rankings');
            }
            
            // Load top agencies if fields are available
            if (hasBrokerFields) {
                topAgencies = await this.orm.call(
                    'sale.order',
                    'get_top_performers_data',
                    [this.state.startDate, this.state.endDate, 'agency', 10]
                );
                console.log('Agency data loaded using broker_partner_id field');
            } else {
                console.warn('Broker fields not available - skipping agency rankings');
            }
            
            this.state.topAgentsData = topAgents || [];
            this.state.topAgenciesData = topAgencies || [];
            
            console.log('Top performers loaded:', { 
                agents: topAgents.length, 
                agencies: topAgencies.length,
                agentSample: topAgents.length > 0 ? topAgents[0] : null,
                agencySample: topAgencies.length > 0 ? topAgencies[0] : null
            });
            
            // Debug: Log agent1+partner field usage
            if (topAgents.length > 0) {
                console.log('Agent ranking using agent1_partner_id and agent1_amount fields');
                console.log('Sample agent data:', topAgents[0]);
            }
            if (topAgencies.length > 0) {
                console.log('Agency ranking using broker_partner_id and broker_amount fields');
                console.log('Sample agency data:', topAgencies[0]);
            }
            
        } catch (error) {
            console.warn('Error loading top performers:', error);
            this.state.topAgentsData = [];
            this.state.topAgenciesData = [];
        }
    }
    
    async _loadRecentOrders(dateDomain) {
        try {
            const dateField = getFieldName('booking_date');
            const amountField = isFieldAvailable('sale_value') ? 'sale_value' : 'amount_total';
            
            const recentOrdersFields = ['name', 'partner_id', dateField, amountField, 'state'];
            
            console.log('Loading recent orders with fields:', recentOrdersFields);
            
            const recentOrders = await this.orm.searchRead(
                'sale.order',
                dateDomain,
                recentOrdersFields,
                { 
                    limit: 10, 
                    order: `${dateField} desc` 
                }
            );
            
            // Format the recent orders data
            this.state.recentOrders = recentOrders.map(order => ({
                id: order.id,
                name: order.name,
                partner_name: order.partner_id ? order.partner_id[1] : 'Unknown Customer',
                date: this._formatDate(order[dateField]),
                amount_formatted: this._formatCurrency(order[amountField] || 0),
                status_text: this._getStatusText(order.state),
                status_class: this._getStatusClass(order.state)
            }));
            
            console.log('Loaded recent orders:', this.state.recentOrders.length);
            
        } catch (error) {
            console.warn('Could not load recent orders:', error);
            this.state.recentOrders = [];
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
    
    formatDashboardValue(value) {
        // This method is called from template, so keep it accessible
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
