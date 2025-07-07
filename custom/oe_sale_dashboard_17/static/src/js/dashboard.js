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
            postedSalesData: [],
            unpostedSalesData: [],
            quotationsData: [],
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
     * Fetches sales data for a specific company within the selected date range.
     * @param {number} companyId - The ID of the company.
     * @param {string} start_date_str - The start date in YYYY-MM-DD format.
     * @param {string} end_date_str - The end date in YYYY-MM-DD format.
     * @param {Array} baseDomain - The base domain for the sales order query (e.g., state, invoice_status).
     * @returns {Object} Object with amount_total, sale_value totals and count for the given period.
     */
    async _fetchSalesByCompanyAndDateRange(companyId, start_date_str, end_date_str, baseDomain) {
        // Convert dates to datetime strings for proper filtering
        const startDateTime = start_date_str + ' 00:00:00';
        const endDateTime = end_date_str + ' 23:59:59';
        
        let domain = [
            ['company_id', '=', companyId],
            ['booking_date', '>=', startDateTime],
            ['booking_date', '<=', endDateTime],
            ...baseDomain
        ];

        // Fetch both amount_total and sale_value fields
        const salesOrders = await this.orm.searchRead(
            "sale.order",
            domain,
            ['amount_total', 'sale_value']
        );

        // Sum both totals and count records
        let totalAmount = 0.0;
        let totalSaleValue = 0.0;
        const count = salesOrders.length;
        
        for (const order of salesOrders) {
            totalAmount += order.amount_total || 0.0;
            totalSaleValue += order.sale_value || 0.0;
        }
        return {
            amount_total: totalAmount,
            sale_value: totalSaleValue,
            count: count
        };
    }

    /**
     * Loads all dashboard data (posted, unposted, quotations) for the selected date range.
     */
    async _loadDashboardData() {
        this.state.isLoading = true;
        try {
            // Validate date range
            if (this.state.startDate > this.state.endDate) {
                this.notification.add(_t("Start date cannot be later than end date"), { type: 'warning' });
                this.state.isLoading = false;
                return;
            }

            const companies = await this.orm.searchRead(
                "res.company",
                [],
                ['id', 'name']
            );

            const postedSales = [];
            const unpostedSales = [];
            const quotations = [];

            for (const company of companies) {
                const companyId = company.id;
                const companyName = company.name;

                // Fetch Posted Sale Orders (confirmed and invoiced)
                const postedAmounts = await this._fetchSalesByCompanyAndDateRange(
                    companyId, 
                    this.state.startDate, 
                    this.state.endDate, 
                    [['state', '=', 'sale'], ['invoice_status', '=', 'invoiced']]
                );

                postedSales.push({
                    company_name: companyName,
                    count: postedAmounts.count,
                    amount_total: postedAmounts.amount_total,
                    sale_value: postedAmounts.sale_value,
                });

                // Fetch Unposted Sale Orders (confirmed but not invoiced)
                const unpostedAmounts = await this._fetchSalesByCompanyAndDateRange(
                    companyId, 
                    this.state.startDate, 
                    this.state.endDate, 
                    [['state', '=', 'sale'], '|', ['invoice_status', '=', 'to invoice'], ['invoice_status', '=', 'no']]
                );

                unpostedSales.push({
                    company_name: companyName,
                    count: unpostedAmounts.count,
                    amount: unpostedAmounts.amount_total,
                });

                // Fetch All Quotations (draft and sent)
                const quotationsAmounts = await this._fetchSalesByCompanyAndDateRange(
                    companyId, 
                    this.state.startDate, 
                    this.state.endDate, 
                    [['state', 'in', ['draft', 'sent']]]
                );

                quotations.push({
                    company_name: companyName,
                    count: quotationsAmounts.count,
                    amount: quotationsAmounts.amount_total,
                });
            }

            // Calculate "Total" rows for each section
            const calculateTotals = (data, hasAmountField = false, hasSaleValueField = false) => {
                if (data.length === 0) {
                    const result = {
                        company_name: "Total", 
                        count: 0
                    };
                    if (hasAmountField) result.amount = 0;
                    if (hasSaleValueField) {
                        result.amount_total = 0;
                        result.sale_value = 0;
                    }
                    return result;
                }
                
                const result = {
                    company_name: "Total",
                    count: data.reduce((sum, item) => sum + item.count, 0)
                };
                
                if (hasAmountField) {
                    result.amount = data.reduce((sum, item) => sum + item.amount, 0);
                }
                if (hasSaleValueField) {
                    result.amount_total = data.reduce((sum, item) => sum + item.amount_total, 0);
                    result.sale_value = data.reduce((sum, item) => sum + item.sale_value, 0);
                }
                
                return result;
            };

            const postedSalesTotal = calculateTotals(postedSales, false, true);
            const unpostedSalesTotal = calculateTotals(unpostedSales, true, false);
            const quotationsTotal = calculateTotals(quotations, true, false);

            this.state.postedSalesData = [...postedSales, postedSalesTotal];
            this.state.unpostedSalesData = [...unpostedSales, unpostedSalesTotal];
            this.state.quotationsData = [...quotations, quotationsTotal];

            this.notification.add(_t(`Sales data updated for: ${this.state.startDate} to ${this.state.endDate}`), { type: 'success' });

        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.notification.add(_t("Error loading sales data. Please check console for details."), { type: 'danger' });
        } finally {
            this.state.isLoading = false;
        }
    }
}

// Register the component as an Odoo client action
OeSaleDashboard.template = "oe_sale_dashboard_17.yearly_sales_dashboard_template";
actionRegistry.add("oe_sale_dashboard_17_tag", OeSaleDashboard);
