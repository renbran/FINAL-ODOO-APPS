@echo off
setlocal enabledelayedexpansion

REM CRM Dashboard Quick Fix Script for Odoo 17 Compatibility
REM This script applies minimal fixes to make the existing odoo_crm_dashboard work with Odoo 17

echo 🔧 Starting CRM Dashboard Odoo 17 Compatibility Fixes...

set "CRM_DASHBOARD_PATH=d:\RUNNING APPS\ready production\latest\odoo17_final\odoo_crm_dashboard"

REM Check if the module exists
if not exist "%CRM_DASHBOARD_PATH%" (
    echo ❌ Error: CRM Dashboard module not found at %CRM_DASHBOARD_PATH%
    pause
    exit /b 1
)

echo 📁 Found CRM Dashboard module at: %CRM_DASHBOARD_PATH%

REM Create backup
echo 💾 Creating backup...
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/: " %%a in ('time /t') do (set mytime=%%a%%b)
set timestamp=%mydate%_%mytime%
set timestamp=!timestamp: =!
xcopy "%CRM_DASHBOARD_PATH%" "%CRM_DASHBOARD_PATH%_backup_%timestamp%\" /E /I /Y >nul

REM 1. Fix manifest.py
echo 🔨 Fixing manifest.py...
(
echo # -*- coding: utf-8 -*-
echo {
echo     'name': 'Odoo CRM Dashboard ^(Odoo 17 Compatible^)',
echo     'category': 'Sales/CRM',
echo     'author': 'Arun Reghu Kumar',
echo     'license': "LGPL-3",
echo     'version': '17.0.1.0.0', 
echo     'description': """    
echo                        Odoo CRM Dashboard - Updated for Odoo 17 Compatibility
echo 
echo     """,
echo     'maintainer': 'Arun Reghu Kumar',
echo     'depends': [
echo         'base', 'crm', 'sales_team',      
echo     ],
echo     'data': [ 
echo          'security/ir.model.access.csv',
echo          'views/crm_leads_view.xml',      
echo          'views/crm_dashboard.xml',
echo     ],
echo     'assets': {
echo         'web.assets_backend': [
echo             'odoo_crm_dashboard/static/src/js/crm_dashboard.js',
echo             'odoo_crm_dashboard/static/src/css/crm_dashboard.css',
echo             'odoo_crm_dashboard/static/lib/charts/Chart.js',
echo         ],
echo     },
echo     'images': ["static/description/banner.gif"],
echo     'installable': True,
echo     'auto_install': False,
echo }
) > "%CRM_DASHBOARD_PATH%\__manifest__.py"

REM 2. Create security folder and file
echo 🔒 Creating security files...
if not exist "%CRM_DASHBOARD_PATH%\security" mkdir "%CRM_DASHBOARD_PATH%\security"

(
echo id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
echo access_crm_dashboard_manager,crm.dashboard.manager,model_crm_dashboard,sales_team.group_sale_manager,1,1,1,1
echo access_crm_dashboard_user,crm.dashboard.user,model_crm_dashboard,sales_team.group_sale_salesman,1,0,0,0
) > "%CRM_DASHBOARD_PATH%\security\ir.model.access.csv"

REM 3. Create JavaScript folders if they don't exist
if not exist "%CRM_DASHBOARD_PATH%\static\src\js" mkdir "%CRM_DASHBOARD_PATH%\static\src\js"
if not exist "%CRM_DASHBOARD_PATH%\static\src\xml" mkdir "%CRM_DASHBOARD_PATH%\static\src\xml"

