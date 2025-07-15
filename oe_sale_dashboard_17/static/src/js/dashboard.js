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
            console.log("OE Sales Dashboard - Date Range:", this.state.startDate, "to", this.state.endDate);
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

            // Create visualizations after data is loaded
            this._createVisualizations();

            this.notification.add(_t(`Sales data updated for: ${this.state.startDate} to ${this.state.endDate}`), { type: 'success' });

        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.notification.add(_t("Error loading sales data. Please check console for details."), { type: 'danger' });
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Creates visual charts and KPI cards for the dashboard
     */
    _createVisualizations() {
        // Remove existing charts
        this._removeExistingCharts();
        
        // Create KPI cards
        this._createKPICards();
        
        // Create charts with a small delay to ensure DOM is ready
        setTimeout(() => {
            this._createSalesTypeChart();
            this._createSalesFunnelChart();
            this._createTrendChart();
        }, 100);
    }

    /**
     * Remove existing charts to prevent duplication
     */
    _removeExistingCharts() {
        const existingCharts = document.querySelectorAll('.chart-container');
        existingCharts.forEach(chart => chart.remove());
    }

    /**
     * Create KPI cards with key business metrics
     */
    _createKPICards() {
        const kpiContainer = document.querySelector('.kpi-container');
        if (!kpiContainer) return;

        const quotationsTotal = this.state.quotationsData.find(item => item.sales_type_name === 'Total') || {};
        const salesOrdersTotal = this.state.salesOrdersData.find(item => item.sales_type_name === 'Total') || {};
        const invoicedSalesTotal = this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total') || {};

        const totalPipeline = (quotationsTotal.amount || 0) + (salesOrdersTotal.amount || 0) + (invoicedSalesTotal.amount || 0);
        const conversionRate = quotationsTotal.count > 0 ? ((invoicedSalesTotal.count / quotationsTotal.count) * 100).toFixed(1) : 0;
        
        kpiContainer.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-blue-100 text-sm font-medium">Total Pipeline</p>
                            <p class="text-2xl font-bold">${this.formatNumber(totalPipeline)}</p>
                        </div>
                        <div class="text-blue-200">
                            <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
                            </svg>
                        </div>
                    </div>
                </div>
                
                <div class="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-green-100 text-sm font-medium">Revenue Realized</p>
                            <p class="text-2xl font-bold">${this.formatNumber(invoicedSalesTotal.invoiced_amount || 0)}</p>
                        </div>
                        <div class="text-green-200">
                            <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
                            </svg>
                        </div>
                    </div>
                </div>
                
                <div class="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-purple-100 text-sm font-medium">Conversion Rate</p>
                            <p class="text-2xl font-bold">${conversionRate}%</p>
                        </div>
                        <div class="text-purple-200">
                            <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                            </svg>
                        </div>
                    </div>
                </div>
                
                <div class="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg p-6 text-white">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-orange-100 text-sm font-medium">Pending Orders</p>
                            <p class="text-2xl font-bold">${salesOrdersTotal.count || 0}</p>
                        </div>
                        <div class="text-orange-200">
                            <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                            </svg>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Create sales type distribution chart
     */
    _createSalesTypeChart() {
        const chartContainer = document.querySelector('.sales-type-chart');
        if (!chartContainer) return;

        const invoicedData = this.state.invoicedSalesData.filter(item => item.sales_type_name !== 'Total');
        
        const chartHtml = `
            <div class="chart-container bg-white p-6 rounded-lg shadow-lg mb-8">
                <h3 class="text-xl font-semibold mb-4 text-gray-800">Revenue by Sales Type</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <canvas id="salesTypeChart" width="300" height="200"></canvas>
                    </div>
                    <div class="flex flex-col justify-center">
                        ${invoicedData.map((item, index) => `
                            <div class="flex items-center mb-2">
                                <div class="w-4 h-4 rounded mr-3" style="background-color: ${this._getChartColor(index)}"></div>
                                <span class="text-sm text-gray-700">${item.sales_type_name}: ${this.formatNumber(item.invoiced_amount || 0)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        chartContainer.innerHTML = chartHtml;
        this._renderSalesTypeChart(invoicedData);
    }

    /**
     * Create sales funnel chart
     */
    _createSalesFunnelChart() {
        const chartContainer = document.querySelector('.sales-funnel-chart');
        if (!chartContainer) return;

        const quotationsTotal = this.state.quotationsData.find(item => item.sales_type_name === 'Total') || {};
        const salesOrdersTotal = this.state.salesOrdersData.find(item => item.sales_type_name === 'Total') || {};
        const invoicedSalesTotal = this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total') || {};

        const chartHtml = `
            <div class="chart-container bg-white p-6 rounded-lg shadow-lg mb-8">
                <h3 class="text-xl font-semibold mb-4 text-gray-800">Sales Funnel</h3>
                <div class="space-y-4">
                    <div class="funnel-stage">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-sm font-medium text-gray-700">Quotations</span>
                            <span class="text-sm text-gray-600">${quotationsTotal.count || 0} orders</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-8">
                            <div class="bg-purple-500 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium" style="width: 100%">
                                ${this.formatNumber(quotationsTotal.amount || 0)}
                            </div>
                        </div>
                    </div>
                    
                    <div class="funnel-stage">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-sm font-medium text-gray-700">Sales Orders</span>
                            <span class="text-sm text-gray-600">${salesOrdersTotal.count || 0} orders</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-8">
                            <div class="bg-green-500 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium" style="width: ${this._calculateFunnelWidth(salesOrdersTotal.amount, quotationsTotal.amount)}%">
                                ${this.formatNumber(salesOrdersTotal.amount || 0)}
                            </div>
                        </div>
                    </div>
                    
                    <div class="funnel-stage">
                        <div class="flex justify-between items-center mb-2">
                            <span class="text-sm font-medium text-gray-700">Invoiced Sales</span>
                            <span class="text-sm text-gray-600">${invoicedSalesTotal.count || 0} orders</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-8">
                            <div class="bg-blue-500 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium" style="width: ${this._calculateFunnelWidth(invoicedSalesTotal.amount, quotationsTotal.amount)}%">
                                ${this.formatNumber(invoicedSalesTotal.invoiced_amount || 0)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        chartContainer.innerHTML = chartHtml;
    }

    /**
     * Helper method to calculate funnel width percentage
     */
    _calculateFunnelWidth(current, total) {
        if (!total || total === 0) return 0;
        return Math.min(100, Math.max(10, (current / total) * 100));
    }

    /**
     * Helper method to get chart colors
     */
    _getChartColor(index) {
        const colors = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444', '#6B7280'];
        return colors[index % colors.length];
    }

    /**
     * Create trend chart placeholder
     */
    _createTrendChart() {
        const chartContainer = document.querySelector('.trend-chart');
        if (!chartContainer) return;

        const chartHtml = `
            <div class="chart-container bg-white p-6 rounded-lg shadow-lg mb-8">
                <h3 class="text-xl font-semibold mb-4 text-gray-800">Sales Performance Summary</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="text-center p-4 bg-blue-50 rounded-lg">
                        <div class="text-2xl font-bold text-blue-600">${this.state.quotationsData.find(item => item.sales_type_name === 'Total')?.count || 0}</div>
                        <div class="text-sm text-blue-800">Active Quotations</div>
                    </div>
                    <div class="text-center p-4 bg-green-50 rounded-lg">
                        <div class="text-2xl font-bold text-green-600">${this.state.salesOrdersData.find(item => item.sales_type_name === 'Total')?.count || 0}</div>
                        <div class="text-sm text-green-800">Pending Orders</div>
                    </div>
                    <div class="text-center p-4 bg-purple-50 rounded-lg">
                        <div class="text-2xl font-bold text-purple-600">${this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total')?.count || 0}</div>
                        <div class="text-sm text-purple-800">Completed Sales</div>
                    </div>
                </div>
            </div>
        `;
        
        chartContainer.innerHTML = chartHtml;
    }

    /**
     * Render the sales type chart (simplified version without Chart.js)
     */
    _renderSalesTypeChart(data) {
        // This is a placeholder for actual chart rendering
        // In a real implementation, you would use Chart.js or similar library
        console.log('Sales Type Chart Data:', data);
    }
}

// Register the component as an Odoo client action
OeSaleDashboard.template = "oe_sale_dashboard_17.yearly_sales_dashboard_template";
actionRegistry.add("oe_sale_dashboard_17_tag", OeSaleDashboard);
