# 🧠 Copilot Instructions for FINAL-ODOO-APPS (Odoo 17)

## Project Overview & Architecture

**FINAL-ODOO-APPS** is a production-ready collection of 50+ custom Odoo 17 modules deployed on CloudPepper hosting at `https://stagingtry.cloudpepper.site/` (login: `salescompliance@osusproperties.com`). This is a **non-Docker deployment** - modules run directly on CloudPepper's Odoo installation via SSH deployment.

### Module Categories & Examples
- **Payment Workflows**: `account_payment_approval/`, `account_payment_final/` - Multi-stage approval with digital signatures, QR verification
- **Property Management**: `rental_management/` (v3.4.0) - Complete real estate sales/rental with flexible payment plans, SPA reports, bank integration
- **Dashboards**: `oe_sale_dashboard_17/`, `crm_executive_dashboard/`, `odoo_dynamic_dashboard/` - Chart.js + OWL components
- **REST APIs**: `enhanced_rest_api/` (JWT auth, server-wide), `rest_api_odoo/` (base API)
- **Commission Systems**: `commission_ax/`, `order_net_commission/` - Automated calculations with sales/payment integration
- **HR Platform**: `scholarix_recruitment/`, `scholarix_assessment/` - Complete recruitment workflow
- **Theming**: `muk_web_theme/` (OSUS branding), `sgc_tech_ai_theme/` (SGC Tech AI branding)
- **CRM/Sales**: `llm_lead_scoring/`, `order_status_override/`, `contact_kyc/`, `all_in_one_sales_kit/`

### Critical Architecture Concepts

**CloudPepper-First Design**: All modules include compatibility layers for production hosting:
- **Global Protection**: `report_font_enhancement/static/src/js/cloudpepper_global_protection.js` wraps MutationObserver and setAttribute to prevent infinite recursion
- **Module Compatibility**: `commission_ax/models/cloudpepper_compatibility.py` adds missing fields (`task_count`, `x_lead_id`) for cross-module references
- **Emergency Fixes**: `create_emergency_cloudpepper_fix.py` generates production hotfixes without full redeployment

**Dual Branding System**:
- **OSUS Properties** (`#800020` maroon, `#FFD700` gold): Business/property modules (`account_payment_*`, `muk_web_theme/`, reports)
- **SGC Tech AI** (`#0c1e34` deep navy, `#00FFF0` electric cyan, `#00FF88` neon green): Innovation modules (`scholarix_*`, `sgc_tech_ai_theme/`)

**Deployment Note**: Despite some README mentions of docker-compose, CloudPepper production uses direct Odoo installation. Use Odoo CLI (`odoo -u module_name`) not docker commands.

---

## Developer Workflows

### Pre-Deployment Validation (ALWAYS RUN FIRST) 🚨
```powershell
# In module directory, run validation before ANY changes
python validate_module.py              # Module-specific checks (if exists)
python validate_production_ready.py    # Production readiness audit (if exists)
python validate_modern_syntax.py       # Odoo 17 compliance (if exists)

# Note: Not all modules have all validators - use what's available
# Check module directory for specific validation scripts
```

**What These Scripts Check**:
- Python syntax, proper `@api.depends` decorators
- XML parsing, field existence in models, view-action consistency
- Security groups defined in `ir.model.access.csv`
- Asset paths exist, no broken references
- Modern Odoo 17 syntax (see "Modern Syntax Migration" below)

### Emergency Fix Workflow (Production Issues)
```powershell
# For critical CloudPepper issues (infinite loops, RPC errors)
python create_emergency_cloudpepper_fix.py

# Emergency fix already deployed globally:
# report_font_enhancement/static/src/js/cloudpepper_global_protection.js

# For rental_management dependency error (Nov 30, 2025):
.\deploy_rental_emergency_fix.ps1  # Installs crm_ai_field_compatibility + upgrades module
# See: EMERGENCY_FIX_rental_management_dependency.md
```

### Testing & Development Cycle
1. **Validate First**: Run `validate_*.py` in module directory
2. **Make Changes**: Edit Python/JS/XML files
3. **Clear Cache**: Delete `__pycache__` directories after Python changes
4. **Test Locally**: Run unit tests (`python -m pytest tests/` or Odoo test mode)
5. **Validate Again**: Re-run validation scripts
6. **Deploy**: SSH to CloudPepper, `odoo -u module_name --stop-after-init`

