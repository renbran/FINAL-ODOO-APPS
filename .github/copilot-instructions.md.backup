
# 🧠 Copilot Instructions for odoo17_final

## Project Architecture & Big Picture
- **Odoo 17 Production Collection**: 50+ custom modules for CloudPepper deployment at `https://stagingtry.cloudpepper.site/` (login: `salescompliance@osusproperties.com`)
- **Module Categories**: Payment workflows (`account_payment_approval/`, `account_payment_final/`), dashboards (`oe_sale_dashboard_17/`, `crm_executive_dashboard/`, `odoo_dynamic_dashboard/`), API services (`enhanced_rest_api/`, `rest_api_odoo/`), commission systems (`commission_ax/`, `order_net_commission/`), workflow automation, HR (`scholarix_recruitment/`, `scholarix_assessment/`), theming (`muk_web_theme/`, `sgc_tech_ai_theme/`), and CRM/Sales enhancements
- **Emergency Response Architecture**: Validation/fix scripts for critical issues - run `validate_*.py` for pre-deployment checks, emergency scripts (`emergency_*.py`) for production hotfixes
- **CloudPepper-First Design**: All modules include CloudPepper compatibility patches, global error handlers, and OWL lifecycle protection (see `commission_ax/models/cloudpepper_compatibility.py`)
- **Dual Branding System**: 
  - **OSUS Properties**: `#800020` (maroon), `#FFD700` (gold) - for property/real estate modules
  - **SGC Tech AI**: `#0c1e34` (deep navy), `#00FFF0` (electric cyan), `#00FF88` (neon green) - for Scholarix/tech modules
- **No Docker**: Direct Odoo installation (not containerized) - deployment via SSH to CloudPepper server, not via docker-compose

## Developer Workflows

### Pre-Deployment Validation (CRITICAL - ALWAYS RUN FIRST)
```powershell
# Module-specific validation scripts - run before any deployment
python validate_module.py  # In specific module directories
python validate_production_ready.py  # For production modules
python validate_modern_syntax.py  # Check Odoo 17 syntax compliance
```

### Emergency Fix System (Production Hotfixes)
```powershell
# For critical CloudPepper production issues (infinite recursion/RPC errors)
python create_emergency_cloudpepper_fix.py
# Global JavaScript protection already in: report_font_enhancement/static/src/js/cloudpepper_global_protection.js
```

### Development & Testing Patterns
- **Validation First**: Run validation scripts in module directory before ANY code changes or deployment
- **Testing**: Standard Odoo `TransactionCase` with `@tagged('module_name')` decorators (see `account_payment_final/tests/`)
- **JavaScript Safety**: All JS must include CloudPepper compatibility patches and OWL lifecycle error handlers (extend from `cloudpepper_global_protection.js`)
- **Asset Loading**: Use `('prepend', 'path/to/fix.js')` in `__manifest__.py` assets for critical fixes that must load first
- **Cache Management**: Clean `__pycache__` after model/Python changes
- **Security Groups**: Always define 4-6 tier permission hierarchy (User→Reviewer→Approver→Authorizer→Manager→Admin) in `security/` folder

## Critical Architecture Patterns

### Unified State Workflow Pattern
```python
# Example: account_payment_final/models/account_payment.py
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
- **Report Generation**: QWeb XML for PDF (`payment_voucher_report.xml`), controllers for Excel/CSV with `report_xlsx` fallbacks
- **Multi-App Integration**: Modules extend Account, CRM, Sales, Website with unified UX
- **Email Integration**: Template-based with `mail.thread` inheritance and activity tracking

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

### Branding & Theme Architecture
**OSUS Properties Theme** (Real Estate/Property modules):
- Colors: `#800020` (maroon), `#FFD700` (gold), `#FFF8DC` (light gold)
- Modules: `muk_web_theme/`, `muk_web_colors/`, `muk_web_chatter/`, `muk_web_dialog/`
- Modern OWL components, CloudPepper error protection
- Files: See `OSUS_WEB_MODULES_QA_REPORT.md` for implementation details

**SGC Tech AI Theme** (Scholarix/AI modules):
- Colors: `#0c1e34` (deep navy), `#00FFF0` (electric cyan), `#00FF88` (neon green)
- Module: `sgc_tech_ai_theme/` with modular SCSS architecture
- Variables: SCSS only (no CSS custom properties) for Odoo 17 compliance
- Structure: `sgc_colors.scss` → `typography.scss` → component themes
- Gradients: `\-gradient-ocean`, `\-gradient-electric` for modern AI aesthetic

**Shared Patterns**:
- Chart.js integration for dashboards with mobile-first responsive design
- BEM methodology with module prefixing (`.o_module_name_component`)
- Asset loading order: colors → typography → layout → components
- CloudPepper compatibility: all JS wrapped in try-catch with fallbacks

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

## Quality Assurance & Validation

### Pre-Deployment Validation Pattern
```python
# Example: validate_module.py structure
import xml.etree.ElementTree as ET
from pathlib import Path

def validate_manifest():
    # Check all assets paths exist
    # Verify dependencies are declared
    # Validate version format
    
def validate_views():
    # Parse XML files with ET.parse()
    # Check field references exist in models
    # Verify actions have corresponding methods
    
def validate_python():
    # Check syntax with compile()
    # Verify proper decorators (@api.depends)
    # Validate security groups defined
```

### Error Handling Pattern (CloudPepper Compatible)
```javascript
// Always wrap OWL setup methods
setup() {
    try {
        super.setup();
        // Component logic
    } catch (error) {
        console.error('Module: Error description', error);
        // Fallback logic
    }
}
```

### Recent Quality Improvements (Nov 2025)
- Fixed JavaScript syntax errors in `muk_web_theme/` components (semicolons, object properties)
- Added comprehensive error handling to all OWL components
- Updated localStorage keys to module-namespaced (`osus_*`, `sgc_*`)
- Implemented CloudPepper compatibility in `muk_web_chatter/`, `muk_web_dialog/`
- See `OSUS_WEB_MODULES_QA_REPORT.md` for complete audit results

## Examples & References
- **Complete Module**: `account_payment_approval/` - enterprise payment workflow with signatures, QR, reports
- **API Implementation**: `enhanced_rest_api/controllers/` - JWT auth, CRUD endpoints, error handling
- **Dashboard Pattern**: `oe_sale_dashboard_17/static/src/js/` - Chart.js integration with OWL
- **Security Model**: `account_payment_approval/security/` - 6-tier groups with access rules
- **Report Templates**: `account_payment_approval/reports/` - OSUS-branded QWeb with digital signatures
- **Theme Implementation**: `muk_web_theme/` - OSUS Properties branded backend (see QA report)
- **SCSS Architecture**: `sgc_tech_ai_theme/` - Modular SCSS with proper variable structure

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
- **Always validate first**: Run validation scripts in module directory before ANY changes or deployment
- **Modern syntax only**: Replace ALL `attrs={}` and `states=` with modern `invisible=`, `readonly=` patterns
- **Complete implementations**: If adding view elements, ensure ALL referenced methods/fields exist in models
- **CloudPepper compatibility**: Include error handlers and compatibility patches for all JavaScript
- **Dual branding**: Use OSUS colors for property modules, SGC Tech AI colors for Scholarix modules
- **Emergency procedures**: For production issues, use `emergency_*.py` scripts with validation and rollback
- **Theme selection**: OSUS theme for business workflows, SGC Tech AI theme for innovative/AI features
- **SCSS compliance**: Use SCSS variables (not CSS custom properties) for Odoo 17 compatibility
- **Asset order**: Always load colors first, then typography, then components in manifest assets
