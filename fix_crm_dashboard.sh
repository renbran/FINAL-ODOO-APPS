#!/bin/bash

# CRM Dashboard Quick Fix Script for Odoo 17 Compatibility
# This script applies minimal fixes to make the existing odoo_crm_dashboard work with Odoo 17

echo "🔧 Starting CRM Dashboard Odoo 17 Compatibility Fixes..."

CRM_DASHBOARD_PATH="d:/RUNNING APPS/ready production/latest/odoo17_final/odoo_crm_dashboard"

# Check if the module exists
if [ ! -d "$CRM_DASHBOARD_PATH" ]; then
    echo "❌ Error: CRM Dashboard module not found at $CRM_DASHBOARD_PATH"
    exit 1
fi

echo "📁 Found CRM Dashboard module at: $CRM_DASHBOARD_PATH"

# Create backup
echo "💾 Creating backup..."
cp -r "$CRM_DASHBOARD_PATH" "${CRM_DASHBOARD_PATH}_backup_$(date +%Y%m%d_%H%M%S)"

# 1. Fix manifest.py - Remove qweb and add assets
echo "🔨 Fixing manifest.py..."
cat > "$CRM_DASHBOARD_PATH/__manifest__.py" << 'EOF'
# -*- coding: utf-8 -*-
{
    'name': 'Odoo CRM Dashboard (Odoo 17 Compatible)',
    'category': 'Sales/CRM',
    'author': 'Arun Reghu Kumar',
    'license': "LGPL-3",
    'version': '17.0.1.0.0', 
    'description': """    
                       Odoo CRM Dashboard - Updated for Odoo 17 Compatibility

    """,
    'maintainer': 'Arun Reghu Kumar',
    'depends': [
        'base', 'crm', 'sales_team',      
    ],
    'data': [ 
         'security/ir.model.access.csv',
         'views/crm_leads_view.xml',      
         'views/crm_dashboard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_crm_dashboard/static/src/js/crm_dashboard.js',
            'odoo_crm_dashboard/static/src/css/crm_dashboard.css',
            'odoo_crm_dashboard/static/lib/charts/Chart.js',
        ],
    },
    'images': ["static/description/banner.gif"],
    'installable': True,
    'auto_install': False,
}
EOF

# 2. Create security folder and file
echo "🔒 Creating security files..."
mkdir -p "$CRM_DASHBOARD_PATH/security"

cat > "$CRM_DASHBOARD_PATH/security/ir.model.access.csv" << 'EOF'
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_crm_dashboard_manager,crm.dashboard.manager,model_crm_dashboard,sales_team.group_sale_manager,1,1,1,1
access_crm_dashboard_user,crm.dashboard.user,model_crm_dashboard,sales_team.group_sale_salesman,1,0,0,0
EOF

# 3. Create a simplified Odoo 17 compatible JavaScript file
echo "⚙️ Creating Odoo 17 compatible JavaScript..."
cat > "$CRM_DASHBOARD_PATH/static/src/js/crm_dashboard.js" << 'EOF'
/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class CRMDashboardLegacy extends Component {
    static template = "crm_dashboard.dashboard";
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        
        this.state = useState({
            isLoading: true,
            crmData: {},
        });

        onWillStart(this.loadData);
        onMounted(this.initCharts);
    }

    async loadData() {
        try {
            const result = await this.orm.call(
                'crm.dashboard',
                'get_crm_info',
                []
            );
            this.state.crmData = result[0] || {};
        } catch (error) {
            console.error("Error loading CRM data:", error);
            this.notification.add("Failed to load CRM data", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    initCharts() {
        // Simple chart initialization - placeholder for Chart.js
        if (typeof Chart !== 'undefined' && this.state.crmData.graph_exp_revenue_label) {
            const ctx = document.getElementById('Chart');
            if (ctx) {
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: this.state.crmData.graph_exp_revenue_label,
                        datasets: [{
                            label: 'Expected Revenue',
                            data: this.state.crmData.graph_exp_revenue_dataset,
                            backgroundColor: 'rgba(54, 162, 235, 0.8)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Expected Revenue by Month'
                            }
                        }
                    }
                });
            }
        }
    }

    // Action methods for button clicks
    actionMyPipeline() {
        this.env.services.action.doAction({
            name: "My Pipeline",
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'kanban,tree,form',
            domain: [['user_id', '=', this.env.services.user.userId]],
            target: 'current'
        });
    }

    actionOverdueOpportunities() {
        this.env.services.action.doAction({
            name: "Overdue Opportunities",
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'tree,form',
            domain: [
                ['type', '=', 'opportunity'],
                ['date_deadline', '<', new Date().toISOString().split('T')[0]],
                ['active', '=', true]
            ],
            target: 'current'
        });
    }

    actionOpenOpportunities() {
        this.env.services.action.doAction({
            name: "Open Opportunities",
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'kanban,tree,form',
            domain: [
                ['type', '=', 'opportunity'],
                ['probability', '<', 100]
            ],
            target: 'current'
        });
    }

    actionWonCount() {
        this.env.services.action.doAction({
            name: "Won Opportunities",
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'kanban,tree,form',
            domain: [
                ['probability', '=', 100],
                ['active', '=', true]
            ],
            target: 'current'
        });
    }

    actionLossCount() {
        this.env.services.action.doAction({
            name: "Lost Opportunities",
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            view_mode: 'tree,form',
            domain: [
                ['probability', '=', 0],
                ['active', '=', false]
            ],
            target: 'current'
        });
    }
}

