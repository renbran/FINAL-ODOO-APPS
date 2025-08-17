#!/usr/bin/env python3
"""
Comprehensive JavaScript Cleanup and Rebuild Tool
Removes backup files, orphaned code, and rebuilds JavaScript from scratch
"""

import os
import shutil
import json
import re
from pathlib import Path
from datetime import datetime

class JavaScriptCleanupRebuild:
    def __init__(self):
        self.backup_files_removed = []
        self.orphaned_files_removed = []
        self.rebuilt_files = []
        self.validation_results = []
        
        # OSUS Properties branding
        self.osus_colors = {
            'primary': '#800020',
            'gold': '#FFD700',
            'light_gold': '#FFF8DC',
            'dark_gold': '#B8860B',
            'white': '#FFFFFF',
            'accent': '#A0522D'
        }
        
        # Priority modules to clean and rebuild
        self.priority_modules = [
            'account_payment_final',
            'order_status_override',
            'oe_sale_dashboard_17',
            'commission_ax',
            'enhanced_rest_api',
            'crm_executive_dashboard',
            'odoo_crm_dashboard'
        ]

    def remove_backup_files(self):
        """Remove all JavaScript backup files"""
        print("🗑️ REMOVING JAVASCRIPT BACKUP FILES...")
        print("-" * 50)
        
        backup_patterns = [
            '*.backup',
            '*.backup.*',
            '*.bak',
            '*.old',
            '*_backup.js',
            '*_old.js'
        ]
        
        for module in self.priority_modules:
            if not os.path.exists(module):
                continue
                
            static_path = os.path.join(module, 'static')
            if not os.path.exists(static_path):
                continue
            
            for root, dirs, files in os.walk(static_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check if file matches backup patterns
                    is_backup = any(
                        file.endswith(pattern.replace('*', '')) or
                        pattern.replace('*', '') in file
                        for pattern in backup_patterns
                    )
                    
                    if is_backup:
                        try:
                            os.remove(file_path)
                            self.backup_files_removed.append(file_path)
                            print(f"✅ Removed backup: {file_path}")
                        except Exception as e:
                            print(f"❌ Error removing {file_path}: {e}")

    def identify_orphaned_files(self):
        """Identify and remove orphaned JavaScript files"""
        print("\n🔍 IDENTIFYING ORPHANED FILES...")
        print("-" * 50)
        
        orphaned_files = []
        
        for module in self.priority_modules:
            if not os.path.exists(module):
                continue
            
            js_files = []
            static_path = os.path.join(module, 'static', 'src', 'js')
            
            if os.path.exists(static_path):
                for root, dirs, files in os.walk(static_path):
                    for file in files:
                        if file.endswith('.js'):
                            file_path = os.path.join(root, file)
                            js_files.append(file_path)
            
            # Check each JS file for orphaned patterns
            for js_file in js_files:
                if self.is_orphaned_file(js_file):
                    orphaned_files.append(js_file)
        
        # Remove orphaned files
        for orphaned_file in orphaned_files:
            try:
                os.remove(orphaned_file)
                self.orphaned_files_removed.append(orphaned_file)
                print(f"✅ Removed orphaned: {orphaned_file}")
            except Exception as e:
                print(f"❌ Error removing {orphaned_file}: {e}")

    def is_orphaned_file(self, file_path):
        """Check if a JavaScript file is orphaned"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for orphaned patterns
            orphaned_indicators = [
                len(content.strip()) < 50,  # Very small files
                'TODO: Remove this file' in content,
                'DEPRECATED' in content,
                content.count('//') > content.count('\n') / 2,  # Mostly comments
                not content.strip(),  # Empty files
            ]
            
            return any(orphaned_indicators)
            
        except Exception:
            return True  # If can't read, consider orphaned

    def rebuild_core_javascript_files(self):
        """Rebuild core JavaScript files with modern Odoo 17 syntax"""
        print("\n🔨 REBUILDING CORE JAVASCRIPT FILES...")
        print("-" * 50)
        
        # Define core JavaScript templates for each module
        js_templates = {
            'account_payment_final': self.create_payment_dashboard_js(),
            'order_status_override': self.create_order_status_js(), 
            'oe_sale_dashboard_17': self.create_sales_dashboard_js(),
            'commission_ax': self.create_commission_js(),
            'enhanced_rest_api': self.create_api_js(),
            'crm_executive_dashboard': self.create_crm_dashboard_js(),
            'odoo_crm_dashboard': self.create_crm_modern_js()
        }
        
        for module, js_content in js_templates.items():
            if os.path.exists(module):
                self.create_module_javascript(module, js_content)

    def create_payment_dashboard_js(self):
        """Create modern payment dashboard JavaScript"""
        return f'''/** @odoo-module **/

import {{ Component, useState, onMounted, onWillUnmount }} from "@odoo/owl";
import {{ registry }} from "@web/core/registry";
import {{ useService }} from "@web/core/utils/hooks";
import {{ _t }} from "@web/core/l10n/translation";

// OSUS Properties Brand Colors
const brandColors = {{
    primary: '{self.osus_colors["primary"]}',
    gold: '{self.osus_colors["gold"]}',
    lightGold: '{self.osus_colors["light_gold"]}',
    darkGold: '{self.osus_colors["dark_gold"]}',
    white: '{self.osus_colors["white"]}',
    accent: '{self.osus_colors["accent"]}'
}};

export class PaymentDashboardView extends Component {{
    static template = "account_payment_final.Dashboard";
    static props = ["*"];
    
    setup() {{
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
        
        this.state = useState({{
            isLoading: true,
            paymentData: {{}},
            error: null
        }});
        
        onMounted(async () => {{
            await this.loadPaymentData();
        }});
        
        onWillUnmount(() => {{
            this.cleanupResources();
        }});
    }}
    
    async loadPaymentData() {{
        try {{
            this.state.isLoading = true;
            const data = await this.orm.call("account.payment", "get_dashboard_data", []);
            this.state.paymentData = data;
            this.state.error = null;
        }} catch (error) {{
            console.error("Payment dashboard error:", error);
            this.state.error = error.message;
            this.notification.add(_t("Failed to load payment data"), {{ type: "danger" }});
        }} finally {{
            this.state.isLoading = false;
        }}
    }}
    
    async onCreatePayment() {{
        try {{
            const action = await this.orm.call("account.payment", "action_create_payment", []);
            this.actionService.doAction(action);
        }} catch (error) {{
            this.notification.add(_t("Error creating payment"), {{ type: "danger" }});
        }}
    }}
    
    cleanupResources() {{
        // Cleanup any resources, event listeners, etc.
        console.log("Payment dashboard cleanup");
    }}
}}

registry.category("views").add("payment_dashboard", PaymentDashboardView);
'''

    def create_order_status_js(self):
        """Create modern order status JavaScript"""
        return f'''/** @odoo-module **/

import {{ Component, useState, onMounted }} from "@odoo/owl";
import {{ registry }} from "@web/core/registry";
import {{ useService }} from "@web/core/utils/hooks";
import {{ _t }} from "@web/core/l10n/translation";

export class OrderStatusWidget extends Component {{
    static template = "order_status_override.StatusWidget";
    static props = ["*"];
    
    setup() {{
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({{
            orderStatus: null,
            isLoading: false
        }});
        
        onMounted(() => {{
            this.loadOrderStatus();
        }});
    }}
    
    async loadOrderStatus() {{
        try {{
            this.state.isLoading = true;
            const status = await this.orm.call("sale.order", "get_order_status", [this.props.orderId]);
            this.state.orderStatus = status;
        }} catch (error) {{
            console.error("Order status error:", error);
            this.notification.add(_t("Failed to load order status"), {{ type: "danger" }});
        }} finally {{
            this.state.isLoading = false;
        }}
    }}
    
    async onStatusChange(newStatus) {{
        try {{
            await this.orm.call("sale.order", "update_status", [this.props.orderId, newStatus]);
            await this.loadOrderStatus();
            this.notification.add(_t("Status updated successfully"), {{ type: "success" }});
        }} catch (error) {{
            this.notification.add(_t("Failed to update status"), {{ type: "danger" }});
        }}
    }}
}}

registry.category("fields").add("order_status_widget", OrderStatusWidget);
'''

    def create_sales_dashboard_js(self):
        """Create modern sales dashboard JavaScript"""
        return f'''/** @odoo-module **/

import {{ Component, useState, useRef, onMounted }} from "@odoo/owl";
import {{ registry }} from "@web/core/registry";
import {{ useService }} from "@web/core/utils/hooks";
import {{ _t }} from "@web/core/l10n/translation";
import {{ loadJS }} from "@web/core/assets";

export class SalesDashboardView extends Component {{
    static template = "oe_sale_dashboard_17.Dashboard";
    static props = ["*"];
    
    setup() {{
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({{
            isLoading: true,
            salesData: {{}},
            chartData: null
        }});
        
        this.chartRef = useRef("salesChart");
        this.chartInstance = null;
        
        onMounted(async () => {{
            await this.loadChartLibrary();
            await this.loadSalesData();
            this.renderChart();
        }});
    }}
    
    async loadChartLibrary() {{
        await loadJS("/oe_sale_dashboard_17/static/lib/charts/Chart.min.js");
    }}
    
    async loadSalesData() {{
        try {{
            const data = await this.orm.call("sale.order", "get_dashboard_data", []);
            this.state.salesData = data;
            this.prepareChartData(data);
        }} catch (error) {{
            console.error("Sales dashboard error:", error);
            this.notification.add(_t("Failed to load sales data"), {{ type: "danger" }});
        }} finally {{
            this.state.isLoading = false;
        }}
    }}
    
    prepareChartData(data) {{
        this.state.chartData = {{
            labels: data.labels || [],
            datasets: [{{
                label: _t("Sales"),
                data: data.values || [],
                backgroundColor: '{self.osus_colors["primary"]}20',
                borderColor: '{self.osus_colors["primary"]}',
                borderWidth: 2
            }}]
        }};
    }}
    
    renderChart() {{
        if (!this.chartRef.el || !this.state.chartData) return;
        
        const ctx = this.chartRef.el.getContext('2d');
        this.chartInstance = new Chart(ctx, {{
            type: 'bar',
            data: this.state.chartData,
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: _t("Sales Dashboard")
                    }}
                }}
            }}
        }});
    }}
}}

registry.category("views").add("sales_dashboard", SalesDashboardView);
'''

    def create_commission_js(self):
        """Create modern commission JavaScript"""
        return f'''/** @odoo-module **/

import {{ Component, useState, onMounted }} from "@odoo/owl";
import {{ registry }} from "@web/core/registry";
import {{ useService }} from "@web/core/utils/hooks";
import {{ _t }} from "@web/core/l10n/translation";

export class CommissionWidget extends Component {{
    static template = "commission_ax.CommissionWidget";
    static props = ["*"];
    
    setup() {{
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({{
            commissionData: null,
            isCalculating: false
        }});
        
        onMounted(() => {{
            this.loadCommissionData();
        }});
    }}
    
    async loadCommissionData() {{
        try {{
            const data = await this.orm.call("commission.ax", "get_commission_data", [this.props.recordId]);
            this.state.commissionData = data;
        }} catch (error) {{
            console.error("Commission error:", error);
            this.notification.add(_t("Failed to load commission data"), {{ type: "danger" }});
        }}
    }}
    
    async calculateCommission() {{
        try {{
            this.state.isCalculating = true;
            await this.orm.call("commission.ax", "calculate_commission", [this.props.recordId]);
            await this.loadCommissionData();
            this.notification.add(_t("Commission calculated successfully"), {{ type: "success" }});
        }} catch (error) {{
            this.notification.add(_t("Failed to calculate commission"), {{ type: "danger" }});
        }} finally {{
            this.state.isCalculating = false;
        }}
    }}
}}

registry.category("fields").add("commission_widget", CommissionWidget);
'''

    def create_api_js(self):
        """Create modern REST API JavaScript"""
        return f'''/** @odoo-module **/

import {{ Component, useState }} from "@odoo/owl";
import {{ registry }} from "@web/core/registry";
import {{ useService }} from "@web/core/utils/hooks";
import {{ _t }} from "@web/core/l10n/translation";

export class RestApiWidget extends Component {{
    static template = "enhanced_rest_api.ApiWidget";
    static props = ["*"];
    
    setup() {{
        this.http = useService("http");
        this.notification = useService("notification");
        
        this.state = useState({{
            apiStatus: null,
            isConnecting: false
        }});
    }}
    
    async testApiConnection() {{
        try {{
            this.state.isConnecting = true;
            const response = await this.http.get("/api/v1/status");
            this.state.apiStatus = response.data;
            this.notification.add(_t("API connection successful"), {{ type: "success" }});
        }} catch (error) {{
            console.error("API connection error:", error);
            this.notification.add(_t("API connection failed"), {{ type: "danger" }});
        }} finally {{
            this.state.isConnecting = false;
        }}
    }}
}}

registry.category("widgets").add("rest_api_widget", RestApiWidget);
'''

    def create_crm_dashboard_js(self):
        """Create modern CRM dashboard JavaScript"""
        return f'''/** @odoo-module **/

import {{ Component, useState, useRef, onMounted }} from "@odoo/owl";
import {{ registry }} from "@web/core/registry";
import {{ useService }} from "@web/core/utils/hooks";
import {{ _t }} from "@web/core/l10n/translation";
import {{ loadJS }} from "@web/core/assets";

export class CRMDashboardView extends Component {{
    static template = "crm_executive_dashboard.Dashboard";
    static props = ["*"];
    
    setup() {{
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({{
            isLoading: true,
            crmData: {{}},
            error: null
        }});
        
        this.chartRefs = {{
            leads: useRef("leadsChart"),
            opportunities: useRef("opportunitiesChart"),
            pipeline: useRef("pipelineChart")
        }};
        
        onMounted(async () => {{
            await this.loadChartLibrary();
            await this.loadCRMData();
            this.renderCharts();
        }});
    }}
    
    async loadChartLibrary() {{
        await loadJS("/crm_executive_dashboard/static/lib/charts/Chart.min.js");
    }}
    
    async loadCRMData() {{
        try {{
            const data = await this.orm.call("crm.lead", "get_dashboard_data", []);
            this.state.crmData = data;
            this.state.error = null;
        }} catch (error) {{
            console.error("CRM dashboard error:", error);
            this.state.error = error.message;
            this.notification.add(_t("Failed to load CRM data"), {{ type: "danger" }});
        }} finally {{
            this.state.isLoading = false;
        }}
    }}
    
    renderCharts() {{
        // Render multiple charts with OSUS branding
        this.renderLeadsChart();
        this.renderOpportunitiesChart();
        this.renderPipelineChart();
    }}
    
    renderLeadsChart() {{
        if (!this.chartRefs.leads.el) return;
        
        const ctx = this.chartRefs.leads.el.getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: this.state.crmData.leadLabels || [],
                datasets: [{{
                    data: this.state.crmData.leadData || [],
                    backgroundColor: [
                        '{self.osus_colors["primary"]}',
                        '{self.osus_colors["gold"]}',
                        '{self.osus_colors["accent"]}'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: _t("Leads Distribution")
                    }}
                }}
            }}
        }});
    }}
    
    renderOpportunitiesChart() {{
        if (!this.chartRefs.opportunities.el) return;
        
        const ctx = this.chartRefs.opportunities.el.getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: this.state.crmData.opportunityLabels || [],
                datasets: [{{
                    label: _t("Opportunities"),
                    data: this.state.crmData.opportunityData || [],
                    backgroundColor: '{self.osus_colors["primary"]}80',
                    borderColor: '{self.osus_colors["primary"]}',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: _t("Opportunities Pipeline")
                    }}
                }}
            }}
        }});
    }}
    
    renderPipelineChart() {{
        if (!this.chartRefs.pipeline.el) return;
        
        const ctx = this.chartRefs.pipeline.el.getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: this.state.crmData.pipelineLabels || [],
                datasets: [{{
                    label: _t("Pipeline Value"),
                    data: this.state.crmData.pipelineData || [],
                    borderColor: '{self.osus_colors["gold"]}',
                    backgroundColor: '{self.osus_colors["gold"]}20',
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: _t("Pipeline Trend")
                    }}
                }}
            }}
        }});
    }}
}}

registry.category("views").add("crm_dashboard", CRMDashboardView);
'''

    def create_crm_modern_js(self):
        """Create modern CRM dashboard JavaScript for odoo_crm_dashboard"""
        return f'''/** @odoo-module **/

import {{ Component, useState, useRef, onMounted, onWillUnmount }} from "@odoo/owl";
import {{ registry }} from "@web/core/registry";
import {{ useService }} from "@web/core/utils/hooks";
import {{ _t }} from "@web/core/l10n/translation";
import {{ loadJS }} from "@web/core/assets";

export class ModernCRMDashboard extends Component {{
    static template = "odoo_crm_dashboard.Dashboard";
    static props = ["*"];
    
    setup() {{
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
        
        this.state = useState({{
            isLoading: true,
            crmData: {{}},
            error: null
        }});
        
        this.chartRefs = {{
            overdue_chart: useRef("overdue_chart"),
            pipeline_chart: useRef("pipeline_chart"),
            lead_chart: useRef("lead_chart"),
            won_chart: useRef("won_chart"),
            yearly_chart: useRef("yearly_chart")
        }};
        
        this.chartInstances = {{}};
        
        onMounted(async () => {{
            try {{
                await this.loadChartLibraries();
                await this.loadDashboardData();
                await this.renderGraphs();
                this.state.isLoading = false;
            }} catch (error) {{
                console.error("CRM Dashboard initialization error:", error);
                this.state.error = error.message;
                this.state.isLoading = false;
            }}
        }});
        
        onWillUnmount(() => {{
            this.destroyCharts();
        }});
    }}
    
    async loadChartLibraries() {{
        await loadJS("/odoo_crm_dashboard/static/lib/charts/Chart.min.js");
    }}
    
    async loadDashboardData() {{
        try {{
            const data = await this.orm.call("crm.lead", "get_crm_dashboard_data", []);
            this.state.crmData = data;
        }} catch (error) {{
            console.error("Failed to load CRM data:", error);
            throw error;
        }}
    }}
    
    async renderGraphs() {{
        const chartConfigs = {{
            overdue_chart: {{
                type: 'doughnut',
                data: this.state.crmData.overdueData || {{}},
                title: _t("Overdue Opportunities")
            }},
            pipeline_chart: {{
                type: 'bar',
                data: this.state.crmData.pipelineData || {{}},
                title: _t("Sales Pipeline")
            }},
            lead_chart: {{
                type: 'pie',
                data: this.state.crmData.leadData || {{}},
                title: _t("Lead Sources")
            }},
            won_chart: {{
                type: 'line',
                data: this.state.crmData.wonData || {{}},
                title: _t("Won Opportunities")
            }},
            yearly_chart: {{
                type: 'bar',
                data: this.state.crmData.yearlyData || {{}},
                title: _t("Yearly Performance")
            }}
        }};
        
        for (const [chartId, config] of Object.entries(chartConfigs)) {{
            this.renderChart(chartId, config);
        }}
    }}
    
    renderChart(chartId, config) {{
        const chartRef = this.chartRefs[chartId];
        if (!chartRef?.el) return;
        
        const ctx = chartRef.el.getContext('2d');
        
        // Destroy existing chart if it exists
        if (this.chartInstances[chartId]) {{
            this.chartInstances[chartId].destroy();
        }}
        
        // Apply OSUS branding colors
        if (config.data.datasets) {{
            config.data.datasets = config.data.datasets.map(dataset => ({{
                ...dataset,
                backgroundColor: dataset.backgroundColor || [
                    '{self.osus_colors["primary"]}',
                    '{self.osus_colors["gold"]}',
                    '{self.osus_colors["accent"]}',
                    '{self.osus_colors["light_gold"]}'
                ],
                borderColor: dataset.borderColor || '{self.osus_colors["primary"]}'
            }}));
        }}
        
        this.chartInstances[chartId] = new Chart(ctx, {{
            type: config.type,
            data: config.data,
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: config.title,
                        color: '{self.osus_colors["primary"]}',
                        font: {{
                            size: 16,
                            weight: 'bold'
                        }}
                    }},
                    legend: {{
                        labels: {{
                            color: '{self.osus_colors["primary"]}'
                        }}
                    }}
                }},
                scales: config.type !== 'doughnut' && config.type !== 'pie' ? {{
                    x: {{
                        ticks: {{
                            color: '{self.osus_colors["primary"]}'
                        }}
                    }},
                    y: {{
                        ticks: {{
                            color: '{self.osus_colors["primary"]}'
                        }}
                    }}
                }} : {{}}
            }}
        }});
    }}
    
    destroyCharts() {{
        Object.values(this.chartInstances).forEach(chart => {{
            if (chart && typeof chart.destroy === 'function') {{
                chart.destroy();
            }}
        }});
        this.chartInstances = {{}};
    }}
    
    async onRefreshData() {{
        try {{
            this.state.isLoading = true;
            await this.loadDashboardData();
            await this.renderGraphs();
            this.notification.add(_t("Dashboard refreshed successfully"), {{ type: "success" }});
        }} catch (error) {{
            this.notification.add(_t("Failed to refresh dashboard"), {{ type: "danger" }});
        }} finally {{
            this.state.isLoading = false;
        }}
    }}
}}

registry.category("views").add("modern_crm_dashboard", ModernCRMDashboard);
'''

    def create_module_javascript(self, module, js_content):
        """Create JavaScript file for a module"""
        static_js_path = os.path.join(module, 'static', 'src', 'js')
        os.makedirs(static_js_path, exist_ok=True)
        
        # Determine main JS file name
        main_js_files = {
            'account_payment_final': 'payment_dashboard.js',
            'order_status_override': 'order_status_widget.js',
            'oe_sale_dashboard_17': 'sales_dashboard.js',
            'commission_ax': 'commission_widget.js',
            'enhanced_rest_api': 'api_widget.js',
            'crm_executive_dashboard': 'crm_dashboard.js',
            'odoo_crm_dashboard': 'crm_dashboard.js'
        }
        
        js_filename = main_js_files.get(module, 'main.js')
        js_file_path = os.path.join(static_js_path, js_filename)
        
        # Write the JavaScript content
        with open(js_file_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        self.rebuilt_files.append(js_file_path)
        print(f"✅ Rebuilt: {js_file_path}")

    def validate_rebuilt_files(self):
        """Validate all rebuilt JavaScript files"""
        print("\n✅ VALIDATING REBUILT FILES...")
        print("-" * 50)
        
        for js_file in self.rebuilt_files:
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Validation checks
                validations = {
                    'has_odoo_module_declaration': '/** @odoo-module **/' in content,
                    'has_modern_imports': 'import {' in content,
                    'has_component_class': 'extends Component' in content,
                    'has_registry_registration': 'registry.category(' in content,
                    'has_error_handling': 'try {' in content and 'catch' in content,
                    'has_osus_branding': self.osus_colors['primary'] in content,
                    'no_legacy_define': 'odoo.define(' not in content,
                    'no_jquery_dependency': '$(document)' not in content
                }
                
                passed_validations = sum(validations.values())
                total_validations = len(validations)
                
                self.validation_results.append({
                    'file': js_file,
                    'passed': passed_validations,
                    'total': total_validations,
                    'validations': validations
                })
                
                status = "✅" if passed_validations >= total_validations * 0.8 else "⚠️"
                print(f"{status} {js_file}: {passed_validations}/{total_validations} validations passed")
                
            except Exception as e:
                print(f"❌ Error validating {js_file}: {e}")

    def create_asset_bundle_updates(self):
        """Create asset bundle updates for each module"""
        print("\n📦 UPDATING ASSET BUNDLES...")
        print("-" * 50)
        
        for module in self.priority_modules:
            if not os.path.exists(module):
                continue
            
            views_path = os.path.join(module, 'views')
            os.makedirs(views_path, exist_ok=True)
            
            assets_xml_path = os.path.join(views_path, 'assets.xml')
            
            # Create modern assets.xml
            assets_content = f'''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Modern Odoo 17 Asset Bundle for {module} -->
    <template id="assets_backend" inherit_id="web.assets_backend">
        <!-- JavaScript Files -->
        <script type="text/javascript" src="/{module}/static/src/js/*.js"/>
        
        <!-- CSS Files -->
        <link rel="stylesheet" type="text/scss" src="/{module}/static/src/scss/*.scss"/>
        <link rel="stylesheet" type="text/css" src="/{module}/static/src/css/*.css"/>
    </template>
    
    <!-- Frontend Assets (if needed) -->
    <template id="assets_frontend" inherit_id="web.assets_frontend">
        <script type="text/javascript" src="/{module}/static/src/js/frontend.js"/>
        <link rel="stylesheet" type="text/css" src="/{module}/static/src/css/frontend.css"/>
    </template>
    
    <!-- QWeb Templates -->
    <template id="dashboard_template" name="{module}.Dashboard">
        <div class="o_{module.replace('_', '-')}_dashboard">
            <div class="o_dashboard_header">
                <h2>OSUS Properties Dashboard</h2>
                <div class="o_dashboard_controls">
                    <button class="btn btn-primary" t-on-click="onRefreshData">
                        <i class="fa fa-refresh"/> Refresh
                    </button>
                </div>
            </div>
            <div class="o_dashboard_content">
                <t t-if="state.isLoading">
                    <div class="text-center p-4">
                        <i class="fa fa-spinner fa-spin fa-2x"/>
                        <p>Loading...</p>
                    </div>
                </t>
                <t t-elif="state.error">
                    <div class="alert alert-danger">
                        <strong>Error:</strong> <t t-esc="state.error"/>
                    </div>
                </t>
                <t t-else="">
                    <div class="row">
                        <div class="col-md-6">
                            <canvas t-ref="chart1"/>
                        </div>
                        <div class="col-md-6">
                            <canvas t-ref="chart2"/>
                        </div>
                    </div>
                </t>
            </div>
        </div>
    </template>
</odoo>
'''
            
            with open(assets_xml_path, 'w', encoding='utf-8') as f:
                f.write(assets_content)
            
            print(f"✅ Updated assets: {assets_xml_path}")

    def create_cleanup_report(self):
        """Create comprehensive cleanup report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"js_cleanup_rebuild_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'cleanup_summary': {
                'backup_files_removed': len(self.backup_files_removed),
                'orphaned_files_removed': len(self.orphaned_files_removed),
                'files_rebuilt': len(self.rebuilt_files),
                'modules_processed': len(self.priority_modules)
            },
            'backup_files_removed': self.backup_files_removed,
            'orphaned_files_removed': self.orphaned_files_removed,
            'rebuilt_files': self.rebuilt_files,
            'validation_results': self.validation_results,
            'osus_branding': self.osus_colors,
            'next_steps': [
                "Test all rebuilt JavaScript files in browser",
                "Verify CloudPepper compatibility",
                "Run comprehensive error detection",
                "Deploy to production environment",
                "Monitor for JavaScript errors in console"
            ]
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return report_file, report

    def run_comprehensive_cleanup(self):
        """Run complete JavaScript cleanup and rebuild process"""
        print("🚀 COMPREHENSIVE JAVASCRIPT CLEANUP & REBUILD")
        print("=" * 60)
        print("OSUS Properties - Odoo 17 Module Modernization")
        print("=" * 60)
        
        try:
            # Step 1: Remove backup files
            self.remove_backup_files()
            
            # Step 2: Identify and remove orphaned files
            self.identify_orphaned_files()
            
            # Step 3: Rebuild core JavaScript files
            self.rebuild_core_javascript_files()
            
            # Step 4: Validate rebuilt files
            self.validate_rebuilt_files()
            
            # Step 5: Update asset bundles
            self.create_asset_bundle_updates()
            
            # Step 6: Create comprehensive report
            report_file, report = self.create_cleanup_report()
            
            # Summary
            print(f"\n🎉 CLEANUP & REBUILD COMPLETE!")
            print("=" * 60)
            print(f"📊 SUMMARY:")
            print(f"   • Backup files removed: {len(self.backup_files_removed)}")
            print(f"   • Orphaned files removed: {len(self.orphaned_files_removed)}")  
            print(f"   • JavaScript files rebuilt: {len(self.rebuilt_files)}")
            print(f"   • Modules processed: {len(self.priority_modules)}")
            print(f"📄 Report saved: {report_file}")
            
            if self.validation_results:
                print(f"\n✅ VALIDATION RESULTS:")
                for result in self.validation_results:
                    status = "✅" if result['passed'] >= result['total'] * 0.8 else "⚠️"
                    print(f"   {status} {os.path.basename(result['file'])}: {result['passed']}/{result['total']}")
            
            print(f"\n🎯 NEXT STEPS:")
            print("   1. Run CloudPepper deployment validation")
            print("   2. Test JavaScript functionality in browser")
            print("   3. Monitor browser console for errors")
            print("   4. Deploy to CloudPepper production")
            
            return report
            
        except Exception as e:
            print(f"\n❌ CLEANUP FAILED: {e}")
            raise

if __name__ == "__main__":
    cleaner = JavaScriptCleanupRebuild()
    report = cleaner.run_comprehensive_cleanup()
