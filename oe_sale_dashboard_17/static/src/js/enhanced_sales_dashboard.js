/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

/**
 * Enhanced Sales Dashboard Component
 * Professional analytics with OSUS branding
 */
class EnhancedSalesDashboard extends Component {
    static template = "oe_sale_dashboard_17.enhanced_sales_dashboard";
    
    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        
        this.state = useState({
            isLoading: true,
            data: {
                performance: {
                    total_orders: 0,
                    total_quotations: 0,
                    total_sales: 0,
                    total_invoiced: 0,
                    total_amount: 0,
                    currency_symbol: '$'
                },
                monthly_trend: { labels: [], datasets: [] },
                pipeline: { labels: [], datasets: [] },
                agent_rankings: { rankings: [] },
                broker_rankings: { rankings: [] },
                sale_types: { sale_types: [] }
            },
            // Enhanced filtering options
            filters: {
                start_date: this._getDefaultStartDate(),
                end_date: this._getDefaultEndDate(),
                sale_type_ids: [],
                booking_date: null,
                sale_order_type_id: null,
                project_ids: [],
                buyer_ids: []
            },
            // Enhanced scorecard metrics
            enhanced_scorecard: {
                total_sales_value: 0,
                total_invoiced_amount: 0,
                total_paid_amount: 0,
                payment_completion_rate: 0,
                total_sale_value_realestate: 0,
                total_developer_commission: 0,
                sale_type_breakdown: {},
                project_breakdown: {}
            },
            // Enhanced charts data
            enhanced_charts: {
                trends_chart: null,
                comparison_chart: null,
                project_performance: null,
                commission_analysis: null
            },
            // Integration status
            integration_status: {
                le_sale_type_available: false,
                real_estate_available: false,
                project_field_available: false,
                buyer_field_available: false,
                commission_field_available: false
            },
            charts: {},
            showEnhancedView: false
        });
        
        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }
    
    _getDefaultStartDate() {
        const today = new Date();
        return new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0];
    }
    
    _getDefaultEndDate() {
        return new Date().toISOString().split('T')[0];
    }
    
    async loadDashboardData() {
        try {
            this.state.isLoading = true;
            
            const result = await this.rpc("/web/dataset/call_kw", {
                model: "sale.dashboard",
                method: "get_dashboard_data",
                args: [],
                kwargs: {
                    start_date: this.state.filters.start_date,
                    end_date: this.state.filters.end_date,
                    sale_type_ids: this.state.filters.sale_type_ids
                }
            });
            
            if (result.error) {
                this.notification.add(`Dashboard Error: ${result.error}`, { type: "danger" });
                return;
            }
            
            this.state.data = result;
            this.state.isLoading = false;
            
            // Initialize charts after data is loaded
            setTimeout(() => this.initializeCharts(), 100);
            
        } catch (error) {
            console.error("Dashboard loading error:", error);
            this.notification.add("Failed to load dashboard data", { type: "danger" });
            this.state.isLoading = false;
        }
    }
    
    initializeCharts() {
        try {
            if (typeof Chart === 'undefined') {
                console.warn('Chart.js not loaded, retrying...');
                setTimeout(() => this.initializeCharts(), 500);
                return;
            }
            
            this.renderMonthlyTrendChart();
            this.renderPipelineChart();
            
        } catch (error) {
            console.error("Chart initialization error:", error);
            if (window.dashboardErrorHandler) {
                window.dashboardErrorHandler(error, 'Chart Init');
            }
        }
    }
    
    renderMonthlyTrendChart() {
        const canvas = document.getElementById('monthly_trend_chart');
        if (!canvas) return;
        
        // Destroy existing chart if exists
        if (this.state.charts.monthlyTrend) {
            this.state.charts.monthlyTrend.destroy();
        }
        
        const ctx = canvas.getContext('2d');
        const data = this.state.data.monthly_trend;
        
        // OSUS brand colors
        const brandColors = window.OSUSBrandColors || {
            primary: '#4d1a1a',
            gold: '#b8a366'
        };
        
        this.state.charts.monthlyTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: (data.datasets || []).map((dataset, index) => ({
                    ...dataset,
                    borderColor: index === 0 ? brandColors.primary : brandColors.gold,
                    backgroundColor: index === 0 ? 
                        'rgba(77, 26, 26, 0.1)' : 'rgba(184, 163, 102, 0.1)',
                    tension: 0.4
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Sales Trend',
                        color: brandColors.primary,
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'Order Count' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'Amount' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    }
    
    renderPipelineChart() {
        const canvas = document.getElementById('pipeline_chart');
        if (!canvas) return;
        
        // Destroy existing chart if exists
        if (this.state.charts.pipeline) {
            this.state.charts.pipeline.destroy();
        }
        
        const ctx = canvas.getContext('2d');
        const data = this.state.data.pipeline;
        
        // OSUS brand colors
        const brandColors = window.OSUSBrandColors || {
            chartColors: ['#4d1a1a', '#b8a366', '#7d1e2d', '#d4c299', '#cc4d66']
        };
        
        this.state.charts.pipeline = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.datasets?.[0]?.data || [],
                    backgroundColor: brandColors.chartColors,
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Sales Pipeline',
                        color: brandColors.chartColors[0],
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    formatCurrency(amount) {
        const symbol = this.state.data.performance?.currency_symbol || '$';
        return `${symbol}${this.formatNumber(amount)}`;
    }
    
    formatNumber(value) {
        if (!value || value === 0) return "0";
        
        const abs = Math.abs(value);
        if (abs >= 1_000_000_000) {
            return (value / 1_000_000_000).toFixed(2) + 'B';
        } else if (abs >= 1_000_000) {
            return (value / 1_000_000).toFixed(2) + 'M';
        } else if (abs >= 1_000) {
            return (value / 1_000).toFixed(0) + 'K';
        }
        return value.toFixed(0);
    }
    
    async onRefreshDashboard() {
        await this.loadDashboardData();
    }
    
    onFilterChange(field, value) {
        this.state.filters[field] = value;
    }
    
    async onApplyFilters() {
        await this.loadDashboardData();
    }

    // Enhanced Dashboard Methods for Real Estate Integration

    async loadEnhancedDashboardData() {
        """Load enhanced dashboard data with real estate integration"""
        try {
            this.state.isLoading = true;
            
            const result = await this.rpc("/web/dataset/call_kw", {
                model: "sale.dashboard",
                method: "get_enhanced_dashboard_data",
                args: [
                    this.state.filters.start_date,
                    this.state.filters.end_date,
                    {
                        booking_date: this.state.filters.booking_date,
                        sale_order_type_id: this.state.filters.sale_order_type_id,
                        project_ids: this.state.filters.project_ids,
                        buyer_ids: this.state.filters.buyer_ids,
                        sale_type_ids: this.state.filters.sale_type_ids
                    }
                ],
                kwargs: {}
            });
            
            if (result.error) {
                this.notification.add(`Enhanced Dashboard Error: ${result.error}`, { type: "danger" });
                return;
            }
            
            // Update state with enhanced data
            this.state.enhanced_scorecard = result.enhanced_scorecard || {};
            this.state.enhanced_charts = result.enhanced_charts || {};
            this.state.integration_status = result.integration_status || {};
            this.state.data = result.base_dashboard || this.state.data;
            this.state.isLoading = false;
            
            // Initialize enhanced charts
            setTimeout(() => this.initializeEnhancedCharts(), 100);
            
        } catch (error) {
            console.error("Enhanced dashboard loading error:", error);
            this.notification.add("Failed to load enhanced dashboard data", { type: "danger" });
            this.state.isLoading = false;
        }
    }

    initializeEnhancedCharts() {
        """Initialize all enhanced charts including trends, comparison, and real estate specific"""
        try {
            if (typeof Chart === 'undefined') {
                console.warn('Chart.js not loaded for enhanced charts, retrying...');
                setTimeout(() => this.initializeEnhancedCharts(), 500);
                return;
            }
            
            // Render enhanced charts
            this.renderTrendsChart();
            this.renderComparisonChart();
            this.renderProjectPerformanceChart();
            this.renderCommissionAnalysisChart();
            
        } catch (error) {
            console.error("Enhanced chart initialization error:", error);
        }
    }

    renderTrendsChart() {
        """Render sales trends chart using booking_date data"""
        const canvas = document.getElementById('trends_chart');
        if (!canvas || !this.state.enhanced_charts.trends_chart) return;
        
        // Destroy existing chart
        if (this.state.charts.trendsChart) {
            this.state.charts.trendsChart.destroy();
        }
        
        const ctx = canvas.getContext('2d');
        const chartData = this.state.enhanced_charts.trends_chart;
        
        this.state.charts.trendsChart = new Chart(ctx, {
            type: chartData.type,
            data: chartData.data,
            options: {
                ...chartData.options,
                plugins: {
                    ...chartData.options.plugins,
                    title: {
                        display: true,
                        text: 'Sales Trends Analysis',
                        color: '#800020',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
    }

    renderComparisonChart() {
        """Render sale type comparison chart"""
        const canvas = document.getElementById('comparison_chart');
        if (!canvas || !this.state.enhanced_charts.comparison_chart) return;
        
        // Destroy existing chart
        if (this.state.charts.comparisonChart) {
            this.state.charts.comparisonChart.destroy();
        }
        
        const ctx = canvas.getContext('2d');
        const chartData = this.state.enhanced_charts.comparison_chart;
        
        this.state.charts.comparisonChart = new Chart(ctx, {
            type: chartData.type,
            data: chartData.data,
            options: {
                ...chartData.options,
                plugins: {
                    ...chartData.options.plugins,
                    title: {
                        display: true,
                        text: 'Sales by Type Comparison',
                        color: '#800020',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
    }

    renderProjectPerformanceChart() {
        """Render project performance chart for real estate"""
        const canvas = document.getElementById('project_performance_chart');
        if (!canvas || !this.state.enhanced_charts.project_performance) return;
        
        // Destroy existing chart
        if (this.state.charts.projectChart) {
            this.state.charts.projectChart.destroy();
        }
        
        const ctx = canvas.getContext('2d');
        const chartData = this.state.enhanced_charts.project_performance;
        
        this.state.charts.projectChart = new Chart(ctx, {
            type: chartData.type,
            data: chartData.data,
            options: {
                ...chartData.options,
                plugins: {
                    ...chartData.options.plugins,
                    title: {
                        display: true,
                        text: 'Project Performance Analysis',
                        color: '#800020',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
    }

    renderCommissionAnalysisChart() {
        """Render commission analysis chart"""
        const canvas = document.getElementById('commission_analysis_chart');
        if (!canvas || !this.state.enhanced_charts.commission_analysis) return;
        
        // Destroy existing chart
        if (this.state.charts.commissionChart) {
            this.state.charts.commissionChart.destroy();
        }
        
        const ctx = canvas.getContext('2d');
        const chartData = this.state.enhanced_charts.commission_analysis;
        
        this.state.charts.commissionChart = new Chart(ctx, {
            type: chartData.type,
            data: chartData.data,
            options: {
                ...chartData.options,
                plugins: {
                    ...chartData.options.plugins,
                    title: {
                        display: true,
                        text: 'Commission Distribution Analysis',
                        color: '#800020',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
    }

    onToggleEnhancedView() {
        """Toggle between standard and enhanced dashboard view"""
        this.state.showEnhancedView = !this.state.showEnhancedView;
        
        if (this.state.showEnhancedView) {
            this.loadEnhancedDashboardData();
        } else {
            this.loadDashboardData();
        }
    }

    onEnhancedFilterChange(field, value) {
        """Handle enhanced filter changes"""
        this.state.filters[field] = value;
        
        // Auto-refresh if enhanced view is active
        if (this.state.showEnhancedView) {
            setTimeout(() => this.loadEnhancedDashboardData(), 300);
        }
    }

    async onApplyEnhancedFilters() {
        """Apply enhanced filters and reload data"""
        if (this.state.showEnhancedView) {
            await this.loadEnhancedDashboardData();
        } else {
            await this.loadDashboardData();
        }
    }

    getEnhancedScorecard() {
        """Get enhanced scorecard data for display"""
        return this.state.enhanced_scorecard;
    }

    getSaleTypeBreakdown() {
        """Get sale type breakdown for enhanced view"""
        return Object.entries(this.state.enhanced_scorecard.sale_type_breakdown || {}).map(([type, data]) => ({
            type,
            count: data.count,
            amount: this.formatCurrency(data.amount),
            avg_value: this.formatCurrency(data.avg_value)
        }));
    }

    getProjectBreakdown() {
        """Get project breakdown for real estate view"""
        return Object.entries(this.state.enhanced_scorecard.project_breakdown || {}).map(([project, data]) => ({
            project,
            count: data.count,
            amount: this.formatCurrency(data.amount),
            units_sold: data.units_sold
        }));
    }

    getIntegrationStatus() {
        """Get integration status for conditional display"""
        return this.state.integration_status;
    }
}

// Register the component
registry.category("actions").add("enhanced_sales_dashboard", EnhancedSalesDashboard);
