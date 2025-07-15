/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Enterprise Dashboard Main Component
 */
class EnterpriseDashboardMain extends Component {
    static template = "enterprise_dynamic_reports.DashboardMain";
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            dashboards: [],
            currentDashboard: null,
            widgets: [],
            isLoading: true
        });
        
        onMounted(() => {
            this.loadDashboardData();
        });
    }
    
    async loadDashboardData() {
        try {
            // Load user's dashboards
            const dashboards = await this.orm.searchRead(
                "enterprise.dashboard",
                [["user_id", "=", this.env.services.user.userId]],
                ["id", "name", "is_default", "layout_config"]
            );
            
            this.state.dashboards = dashboards;
            
            // Load default dashboard or first available
            const defaultDashboard = dashboards.find(d => d.is_default) || dashboards[0];
            if (defaultDashboard) {
                await this.loadDashboard(defaultDashboard.id);
            }
            
            this.state.isLoading = false;
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            this.notification.add("Error loading dashboard data", { type: "danger" });
            this.state.isLoading = false;
        }
    }
    
    async loadDashboard(dashboardId) {
        try {
            const dashboard = await this.orm.read("enterprise.dashboard", [dashboardId], [
                "name", "layout_config", "widget_ids"
            ]);
            
            if (dashboard.length > 0) {
                this.state.currentDashboard = dashboard[0];
                
                // Load widgets
                if (dashboard[0].widget_ids.length > 0) {
                    const widgets = await this.orm.read("enterprise.dashboard.widget", 
                        dashboard[0].widget_ids, [
                            "name", "widget_type", "config", "position", "is_active"
                        ]);
                    this.state.widgets = widgets.filter(w => w.is_active);
                }
            }
        } catch (error) {
            console.error("Error loading dashboard:", error);
            this.notification.add("Error loading dashboard", { type: "danger" });
        }
    }
    
    onDashboardChange(event) {
        const dashboardId = parseInt(event.target.value);
        if (dashboardId) {
            this.loadDashboard(dashboardId);
        }
    }
    
    async refreshDashboard() {
        if (this.state.currentDashboard) {
            await this.loadDashboard(this.state.currentDashboard.id);
            this.notification.add("Dashboard refreshed", { type: "success" });
        }
    }
    
    openReportConfig() {
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            res_model: "enterprise.dashboard",
            view_mode: "tree,form",
            views: [[false, "tree"], [false, "form"]],
            target: "current",
            context: { search_default_my_dashboards: 1 }
        });
    }
}

/**
 * Enterprise Balance Sheet Report Component
 */
class EnterpriseBalanceSheetReport extends Component {
    static template = "enterprise_dynamic_reports.BalanceSheetReport";
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            reportData: null,
            isLoading: true,
            reportId: null
        });
        
        onMounted(() => {
            this.loadReportData();
        });
    }
    
    async loadReportData() {
        try {
            const reportId = this.env.config.context?.report_id;
            if (reportId) {
                const reportData = await this.orm.read("enterprise.balance.sheet.report", 
                    [reportId], ["report_data", "name", "date_from", "date_to"]);
                
                if (reportData.length > 0 && reportData[0].report_data) {
                    this.state.reportData = JSON.parse(reportData[0].report_data);
                    this.state.reportId = reportId;
                }
            }
            this.state.isLoading = false;
        } catch (error) {
            console.error("Error loading report data:", error);
            this.notification.add("Error loading report data", { type: "danger" });
            this.state.isLoading = false;
        }
    }
    
    async exportToPDF() {
        if (this.state.reportId) {
            try {
                await this.orm.call("enterprise.balance.sheet.report", "action_export_pdf", 
                    [this.state.reportId]);
                this.notification.add("PDF export initiated", { type: "success" });
            } catch (error) {
                console.error("Error exporting PDF:", error);
                this.notification.add("Error exporting PDF", { type: "danger" });
            }
        }
    }
    
    async exportToExcel() {
        if (this.state.reportId) {
            try {
                await this.orm.call("enterprise.balance.sheet.report", "action_export_xlsx", 
                    [this.state.reportId]);
                this.notification.add("Excel export initiated", { type: "success" });
            } catch (error) {
                console.error("Error exporting Excel:", error);
                this.notification.add("Error exporting Excel", { type: "danger" });
            }
        }
    }
    
    drillDownAccount(accountId) {
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            res_model: "account.move.line",
            view_mode: "tree",
            domain: [["account_id", "=", accountId]],
            target: "new",
            context: { search_default_posted: 1 }
        });
    }
}

