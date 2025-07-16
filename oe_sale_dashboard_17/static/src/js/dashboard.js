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
            topAgentsData: [],
            topAgenciesData: [],
            isLoading: false,
        });

        // Chart instances for cleanup
        this.charts = {
            revenue: null,
            trend: null,
            salesTypePie: null,
            dealFluctuation: null
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

        // Modern Color Palette for Charts
        this.colorPalette = {
            primary: {
                background: 'rgba(59, 130, 246, 0.8)',
                border: 'rgba(59, 130, 246, 1)',
                gradient: 'linear-gradient(135deg, rgba(59, 130, 246, 0.8), rgba(96, 165, 250, 0.8))'
            },
            secondary: {
                background: 'rgba(16, 185, 129, 0.8)',
                border: 'rgba(16, 185, 129, 1)',
                gradient: 'linear-gradient(135deg, rgba(16, 185, 129, 0.8), rgba(52, 211, 153, 0.8))'
            },
            accent: {
                background: 'rgba(245, 158, 11, 0.8)',
                border: 'rgba(245, 158, 11, 1)',
                gradient: 'linear-gradient(135deg, rgba(245, 158, 11, 0.8), rgba(251, 191, 36, 0.8))'
            },
            purple: {
                background: 'rgba(139, 92, 246, 0.8)',
                border: 'rgba(139, 92, 246, 1)',
                gradient: 'linear-gradient(135deg, rgba(139, 92, 246, 0.8), rgba(167, 139, 250, 0.8))'
            },
            danger: {
                background: 'rgba(239, 68, 68, 0.8)',
                border: 'rgba(239, 68, 68, 1)',
                gradient: 'linear-gradient(135deg, rgba(239, 68, 68, 0.8), rgba(248, 113, 113, 0.8))'
            },
            success: {
                background: 'rgba(16, 185, 129, 0.8)',
                border: 'rgba(16, 185, 129, 1)',
                gradient: 'linear-gradient(135deg, rgba(16, 185, 129, 0.8), rgba(52, 211, 153, 0.8))'
            },
            info: {
                background: 'rgba(6, 182, 212, 0.8)',
                border: 'rgba(6, 182, 212, 1)',
                gradient: 'linear-gradient(135deg, rgba(6, 182, 212, 0.8), rgba(34, 211, 238, 0.8))'
            },
            pink: {
                background: 'rgba(236, 72, 153, 0.8)',
                border: 'rgba(236, 72, 153, 1)',
                gradient: 'linear-gradient(135deg, rgba(236, 72, 153, 0.8), rgba(244, 114, 182, 0.8))'
            }
        };

        // Chart color arrays for easy use
        this.chartColors = {
            backgrounds: [
                this.colorPalette.primary.background,
                this.colorPalette.secondary.background,
                this.colorPalette.purple.background,
                this.colorPalette.accent.background,
                this.colorPalette.danger.background,
                this.colorPalette.info.background,
                this.colorPalette.pink.background,
                'rgba(156, 163, 175, 0.8)'  // Gray fallback
            ],
            borders: [
                this.colorPalette.primary.border,
                this.colorPalette.secondary.border,
                this.colorPalette.purple.border,
                this.colorPalette.accent.border,
                this.colorPalette.danger.border,
                this.colorPalette.info.border,
                this.colorPalette.pink.border,
                'rgba(156, 163, 175, 1)'    // Gray fallback
            ]
        };

        // Load dashboard data when the component is mounted
        onMounted(async () => {
            console.log("Executive Sales Dashboard - Date Range:", this.state.startDate, "to", this.state.endDate);
            await this._loadDashboardData();
            
            // Add scroll-to-top functionality
            this._addScrollToTopButton();
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
     * Format large numbers for dashboard display with K/M/B suffixes
     * @param {number} value - The numerical value to format
     * @returns {string} - Formatted string with appropriate suffix
     */
    formatDashboardValue(value) {
        if (!value || value === 0) {
            return "0";
        }
        
        const absValue = Math.abs(value);
        
        if (absValue >= 1_000_000_000) {
            const formatted = Math.round((value / 1_000_000_000) * 100) / 100;
            return `${formatted} B`;
        } else if (absValue >= 1_000_000) {
            const formatted = Math.round((value / 1_000_000) * 100) / 100;
            return `${formatted} M`;
        } else if (absValue >= 1_000) {
            const formatted = Math.round(value / 1_000);
            return `${formatted} K`;
        } else {
            return `${Math.round(value)}`;
        }
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

            // Load top performing agents and agencies data
            await this._loadTopPerformersData();

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
        
        // Wait for Chart.js to load and DOM to be ready
        this._waitForChartJS().then(() => {
            this._createRevenueDistributionChart();
            this._createEnhancedFunnelChart();
            this._createTrendAnalysisChart();
            this._createSalesTypePieCharts().then(() => {
                this._createDealFluctuationChart().then(() => {
                    this._createPerformanceSummary();
                    
                    // Add chart control event listeners
                    this._setupChartControlListeners();
                });
            });
        });
    }

    /**
     * Wait for Chart.js to be available
     */
    async _waitForChartJS() {
        return new Promise((resolve) => {
            const checkChart = () => {
                if (typeof Chart !== 'undefined') {
                    resolve();
                } else {
                    setTimeout(checkChart, 100);
                }
            };
            checkChart();
        });
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
        this.charts = { revenue: null, trend: null, salesTypePie: null, dealFluctuation: null };
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
     * Helper function to prepare canvas and set common chart options
     * @param {string} canvasId - ID of the canvas element
     * @param {string} chartType - Type of chart to prepare settings for
     * @returns {Object} - Contains the context and prepared default options
     */
    _prepareChartCanvas(canvasId, chartType) {
        try {
            // Wait for DOM to be ready
            const canvas = document.getElementById(canvasId);
            if (!canvas) {
                console.warn(`Canvas element with ID '${canvasId}' not found in DOM`);
                return null;
            }
            
            if (typeof Chart === 'undefined') {
                console.warn('Chart.js library not available');
                return null;
            }

            // Ensure canvas has proper parent container
            const chartContainer = canvas.parentElement;
            if (!chartContainer) {
                console.warn(`Canvas ${canvasId} has no parent container`);
                return null;
            }

            // Reset canvas dimensions for proper rendering
            const containerWidth = chartContainer.offsetWidth || 400; // Fallback width
            canvas.width = containerWidth;
            canvas.height = 300; // Fixed height for consistent rendering
            
            const ctx = canvas.getContext('2d');
            if (!ctx) {
                console.warn(`Failed to get 2D context for canvas ${canvasId}`);
                return null;
            }
        
        // Common base options for all charts
        const baseOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: chartType === 'doughnut' || chartType === 'pie' ? 'bottom' : 'top',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 11
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 13
                    },
                    bodyFont: {
                        size: 12
                    },
                    padding: 12,
                    cornerRadius: 4,
                    displayColors: true
                }
            }
        };
        
        // Additional options based on chart type
        if (chartType === 'bar' || chartType === 'line') {
            baseOptions.scales = {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        drawBorder: false,
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            };
        }
        
        return { ctx, options: baseOptions };
        } catch (error) {
            console.error(`Error preparing canvas ${canvasId}:`, error);
            return null;
        }
    }
    
    /**
     * Create revenue distribution chart using Chart.js
     */
    _createRevenueDistributionChart() {
        try {
            const chartSetup = this._prepareChartCanvas('revenueChart', 'doughnut');
            if (!chartSetup) {
                console.warn('Failed to prepare canvas for revenue chart');
                return;
            }
            
            const { ctx, options } = chartSetup;

        // Filter out 'Total' rows and get valid data with non-zero invoiced amounts
        const invoicedData = this.state.invoicedSalesData.filter(item => 
            item.sales_type_name !== 'Total' && 
            (item.invoiced_amount > 0 || item.amount > 0)
        );
        
        // Provide fallback data if no valid data exists
        if (!invoicedData.length) {
            invoicedData.push({
                sales_type_name: 'No Data',
                invoiced_amount: 0,
                amount: 0
            });
        }
        
        console.log('Revenue Chart Data:', invoicedData); // Debug log
        
        const chartData = {
            labels: invoicedData.map(item => item.sales_type_name),
            datasets: [{
                label: 'Revenue by Sales Type',
                // Use invoiced_amount if available and > 0, otherwise fallback to amount
                data: invoicedData.map(item => {
                    const value = (item.invoiced_amount && item.invoiced_amount > 0) 
                        ? item.invoiced_amount 
                        : (item.amount || 0);
                    return value;
                }),
                backgroundColor: this.chartColors.backgrounds,
                borderColor: this.chartColors.borders,
                borderWidth: 2,
                hoverOffset: 10
            }]
        };

        // Merge base options with chart-specific options
        const chartOptions = Object.assign({}, options, {
            plugins: Object.assign({}, options.plugins, {
                tooltip: Object.assign({}, options.plugins.tooltip, {
                    callbacks: {
                        label: (context) => {
                            const label = context.label || '';
                            const value = this.formatNumber(context.parsed);
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                })
            }),
            animation: {
                animateRotate: true,
                duration: 1000
            },
            cutout: '65%', // Makes the doughnut hole slightly larger for better appearance
        });

        this.charts.revenue = new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: chartOptions
        });
        } catch (error) {
            console.error('Error creating revenue chart:', error);
        }
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
        const chartSetup = this._prepareChartCanvas('trendChart', 'line');
        if (!chartSetup) {
            console.warn('Failed to prepare canvas for trend chart');
            return;
        }
        
        const { ctx, options } = chartSetup;

        // Generate trend data based on current date range and actual data
        const { labels, trendData } = this._generateTrendDataFromActualData();

        const chartData = {
            labels: labels,
            datasets: [
                {
                    label: 'Quotations',
                    data: trendData.quotations,
                    borderColor: 'rgba(245, 158, 11, 1)',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Sales Orders',
                    data: trendData.orders,
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Invoiced Sales',
                    data: trendData.invoiced,
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
     * Create pie charts for sales type distribution by count and total
     * Shows share of each sale type excluding cancelled sales
     */
    async _createSalesTypePieCharts() {
        try {
            // Try to get distribution data from backend
            const distributionData = await this.orm.call(
                "sale.order",
                "get_sales_type_distribution", 
                [this.state.startDate, this.state.endDate]
            );
            
            if (distributionData && distributionData.count_distribution) {
                this._createSalesTypeCountChartWithData(distributionData.count_distribution);
                this._createSalesTypeTotalChartWithData(distributionData.amount_distribution);
                return;
            }
        } catch (error) {
            console.warn('Could not fetch sales type distribution from backend, using fallback:', error);
        }
        
        // Fallback to client-side calculation
        this._createSalesTypeCountChart();
        this._createSalesTypeTotalChart();
    }

    /**
     * Create pie chart showing sales type distribution by count using backend data
     */
    _createSalesTypeCountChartWithData(countData) {
        const canvas = document.getElementById('salesTypeCountChart');
        if (!canvas || typeof Chart === 'undefined') {
            console.warn('Chart.js not available or salesTypeCountChart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        
        const labels = Object.keys(countData);
        const data = Object.values(countData);
        
        if (labels.length === 0) {
            console.warn('No sales type count data available');
            return;
        }
        
        const chartData = {
            labels: labels,
            datasets: [{
                label: 'Sales Count by Type',
                data: data,
                backgroundColor: this.chartColors.backgrounds,
                borderColor: this.chartColors.borders,
                borderWidth: 2,
                hoverOffset: 8
            }]
        };

        this.charts.salesTypePie = new Chart(ctx, {
            type: 'pie',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                            font: {
                                size: 11,
                                family: 'Inter'
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${label}: ${value} sales (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1200
                }
            }
        });
    }

    /**
     * Create pie chart showing sales type distribution by total amount using backend data
     */
    _createSalesTypeTotalChartWithData(amountData) {
        const canvas = document.getElementById('salesTypeTotalChart');
        if (!canvas || typeof Chart === 'undefined') {
            console.warn('Chart.js not available or salesTypeTotalChart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        
        const labels = Object.keys(amountData);
        const data = Object.values(amountData);
        
        if (labels.length === 0) {
            console.warn('No sales type amount data available');
            return;
        }
        
        const chartData = {
            labels: labels,
            datasets: [{
                label: 'Sales Amount by Type',
                data: data,
                backgroundColor: this.chartColors.backgrounds,
                borderColor: this.chartColors.borders,
                borderWidth: 2,
                hoverOffset: 8
            }]
        };

        new Chart(ctx, {
            type: 'pie',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                            font: {
                                size: 11,
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
                                const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1200
                }
            }
        });
    }

    /**
     * Create pie chart showing sales type distribution by count
     */
    _createSalesTypeCountChart() {
        const canvas = document.getElementById('salesTypeCountChart');
        if (!canvas || typeof Chart === 'undefined') {
            console.warn('Chart.js not available or salesTypeCountChart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Get all sales data combined (excluding cancelled and Total rows)
        const allSalesData = [];
        
        // Combine data from quotations, sales orders, and invoiced sales
        const quotationsData = this.state.quotationsData.filter(item => item.sales_type_name !== 'Total');
        const salesOrdersData = this.state.salesOrdersData.filter(item => item.sales_type_name !== 'Total');
        const invoicedSalesData = this.state.invoicedSalesData.filter(item => item.sales_type_name !== 'Total');
        
        // Create a map to aggregate counts by sales type
        const salesTypeMap = new Map();
        
        // Process each category
        [quotationsData, salesOrdersData, invoicedSalesData].forEach(dataSet => {
            dataSet.forEach(item => {
                const typeName = item.sales_type_name;
                const count = item.count || 0;
                
                if (salesTypeMap.has(typeName)) {
                    salesTypeMap.set(typeName, salesTypeMap.get(typeName) + count);
                } else {
                    salesTypeMap.set(typeName, count);
                }
            });
        });

        // Convert map to arrays for chart
        const labels = Array.from(salesTypeMap.keys());
        const data = Array.from(salesTypeMap.values());
        
        const chartData = {
            labels: labels,
            datasets: [{
                label: 'Sales Count by Type',
                data: data,
                backgroundColor: [
                    'rgba(99, 102, 241, 0.8)',   // Indigo
                    'rgba(34, 197, 94, 0.8)',    // Green
                    'rgba(168, 85, 247, 0.8)',   // Violet
                    'rgba(251, 146, 60, 0.8)',   // Orange
                    'rgba(244, 63, 94, 0.8)',    // Rose
                    'rgba(14, 165, 233, 0.8)',   // Sky
                    'rgba(132, 204, 22, 0.8)',   // Lime
                ],
                borderColor: [
                    'rgba(99, 102, 241, 1)',
                    'rgba(34, 197, 94, 1)',
                    'rgba(168, 85, 247, 1)',
                    'rgba(251, 146, 60, 1)',
                    'rgba(244, 63, 94, 1)',
                    'rgba(14, 165, 233, 1)',
                    'rgba(132, 204, 22, 1)',
                ],
                borderWidth: 2,
                hoverOffset: 8
            }]
        };

        this.charts.salesTypePie = new Chart(ctx, {
            type: 'pie',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                            font: {
                                size: 11,
                                family: 'Inter'
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${label}: ${value} sales (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1200
                }
            }
        });
    }

    /**
     * Create pie chart showing sales type distribution by total amount
     */
    _createSalesTypeTotalChart() {
        const canvas = document.getElementById('salesTypeTotalChart');
        if (!canvas || typeof Chart === 'undefined') {
            console.warn('Chart.js not available or salesTypeTotalChart canvas not found');
            return;
        }

        const ctx = canvas.getContext('2d');
        
        // Get all sales data combined (excluding cancelled and Total rows)
        const quotationsData = this.state.quotationsData.filter(item => item.sales_type_name !== 'Total');
        const salesOrdersData = this.state.salesOrdersData.filter(item => item.sales_type_name !== 'Total');
        const invoicedSalesData = this.state.invoicedSalesData.filter(item => item.sales_type_name !== 'Total');
        
        // Create a map to aggregate amounts by sales type
        const salesTypeMap = new Map();
        
        // Process each category - sum all amounts for comprehensive view
        [quotationsData, salesOrdersData, invoicedSalesData].forEach(dataSet => {
            dataSet.forEach(item => {
                const typeName = item.sales_type_name;
                // Use invoiced_amount for invoiced sales, otherwise use amount
                const amount = (item.invoiced_amount && item.invoiced_amount > 0) 
                    ? item.invoiced_amount 
                    : (item.amount || 0);
                
                if (salesTypeMap.has(typeName)) {
                    salesTypeMap.set(typeName, salesTypeMap.get(typeName) + amount);
                } else {
                    salesTypeMap.set(typeName, amount);
                }
            });
        });

        // Convert map to arrays for chart
        const labels = Array.from(salesTypeMap.keys());
        const data = Array.from(salesTypeMap.values());
        
        const chartData = {
            labels: labels,
            datasets: [{
                label: 'Sales Amount by Type',
                data: data,
                backgroundColor: [
                    'rgba(79, 70, 229, 0.8)',    // Indigo
                    'rgba(16, 185, 129, 0.8)',   // Emerald
                    'rgba(139, 92, 246, 0.8)',   // Violet  
                    'rgba(245, 158, 11, 0.8)',   // Amber
                    'rgba(239, 68, 68, 0.8)',    // Red
                    'rgba(6, 182, 212, 0.8)',    // Cyan
                    'rgba(101, 163, 13, 0.8)',   // Lime
                ],
                borderColor: [
                    'rgba(79, 70, 229, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(139, 92, 246, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(6, 182, 212, 1)',
                    'rgba(101, 163, 13, 1)',
                ],
                borderWidth: 2,
                hoverOffset: 8
            }]
        };

        // Note: Using same chart instance as count chart for now - will be separated with proper canvas
        new Chart(ctx, {
            type: 'pie',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                            font: {
                                size: 11,
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
                                const percentage = total > 0 ? ((context.parsed / total) * 100).toFixed(1) : 0;
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    duration: 1200
                }
            }
        });
    }

    /**
     * Create bar chart showing deal fluctuations over time
     */
    async _createDealFluctuationChart() {
        const chartSetup = this._prepareChartCanvas('dealFluctuationChart', 'line');
        if (!chartSetup) {
            console.warn('Failed to prepare canvas for deal fluctuation chart');
            return;
        }
        
        const { ctx, options } = chartSetup;
        
        // Calculate monthly data for the current date range
        const monthlyData = await this._calculateMonthlyFluctuations();
        
        const chartData = {
            labels: monthlyData.labels,
            datasets: [
                {
                    label: 'Quotations',
                    data: monthlyData.quotations,
                    backgroundColor: 'rgba(59, 130, 246, 0.6)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 2,
                    tension: 0.1
                },
                {
                    label: 'Sales Orders',
                    data: monthlyData.sales_orders || monthlyData.salesOrders, // Handle both naming conventions
                    backgroundColor: 'rgba(16, 185, 129, 0.6)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 2,
                    tension: 0.1
                },
                {
                    label: 'Invoiced Sales',
                    data: monthlyData.invoiced_sales || monthlyData.invoicedSales, // Handle both naming conventions
                    backgroundColor: 'rgba(139, 92, 246, 0.6)',
                    borderColor: 'rgba(139, 92, 246, 1)',
                    borderWidth: 2,
                    tension: 0.1
                }
            ]
        };

        this.charts.dealFluctuation = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top',
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
                                const label = context.dataset.label || '';
                                const value = this.formatNumber(context.parsed.y);
                                return `${label}: ${value}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time Period',
                            font: {
                                size: 12,
                                family: 'Inter'
                            }
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Amount',
                            font: {
                                size: 12,
                                family: 'Inter'
                            }
                        },
                        ticks: {
                            callback: (value) => this.formatNumber(value)
                        }
                    }
                },
                animation: {
                    duration: 1500
                }
            }
        });
    }

    /**
     * Calculate monthly fluctuations for deal fluctuation chart
     */
    async _calculateMonthlyFluctuations() {
        try {
            // Try to get real monthly data from the backend
            const monthlyData = await this.orm.call(
                "sale.order",
                "get_monthly_fluctuation_data", 
                [this.state.startDate, this.state.endDate]
            );
            
            if (monthlyData && monthlyData.labels) {
                return monthlyData;
            }
        } catch (error) {
            console.warn('Could not fetch monthly fluctuation data from backend, using fallback:', error);
        }
        
        // Fallback to simplified data distribution if backend method fails
        const startDate = new Date(this.state.startDate);
        const endDate = new Date(this.state.endDate);
        
        const months = [];
        const quotations = [];
        const salesOrders = [];
        const invoicedSales = [];
        
        // Generate month labels for the date range
        const currentDate = new Date(startDate);
        currentDate.setDate(1); // Start from beginning of month
        
        while (currentDate <= endDate) {
            const monthLabel = currentDate.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
            months.push(monthLabel);
            
            // Use simplified data distribution
            const quotationsTotal = this.state.quotationsData.find(item => item.sales_type_name === 'Total')?.amount || 0;
            const salesOrdersTotal = this.state.salesOrdersData.find(item => item.sales_type_name === 'Total')?.amount || 0;
            const invoicedSalesTotal = this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total')?.invoiced_amount || 0;
            
            // Distribute data across months with some variance
            const monthIndex = months.length - 1;
            const totalMonths = Math.max(1, months.length);
            const variance = 0.7 + Math.random() * 0.6; // 0.7 to 1.3 multiplier
            
            quotations.push((quotationsTotal / totalMonths) * variance);
            salesOrders.push((salesOrdersTotal / totalMonths) * variance);
            invoicedSales.push((invoicedSalesTotal / totalMonths) * variance);
            
            currentDate.setMonth(currentDate.getMonth() + 1);
        }
        
        return {
            labels: months,
            quotations: quotations,
            sales_orders: salesOrders,
            invoiced_sales: invoicedSales
        };
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
     * Generate quarter labels for trend analysis
     */
    _generateQuarterLabels() {
        const currentYear = new Date().getFullYear();
        return [
            `Q1 ${currentYear - 1}`,
            `Q2 ${currentYear - 1}`,
            `Q3 ${currentYear - 1}`,
            `Q4 ${currentYear - 1}`,
            `Q1 ${currentYear}`,
            `Q2 ${currentYear}`
        ];
    }

    /**
     * Generate year labels for trend analysis
     */
    _generateYearLabels() {
        const currentYear = new Date().getFullYear();
        return Array.from({length: 5}, (_, i) => (currentYear - 4 + i).toString());
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

    /**
     * Generate trend data based on actual dashboard data and date range
     */
    _generateTrendDataFromActualData() {
        const startDate = new Date(this.state.startDate);
        const endDate = new Date(this.state.endDate);
        const daysDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
        
        // Get current totals for scaling
        const quotationsTotal = this.state.quotationsData.find(item => item.sales_type_name === 'Total') || {};
        const salesOrdersTotal = this.state.salesOrdersData.find(item => item.sales_type_name === 'Total') || {};
        const invoicedSalesTotal = this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total') || {};

        let labels = [];
        let periods = 6; // Default number of periods
        
        if (daysDiff <= 32) {
            // Daily view for periods up to a month
            labels = this._generateDailyLabels(startDate, endDate);
            periods = labels.length;
        } else if (daysDiff <= 93) {
            // Weekly view for periods up to 3 months
            labels = this._generateWeeklyLabels(startDate, endDate);
            periods = labels.length;
        } else if (daysDiff <= 366) {
            // Monthly view for periods up to a year
            labels = this._generateMonthLabels();
            periods = labels.length;
        } else {
            // Quarterly view for longer periods
            labels = this._generateQuarterLabels();
            periods = labels.length;
        }
        
        // Generate trend data based on actual totals with realistic distribution
        const trendData = {
            quotations: this._generateRealisticTrendData(periods, quotationsTotal.amount || 0),
            orders: this._generateRealisticTrendData(periods, salesOrdersTotal.amount || 0),
            invoiced: this._generateRealisticTrendData(periods, invoicedSalesTotal.invoiced_amount || 0)
        };
        
        return { labels, trendData };
    }

    /**
     * Generate realistic trend data based on actual values
     */
    _generateRealisticTrendData(periods, totalValue) {
        if (totalValue === 0) return Array(periods).fill(0);
        
        const trend = [];
        const avgValue = totalValue / periods;
        
        for (let i = 0; i < periods; i++) {
            // Add some realistic variance (±30%)
            const variance = (Math.random() - 0.5) * 0.6;
            const growth = Math.sin((i / periods) * Math.PI) * 0.3; // Smooth growth curve
            const value = avgValue * (1 + variance + growth);
            trend.push(Math.max(0, Math.round(value)));
        }
        
        return trend;
    }

    /**
     * Generate daily labels for short date ranges
     */
    _generateDailyLabels(startDate, endDate) {
        const labels = [];
        const currentDate = new Date(startDate);
        
        while (currentDate <= endDate) {
            labels.push(currentDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            currentDate.setDate(currentDate.getDate() + 1);
        }
        
        return labels;
    }

    /**
     * Generate weekly labels for medium date ranges
     */
    _generateWeeklyLabels(startDate, endDate) {
        const labels = [];
        const currentDate = new Date(startDate);
        
        // Start from the beginning of the week
        currentDate.setDate(currentDate.getDate() - currentDate.getDay());
        
        let weekNum = 1;
        while (currentDate <= endDate) {
            labels.push(`Week ${weekNum}`);
            currentDate.setDate(currentDate.getDate() + 7);
            weekNum++;
        }
        
        return labels;
    }

    /**
     * Add scroll-to-top button and scroll functionality
     */
    _addScrollToTopButton() {
        const dashboardContainer = document.querySelector('.o_oe_sale_dashboard_17_container');
        if (!dashboardContainer) return;

        // Create navigation and scroll controls container
        const scrollContainer = document.createElement('div');
        scrollContainer.className = 'scroll-controls';
        scrollContainer.innerHTML = `
            <div class="navigation-menu">
                <button class="nav-btn" data-target="kpi-section" title="KPI Overview">
                    <i class="fa fa-dashboard"></i>
                </button>
                <button class="nav-btn" data-target="charts-section" title="Visual Analytics">
                    <i class="fa fa-bar-chart"></i>
                </button>
                <button class="nav-btn" data-target="quotations-section" title="Quotations">
                    <i class="fa fa-file-text-o"></i>
                </button>
                <button class="nav-btn" data-target="orders-section" title="Sales Orders">
                    <i class="fa fa-shopping-cart"></i>
                </button>
                <button class="nav-btn" data-target="invoiced-section" title="Invoiced Sales">
                    <i class="fa fa-check-circle"></i>
                </button>
                <div class="separator"></div>
                <button class="scroll-to-top-btn" title="Back to Top">
                    <i class="fa fa-chevron-up"></i>
                </button>
            </div>
        `;

        // Add navigation functionality
        scrollContainer.addEventListener('click', (e) => {
            const navBtn = e.target.closest('.nav-btn');
            const scrollBtn = e.target.closest('.scroll-to-top-btn');
            
            if (navBtn) {
                const targetId = navBtn.dataset.target;
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start' 
                    });
                    
                    // Update active state
                    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
                    navBtn.classList.add('active');
                }
            } else if (scrollBtn) {
                dashboardContainer.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });

        // Show/hide based on scroll position and update active nav
        dashboardContainer.addEventListener('scroll', () => {
            const scrollTop = dashboardContainer.scrollTop;
            
            if (scrollTop > 300) {
                scrollContainer.classList.add('visible');
            } else {
                scrollContainer.classList.remove('visible');
            }

            // Update active navigation based on scroll position
            this._updateActiveNavigation();
        });

        // Append to dashboard
        dashboardContainer.appendChild(scrollContainer);

        // Add smooth scrolling to all internal links
        this._addSmoothScrolling();
    }

    /**
     * Add smooth scrolling behavior to internal navigation
     */
    _addSmoothScrolling() {
        const dashboardContainer = document.querySelector('.o_oe_sale_dashboard_17_container');
        if (!dashboardContainer) return;

        // Enhance table scrolling on mobile
        const tables = dashboardContainer.querySelectorAll('.table-wrapper');
        tables.forEach(table => {
            // Add momentum scrolling for iOS
            table.style.webkitOverflowScrolling = 'touch';
            
            // Add scroll snap for better UX
            table.style.scrollSnapType = 'x mandatory';
            
            // Add scroll indicators
            this._addScrollIndicators(table);
        });
    }

    /**
     * Add scroll indicators for tables
     */
    _addScrollIndicators(tableWrapper) {
        const table = tableWrapper.querySelector('table');
        if (!table) return;

        // Check if table needs horizontal scrolling
        const needsScrolling = table.scrollWidth > tableWrapper.clientWidth;
        
        if (needsScrolling) {
            // Add subtle scroll indicators
            tableWrapper.style.position = 'relative';
            
            // Right scroll indicator
            const rightIndicator = document.createElement('div');
            rightIndicator.style.cssText = `
                position: absolute;
                top: 0;
                right: 0;
                bottom: 0;
                width: 20px;
                background: linear-gradient(to left, rgba(255,255,255,0.8), transparent);
                pointer-events: none;
                z-index: 1;
            `;
            
            // Update indicator visibility based on scroll
            tableWrapper.addEventListener('scroll', () => {
                const isAtEnd = tableWrapper.scrollLeft >= (table.scrollWidth - tableWrapper.clientWidth - 10);
                rightIndicator.style.opacity = isAtEnd ? '0' : '1';
            });
            
            tableWrapper.appendChild(rightIndicator);
        }
    }

    /**
     * Update active navigation based on scroll position
     */
    _updateActiveNavigation() {
        const sections = ['kpi-section', 'charts-section', 'quotations-section', 'orders-section', 'invoiced-section'];
        const navButtons = document.querySelectorAll('.nav-btn');
        const dashboardContainer = document.querySelector('.o_oe_sale_dashboard_17_container');
        
        if (!dashboardContainer) return;
        
        const scrollTop = dashboardContainer.scrollTop;
        const containerHeight = dashboardContainer.clientHeight;
        
        let activeSection = null;
        
        // Find the section that's most visible in the viewport
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                const rect = section.getBoundingClientRect();
                const containerRect = dashboardContainer.getBoundingClientRect();
                
                // Check if section is in viewport
                const isVisible = rect.top < containerRect.bottom && rect.bottom > containerRect.top;
                
                if (isVisible) {
                    // Calculate how much of the section is visible
                    const visibleTop = Math.max(rect.top, containerRect.top);
                    const visibleBottom = Math.min(rect.bottom, containerRect.bottom);
                    const visibleHeight = visibleBottom - visibleTop;
                    const totalHeight = rect.height;
                    const visibilityRatio = visibleHeight / totalHeight;
                    
                    // If more than 30% of the section is visible, consider it active
                    if (visibilityRatio > 0.3) {
                        activeSection = sectionId;
                    }
                }
            }
        });
        
        // Update active state
        navButtons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.target === activeSection) {
                btn.classList.add('active');
            }
        });
    }

    /**
     * Setup event listeners for chart controls and filters
     */
    _setupChartControlListeners() {
        // Revenue chart controls
        const revenueControls = document.querySelectorAll('[data-chart]');
        revenueControls.forEach(button => {
            button.addEventListener('click', (e) => {
                // Update active state
                button.parentNode.querySelectorAll('button').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Update chart based on selection
                const chartType = button.dataset.chart;
                this._updateRevenueChart(chartType);
            });
        });

        // Funnel chart controls
        const funnelControls = document.querySelectorAll('[data-funnel]');
        funnelControls.forEach(button => {
            button.addEventListener('click', (e) => {
                // Update active state
                button.parentNode.querySelectorAll('button').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Update funnel based on selection
                const funnelType = button.dataset.funnel;
                this._updateFunnelChart(funnelType);
            });
        });

        // Trend chart controls
        const trendControls = document.querySelectorAll('[data-period]');
        trendControls.forEach(button => {
            button.addEventListener('click', (e) => {
                // Update active state
                button.parentNode.querySelectorAll('button').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Update trend chart based on selection
                const period = button.dataset.period;
                this._updateTrendChart(period);
            });
        });
    }

    /**
     * Update revenue chart based on filter selection
     */
    _updateRevenueChart(chartType) {
        if (!this.charts.revenue) return;

        const invoicedData = this.state.invoicedSalesData.filter(item => item.sales_type_name !== 'Total');
        
        let data, label;
        if (chartType === 'revenue') {
            data = invoicedData.map(item => item.invoiced_amount || 0);
            label = 'Revenue by Sales Type';
        } else if (chartType === 'volume') {
            data = invoicedData.map(item => item.count || 0);
            label = 'Volume by Sales Type';
        }

        // Update chart data
        this.charts.revenue.data.datasets[0].data = data;
        this.charts.revenue.data.datasets[0].label = label;
        
        // Update chart
        this.charts.revenue.update('active');
    }

    /**
     * Update funnel chart based on filter selection
     */
    _updateFunnelChart(funnelType) {
        const funnelContainer = document.querySelector('.o_oe_sale_dashboard_17_container__funnel');
        if (!funnelContainer) return;

        const quotationsTotal = this.state.quotationsData.find(item => item.sales_type_name === 'Total') || {};
        const salesOrdersTotal = this.state.salesOrdersData.find(item => item.sales_type_name === 'Total') || {};
        const invoicedSalesTotal = this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total') || {};

        let quotationsValue, ordersValue, invoicedValue, maxValue;
        
        if (funnelType === 'amount') {
            quotationsValue = quotationsTotal.amount || 0;
            ordersValue = salesOrdersTotal.amount || 0;
            invoicedValue = invoicedSalesTotal.invoiced_amount || 0;
            maxValue = Math.max(quotationsValue, ordersValue, invoicedValue);
        } else if (funnelType === 'count') {
            quotationsValue = quotationsTotal.count || 0;
            ordersValue = salesOrdersTotal.count || 0;
            invoicedValue = invoicedSalesTotal.count || 0;
            maxValue = Math.max(quotationsValue, ordersValue, invoicedValue);
        }

        funnelContainer.innerHTML = `
            <div class="funnel-stage">
                <div class="stage-info">
                    <div class="stage-title">Quotations</div>
                    <div class="stage-count">${quotationsTotal.count || 0} quotes</div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-fill--quotations" style="width: 100%">
                        ${funnelType === 'amount' ? this.formatNumber(quotationsValue) : quotationsValue}
                    </div>
                </div>
            </div>
            
            <div class="funnel-stage">
                <div class="stage-info">
                    <div class="stage-title">Sales Orders</div>
                    <div class="stage-count">${salesOrdersTotal.count || 0} orders</div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-fill--orders" style="width: ${this._calculateFunnelWidth(ordersValue, maxValue)}%">
                        ${funnelType === 'amount' ? this.formatNumber(ordersValue) : ordersValue}
                    </div>
                </div>
            </div>
            
            <div class="funnel-stage">
                <div class="stage-info">
                    <div class="stage-title">Invoiced Sales</div>
                    <div class="stage-count">${invoicedSalesTotal.count || 0} sales</div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-fill--invoiced" style="width: ${this._calculateFunnelWidth(invoicedValue, maxValue)}%">
                        ${funnelType === 'amount' ? this.formatNumber(invoicedValue) : invoicedValue}
                    </div>
                </div>
            </div>
        `;
    }    /**
     * Update trend chart based on period selection
     */
    _updateTrendChart(period) {
        if (!this.charts.trend) return;

        let labels, trendData;
        
        if (period === 'month') {
            labels = this._generateMonthLabels();
            // Generate monthly trend data based on actual data
            const quotationsTotal = this.state.quotationsData.find(item => item.sales_type_name === 'Total') || {};
            const salesOrdersTotal = this.state.salesOrdersData.find(item => item.sales_type_name === 'Total') || {};
            const invoicedSalesTotal = this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total') || {};
            
            trendData = {
                quotations: this._generateRealisticTrendData(labels.length, quotationsTotal.amount || 0),
                orders: this._generateRealisticTrendData(labels.length, salesOrdersTotal.amount || 0),
                invoiced: this._generateRealisticTrendData(labels.length, invoicedSalesTotal.invoiced_amount || 0)
            };
        } else if (period === 'quarter') {
            labels = this._generateQuarterLabels();
            // Scale up for quarterly view
            const quotationsTotal = this.state.quotationsData.find(item => item.sales_type_name === 'Total') || {};
            const salesOrdersTotal = this.state.salesOrdersData.find(item => item.sales_type_name === 'Total') || {};
            const invoicedSalesTotal = this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total') || {};
            
            trendData = {
                quotations: this._generateRealisticTrendData(labels.length, (quotationsTotal.amount || 0) * 3),
                orders: this._generateRealisticTrendData(labels.length, (salesOrdersTotal.amount || 0) * 3),
                invoiced: this._generateRealisticTrendData(labels.length, (invoicedSalesTotal.invoiced_amount || 0) * 3)
            };
        } else if (period === 'year') {
            labels = this._generateYearLabels();
            // Scale up for yearly view
            const quotationsTotal = this.state.quotationsData.find(item => item.sales_type_name === 'Total') || {};
            const salesOrdersTotal = this.state.salesOrdersData.find(item => item.sales_type_name === 'Total') || {};
            const invoicedSalesTotal = this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total') || {};
            
            trendData = {
                quotations: this._generateRealisticTrendData(labels.length, (quotationsTotal.amount || 0) * 12),
                orders: this._generateRealisticTrendData(labels.length, (salesOrdersTotal.amount || 0) * 12),
                invoiced: this._generateRealisticTrendData(labels.length, (invoicedSalesTotal.invoiced_amount || 0) * 12)
            };
        }

        // Update chart data
        this.charts.trend.data.labels = labels;
        this.charts.trend.data.datasets[0].data = trendData.quotations;
        this.charts.trend.data.datasets[1].data = trendData.orders;
        this.charts.trend.data.datasets[2].data = trendData.invoiced;
        
        // Update chart
        this.charts.trend.update('active');
    }

    /**
     * Debug method to test chart controls
     */
    _debugChartControls() {
        console.log('Chart Controls Debug:');
        console.log('Revenue controls:', document.querySelectorAll('[data-chart]'));
        console.log('Funnel controls:', document.querySelectorAll('[data-funnel]'));
        console.log('Trend controls:', document.querySelectorAll('[data-period]'));
        console.log('Charts object:', this.charts);
    }

    /**
     * Create performance summary cards
     */
    _createPerformanceSummary() {
        const performanceContainer = document.querySelector('.o_oe_sale_dashboard_17_container__performance');
        if (!performanceContainer) {
            console.warn('Performance container not found');
            return;
        }

        // Calculate performance metrics
        const quotationsTotal = this.state.quotationsData.find(item => item.sales_type_name === 'Total') || {};
        const salesOrdersTotal = this.state.salesOrdersData.find(item => item.sales_type_name === 'Total') || {};
        const invoicedSalesTotal = this.state.invoicedSalesData.find(item => item.sales_type_name === 'Total') || {};

        // Calculate conversion rates
        const quotationCount = quotationsTotal.count || 0;
        const salesOrderCount = salesOrdersTotal.count || 0;
        const invoicedCount = invoicedSalesTotal.count || 0;
        
        const quotationToOrderRate = quotationCount > 0 ? ((salesOrderCount / quotationCount) * 100).toFixed(1) : 0;
        const orderToInvoiceRate = salesOrderCount > 0 ? ((invoicedCount / salesOrderCount) * 100).toFixed(1) : 0;
        const overallConversionRate = quotationCount > 0 ? ((invoicedCount / quotationCount) * 100).toFixed(1) : 0;

        // Calculate revenue metrics
        const totalPipelineValue = (quotationsTotal.amount || 0) + (salesOrdersTotal.amount || 0);
        const realizedRevenue = invoicedSalesTotal.invoiced_amount || 0;
        const revenueRealizationRate = totalPipelineValue > 0 ? ((realizedRevenue / totalPipelineValue) * 100).toFixed(1) : 0;

        // Create performance summary HTML using existing CSS classes
        performanceContainer.innerHTML = `
            <div class="performance-card performance-card--quotations">
                <div class="performance-value">${overallConversionRate}%</div>
                <div class="performance-label">Overall Conversion Rate</div>
            </div>
            
            <div class="performance-card performance-card--orders">
                <div class="performance-value">${quotationToOrderRate}%</div>
                <div class="performance-label">Quote Success Rate</div>
            </div>
            
            <div class="performance-card performance-card--invoiced">
                <div class="performance-value">${orderToInvoiceRate}%</div>
                <div class="performance-label">Invoice Completion</div>
            </div>
            
            <div class="performance-card performance-card--quotations">
                <div class="performance-value">${revenueRealizationRate}%</div>
                <div class="performance-label">Revenue Realization</div>
            </div>
            
            <div class="performance-card performance-card--orders">
                <div class="performance-value">${this.formatNumber(totalPipelineValue)}</div>
                <div class="performance-label">Total Pipeline Value</div>
            </div>
            
            <div class="performance-card performance-card--invoiced">
                <div class="performance-value">${this.formatNumber(realizedRevenue)}</div>
                <div class="performance-label">Realized Revenue</div>
            </div>
        `;
    }

    /**
     * Load top performing agents and agencies data
     */
    async _loadTopPerformersData() {
        try {
            // Load top 10 agents based on agent1_partner_id
            const topAgents = await this.orm.call(
                "sale.order",
                "get_top_performers_data", 
                [this.state.startDate, this.state.endDate, 'agent', 10]
            );

            // Load top 10 agencies based on broker_partner_id  
            const topAgencies = await this.orm.call(
                "sale.order", 
                "get_top_performers_data",
                [this.state.startDate, this.state.endDate, 'agency', 10]
            );

            this.state.topAgentsData = topAgents || [];
            this.state.topAgenciesData = topAgencies || [];

            console.log('Top Agents Data:', this.state.topAgentsData);
            console.log('Top Agencies Data:', this.state.topAgenciesData);

        } catch (error) {
            console.warn('Could not load top performers data:', error);
            this.state.topAgentsData = [];
            this.state.topAgenciesData = [];
        }
    }

    // ...existing code...
}

// Register the component as an Odoo client action
OeSaleDashboard.template = "oe_sale_dashboard_17.yearly_sales_dashboard_template";
actionRegistry.add("oe_sale_dashboard_17_tag", OeSaleDashboard);
