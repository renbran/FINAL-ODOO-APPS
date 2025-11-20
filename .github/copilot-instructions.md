
# 🧠 Copilot Instructions for odoo17_final

## Project Architecture & Big Picture
<<<<<<< HEAD
- **Odoo 17 Multi-Module Repository**: Production-ready Odoo addons with Dockerfile for containerized deployment
- **Module Portfolio**: ~50+ custom modules spanning accounting, sales, HR, reporting, theming, and workflow automation
- **No Docker Compose**: Uses standalone Dockerfile with custom Python dependencies (xlsxwriter, qrcode, pandas, etc.)
- **Setup Scripts**: Use `setup.bat` (Windows) or `setup.sh` (Linux/Mac) for docker operations (start, stop, logs, build, shell)
- **Module Deployment**: Individual modules have `deploy.sh/deploy.ps1` scripts for production deployment (see `oe_sale_dashboard_17/`)

## Developer Workflows
- **Container Operations**: Use `setup.bat start|stop|restart|logs|build|shell|update|status` or `setup.sh` equivalent
- **Module Updates**: `./setup.sh update_mod MODULE_NAME` for single module or `./setup.sh update` for all
- **Shell Access**: `./setup.sh shell` to enter container bash
- **Module Deployment**: Use module-specific `deploy.sh` scripts (see `oe_sale_dashboard_17/deploy.sh`)
- **Testing**: Standard Odoo `TransactionCase` in `tests/` directories (see `tk_sale_split_invoice/tests/`)
- **Documentation**: Check module `docs/` folders for deployment guides and troubleshooting

## Project Conventions & Patterns
- **Module Structure**: Standard Odoo with `__manifest__.py`, `models/`, `views/`, `security/`, `data/`, `static/`, `tests/`, optional `docs/`
- **Odoo 17 Syntax**: **CRITICAL** - Use modern XML syntax: `invisible="condition"` NOT `states=` or `attrs={}` (see `ODOO17_SYNTAX_GUIDELINES.md`)
- **Dependencies**: Dockerfile pre-installs: `xlsxwriter`, `qrcode`, `pandas`, `python-dateutil`, `PyPDF2`, `reportlab`, `num2words`
- **Module Categories**: Sales dashboards, accounting enhancements, report theming, HR automation, website customization, workflow approval
- **Naming**: snake_case modules, descriptive manifests with version `17.0.x.y.z`, proper category classification
- **Security**: Always include `security/ir.model.access.csv` and security groups for new models
- **Testing**: Use `@tagged('module_name')` and `TransactionCase` for comprehensive test coverage

## Integration & Cross-Component Patterns
- **Dashboard Architecture**: Chart.js with CDN fallback, responsive design, mobile-optimized (see `oe_sale_dashboard_17/`)
- **Report Theming**: Universal CSS variables system with high-contrast, adaptive transparency (see `report_font_enhancement/`)
- **Commission Systems**: Dual-group structure (external/internal) with flexible calculation methods (see `commission_ax/`)
- **Multi-App Integration**: Modules span Contacts, Accounting, Sales, HR apps with cross-app data flows
- **Deployment Patterns**: Module-specific deployment scripts with backup, cache clearing, and robustness checks
- **Theme Integration**: Multiple web theme modules (`muk_web_*`, `web_login_styles`) with cohesive styling approach

## Examples & References
- **Complete Module**: `commission_ax/` (manifest, models, views, data, security)
- **Testing Pattern**: `tk_sale_split_invoice/tests/test_sale_split_invoice.py` (TransactionCase with @tagged)
- **Dashboard Module**: `oe_sale_dashboard_17/` (Chart.js, deployment scripts, documentation)
- **Report Theming**: `report_font_enhancement/README.md` (CSS variables, accessibility)
- **Deployment Script**: `oe_sale_dashboard_17/deploy.sh` (backup, cache clearing, robustness)
- **Odoo 17 Syntax**: `ODOO17_SYNTAX_GUIDELINES.md` (modern XML attributes)