/**
 * Enterprise Profit Loss Report Component
 */
class EnterpriseProfitLossReport extends Component {
    static template = "enterprise_dynamic_reports.ProfitLossReport";
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            reportData: null,
            isLoading: true,
            reportId: null,
            chartData: null
        });
        
        onMounted(() => {
            this.loadReportData();
        });
    }
    
    async loadReportData() {
        try {
            const reportId = this.env.config.context?.report_id;
            if (reportId) {
                const reportData = await this.orm.read("enterprise.profit.loss.report", 
                    [reportId], ["report_data", "name", "date_from", "date_to"]);
                
                if (reportData.length > 0 && reportData[0].report_data) {
                    this.state.reportData = JSON.parse(reportData[0].report_data);
                    this.state.reportId = reportId;
                    this.prepareChartData();
                }
            }
            this.state.isLoading = false;
        } catch (error) {
            console.error("Error loading report data:", error);
            this.notification.add("Error loading report data", { type: "danger" });
            this.state.isLoading = false;
        }
    }
    
    prepareChartData() {
        if (this.state.reportData && this.state.reportData.summary) {
            const summary = this.state.reportData.summary;
            this.state.chartData = {
                labels: ['Revenue', 'Cost of Sales', 'Operating Expenses'],
                datasets: [{
                    label: 'Financial Performance',
                    data: [
                        summary.total_revenue,
                        summary.cost_of_sales,
                        summary.operating_expenses
                    ],
                    backgroundColor: [
                        'rgba(34, 197, 94, 0.8)',   // Green for revenue
                        'rgba(239, 68, 68, 0.8)',    // Red for costs
                        'rgba(251, 146, 60, 0.8)'    // Orange for expenses
                    ],
                    borderColor: [
                        'rgba(34, 197, 94, 1)',
                        'rgba(239, 68, 68, 1)',
                        'rgba(251, 146, 60, 1)'
                    ],
                    borderWidth: 2
                }]
            };
        }
    }
    
    async exportToPDF() {
        if (this.state.reportId) {
            try {
                await this.orm.call("enterprise.profit.loss.report", "action_export_pdf", 
                    [this.state.reportId]);
                this.notification.add("PDF export initiated", { type: "success" });
            } catch (error) {
                console.error("Error exporting PDF:", error);
                this.notification.add("Error exporting PDF", { type: "danger" });
            }
        }
    }
    
    drillDownCategory(category) {
        // Implementation for drilling down into specific P&L categories
        console.log("Drill down into category:", category);
    }
}

/**
 * Enterprise Trial Balance Report Component
 */
class EnterpriseTrialBalanceReport extends Component {
    static template = "enterprise_dynamic_reports.TrialBalanceReport";
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            reportData: null,
            isLoading: true,
            reportId: null,
            expandedTypes: new Set()
        });
        
        onMounted(() => {
            this.loadReportData();
        });
    }
    
    async loadReportData() {
        try {
            const reportId = this.env.config.context?.report_id;
            if (reportId) {
                const reportData = await this.orm.read("enterprise.trial.balance.report", 
                    [reportId], ["report_data", "name", "date_from", "date_to"]);
                
                if (reportData.length > 0 && reportData[0].report_data) {
                    this.state.reportData = JSON.parse(reportData[0].report_data);
                    this.state.reportId = reportId;
                }
            }
            this.state.isLoading = false;
        } catch (error) {
            console.error("Error loading report data:", error);
            this.notification.add("Error loading report data", { type: "danger" });
            this.state.isLoading = false;
        }
    }
    
    toggleAccountType(accountType) {
        if (this.state.expandedTypes.has(accountType)) {
            this.state.expandedTypes.delete(accountType);
        } else {
            this.state.expandedTypes.add(accountType);
        }
    }
    
    isTypeExpanded(accountType) {
        return this.state.expandedTypes.has(accountType);
    }
    
    drillDownAccount(accountId) {
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            res_model: "account.move.line",
            view_mode: "tree",
            domain: [["account_id", "=", accountId]],
            target: "new",
            context: { search_default_posted: 1 }
        });
    }
}

// Register client actions
registry.category("actions").add("enterprise_dashboard_main", EnterpriseDashboardMain);
registry.category("actions").add("enterprise_balance_sheet_report", EnterpriseBalanceSheetReport);
registry.category("actions").add("enterprise_profit_loss_report", EnterpriseProfitLossReport);
registry.category("actions").add("enterprise_trial_balance_report", EnterpriseTrialBalanceReport);