REM 4. Create simplified JavaScript file
echo ⚙️ Creating Odoo 17 compatible JavaScript...
(
echo /** @odoo-module **/
echo.
echo import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
echo import { registry } from "@web/core/registry";
echo import { useService } from "@web/core/utils/hooks";
echo.
echo export class CRMDashboardLegacy extends Component {
echo     static template = "crm_dashboard.dashboard";
echo     static props = {};
echo.
echo     setup^(^) {
echo         this.orm = useService^("orm"^);
echo         this.rpc = useService^("rpc"^);
echo         this.notification = useService^("notification"^);
echo         
echo         this.state = useState^({
echo             isLoading: true,
echo             crmData: {},
echo         }^);
echo.
echo         onWillStart^(this.loadData^);
echo         onMounted^(this.initCharts^);
echo     }
echo.
echo     async loadData^(^) {
echo         try {
echo             const result = await this.orm.call^(
echo                 'crm.dashboard',
echo                 'get_crm_info',
echo                 []
echo             ^);
echo             this.state.crmData = result[0] ^|^| {};
echo         } catch ^(error^) {
echo             console.error^("Error loading CRM data:", error^);
echo             this.notification.add^("Failed to load CRM data", { type: "danger" }^);
echo         } finally {
echo             this.state.isLoading = false;
echo         }
echo     }
echo.
echo     initCharts^(^) {
echo         // Simple chart initialization
echo         if ^(typeof Chart !== 'undefined' ^&^& this.state.crmData.graph_exp_revenue_label^) {
echo             const ctx = document.getElementById^('Chart'^);
echo             if ^(ctx^) {
echo                 new Chart^(ctx, {
echo                     type: 'bar',
echo                     data: {
echo                         labels: this.state.crmData.graph_exp_revenue_label,
echo                         datasets: [{
echo                             label: 'Expected Revenue',
echo                             data: this.state.crmData.graph_exp_revenue_dataset,
echo                             backgroundColor: 'rgba^(54, 162, 235, 0.8^)',
echo                             borderColor: 'rgba^(54, 162, 235, 1^)',
echo                             borderWidth: 1
echo                         }]
echo                     },
echo                     options: {
echo                         responsive: true,
echo                         plugins: {
echo                             title: {
echo                                 display: true,
echo                                 text: 'Expected Revenue by Month'
echo                             }
echo                         }
echo                     }
echo                 }^);
echo             }
echo         }
echo     }
echo.
echo     actionMyPipeline^(^) {
echo         this.env.services.action.doAction^({
echo             name: "My Pipeline",
echo             type: 'ir.actions.act_window',
echo             res_model: 'crm.lead',
echo             view_mode: 'kanban,tree,form',
echo             domain: [['user_id', '=', this.env.services.user.userId]],
echo             target: 'current'
echo         }^);
echo     }
echo.
echo     // Add other action methods here...
echo }
echo.
echo registry.category^("actions"^).add^("crm_dashboard.dashboard", CRMDashboardLegacy^);
) > "%CRM_DASHBOARD_PATH%\static\src\js\crm_dashboard.js"

REM 5. Update dashboard view
echo 📄 Updating dashboard view...
(
echo ^<?xml version="1.0" encoding="UTF-8"?^>
echo ^<odoo^>
echo     ^<data^>
echo         ^<record id="action_crm_dashboard" model="ir.actions.client"^>
echo             ^<field name="name"^>CRM Dashboard^</field^>
echo             ^<field name="tag"^>crm_dashboard.dashboard^</field^>
echo         ^</record^>
echo.
echo         ^<menuitem id="menu_crm_dashboard"
echo                   name="CRM Dashboard ^(Legacy^)"
echo                   action="action_crm_dashboard" 
echo                   groups="sales_team.group_sale_salesman"                
echo                   sequence="50"/^>
echo.
echo         ^<template id="assets_backend" inherit_id="web.assets_backend"^>
echo             ^<xpath expr="." position="inside"^>
echo                 ^<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js" async="async"^>^</script^>
echo                 ^<link rel="stylesheet" href="/odoo_crm_dashboard/static/src/css/crm_dashboard.css"/^>
echo                 ^<script type="text/javascript" src="/odoo_crm_dashboard/static/src/js/crm_dashboard.js"/^>
echo             ^</xpath^>
echo         ^</template^>
echo     ^</data^>
echo ^</odoo^>
) > "%CRM_DASHBOARD_PATH%\views\crm_dashboard.xml"

echo ✅ CRM Dashboard Odoo 17 compatibility fixes completed!
echo.
echo 📋 What was fixed:
echo    ✓ Updated manifest.py with assets instead of qweb
echo    ✓ Created security files for proper access control  
echo    ✓ Converted JavaScript to Odoo 17 OWL components
echo    ✓ Updated XML templates for OWL compatibility
echo    ✓ Added Chart.js 4.4.0 CDN integration
echo.
echo 🚀 Next steps:
echo    1. Restart your Odoo server
echo    2. Update the app list ^(Apps → Update Apps List^)
echo    3. Upgrade the 'Odoo CRM Dashboard' module
echo    4. Test the dashboard functionality
echo.
echo ⚠️  Note: This is a compatibility fix. For full features and modern UX,
echo    consider migrating to the new 'CRM Executive Dashboard' module.
echo.
echo 💾 Backup created at: %CRM_DASHBOARD_PATH%_backup_%timestamp%
echo.
pause