**Testing Pattern** (see `account_payment_final/tests/`):
```python
from odoo.tests import TransactionCase, tagged

@tagged('account_payment_final', 'post_install', '-at_install')
class TestPaymentWorkflow(TransactionCase):
    def setUp(self):
        super().setUp()
        # Setup test data
    
    def test_approval_workflow(self):
        # Test multi-stage approval
```

---

## Critical Code Patterns

### Modern Odoo 17 XML Syntax (MANDATORY)

**❌ DEPRECATED - DO NOT USE**:
```xml
<!-- OLD: attrs syntax -->
<field name="custom_status" attrs="{'readonly': [('state', 'in', ['sale', 'done'])]}"/>
<button name="action_approve" states="draft"/>
```

**✅ CORRECT - Modern Syntax**:
```xml
<!-- NEW: Python-like expressions -->
<field name="custom_status" readonly="state in ['sale', 'done', 'cancel']"/>
<button name="action_approve" invisible="state != 'draft' or not approver_id"/>
```

**Migration Guide**: See `order_status_override/MODERN_SYNTAX_UPGRADE_SUMMARY.md` for complete examples.

### Unified Workflow State Pattern
```python
# Standard 4-6 stage approval workflow (account_payment_final/models/account_payment.py)
state = fields.Selection([
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('under_review', 'Under Review'),
    ('approved', 'Approved'),
    ('authorized', 'Authorized'),
    ('posted', 'Posted'),
], default='draft', tracking=True)

# State transition buttons with proper security
def action_submit_for_review(self):
    self.ensure_one()
    if not self.env.user.has_group('module.group_user'):
        raise AccessError(_("You don't have permission to submit payments."))
    self.write({'state': 'submitted'})
```

### Digital Signature & QR Verification
**Pattern from** `account_payment_approval/`:
```python
# Binary signature fields with attachment storage
creator_signature = fields.Binary("Creator Signature", attachment=True)
reviewer_signature = fields.Binary("Reviewer Signature", attachment=True)

# QR code generation with public verification
def generate_qr_code(self):
    token = secrets.token_urlsafe(32)
    self.verification_token = token
    verify_url = f"{self.get_base_url()}/payment/verify/{token}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(verify_url)
    qr.make(fit=True)
    # ... generate image and store in Binary field
```

**Controller for Public Verification**:
```python
@http.route('/payment/verify/<string:token>', auth='public', website=True)
def verify_payment(self, token, **kwargs):
    payment = request.env['account.payment'].sudo().search([
        ('verification_token', '=', token)
    ], limit=1)
    return request.render('module.payment_verification_template', {
        'payment': payment,
        'is_valid': bool(payment)
    })
```

### Computed Fields Implementation
```python
# Always define field + compute method + @api.depends
is_approve_person = fields.Boolean(
    compute='_compute_is_approve_person',
    help="Current user can approve this record"
)

@api.depends('user_id', 'state', 'approver_id')
def _compute_is_approve_person(self):
    for record in self:
        record.is_approve_person = (
            record.state == 'under_review' and
            record.approver_id == self.env.user
        )
```

### OWL Component Pattern (Odoo 17 Modern JS)
```javascript
/** @odoo-module **/
import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class PaymentDashboard extends Component {
    static template = "account_payment_final.PaymentDashboard";
    static props = ["*"];
    
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({ 
            payments: [],
            isLoading: false 
        });
        this.chartRef = useRef("chartContainer");
        
        onMounted(async () => {
            await this.loadData();
        });
        
        onWillUnmount(() => {
            // Cleanup chart instance if exists
            if (this.chart) {
                this.chart.destroy();
            }
        });
    }
    
    async loadData() {
        this.state.isLoading = true;
        try {
            const result = await this.orm.call(
                "account.payment",
                "get_dashboard_data",
                []
            );
            this.state.payments = result.payments;
            this.renderChart(result.chart_data);
        } catch (error) {
            this.notification.add(error.message, { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }
}
```

### CloudPepper Compatibility Pattern
**Asset Loading Order** (in `__manifest__.py`):
```python
'assets': {
    'web.assets_backend': [
        # CRITICAL: Emergency fixes MUST load first with 'prepend'
        ('prepend', 'module_name/static/src/js/cloudpepper_compatibility_patch.js'),
        ('prepend', 'report_font_enhancement/static/src/js/cloudpepper_global_protection.js'),
        
        # Then load regular components
        'module_name/static/src/js/main_component.js',
        'module_name/static/src/scss/styles.scss',
        'module_name/static/src/xml/templates.xml',
    ],
}
```

