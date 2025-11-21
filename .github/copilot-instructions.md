
# 🧠 Copilot Instructions for odoo17_final

## Project Architecture & Big Picture
- **Odoo 17 Production Collection**: 50+ custom modules for CloudPepper deployment at `https://stagingtry.cloudpepper.site/` (login: `salescompliance@osusproperties.com`)
- **Module Portfolio**: Payment workflows (`account_payment_approval/`, `account_payment_final/`), dashboards (`oe_sale_dashboard_17/`, `crm_executive_dashboard/`), API services (`enhanced_rest_api/`), commission systems (`commission_ax/`), and workflow automation
- **Emergency Response Architecture**: 200+ validation/fix scripts (`cloudpepper_*.py`, `validate_*.py`, `emergency_*.py`) with comprehensive error detection and automated recovery
- **CloudPepper-First Design**: All modules include CloudPepper compatibility patches, global error handlers, and OWL lifecycle protection
- **OSUS Properties Branding**: Consistent color scheme `#800020` (maroon), `#FFD700` (gold), unified UX patterns across all modules

## Developer Workflows

### Pre-Deployment Validation (CRITICAL - ALWAYS RUN FIRST)
```bash
# CloudPepper deployment readiness - MANDATORY before any deployment
python cloudpepper_deployment_final_validation.py

# Module-specific validation scripts (200+ available)
python validate_commission_enhancement.py
python validate_order_net_commission.py
python commission_ax_deployment_validator.py
```

### Emergency Fix System (Production Hotfixes)
```bash
# For critical CloudPepper production issues (infinite recursion/RPC errors)
python create_emergency_cloudpepper_fix.py
python create_simple_emergency_fix.py
python emergency_odoo_define_global_fix.js  # JavaScript compatibility
```

### Development & Testing Patterns
- **Validation First**: Run validation scripts before ANY code changes or deployment
- **JavaScript Safety**: All JS must include CloudPepper compatibility patches and OWL lifecycle error handlers
- **Emergency Deployment**: Use emergency scripts for critical hotfixes with automatic rollback capabilities
- **Cache Management**: Clean `__pycache__` after major changes; run `final_manual_cleanup.py` for comprehensive cleanup
- **Asset Loading**: Use `('prepend', 'path/to/fix.js')` in manifest for critical fixes that must load first
- **Testing**: Standard Odoo `TransactionCase` with `@tagged('module_name')` decorators

## Critical Architecture Patterns

### Unified State Workflow Pattern
```python
# Example: account_payment_approval/models/account_payment.py lines 25-42
state = fields.Selection([
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('under_review', 'Under Review'), 
    ('approved', 'Approved'),
    ('authorized', 'Authorized'),
    ('posted', 'Posted'),
], default='draft', tracking=True)
```

### Digital Signature & QR Verification System
- **Binary Signature Fields**: `attachment=True` for all workflow stages (`creator_signature`, `reviewer_signature`, etc.)
- **QR Generation**: Use `qrcode` library with public verification controllers (`/payment/verify/{token}`)
- **Security Architecture**: 6-tier hierarchy (Creator→Reviewer→Approver→Authorizer→Manager→Admin) with granular CSV access control

### Computed Field Implementation Pattern
```python
# Always implement field + corresponding compute method
is_approve_person = fields.Boolean(compute='_compute_is_approve_person')

@api.depends('user_id', 'state')
def _compute_is_approve_person(self):
    # Implementation with proper error handling
```

### Module Dependency & Integration Strategy
- **Cross-Module Communication**: Use `enhanced_rest_api/` for JWT-authenticated endpoints across CRM, Sales, Payments
- **Report Generation**: QWeb XML for PDFs, controllers for Excel/CSV with `report_xlsx` fallbacks
- **Email Integration**: `mail.thread` inheritance with activity tracking across all workflow modules

## Frontend Architecture (Odoo 17 Modern Stack)

### OWL Component Pattern (ES6+ Only)
```javascript
/** @odoo-module **/
import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MyComponent extends Component {
    static template = "my_module.MyTemplate";
    static props = ["*"];
    
    setup() {
        this.orm = useService("orm");
        this.state = useState({ isLoading: false });
        this.chartRef = useRef("chartContainer");
        
        onMounted(async () => {
            await this.loadData();
        });
    }
}
```

### Asset Loading & CloudPepper Compatibility
```python
# __manifest__.py pattern for emergency fixes
'assets': {
    'web.assets_backend': [
        # CRITICAL: Emergency fixes MUST load first
        ('prepend', 'module_name/static/src/js/immediate_emergency_fix.js'),
        ('prepend', 'module_name/static/src/js/cloudpepper_compatibility_patch.js'),
        'module_name/static/src/js/main_component.js',
    ],
}
```

