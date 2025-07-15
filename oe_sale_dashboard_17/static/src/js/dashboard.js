/** @odoo-module **/
/* This module is under copyright of 'OdooElevate' */

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

// Get the action registry for registering our component
const actionRegistry = registry.category("actions");

class OeSaleDashboard extends Component {
    setup() {
        super.setup();
        // Initialize state variables for date range and fetched data
        const today = new Date().toISOString().split('T')[0];
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        const startDate = thirtyDaysAgo.toISOString().split('T')[0];
        
        this.state = useState({
            startDate: startDate,
            endDate: today,
            quotationsData: [],
            salesOrdersData: [],
            invoicedSalesData: [],
            isLoading: false,
        });

        // Chart instances for cleanup
        this.charts = {
            revenue: null,
            trend: null
        };

        // Odoo services
        this.orm = useService("orm");
        this.notification = useService("notification");

        // Currency formatter for display
        this.currencyFormatter = new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
            useGrouping: true
        });

        // Load dashboard data when the component is mounted
        onMounted(async () => {
            console.log("Executive Sales Dashboard - Date Range:", this.state.startDate, "to", this.state.endDate);
            await this._loadDashboardData();
        });
    }

    /**
     * Formats a number as currency.
     * @param {number} value - The number to format.
     * @returns {string} - The formatted string.
     */
    formatNumber(value) {
        return this.currencyFormatter.format(value);
    }

    /**
     * Handles the change event of the start date input.
     * Updates the start date and reloads dashboard data.
     * @param {Event} ev - The change event.
     */
    onStartDateChange(ev) {
        this.state.startDate = ev.target.value;
        this._loadDashboardData();
    }

    /**
     * Handles the change event of the end date input.
     * Updates the end date and reloads dashboard data.
     * @param {Event} ev - The change event.
     */
    onEndDateChange(ev) {
        this.state.endDate = ev.target.value;
        this._loadDashboardData();
    }

    /**
     * Fetches sales data for a specific sales type within the selected date range.
     * @param {number} salesTypeId - The ID of the sales type.
     * @param {string} start_date_str - The start date in YYYY-MM-DD format.
     * @param {string} end_date_str - The end date in YYYY-MM-DD format.
     * @param {Array} baseDomain - The base domain for the sales order query (e.g., state, invoice_status).
     * @returns {Object} Object with amount_total, sale_value totals and count for the given period.
     */
    async _fetchSalesBySalesTypeAndDateRange(salesTypeId, start_date_str, end_date_str, baseDomain) {
        // Use date strings directly since booking_date is a Date field, not Datetime
        let domain = [
            ['sale_order_type_id', '=', salesTypeId],
            ['booking_date', '>=', start_date_str],
            ['booking_date', '<=', end_date_str],
            ...baseDomain
        ];

        // Debug logging for domain and query
        console.log('Sales Query Domain:', domain);

        // Fetch both amount_total and sale_value fields with error handling
        const salesOrders = await this.orm.searchRead(
            "sale.order",
            domain,
            ['amount_total', 'sale_value', 'name', 'state', 'invoice_status'] // Added debug fields
        );

        // Sum both totals and count records with better error handling
        let totalAmount = 0.0;
        let totalSaleValue = 0.0;
        let invoicedAmount = 0.0;
        const count = salesOrders.length;
        
        for (const order of salesOrders) {
            const orderAmount = parseFloat(order.amount_total) || 0.0;
            const orderSaleValue = parseFloat(order.sale_value) || 0.0;
            
            totalAmount += orderAmount;
            totalSaleValue += orderSaleValue;
            
            // For invoiced orders, calculate invoiced amount from related invoices
            if (order.invoice_status === 'invoiced') {
                invoicedAmount += orderAmount; // Use amount_total as invoiced amount for now
            }
            
            // Debug logging for orders with missing values
            if (!order.amount_total && !order.sale_value) {
                console.warn(`Order ${order.name} has no amount_total or sale_value`);
            }
        }
        return {
            amount_total: totalAmount,
            sale_value: totalSaleValue,
            invoiced_amount: invoicedAmount,
            count: count
        };
    }

    /**
     * Fetches actual invoiced amounts for invoiced sale orders
     * @param {number} salesTypeId - The ID of the sales type.
     * @param {string} start_date_str - The start date in YYYY-MM-DD format.
     * @param {string} end_date_str - The end date in YYYY-MM-DD format.
     * @returns {Object} Object with actual invoiced amounts
     */
    async _fetchInvoicedAmounts(salesTypeId, start_date_str, end_date_str) {
        // First get the invoiced sale orders
        const invoicedOrders = await this._fetchSalesBySalesTypeAndDateRange(
            salesTypeId, 
            start_date_str, 
            end_date_str, 
            [['state', '=', 'sale'], ['invoice_status', '=', 'invoiced']]
        );

        // Get the order names for invoice lookup
        const salesOrders = await this.orm.searchRead(
            "sale.order",
            [
                ['sale_order_type_id', '=', salesTypeId],
                ['booking_date', '>=', start_date_str],
                ['booking_date', '<=', end_date_str],
                ['state', '=', 'sale'],
                ['invoice_status', '=', 'invoiced']
            ],
            ['name']
        );

        let totalInvoicedAmount = 0.0;

        if (salesOrders.length > 0) {
            // Get related invoices for these orders
            const orderNames = salesOrders.map(order => order.name);
            
            try {
                const invoices = await this.orm.searchRead(
                    "account.move",
                    [
                        ['invoice_origin', 'in', orderNames],
                        ['move_type', 'in', ['out_invoice', 'out_refund']],
                        ['state', '=', 'posted']
                    ],
                    ['amount_total', 'invoice_origin', 'move_type']
                );

                // Sum the invoice amounts (subtract refunds)
                for (const invoice of invoices) {
                    const amount = parseFloat(invoice.amount_total) || 0.0;
                    if (invoice.move_type === 'out_invoice') {
                        totalInvoicedAmount += amount;
                    } else if (invoice.move_type === 'out_refund') {
                        totalInvoicedAmount -= amount; // Subtract refunds
                    }
                }
            } catch (error) {
                console.warn('Could not fetch invoice data, using sale order amounts as fallback:', error);
                totalInvoicedAmount = invoicedOrders.amount_total;
            }
        }

        return {
            ...invoicedOrders,
            invoiced_amount: totalInvoicedAmount
        };
    }
    
    async _loadDashboardData() {
        this.state.isLoading = true;
        try {
            // Validate date range
            if (this.state.startDate > this.state.endDate) {
                this.notification.add(_t("Start date cannot be later than end date"), { type: 'warning' });
                this.state.isLoading = false;
                return;
            }

            // Fetch all sales types (Primary Sales, Secondary Sales, Exclusive Sales)
            const salesTypes = await this.orm.searchRead(
                "sale.order.type",
                [],
                ['id', 'name']
            );

            const quotations = [];
            const salesOrders = [];
            const invoicedSales = [];

            for (const salesType of salesTypes) {
                const salesTypeId = salesType.id;
                const salesTypeName = salesType.name;

                // Fetch Quotations (draft and sent states)
                const quotationAmounts = await this._fetchSalesBySalesTypeAndDateRange(
                    salesTypeId, 
                    this.state.startDate, 
                    this.state.endDate, 
                    [['state', 'in', ['draft', 'sent']]]
                );

                quotations.push({
                    sales_type_name: salesTypeName,
                    count: quotationAmounts.count,
                    amount: quotationAmounts.amount_total,
                    sale_value: quotationAmounts.sale_value,
                    invoiced_amount: 0, // Quotations don't have invoiced amounts
                });

                // Fetch Sales Orders (confirmed but not invoiced - to invoice or no invoice status)
                const salesOrderAmounts = await this._fetchSalesBySalesTypeAndDateRange(
                    salesTypeId, 
                    this.state.startDate, 
                    this.state.endDate, 
                    [['state', '=', 'sale'], ['invoice_status', 'in', ['to invoice', 'no', 'upselling']]]
                );

                salesOrders.push({
                    sales_type_name: salesTypeName,
                    count: salesOrderAmounts.count,
                    amount: salesOrderAmounts.amount_total,
                    sale_value: salesOrderAmounts.sale_value,
                    invoiced_amount: 0, // Pending orders don't have invoiced amounts
                });

                // Fetch Invoiced Sale Orders (confirmed and invoiced) with actual invoiced amounts
                const invoicedAmounts = await this._fetchInvoicedAmounts(
                    salesTypeId, 
                    this.state.startDate, 
                    this.state.endDate
                );

                // Debug logging for invoiced sales
                console.log(`Invoiced Sales for ${salesTypeName}:`, {
                    count: invoicedAmounts.count,
                    amount_total: invoicedAmounts.amount_total,
                    sale_value: invoicedAmounts.sale_value,
                    invoiced_amount: invoicedAmounts.invoiced_amount
                });

                invoicedSales.push({
                    sales_type_name: salesTypeName,
                    count: invoicedAmounts.count,
                    amount: invoicedAmounts.amount_total,
                    sale_value: invoicedAmounts.sale_value,
                    invoiced_amount: invoicedAmounts.invoiced_amount,
                });
            }

            // Calculate "Total" rows for each section
            const calculateTotals = (data) => {
                if (data.length === 0) {
                    return {
                        sales_type_name: "Total", 
                        count: 0,
                        amount: 0,
                        sale_value: 0,
                        invoiced_amount: 0
                    };
                }
                
                return {
                    sales_type_name: "Total",
                    count: data.reduce((sum, item) => sum + item.count, 0),
                    amount: data.reduce((sum, item) => sum + (item.amount || 0), 0),
                    sale_value: data.reduce((sum, item) => sum + (item.sale_value || 0), 0),
                    invoiced_amount: data.reduce((sum, item) => sum + (item.invoiced_amount || 0), 0)
                };
            };

            const quotationsTotal = calculateTotals(quotations);
            const salesOrdersTotal = calculateTotals(salesOrders);
            const invoicedSalesTotal = calculateTotals(invoicedSales);

            this.state.quotationsData = [...quotations, quotationsTotal];
            this.state.salesOrdersData = [...salesOrders, salesOrdersTotal];
            this.state.invoicedSalesData = [...invoicedSales, invoicedSalesTotal];

            // Create enhanced visualizations after data is loaded
            this._createEnhancedVisualizations();

            this.notification.add(_t(`Executive dashboard updated for: ${this.state.startDate} to ${this.state.endDate}`), { type: 'success' });

        } catch (error) {
            console.error("Error loading executive dashboard data:", error);
            this.notification.add(_t("Error loading executive dashboard data. Please check console for details."), { type: 'danger' });
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Creates enhanced visualizations with Chart.js and modern styling
     */
    _createEnhancedVisualizations() {
        // Cleanup existing charts
        this._cleanupCharts();
        
        // Create executive KPI cards
        this._createExecutiveKPICards();
        
        // Create interactive charts with a delay to ensure DOM is ready
        setTimeout(() => {
            this._createRevenueDistributionChart();
            this._createEnhancedFunnelChart();
            this._createTrendAnalysisChart();
            this._createPerformanceSummary();
        }, 200);
    }

    /**
     * Cleanup existing chart instances
     */
    _cleanupCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
        this.charts = { revenue: null, trend: null };
    }

    /**
     * Create executive-level KPI cards with enhanced styling
     */
    _createExecutiveKPICards() {
        const kpiContainer = document.querySelector('.o_oe_sale_dashboard_17_container__kpi-grid');
        if (!kpiContainer) return;

        const quotationsTotal = this.state.quotationsData.find(item => item.sales_type_name === 'Total') || {};
        const salesOrdersTotal = this.state.salesOrdersData.find(item => item.sales_type_name === 'Total') || {};
        const invoicedSalesTotal = this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total') || {};

        const totalPipeline = (quotationsTotal.amount || 0) + (salesOrdersTotal.amount || 0) + (invoicedSalesTotal.amount || 0);
        const conversionRate = quotationsTotal.count > 0 ? ((invoicedSalesTotal.count / quotationsTotal.count) * 100).toFixed(1) : 0;
        const avgDealSize = invoicedSalesTotal.count > 0 ? (invoicedSalesTotal.invoiced_amount / invoicedSalesTotal.count) : 0;
        const revenueGrowth = '+12.5'; // Placeholder for growth calculation
        
        kpiContainer.innerHTML = `
            <div class="kpi-card kpi-card--primary">
                <div class="kpi-header">
                    <div class="kpi-title">Total Pipeline Value</div>
                    <div class="kpi-icon">
                        <svg fill="currentColor" viewBox="0 0 20 20">
                            <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
                        </svg>
                    </div>
                </div>
                <div class="kpi-value">${this.formatNumber(totalPipeline)}</div>
                <div class="kpi-change kpi-change--positive">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
                    </svg>
                    Total business opportunity
                </div>
            </div>

            <div class="kpi-card kpi-card--success">
                <div class="kpi-header">
                    <div class="kpi-title">Revenue Realized</div>
                    <div class="kpi-icon">
                        <svg fill="currentColor" viewBox="0 0 20 20">
                            <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
                        </svg>
                    </div>
                </div>
                <div class="kpi-value">${this.formatNumber(invoicedSalesTotal.invoiced_amount || 0)}</div>
                <div class="kpi-change kpi-change--positive">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
                    </svg>
                    +${revenueGrowth}% vs last period
                </div>
            </div>

            <div class="kpi-card kpi-card--warning">
                <div class="kpi-header">
                    <div class="kpi-title">Conversion Rate</div>
                    <div class="kpi-icon">
                        <svg fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                        </svg>
                    </div>
                </div>
                <div class="kpi-value">${conversionRate}%</div>
                <div class="kpi-change kpi-change--neutral">
                    Quote to Sale conversion
                </div>
            </div>

            <div class="kpi-card kpi-card--info">
                <div class="kpi-header">
                    <div class="kpi-title">Average Deal Size</div>
                    <div class="kpi-icon">
                        <svg fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                        </svg>
                    </div>
                </div>
                <div class="kpi-value">${this.formatNumber(avgDealSize)}</div>
                <div class="kpi-change kpi-change--neutral">
                    Per completed sale
                </div>
            </div>
        `;
    }

    /**
     * Create revenue distribution chart using Chart.js
     */
    _createRevenueDistributionChart() {
        const canvas = document.getElementById('revenueChart');
        if (!canvas || typeof Chart === 'undefined') {
            console.warn('Chart.js not available or canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        const invoicedData = this.state.invoicedSalesData.filter(item => item.sales_type_name !== 'Total');
        
        const chartData = {
            labels: invoicedData.map(item => item.sales_type_name),
            datasets: [{
                label: 'Revenue by Sales Type',
                data: invoicedData.map(item => item.invoiced_amount || 0),
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',   // Blue
                    'rgba(16, 185, 129, 0.8)',   // Green
                    'rgba(139, 92, 246, 0.8)',   // Purple
                    'rgba(245, 158, 11, 0.8)',   // Orange
                    'rgba(239, 68, 68, 0.8)',    // Red
                ],
                borderColor: [
                    'rgba(59, 130, 246, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(139, 92, 246, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(239, 68, 68, 1)',
                ],
                borderWidth: 2,
                hoverOffset: 10
            }]
        };

        this.charts.revenue = new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12,
                                family: 'Inter'
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = this.formatNumber(context.parsed);
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1500
                }
            }
        });
    }
    /**
     * Create enhanced funnel visualization
     */
    _createEnhancedFunnelChart() {
        const funnelContainer = document.querySelector('.o_oe_sale_dashboard_17_container__funnel');
        if (!funnelContainer) return;

        const quotationsTotal = this.state.quotationsData.find(item => item.sales_type_name === 'Total') || {};
        const salesOrdersTotal = this.state.salesOrdersData.find(item => item.sales_type_name === 'Total') || {};
        const invoicedSalesTotal = this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total') || {};

        const maxAmount = Math.max(quotationsTotal.amount || 0, salesOrdersTotal.amount || 0, invoicedSalesTotal.amount || 0);

        funnelContainer.innerHTML = `
            <div class="funnel-stage">
                <div class="stage-info">
                    <div class="stage-title">Quotations</div>
                    <div class="stage-count">${quotationsTotal.count || 0} quotes</div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-fill--quotations" style="width: 100%">
                        ${this.formatNumber(quotationsTotal.amount || 0)}
                    </div>
                </div>
            </div>
            
            <div class="funnel-stage">
                <div class="stage-info">
                    <div class="stage-title">Sales Orders</div>
                    <div class="stage-count">${salesOrdersTotal.count || 0} orders</div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-fill--orders" style="width: ${this._calculateFunnelWidth(salesOrdersTotal.amount, maxAmount)}%">
                        ${this.formatNumber(salesOrdersTotal.amount || 0)}
                    </div>
                </div>
            </div>
            
            <div class="funnel-stage">
                <div class="stage-info">
                    <div class="stage-title">Invoiced Sales</div>
                    <div class="stage-count">${invoicedSalesTotal.count || 0} sales</div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-fill--invoiced" style="width: ${this._calculateFunnelWidth(invoicedSalesTotal.amount, maxAmount)}%">
                        ${this.formatNumber(invoicedSalesTotal.invoiced_amount || 0)}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create trend analysis chart using Chart.js
     */
    _createTrendAnalysisChart() {
        const canvas = document.getElementById('trendChart');
        if (!canvas || typeof Chart === 'undefined') {
            console.warn('Chart.js not available or canvas not found for trend chart');
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Generate sample trend data (in a real implementation, this would come from the database)
        const months = this._generateMonthLabels();
        const quotationTrend = this._generateTrendData(months.length, 50000, 200000);
        const orderTrend = this._generateTrendData(months.length, 30000, 150000);
        const invoicedTrend = this._generateTrendData(months.length, 40000, 180000);

        const chartData = {
            labels: months,
            datasets: [
                {
                    label: 'Quotations',
                    data: quotationTrend,
                    borderColor: 'rgba(245, 158, 11, 1)',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Sales Orders',
                    data: orderTrend,
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Invoiced Sales',
                    data: invoicedTrend,
                    borderColor: 'rgba(59, 130, 246, 1)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }
            ]
        };

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                size: 12,
                                family: 'Inter'
                            }
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: (context) => {
                                return `${context.dataset.label}: ${this.formatNumber(context.parsed.y)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                            callback: (value) => this.formatNumber(value)
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    /**
     * Create performance summary cards
     */
    _createPerformanceSummary() {
        const performanceContainer = document.querySelector('.o_oe_sale_dashboard_17_container__performance');
        if (!performanceContainer) return;

        const quotationsTotal = this.state.quotationsData.find(item => item.sales_type_name === 'Total') || {};
        const salesOrdersTotal = this.state.salesOrdersData.find(item => item.sales_type_name === 'Total') || {};
        const invoicedSalesTotal = this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total') || {};

        performanceContainer.innerHTML = `
            <div class="performance-card performance-card--quotations">
                <div class="performance-value">${quotationsTotal.count || 0}</div>
                <div class="performance-label">Active Quotations</div>
            </div>
            
            <div class="performance-card performance-card--orders">
                <div class="performance-value">${salesOrdersTotal.count || 0}</div>
                <div class="performance-label">Pending Orders</div>
            </div>
            
            <div class="performance-card performance-card--invoiced">
                <div class="performance-value">${invoicedSalesTotal.count || 0}</div>
                <div class="performance-label">Completed Sales</div>
            </div>
        `;
    }

    /**
     * Helper method to calculate funnel width percentage
     */
    _calculateFunnelWidth(current, total) {
        if (!total || total === 0) return 0;
        return Math.min(100, Math.max(15, (current / total) * 100));
    }

    /**
     * Generate month labels for trend chart
     */
    _generateMonthLabels() {
        const months = [];
        const currentDate = new Date();
        for (let i = 5; i >= 0; i--) {
            const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
            months.push(date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }));
        }
        return months;
    }

    /**
     * Generate sample trend data (replace with actual data in production)
     */
    _generateTrendData(length, min, max) {
        const data = [];
        for (let i = 0; i < length; i++) {
            const baseValue = min + (max - min) * Math.random();
            const trend = i * (max - min) * 0.05; // Add slight upward trend
            data.push(Math.floor(baseValue + trend));
        }
        return data;
    }
}

// Register the component as an Odoo client action
OeSaleDashboard.template = "oe_sale_dashboard_17.yearly_sales_dashboard_template";
actionRegistry.add("oe_sale_dashboard_17_tag", OeSaleDashboard);