**Error Handling in OWL Components**:
```javascript
setup() {
    try {
        super.setup();
        // Component initialization
    } catch (error) {
        console.error('[ModuleName] Setup error:', error);
        // Fallback or graceful degradation
    }
}
```

---

## Module Structure & Standards

### Standard Directory Layout
```
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── main_model.py
│   └── inherited_model.py
├── views/
│   ├── main_model_views.xml
│   └── menus.xml
├── security/
│   ├── ir.model.access.csv
│   └── security_groups.xml
├── data/
│   ├── sequences.xml
│   └── email_templates.xml
├── static/
│   └── src/
│       ├── js/
│       ├── scss/
│       └── xml/
├── reports/
│   ├── report_templates.xml
│   └── report_views.xml
├── tests/
│   └── test_main_model.py
└── README.md
```

### Security Group Hierarchy (4-6 Tiers)
**Pattern from** `account_payment_approval/security/`:
```xml
<!-- security/security_groups.xml -->
<record id="group_payment_user" model="res.groups">
    <field name="name">Payment User</field>
    <field name="category_id" ref="base.module_category_accounting"/>
</record>

<record id="group_payment_reviewer" model="res.groups">
    <field name="name">Payment Reviewer</field>
    <field name="implied_ids" eval="[(4, ref('group_payment_user'))]"/>
</record>

<record id="group_payment_approver" model="res.groups">
    <field name="name">Payment Approver</field>
    <field name="implied_ids" eval="[(4, ref('group_payment_reviewer'))]"/>
</record>

<record id="group_payment_authorizer" model="res.groups">
    <field name="name">Payment Authorizer</field>
    <field name="implied_ids" eval="[(4, ref('group_payment_approver'))]"/>
</record>

<record id="group_payment_manager" model="res.groups">
    <field name="name">Payment Manager</field>
    <field name="implied_ids" eval="[(4, ref('group_payment_authorizer'))]"/>
</record>
```

```csv
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_payment_user,payment.user,model_account_payment,group_payment_user,1,0,0,0
access_payment_reviewer,payment.reviewer,model_account_payment,group_payment_reviewer,1,1,0,0
access_payment_approver,payment.approver,model_account_payment,group_payment_approver,1,1,1,0
access_payment_manager,payment.manager,model_account_payment,group_payment_manager,1,1,1,1
```

### Naming Conventions
- **Modules**: `snake_case`, version `17.0.x.y.z`, category from `base.module_category_*`
- **Models**: `singular.dot.notation` (e.g., `sale.order`, `crm.lead`)
- **XML IDs**: `model_name_view_type` (e.g., `sale_order_view_form`, `crm_lead_menu`)
- **Security Groups**: `module_group_role` (e.g., `payment_group_approver`)
- **Python Files**: `lowercase_with_underscores.py`

---

## Integration Patterns

### REST API Integration (`enhanced_rest_api/`)
**Server-Wide Module** with JWT authentication:
```python
# __manifest__.py
'server_wide': True,
'depends': ['base', 'web', 'rest_api_odoo', 'crm', 'sale', 'account'],
'external_dependencies': {'python': ['jwt', 'requests']},

# controllers/crm_controller.py
from odoo import http
from odoo.http import request
import jwt

class CRMAPIController(http.Controller):
    @http.route('/api/v1/crm/leads', auth='none', type='json', csrf=False)
    def get_leads(self, **kwargs):
        # Validate JWT token
        token = request.httprequest.headers.get('Authorization')
        if not token or not self._validate_jwt(token):
            return {'error': 'Unauthorized', 'status': 401}
        
        # Fetch data
        leads = request.env['crm.lead'].sudo().search([])
        return {
            'status': 200,
            'data': [lead.read(['name', 'email_from', 'stage_id']) for lead in leads]
        }
```