### OSUS Branding & Responsive Design
- **Color Variables**: `#800020` (primary maroon), `#FFD700` (gold), `#FFF8DC` (light gold background)
- **Chart.js Integration**: All dashboards (`crm_executive_dashboard/`, `oe_sale_dashboard_17/`) use Chart.js with mobile-first responsive design
- **CSS Structure**: BEM methodology with module prefixing (`.o_module_name_component`)

## Integration & Cross-Component Patterns
- **REST API**: JWT authentication via `enhanced_rest_api/` with endpoints for CRM, Sales, Payments
- **Report Generation**: QWeb XML for PDF (`payment_voucher_report.xml`), controllers for Excel/CSV with `report_xlsx` fallbacks
- **Multi-App Integration**: Modules extend Account, CRM, Sales, Website with unified UX
- **Email Integration**: Template-based with `mail.thread` inheritance and activity tracking

## CloudPepper Deployment Specifics
- **URL**: Production at `https://stagingtry.cloudpepper.site/` (not Docker)
- **Dependencies**: Install `qrcode num2words pillow` before module installation
- **File Validation**: All referenced files must exist (check `data/`, `static/`, `views/` paths in manifest)
- **View-Model Sync**: All view button actions must have corresponding model methods
- **Field References**: All view field references must exist in model (including computed fields)
- **JavaScript Protection**: Always include CloudPepper compatibility patches and error handlers for OWL lifecycle issues
- **Emergency Scripts**: Use `cloudpepper_deployment_final_validation.py` before any deployment
- **Critical Issues**: For infinite recursion/RPC errors, use emergency scripts: `create_emergency_cloudpepper_fix.py`

## Common Issues & Resolution Patterns
- **Missing Action Methods**: Add to model if referenced in views (`action_print_multiple_reports`, `action_view_*`)
- **Missing Computed Fields**: Implement field + `_compute_*` method (see `is_approve_person` pattern)
- **XML Parse Errors**: Validate with `ET.parse()`, check field existence, verify xpath targets
- **JS/CSS Conflicts**: Use module-prefixed classes (`.o_module_name_`), avoid global styles
- **Permission Errors**: Check security groups in `ir.model.access.csv` and record rules in `security.xml`
- **Cache Issues**: Clean `__pycache__` directories and restart after major changes
- **CloudPepper OWL Errors**: Use global error handlers and CloudPepper compatibility patches
- **RPC Errors**: Always wrap RPC calls in try-catch with proper error handling and fallbacks

## Examples & References
- **Complete Module**: `account_payment_approval/` - enterprise payment workflow with signatures, QR, reports
- **API Implementation**: `enhanced_rest_api/controllers/` - JWT auth, CRUD endpoints, error handling
- **Dashboard Pattern**: `oe_sale_dashboard_17/static/src/js/` - Chart.js integration with OWL
- **Security Model**: `account_payment_approval/security/` - 6-tier groups with access rules
- **Report Templates**: `account_payment_approval/reports/` - OSUS-branded QWeb with digital signatures

## Module Structure & Conventions
- **Standard Layout**: `__manifest__.py`, `models/`, `views/`, `security/`, `data/`, `static/`, `tests/`, optional `doc/`, `wizards/`, `reports/`
- **Odoo 17 Modern Syntax**: **CRITICAL** - Use `invisible="condition"` NOT deprecated `states=` or `attrs={}` (see `order_status_override/MODERN_SYNTAX_UPGRADE_SUMMARY.md`)
- **Naming**: snake_case modules, version `17.0.x.y.z`, descriptive categories
- **Security**: Always include `security/ir.model.access.csv` and group definitions in `security/` for new models
- **Dependencies**: Common libs pre-installed: `qrcode`, `num2words`, `pillow`, `xlsxwriter`, `pandas`, `PyJWT`

### XML Modern Syntax Examples
```xml
<!-- ✅ CORRECT - Odoo 17 Modern Syntax -->
<field name="custom_status" readonly="state in ['sale', 'done', 'cancel']"/>
<button name="action_approve" invisible="state != 'draft' or not approver_id"/>

<!-- ❌ WRONG - Deprecated Syntax (DO NOT USE) -->
<field name="custom_status" attrs="{'readonly': [('state', 'in', ['sale', 'done'])]}"/>
<button name="action_approve" states="draft"/>
```

## AI Agent Guidelines
- **Always validate first**: Run `cloudpepper_deployment_final_validation.py` before any deployment
- **Modern syntax only**: Replace ALL `attrs={}` and `states=` with modern `invisible=`, `readonly=` patterns
- **Complete implementations**: If adding view elements, ensure ALL referenced methods/fields exist in models
- **CloudPepper compatibility**: Include error handlers and compatibility patches for all JavaScript
- **OSUS branding**: Maintain color scheme `#800020` (maroon), `#FFD700` (gold) across all UI
- **Emergency procedures**: For production issues, use emergency fix scripts with validation and rollback