// Register the component
registry.category("actions").add("crm_dashboard.dashboard", CRMDashboardLegacy);
EOF

# 4. Create updated XML template
echo "📄 Creating updated XML template..."
cat > "$CRM_DASHBOARD_PATH/static/src/xml/crm_dashboard.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<templates xml:space="preserve">
    <t t-name="crm_dashboard.dashboard" owl="1">
        <div class="crm_dashboard_container" style="padding: 20px;">
            <!-- Loading indicator -->
            <div t-if="state.isLoading" class="text-center">
                <i class="fa fa-spinner fa-spin fa-2x"></i>
                <p>Loading CRM Dashboard...</p>
            </div>
            
            <!-- Dashboard content -->
            <div t-if="!state.isLoading" class="row">
                <!-- Chart section -->
                <div class="col-md-5">
                    <div class="panel panel-default">
                        <div class="panel-heading">
                            <h3 class="panel-title">Total Expected Revenue</h3>
                        </div>
                        <div class="panel-body">
                            <canvas id="Chart" style="width:100%;height:400px;"/>
                        </div>
                    </div>
                </div>
                
                <!-- KPI Cards -->
                <div class="col-md-7">
                    <div class="row">
                        <!-- My Pipeline -->
                        <div class="col-md-4">
                            <div class="card text-center" style="margin: 10px; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px;">
                                <div class="card-body">
                                    <i class="fas fa-grip-lines fa-2x mb-2"></i>
                                    <h4>My Pipeline</h4>
                                    <h2 t-esc="state.crmData.my_pipe_line || 0"></h2>
                                    <button class="btn btn-light btn-sm mt-2" t-on-click="actionMyPipeline">View Details</button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Overdue Opportunities -->
                        <div class="col-md-4">
                            <div class="card text-center" style="margin: 10px; padding: 20px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border-radius: 10px;">
                                <div class="card-body">
                                    <i class="fas fa-user fa-2x mb-2"></i>
                                    <h4>Overdue Opportunities</h4>
                                    <h2 t-esc="state.crmData.tot_overdue_opportunities || 0"></h2>
                                    <button class="btn btn-light btn-sm mt-2" t-on-click="actionOverdueOpportunities">View Details</button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Open Opportunities -->
                        <div class="col-md-4">
                            <div class="card text-center" style="margin: 10px; padding: 20px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border-radius: 10px;">
                                <div class="card-body">
                                    <i class="fas fa-grin-stars fa-2x mb-2"></i>
                                    <h4>Open Opportunities</h4>
                                    <h2 t-esc="state.crmData.tot_open_opportunities || 0"></h2>
                                    <button class="btn btn-light btn-sm mt-2" t-on-click="actionOpenOpportunities">View Details</button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Won Count -->
                        <div class="col-md-4">
                            <div class="card text-center" style="margin: 10px; padding: 20px; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; border-radius: 10px;">
                                <div class="card-body">
                                    <i class="fas fa-trophy fa-2x mb-2"></i>
                                    <h4>Won Opportunities</h4>
                                    <h2 t-esc="state.crmData.tot_won || 0"></h2>
                                    <button class="btn btn-light btn-sm mt-2" t-on-click="actionWonCount">View Details</button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Lost Count -->
                        <div class="col-md-4">
                            <div class="card text-center" style="margin: 10px; padding: 20px; background: linear-gradient(135deg, #ff7b7b 0%, #ff6b6b 100%); color: white; border-radius: 10px;">
                                <div class="card-body">
                                    <i class="fas fa-grin-tears fa-2x mb-2"></i>
                                    <h4>Lost Opportunities</h4>
                                    <h2 t-esc="state.crmData.tot_lost || 0"></h2>
                                    <button class="btn btn-light btn-sm mt-2" t-on-click="actionLossCount">View Details</button>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Expected Revenue -->
                        <div class="col-md-4">
                            <div class="card text-center" style="margin: 10px; padding: 20px; background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%); color: #2d3436; border-radius: 10px;">
                                <div class="card-body">
                                    <i class="fas fa-calculator fa-2x mb-2"></i>
                                    <h4>Expected Revenue</h4>
                                    <h2 t-esc="state.crmData.expected_revenue || 0"></h2>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </t>