## Common Issues & Troubleshooting
- **Odoo 17 Compatibility**: Replace deprecated `states=` and `attrs={}` with modern `invisible=`, `readonly=` syntax
- **Chart.js Issues**: Modules use CDN with fallback mechanism for offline deployment
- **Module Dependencies**: Check `__manifest__.py` dependencies and ensure all required modules are available
- **Security Errors**: Always include `ir.model.access.csv` and proper security groups for new models
- **Deployment Issues**: Use module-specific deploy scripts which handle cache clearing and backups

## Tips for AI Agents
- **Always use modern Odoo 17 XML syntax**: Replace deprecated `states=` and `attrs={}` with `invisible=`, `readonly=` conditions
- **Follow existing patterns**: Study `commission_ax/` for complete module structure, `oe_sale_dashboard_17/` for dashboards
- **Use deployment scripts**: Leverage module-specific `deploy.sh` scripts instead of manual deployment
- **Check documentation**: Many modules have `docs/` folders with deployment guides and troubleshooting
- **Test thoroughly**: Use `@tagged` decorators and `TransactionCase` for comprehensive testing
- **Container-first development**: All operations should work within Docker container using setup scripts

---

**Key Documentation**: `ODOO17_SYNTAX_GUIDELINES.md` for syntax migration, module `docs/` folders for deployment guides
=======
- **Odoo 17 Production Collection**: 50+ custom modules for CloudPepper deployment at `https://stagingtry.cloudpepper.site/` (login: `salescompliance@osusproperties.com`)
- **Module Categories**: Payment workflows (`account_payment_*`), dashboards (`*_dashboard*`, `oe_sale_dashboard_17`), API services (`enhanced_rest_api`), reports, and UI enhancements
- **Emergency Response Architecture**: 200+ validation/fix scripts (`cloudpepper_*.py`, `validate_*.py`, `emergency_*.py`) with comprehensive error detection and automated recovery
- **CloudPepper-First Design**: All modules include CloudPepper compatibility patches, global error handlers, and OWL lifecycle protection
- **OSUS Properties Branding**: Consistent color scheme `#800020` (maroon), `#FFD700` (gold), unified UX patterns across all modules

## Developer Workflows

### Pre-Deployment Validation (CRITICAL)
```bash
# CloudPepper deployment readiness - ALWAYS run before deployment
python cloudpepper_deployment_final_validation.py

# Module-specific deep analysis for compatibility issues  
python comprehensive_module_analyzer.py <module_name>

# Emergency fixes for critical CloudPepper issues
python create_emergency_cloudpepper_fix.py
```

### Development & Testing Patterns
- **JavaScript Safety Protocol**: All JS includes CloudPepper compatibility patches (`cloudpepper_global_protection.js`) and OWL lifecycle error handlers
- **Validation Pipeline**: Every module change requires validation script execution - check 200+ `validate_*.py` scripts for comprehensive testing
- **Emergency Fix System**: For infinite recursion/RPC errors, use emergency scripts (`emergency_*.py`) that create targeted fixes with rollback capabilities
- **Cache Management**: Clean `__pycache__` after major changes; use `final_cleanup_status.py` for comprehensive cleanup
- **Asset Loading Strategy**: Use `('prepend', 'path/to/emergency_fix.js')` pattern for critical fixes that must load first

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

## AI Agent Guidelines
- **Always validate**: Use Python validation scripts before any deployment
- **Follow patterns**: Match existing module structures, especially manifest dependencies and security
- **CloudPepper first**: Test all changes against CloudPepper compatibility patterns
- **Complete implementations**: If adding view elements, ensure all referenced methods/fields exist
- **OSUS branding**: Maintain consistent styling and color schemes across modules
- **Emergency ready**: Document any breaking changes for potential nuclear fix procedures

## Emergency Response & Validation System
- **Real-time Error Detection**: Use `comprehensive_module_analyzer.py` for immediate issue identification
- **CloudPepper Emergencies**: Deploy fixes via `create_emergency_cloudpepper_fix.py` for critical production issues
- **JavaScript Safety**: All modules include `cloudpepper_compatibility_patch.js` and `cloudpepper_global_protection.js`
- **Nuclear Options**: Emergency deployment scripts for system-wide issues requiring immediate resolution
- **Validation Pipeline**: `cloudpepper_deployment_final_validation.py` → Emergency fixes → Production deployment
- **Monitoring**: Post-deployment validation with 24-hour monitoring for CloudPepper stability
>>>>>>> main
