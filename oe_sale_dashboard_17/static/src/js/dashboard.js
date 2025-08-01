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
                conversionRate: '0%'
            },
            quotationsData: [],
            salesOrdersData: [],
            invoicedSalesData: [],
            recentOrders: []
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
            
            // Build date domain using the correct date field
            const dateDomain = buildDateDomain(this.state.startDate, this.state.endDate);
            
            // Get available fields for reading
            const baseFields = ['id', 'name', 'partner_id', 'state'];
            const amountField = getFieldName('amount_total'); // Will fallback to 'amount_total'
            const saleValueField = isFieldAvailable('sale_value') ? 'sale_value' : null;
            const dateField = getFieldName('booking_date'); // Will fallback to 'date_order'
            
            const readFields = [...baseFields, amountField];
            if (saleValueField) readFields.push(saleValueField);
            if (dateField !== 'date_order') readFields.push(dateField);
            
            console.log('Using fields for data loading:', readFields);
            console.log('Date domain:', dateDomain);
            
            // Load quotations (draft and sent states)
            const quotationsDomain = [
                ...dateDomain,
                ['state', 'in', ['draft', 'sent']]
            ];
            
            console.log('Loading quotations with domain:', quotationsDomain);
            const quotations = await this.orm.searchRead(
                'sale.order',
                quotationsDomain,
                readFields,
                { limit: false }
            );
            console.log('Loaded quotations:', quotations.length, quotations);
            
            // Load sales orders (confirmed state)
            const salesOrdersDomain = [
                ...dateDomain,
                ['state', '=', 'sale']
            ];
            
            console.log('Loading sales orders with domain:', salesOrdersDomain);
            const salesOrdersFields = [...readFields, 'invoice_status'];
            const salesOrders = await this.orm.searchRead(
                'sale.order',
                salesOrdersDomain,
                salesOrdersFields,
                { limit: false }
            );
            console.log('Loaded sales orders:', salesOrders.length, salesOrders);
            
            // Filter invoiced orders
            const invoicedOrders = salesOrders.filter(order => order.invoice_status === 'invoiced');
            console.log('Invoiced orders:', invoicedOrders.length);
            
            // Calculate summary data
            this._calculateSummaryData(quotations, salesOrders, invoicedOrders);
            
            // Load recent orders for display
            await this._loadRecentOrders(dateDomain);
            
            console.log('Dashboard data loaded successfully');
            console.log('Summary data:', this.state.summaryData);
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            throw error;
        }
    }
    
    _calculateSummaryData(quotations, salesOrders, invoicedOrders) {
        // Get the best available amount field
        const amountField = isFieldAvailable('sale_value') ? 'sale_value' : 'amount_total';
        console.log('Using amount field for calculations:', amountField);
        
        // Calculate quotations totals
        const quotationsTotal = quotations.reduce((sum, q) => {
            const amount = q[amountField] || q.amount_total || 0;
            return sum + amount;
        }, 0);
        const quotationsCount = quotations.length;
        
        // Calculate sales orders totals
        const salesOrdersTotal = salesOrders.reduce((sum, s) => {
            const amount = s[amountField] || s.amount_total || 0;
            return sum + amount;
        }, 0);
        const salesOrdersCount = salesOrders.length;
        
        // Calculate invoiced totals
        const invoicedTotal = invoicedOrders.reduce((sum, i) => {
            const amount = i[amountField] || i.amount_total || 0;
            return sum + amount;
        }, 0);
        const invoicedCount = invoicedOrders.length;
        
        // Calculate conversion rate
        const conversionRate = quotationsCount > 0 
            ? ((salesOrdersCount / quotationsCount) * 100).toFixed(1) + '%'
            : '0%';
        
        console.log('Calculated totals:', {
            quotations: { count: quotationsCount, total: quotationsTotal },
            salesOrders: { count: salesOrdersCount, total: salesOrdersTotal },
            invoiced: { count: invoicedCount, total: invoicedTotal },
            conversionRate
        });
        
        // Update state
        this.state.summaryData = {
            totalQuotations: {
                count: quotationsCount,
                amount: quotationsTotal,
                formatted: this._formatCurrency(quotationsTotal)
            },
            totalSalesOrders: {
                count: salesOrdersCount,
                amount: salesOrdersTotal,
                formatted: this._formatCurrency(salesOrdersTotal)
            },
            totalInvoiced: {
                count: invoicedCount,
                amount: invoicedTotal,
                formatted: this._formatCurrency(invoicedTotal)
            },
            conversionRate: conversionRate
        };
        
        // Store detailed data for charts
        this.state.quotationsData = quotations;
        this.state.salesOrdersData = salesOrders;
        this.state.invoicedSalesData = invoicedOrders;
        
        console.log('Updated state.summaryData:', this.state.summaryData);
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
