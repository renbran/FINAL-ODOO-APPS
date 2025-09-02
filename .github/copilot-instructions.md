
# 🧠 Copilot Instructions for odoo17_final

## Project Architecture & Big Picture
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