### Report Generation (`account_payment_approval/reports/`)
**QWeb PDF Reports** with OSUS branding:
```xml
<!-- reports/payment_voucher_report.xml -->
<odoo>
    <record id="action_report_payment_voucher" model="ir.actions.report">
        <field name="name">Payment Voucher</field>
        <field name="model">account.payment</field>
        <field name="report_type">qweb-pdf</field>
        <field name="report_name">account_payment_approval.report_payment_voucher</field>
        <field name="print_report_name">'Payment Voucher - %s' % (object.name)</field>
    </record>
</odoo>

<!-- reports/payment_voucher_template.xml -->
<template id="report_payment_voucher">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="o">
            <div class="page" style="font-family: Arial; padding: 20mm;">
                <!-- OSUS Header -->
                <div style="background: #800020; color: #FFD700; padding: 20px;">
                    <h1>OSUS Properties Payment Voucher</h1>
                </div>
                
                <!-- Payment Details -->
                <div style="margin-top: 20px;">
                    <table style="width: 100%;">
                        <tr>
                            <td><strong>Voucher No:</strong></td>
                            <td><t t-esc="o.name"/></td>
                        </tr>
                        <tr>
                            <td><strong>Date:</strong></td>
                            <td><t t-esc="o.date"/></td>
                        </tr>
                    </table>
                </div>
                
                <!-- QR Code -->
                <div style="text-align: center; margin-top: 30px;">
                    <img t-att-src="'data:image/png;base64,%s' % o.qr_code_image" 
                         style="width: 150px; height: 150px;"/>
                    <p>Scan to verify payment authenticity</p>
                </div>
                
                <!-- Digital Signatures -->
                <div style="margin-top: 40px;">
                    <div style="display: inline-block; width: 45%;">
                        <img t-if="o.creator_signature" 
                             t-att-src="'data:image/png;base64,%s' % o.creator_signature"
                             style="max-width: 200px;"/>
                        <p>Creator Signature</p>
                    </div>
                    <div style="display: inline-block; width: 45%;">
                        <img t-if="o.approver_signature" 
                             t-att-src="'data:image/png;base64,%s' % o.approver_signature"
                             style="max-width: 200px;"/>
                        <p>Approver Signature</p>
                    </div>
                </div>
            </div>
        </t>
    </t>
</template>
```

### Email Integration (Mail Thread Pattern)
```python
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(tracking=True)
    state = fields.Selection([...], tracking=True)
    
    def action_approve(self):
        self.write({'state': 'approved'})
        # Send email notification
        template = self.env.ref('module.email_template_approval')
        template.send_mail(self.id, force_send=True)
        # Log message to chatter
        self.message_post(
            body="Payment approved by %s" % self.env.user.name,
            subject="Payment Approval",
            message_type='notification'
        )
```

---

## Theme & Branding Architecture

### OSUS Properties Theme (`muk_web_theme/`)
**Colors & Variables**:
```scss
// static/src/scss/osus_branding.scss
$osus-primary: #800020;        // Maroon
$osus-secondary: #FFD700;      // Gold
$osus-accent: #FFF8DC;         // Light Gold

.o_payment_approval_widget {
    background: linear-gradient(135deg, $osus-primary, darken($osus-primary, 10%));
    border-left: 4px solid $osus-secondary;
    
    &__header {
        color: $osus-secondary;
        font-weight: 600;
    }
    
    &__status-badge {
        background: $osus-secondary;
        color: $osus-primary;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }
}
```

**Modules Using OSUS Branding**: `account_payment_*`, `osus_report_header_footer/`, `muk_web_*`, `partner_statement_followup/`

### SGC Tech AI Theme (`sgc_tech_ai_theme/`)
**SCSS Architecture** (fixed from invalid `\-variable` syntax):
```scss
// static/src/scss/sgc_colors.scss
$sgc-navy: #0c1e34;
$sgc-cyan: #00FFF0;
$sgc-green: #00FF88;
$sgc-gradient-ocean: linear-gradient(135deg, $sgc-navy, darken($sgc-navy, 10%));
$sgc-gradient-electric: linear-gradient(90deg, $sgc-cyan, $sgc-green);

// static/src/scss/dashboard_theme.scss
@import 'sgc_colors';

.o_scholarix_dashboard {
    background: $sgc-gradient-ocean;
    
    .card {
        border-top: 3px solid $sgc-cyan;
        background: rgba($sgc-navy, 0.8);
        
        &:hover {
            box-shadow: 0 4px 20px rgba($sgc-cyan, 0.3);
        }
    }
}
```

**Modules Using SGC Tech AI Branding**: `scholarix_*`, `sgc_tech_ai_theme/`, `llm_lead_scoring/`

**Asset Loading Order**:
```python
'assets': {
    'web.assets_backend': [
        'sgc_tech_ai_theme/static/src/scss/sgc_colors.scss',      # Colors first
        'sgc_tech_ai_theme/static/src/scss/typography.scss',      # Then typography
        'sgc_tech_ai_theme/static/src/scss/header_theme.scss',    # Layout components
        'sgc_tech_ai_theme/static/src/scss/dashboard_theme.scss', # Feature styles
    ],
}
```

---

