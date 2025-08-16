/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

/**
 * Payment Approval Dashboard Component
 * 
 * Provides a comprehensive dashboard for payment approval management
 * Shows statistics, charts, and quick action buttons
 */
export class PaymentApprovalDashboard extends Component {
    static template = "payment_approval_pro.PaymentApprovalDashboard";
    static props = {};

    setup() {
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.action = useService("action");
        
        this.state = useState({
            isLoading: true,
            dashboardData: null,
            chartData: null,
            refreshing: false,
            dateRange: 'month', // week, month, quarter, year
        });
        
        onWillStart(this.loadDashboardData);
        onMounted(this.initializeCharts);
    }

    /**
     * Load dashboard data from server
     */
    async loadDashboardData() {
        this.state.isLoading = true;
        
        try {
            const data = await this.orm.call(
                "payment.voucher",
                "get_dashboard_data",
                [],
                { 
                    context: { 
                        date_range: this.state.dateRange 
                    } 
                }
            );
            
            this.state.dashboardData = data;
            this.state.chartData = data.chart_data;
            
        } catch (error) {
            this.notification.add(
                _t("Failed to load dashboard data: %s", error.message || error),
                { type: "danger" }
            );
        } finally {
            this.state.isLoading = false;
        }
    }

    /**
     * Initialize Chart.js charts
     */
    initializeCharts() {
        if (!this.state.chartData) return;
        
        this.renderStatusChart();
        this.renderAmountChart();
        this.renderTimelineChart();
    }

    /**
     * Render status distribution pie chart
     */
    renderStatusChart() {
        const canvas = this.el.querySelector('#statusChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const chartData = this.state.chartData.status_distribution;
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.data,
                    backgroundColor: [
                        '#6c757d', // Draft - Gray
                        '#fd7e14', // Review - Orange
                        '#20c997', // Approve - Teal
                        '#0d6efd', // Authorize - Blue
                        '#198754', // Paid - Green
                        '#dc3545', // Rejected - Red
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Render amount distribution bar chart
     */
    renderAmountChart() {
        const canvas = this.el.querySelector('#amountChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const chartData = this.state.chartData.amount_distribution;
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: _t('Amount'),
                    data: chartData.data,
                    backgroundColor: 'rgba(13, 110, 253, 0.8)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    borderWidth: 1,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD',
                                    minimumFractionDigits: 0,
                                    maximumFractionDigits: 0,
                                }).format(value);
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD',
                                }).format(context.parsed.y);
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Render timeline chart
     */
    renderTimelineChart() {
        const canvas = this.el.querySelector('#timelineChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const chartData = this.state.chartData.timeline;
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: _t('Created'),
                    data: chartData.created,
                    borderColor: 'rgba(32, 201, 151, 1)',
                    backgroundColor: 'rgba(32, 201, 151, 0.1)',
                    fill: true,
                    tension: 0.4,
                }, {
                    label: _t('Approved'),
                    data: chartData.approved,
                    borderColor: 'rgba(13, 110, 253, 1)',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    fill: true,
                    tension: 0.4,
                }, {
                    label: _t('Paid'),
                    data: chartData.paid,
                    borderColor: 'rgba(25, 135, 84, 1)',
                    backgroundColor: 'rgba(25, 135, 84, 0.1)',
                    fill: true,
                    tension: 0.4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index',
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                        }
                    }
                }
            }
        });
    }

    /**
     * Change date range and refresh data
     */
    async onDateRangeChange(dateRange) {
        if (this.state.dateRange === dateRange) return;
        
        this.state.dateRange = dateRange;
        await this.loadDashboardData();
        this.initializeCharts();
    }

    /**
     * Refresh dashboard data
     */
    async onRefresh() {
        if (this.state.refreshing) return;
        
        this.state.refreshing = true;
        await this.loadDashboardData();
        this.initializeCharts();
        this.state.refreshing = false;
        
        this.notification.add(
            _t("Dashboard refreshed successfully"),
            { type: "success" }
        );
    }

    /**
     * Navigate to specific view
     */
    async onNavigateToView(viewType, domain = []) {
        try {
            await this.action.doAction({
                type: 'ir.actions.act_window',
                name: _t('Payment Vouchers'),
                res_model: 'payment.voucher',
                view_mode: viewType,
                views: [[false, viewType]],
                domain: domain,
                context: {},
                target: 'current',
            });
        } catch (error) {
            this.notification.add(
                _t("Failed to navigate: %s", error.message || error),
                { type: "danger" }
            );
        }
    }

    /**
     * Quick actions
     */
    async onQuickAction(action) {
        switch (action) {
            case 'pending_review':
                await this.onNavigateToView('list', [['state', '=', 'review']]);
                break;
            case 'pending_approval':
                await this.onNavigateToView('list', [['state', '=', 'approve']]);
                break;
            case 'pending_authorization':
                await this.onNavigateToView('list', [['state', '=', 'authorize']]);
                break;
            case 'create_voucher':
                await this.action.doAction({
                    type: 'ir.actions.act_window',
                    name: _t('New Payment Voucher'),
                    res_model: 'payment.voucher',
                    view_mode: 'form',
                    views: [[false, 'form']],
                    target: 'current',
                });
                break;
            case 'reports':
                await this.action.doAction({
                    type: 'ir.actions.act_window',
                    name: _t('Payment Reports'),
                    res_model: 'payment.voucher',
                    view_mode: 'pivot,graph',
                    views: [[false, 'pivot'], [false, 'graph']],
                    target: 'current',
                });
                break;
        }
    }

    /**
     * Format currency amount
     */
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount || 0);
    }

    /**
     * Get status badge class
     */
    getStatusBadgeClass(status) {
        const statusClasses = {
            'draft': 'badge-secondary',
            'review': 'badge-warning',
            'approve': 'badge-info',
            'authorize': 'badge-primary',
            'paid': 'badge-success',
            'rejected': 'badge-danger',
        };
        return statusClasses[status] || 'badge-secondary';
    }

    /**
     * Get date range button class
     */
    getDateRangeClass(range) {
        return this.state.dateRange === range ? 'btn-primary' : 'btn-outline-primary';
    }

    /**
     * Check if data is available
     */
    hasData() {
        return this.state.dashboardData && this.state.dashboardData.total_count > 0;
    }
}

// Register the dashboard component
registry.category("actions").add("payment_approval_dashboard", PaymentApprovalDashboard);
