/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";

export class CRMDashboardView extends Component {
    static template = "crm_executive_dashboard.Dashboard";
    static props = ["*"];
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            isLoading: true,
            crmData: {},
            error: null
        });
        
        this.chartRefs = {
            leads: useRef("leadsChart"),
            opportunities: useRef("opportunitiesChart"),
            pipeline: useRef("pipelineChart")
        };
        
        onMounted(async () => {
            await this.loadChartLibrary();
            await this.loadCRMData();
            this.renderCharts();
        });
    }
    
    async loadChartLibrary() {
        await loadJS("/crm_executive_dashboard/static/lib/charts/Chart.min.js");
    }
    
    async loadCRMData() {
        try {
            const data = await this.orm.call("crm.lead", "get_dashboard_data", []);
            this.state.crmData = data;
            this.state.error = null;
        } catch (error) {
            console.error("CRM dashboard error:", error);
            this.state.error = error.message;
            this.notification.add(_t("Failed to load CRM data"), { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }
    
    renderCharts() {
        // Render multiple charts with OSUS branding
        this.renderLeadsChart();
        this.renderOpportunitiesChart();
        this.renderPipelineChart();
    }
    
    renderLeadsChart() {
        if (!this.chartRefs.leads.el) return;
        
        const ctx = this.chartRefs.leads.el.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.state.crmData.leadLabels || [],
                datasets: [{
                    data: this.state.crmData.leadData || [],
                    backgroundColor: [
                        '#800020',
                        '#FFD700',
                        '#A0522D'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: _t("Leads Distribution")
                    }
                }
            }
        });
    }
    
    renderOpportunitiesChart() {
        if (!this.chartRefs.opportunities.el) return;
        
        const ctx = this.chartRefs.opportunities.el.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.state.crmData.opportunityLabels || [],
                datasets: [{
                    label: _t("Opportunities"),
                    data: this.state.crmData.opportunityData || [],
                    backgroundColor: '#80002080',
                    borderColor: '#800020',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: _t("Opportunities Pipeline")
                    }
                }
            }
        });
    }
    
    renderPipelineChart() {
        if (!this.chartRefs.pipeline.el) return;
        
        const ctx = this.chartRefs.pipeline.el.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.state.crmData.pipelineLabels || [],
                datasets: [{
                    label: _t("Pipeline Value"),
                    data: this.state.crmData.pipelineData || [],
                    borderColor: '#FFD700',
                    backgroundColor: '#FFD70020',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: _t("Pipeline Trend")
                    }
                }
            }
        });
    }
}

registry.category("views").add("crm_dashboard", CRMDashboardView);