## CloudPepper Deployment & Troubleshooting

### Automated Deployment Scripts (RECOMMENDED)
**Location**: Repository root directory

**quick_deploy.ps1** - Simplest one-command deployment:
```powershell
# Check status
.\quick_deploy.ps1 status

# Deploy module (with confirmations)
.\quick_deploy.ps1 deploy

# Verify deployment
.\quick_deploy.ps1 verify

# Fast deploy (skip confirmations)
.\quick_deploy.ps1 deploy -SkipConfirm
```

**deploy_coordinator.ps1** - Advanced step-by-step deployment:
```powershell
# Full deployment with monitoring
.\deploy_coordinator.ps1 -Action deploy

# Individual phases
.\deploy_coordinator.ps1 -Action backup
.\deploy_coordinator.ps1 -Action upload
.\deploy_coordinator.ps1 -Action restart
```

**Key Features**:
- Automatic SSH connection testing
- Database and file backups before deployment
- Service status monitoring
- Error detection and rollback capability
- Color-coded status output
- Deployment verification

### Manual Deployment Checklist
1. **Validate Module**: Run all `validate_*.py` scripts in module directory
2. **Backup Database**: `pg_dump -U odoo_user odoo_db > backup.sql`
3. **Upload Module**: `scp -r module_name/ user@cloudpepper.site:/opt/odoo/addons/`
4. **Update Module**: SSH to CloudPepper, run `odoo -u module_name --stop-after-init`
5. **Restart Odoo**: `sudo systemctl restart odoo`
6. **Clear Browser Cache**: Users must hard-refresh (Ctrl+Shift+R) to load new assets
7. **Monitor Logs**: `tail -f /var/log/odoo/odoo.log | grep ERROR`

### Common Issues & Fixes

**Issue: Infinite Recursion / RPC Timeout**
```javascript
// Already fixed globally in: report_font_enhancement/static/src/js/cloudpepper_global_protection.js
// This wraps MutationObserver and setAttribute to prevent infinite loops

// If issue persists, run emergency script:
python create_emergency_cloudpepper_fix.py
```

**Issue: Missing Fields in Views (e.g., `task_count` on partner)**
```python
# Already fixed in: commission_ax/models/cloudpepper_compatibility.py
# Adds missing computed fields that CloudPepper modules expect

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    task_count = fields.Integer(compute='_compute_task_count')
    
    @api.depends('user_ids.task_ids')
    def _compute_task_count(self):
        # Implementation
```

**Issue: SCSS Compilation Errors**
```bash
# Clear Odoo asset cache
rm -rf /opt/odoo/.local/share/Odoo/filestore/*/assets/*

# Regenerate assets
odoo --update=web --stop-after-init
```

**Issue: Permission Denied Errors**
```python
# Check security groups in ir.model.access.csv
# Verify user has correct group membership via UI: Settings → Users & Companies → Users
```

### Performance Monitoring
```sql
-- Check slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check database connections
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
```

---

## Quality Assurance & Testing

### Validation Scripts (Run Before Deployment)
**Location**: Module root directory or `.github/scripts/`

**validate_production_ready.py** checks:
- Module structure (required directories/files)
- Python syntax (`ast.parse()` on all `.py` files)
- XML syntax (`ET.parse()` on all `.xml` files)
- Security groups defined
- Field references in views exist in models
- Action methods exist for view buttons
- Asset paths valid

**validate_modern_syntax.py** checks:
- No deprecated `attrs={}` syntax
- No deprecated `states=` on buttons
- Modern `invisible=`, `readonly=` expressions

**Output Example**:
```
======================================================================
📊 VALIDATION SUMMARY
======================================================================

Total Checks: 78
✅ Passed: 78
❌ Failed: 0

✅ STATUS: PRODUCTION READY

Module is ready for CloudPepper deployment.
```

