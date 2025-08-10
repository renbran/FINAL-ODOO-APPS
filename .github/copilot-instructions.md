
# 🧠 Copilot Instructions for odoo17_final

## Project Architecture & Big Picture
- **Odoo 17, Direct Installation**: Production-ready Odoo modules collection. Main deployment is CloudPepper (https://stagingtry.cloudpepper.site/) with login `salescompliance@osusproperties.com`.
- **Custom modules**: Each top-level folder is a standard Odoo module. Key examples: `account_payment_approval/` (enhanced payment workflows), `enhanced_rest_api/` (JWT API), `oe_sale_dashboard_17/` (Chart.js dashboards).
- **Validation-First Development**: Extensive Python validation scripts (`validate_*.py`, `cloudpepper_*.py`) for syntax, structure, and deployment readiness.
- **Emergency Response System**: Nuclear fix procedures (`nuclear_fix_*.sh`, `emergency_*.py`) for critical production issues.
- **OSUS Branding**: All modules include OSUS Properties branding with specific color schemes (`#1f4788`, `#f8f9fa`).

## Developer Workflows
- **Module Validation**: Run `python validate_module.py module_name` or specific validators like `validate_account_payment_final.py`
- **CloudPepper Deployment**: Always run `cloudpepper_deployment_validation.py` before deployment
- **Syntax Checking**: Use `python -m py_compile` for Python, `xml.etree.ElementTree.parse()` for XML validation  
- **Production Testing**: Use `final_production_test.py` and `production_readiness_test.py` for comprehensive checks
- **Emergency Fixes**: For critical issues, use nuclear fix scripts: `nuclear_fix_testerp.sh`, `emergency_fix.bat`
- **API Testing**: Use `check_module_installation.py` and `verify_api_installation.py` for endpoint validation
- **Cache Management**: Use PowerShell commands to clean `__pycache__`, `.DS_Store`, and other temp files

## Critical Architecture Patterns
- **Unified State Machines**: Use single `state` field with statusbar (see `account_payment_approval/models/account_payment.py` lines 25-42)
- **Multi-Stage Workflows**: 4-stage payments (draft→submitted→under_review→approved→authorized→posted), 3-stage receipts
- **Digital Signatures**: Binary fields with `attachment=True` for all workflow stages (`creator_signature`, `reviewer_signature`, etc.)
- **QR Verification**: Generate with `qrcode` library, verify via public controllers (`/payment/verify/{token}`)
- **Computed Field Patterns**: Always implement corresponding `_compute_*` methods (e.g., `is_approve_person` requires `_compute_is_approve_person`)
- **Security Groups**: 6-tier hierarchy: Creator→Reviewer→Approver→Authorizer→Manager→Admin with granular `ir.model.access.csv`

## Frontend Architecture (Odoo 17 Modern Stack)
- **OWL Components**: Use `/** @odoo-module **/`, `Component.setup()`, `useState()`, `useService()` patterns
- **SCSS Structure**: Component-based with CSS custom properties (`--bs-primary`, OSUS colors)
- **Asset Loading**: Bundle in `assets_backend`/`assets_frontend` with proper dependency order
- **Mobile-First**: All dashboards responsive with Chart.js integration (`crm_executive_dashboard/`, `oe_sale_dashboard_17/`)

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

## Common Issues & Resolution Patterns
- **Missing Action Methods**: Add to model if referenced in views (`action_print_multiple_reports`, `action_view_*`)
- **Missing Computed Fields**: Implement field + `_compute_*` method (see `is_approve_person` pattern)
- **XML Parse Errors**: Validate with `ET.parse()`, check field existence, verify xpath targets
- **JS/CSS Conflicts**: Use module-prefixed classes (`.o_module_name_`), avoid global styles
- **Permission Errors**: Check security groups in `ir.model.access.csv` and record rules in `security.xml`
- **Cache Issues**: Clean `__pycache__` directories and restart after major changes

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

For detailed frontend patterns, see `.github/instructions/Odoo 17 Copilot Agent Instructions - Enhanced with Frontend Best Practices.instructions.md`.