</templates>
EOF

# 5. Update the view XML to include Chart.js CDN
echo "🌐 Updating dashboard view with Chart.js..."
cat > "$CRM_DASHBOARD_PATH/views/crm_dashboard.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data>
        <!-- Default View for CRM Dashboard -->
        <record model="ir.ui.view" id="crm_dashboard_view">
            <field name="name">CRM Dashboard</field>
            <field name="model">crm.dashboard</field>
            <field name="arch" type="xml">
                <kanban>
                    <!-- Empty kanban view -->
                </kanban>
            </field>
        </record>

        <!-- Action For Menu CRM Dashboard -->
        <record id="action_crm_dashboard" model="ir.actions.client">
            <field name="name">CRM Dashboard</field>
            <field name="tag">crm_dashboard.dashboard</field>
        </record>

        <!-- Menu CRM Dashboard -->
        <menuitem id="menu_crm_dashboard"
                  name="CRM Dashboard (Legacy)"
                  action="action_crm_dashboard" 
                  groups="sales_team.group_sale_salesman"                
                  sequence="50"/>

        <!-- Include Chart.js and Assets -->
        <template id="assets_backend" inherit_id="web.assets_backend">
            <xpath expr="." position="inside">
                <!-- Chart.js Library -->
                <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js" async="async"></script>
                
                <!-- Dashboard CSS -->
                <link rel="stylesheet" href="/odoo_crm_dashboard/static/src/css/crm_dashboard.css"/>
                
                <!-- Dashboard JavaScript -->
                <script type="text/javascript" src="/odoo_crm_dashboard/static/src/js/crm_dashboard.js"/>
            </xpath>
        </template>

    </data>
</odoo>
EOF

echo "✅ CRM Dashboard Odoo 17 compatibility fixes completed!"
echo ""
echo "📋 What was fixed:"
echo "   ✓ Updated manifest.py with assets instead of qweb"
echo "   ✓ Created security files for proper access control"
echo "   ✓ Converted JavaScript to Odoo 17 OWL components"
echo "   ✓ Updated XML templates for OWL compatibility"
echo "   ✓ Added Chart.js 4.4.0 CDN integration"
echo "   ✓ Improved responsive design and modern styling"
echo ""
echo "🚀 Next steps:"
echo "   1. Restart your Odoo server"
echo "   2. Update the app list (Apps → Update Apps List)"
echo "   3. Upgrade the 'Odoo CRM Dashboard' module"
echo "   4. Test the dashboard functionality"
echo ""
echo "⚠️  Note: This is a compatibility fix. For full features and modern UX,"
echo "   consider migrating to the new 'CRM Executive Dashboard' module."
echo ""
echo "💾 Backup created at: ${CRM_DASHBOARD_PATH}_backup_$(date +%Y%m%d_%H%M%S)"