### Test Coverage Standards
```python
# tests/test_payment_workflow.py
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError, AccessError

@tagged('account_payment_final', 'post_install', '-at_install')
class TestPaymentWorkflow(TransactionCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Payment = cls.env['account.payment']
        cls.user_reviewer = cls.env['res.users'].create({
            'name': 'Test Reviewer',
            'login': 'reviewer@test.com',
            'groups_id': [(6, 0, [cls.env.ref('module.group_payment_reviewer').id])]
        })
    
    def test_01_payment_creation(self):
        """Test payment record creation with defaults"""
        payment = self.Payment.create({
            'name': 'TEST-001',
            'amount': 1000.00,
        })
        self.assertEqual(payment.state, 'draft')
    
    def test_02_approval_workflow(self):
        """Test multi-stage approval workflow"""
        payment = self.Payment.create({'name': 'TEST-002', 'amount': 500.00})
        
        # Submit for review
        payment.action_submit_for_review()
        self.assertEqual(payment.state, 'submitted')
        
        # Approve as reviewer
        payment.with_user(self.user_reviewer).action_approve()
        self.assertEqual(payment.state, 'approved')
    
    def test_03_security_constraints(self):
        """Test permission enforcement"""
        payment = self.Payment.create({'name': 'TEST-003', 'amount': 200.00})
        
        # Basic user cannot approve
        with self.assertRaises(AccessError):
            payment.with_user(self.env.ref('base.user_demo')).action_approve()
```

---

## Examples & Reference Modules

**Complete Payment Module**: `account_payment_final/`
- Multi-stage workflow, digital signatures, QR verification
- Professional OSUS-branded reports
- CloudPepper compatibility patches
- Comprehensive test suite

**Property Management System**: `rental_management/` (v3.4.0) ⭐ **PRODUCTION READY**
- Complete real estate sales/rental workflow with world-class SPA reports
- ✅ **Sales Offer Integration**: Fully present in property form (property.vendor)
- ✅ **Printable Payment Plans**: Professional SPA report with automatic percentage calculations
- ✅ **EMI/Installment Compliance**: Template-based system matching agreed payment terms
- 15 bank account fields (IBAN, SWIFT, separate accounts for payment/DLD/admin)
- DLD & Admin fee handling with configurable due dates
- Template-driven payment schedules (monthly, quarterly, bi-annual, annual)
- Automatic date calculation and invoice generation
- See `RENTAL_MANAGEMENT_PRODUCTION_AUDIT.md` for comprehensive quality report
- See `PAYMENT_PLAN_SOLUTION_PACKAGE.md` for 100+ pages of implementation docs

**REST API Reference**: `enhanced_rest_api/`
- JWT authentication, server-wide integration
- CRUD endpoints for CRM, Sales, Payments
- Rate limiting, logging, versioning

**Dashboard Example**: `oe_sale_dashboard_17/`
- Chart.js with OWL components
- Responsive design, mobile-optimized
- CloudPepper error protection

**Theme Reference**: `muk_web_theme/` (OSUS), `sgc_tech_ai_theme/` (SGC Tech AI)
- Complete branding systems
- Modular SCSS architecture
- Component-specific styling

---

## AI Agent Guidelines

**Critical Rules**:
1. **Always validate first**: Run `validate_*.py` scripts before ANY changes
2. **Modern syntax only**: Replace ALL `attrs={}` and `states=` with `invisible=`, `readonly=`
3. **Complete implementations**: If adding view elements, ensure ALL referenced methods/fields exist
4. **CloudPepper compatibility**: Include error handlers and compatibility patches for JavaScript
5. **Correct branding**: OSUS for business modules, SGC Tech AI for innovation/AI modules
6. **Security hierarchy**: Always define 4-6 tier groups (User→Reviewer→Approver→Authorizer→Manager→Admin)
7. **Asset loading order**: Emergency fixes use `('prepend', 'path/to/fix.js')` in manifest
8. **No Docker assumptions**: CloudPepper is direct Odoo install, not containerized

**When Making Changes**:
- Read validation script output to understand what's checked
- Check similar modules for patterns (e.g., `account_payment_final/` for workflows)
- Reference `PRODUCTION_READINESS_AUDIT.md` for quality standards
- Test locally before suggesting CloudPepper deployment
- Provide rollback steps for risky changes

---

## Additional Resources

- **Production Audit**: `PRODUCTION_READINESS_AUDIT.md` - Complete module quality report
- **Modern Syntax Guide**: `order_status_override/MODERN_SYNTAX_UPGRADE_SUMMARY.md`
- **Validation Scripts**: `.github/scripts/ai_*.py`, module-level `validate_*.py`
- **Emergency Procedures**: `create_emergency_cloudpepper_fix.py`
- **Module READMEs**: Each module has detailed documentation in `README.md`
- **Deployment Docs**: `00_START_HERE.txt`, `INDEX.md`, `DEPLOYMENT_README.md`
- **Payment Plan System**: `PAYMENT_PLAN_SOLUTION_PACKAGE.md` (100+ pages), `PAYMENT_PLAN_IMPLEMENTATION_GUIDE.md`

**Last Updated**: November 30, 2025
