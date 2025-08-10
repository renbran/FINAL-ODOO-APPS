
# 🧠 Copilot Instructions for odoo17_final

## Project Architecture & Big Picture
- **Odoo 17, Direct Installation**: Production-ready Odoo modules collection. Main deployment is CloudPepper (https://testerp.cloudpepper.site) but works with any Odoo 17 installation.
- **Custom modules**: Each top-level folder (e.g. `account_payment_approval/`, `enhanced_rest_api/`, `oe_sale_dashboard_17/`) is a standard Odoo module with its own models, views, security, and tests.
- **Testing/Validation**: Extensive Python validation scripts for syntax, structure, and deployment readiness checks.
- **Production Environment**: CloudPepper deployment with login `salescompliance@osusproperties.com`.
- **Module Installation**: Manual via Odoo Apps menu after "Update Apps List" or programmatic via Odoo CLI commands.

## Developer Workflows
- **Module Validation**: Run `python validate_module.py` or specific validators like `validate_account_payment_final.py`
- **Syntax Checking**: Use module-specific validators (e.g. `validate_module_syntax.py`, `validate_xml_syntax.py`)  
- **Production Testing**: Use comprehensive tests like `final_production_test.py` and `production_readiness_test.py`
- **Module Updates**: Direct Odoo commands like `odoo --update=module_name --stop-after-init -d database_name`
- **Installation Testing**: Use `.bat` scripts for Windows or `.sh` scripts for Linux/Mac (e.g. `test_account_payment_final.bat`)
- **API Testing**: Dedicated scripts like `check_module_installation.py` and `verify_api_installation.py`
- **Emergency Fixes**: Specialized fix scripts for critical issues (e.g. `emergency_fix.bat`, `nuclear_fix_testerp.sh`)

## Project Conventions & Patterns
- **Module structure**: Each module has `__manifest__.py`, `models/`, `views/`, `security/`, `data/`, `demo/`, `static/`, `tests/`.
- **Naming**: Use snake_case for modules/models. Prefix custom models with module name (e.g. `enhanced_rest_api.api_config`).
- **Security**: Always define `ir.model.access.csv` and `security.xml` for each module. See `account_payment_approval/security/` for reference.
- **Testing**: Use `TransactionCase` in `tests/` with `@tagged` decorators (see `tk_sale_split_invoice/tests/test_sale_split_invoice.py`).
- **Validation Scripts**: Extensive use of Python validation scripts for module readiness (validate_*.py pattern).
- **Model extension**: Use `_inherit` for extension, `_inherits` for delegation. Example: `account_payment_approval/models/account_payment.py`.
- **State machines**: Use Selection fields and statusbar in form views (see `account_payment_approval`).
- **API endpoints**: Use `@http.route` with proper auth/CSRF. See `enhanced_rest_api/` for comprehensive REST API patterns.
- **Reports**: Use QWeb XML for PDF, controllers for Excel/CSV. See `report_font_enhancement/` for advanced styling.
- **Config/settings**: Use `res.config.settings` and `ir.config_parameter` for settings.
- **Error handling**: Use `ValidationError` for constraints, `UserError` for user-facing errors.
- **Frontend**: Use Chart.js for dashboards (see `oe_sale_dashboard_17/`, `crm_executive_dashboard/`).
- **CloudPepper deployment**: Production modules are optimized for CloudPepper hosting environment.

## Integration & Cross-Component Patterns
- **Excel export**: Use `report_xlsx` if available, but degrade gracefully if not (see `report_xlsx/` module).
- **Multi-app integration**: Some modules add features to multiple Odoo apps (Accounting, CRM, Sales).
- **Security**: Multi-level permissions and record rules with careful CloudPepper compatibility.
- **REST API**: Comprehensive REST endpoints via `enhanced_rest_api/` module with JWT authentication.
- **Mobile/responsive**: Dashboards and reports are designed for mobile (see `crm_executive_dashboard/`, `oe_sale_dashboard_17/`).
- **Deployment validation**: Every module includes validation scripts for CloudPepper deployment readiness.

## Examples & References
- **Module structure**: `account_payment_approval/`, `enhanced_rest_api/`, `crm_executive_dashboard/`
- **API endpoint**: `enhanced_rest_api/controllers/`, comprehensive REST API with authentication
- **Form view**: `account_payment_approval/views/account_payment_views.xml`
- **Testing**: `tk_sale_split_invoice/tests/test_sale_split_invoice.py` with `@tagged` decorators
- **Advanced styling**: `report_font_enhancement/` for print optimization and accessibility
- **Dashboard implementation**: `oe_sale_dashboard_17/` for Chart.js integration patterns

## Common Issues & Troubleshooting
- **DB errors**: If cron jobs fail, check `fix_cron_in_odoo.py`.
- **Duplicate records**: See `fix_duplicate_partners.py` for deduplication logic.
- **JS errors**: Run `fix_dashboard_js.py` for dashboard JS issues.
- **Permission errors**: Check `ir.model.access.csv` and security groups.
- **Module dependencies**: Ensure all dependencies are in `__manifest__.py` before install.
- **Excel export**: If not available, check `xlsxwriter` and `report_xlsx` install.
- **CloudPepper deployment**: Use `cloudpepper_deployment_validation.py` for pre-deployment checks.
- **Emergency fixes**: Nuclear fix scripts available for critical production issues.

## Tips for AI Agents
- Always use Python validation scripts for all dev/test/debug workflows.
- When adding modules, follow structure and manifest patterns of existing modules.
- Prefer Odoo ORM, API, and security mechanisms over custom code.
- Always include security definitions for new models.
- Use Odoo's built-in test infra with `TransactionCase` and `@tagged` decorators.
- For reports, prefer QWeb XML and follow theming patterns in `report_font_enhancement/`.
- CloudPepper deployment requires specific compatibility patterns - check existing modules.

---

For more details, see the root `README.md` and module-level `README.md` files. If in doubt, mimic the structure and patterns of the most recently updated modules.
