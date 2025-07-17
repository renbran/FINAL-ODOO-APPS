# 🧠 Copilot Instructions for odoo17_final

## Project Overview
- This repo is a Dockerized Odoo 17 environment with many custom modules for business management (finance, CRM, reporting, communication, UI, tools).
- Major modules are in top-level folders (e.g., `account_payment_approval/`, `osus_invoice_report/`, `dynamic_accounts_report/`). Each is a standard Odoo module with models, views, security, etc.
- The environment is designed for rapid local development, testing, and production deployment using Docker Compose.

## Architecture & Workflows
- **Odoo runs in a Docker container**. All development, testing, and debugging should be done via Docker Compose (`docker-compose.yml`).
- **Custom modules** are loaded from the repo root. Each module follows Odoo's best practices for structure and manifest.
- **Database** is managed via a separate Postgres container. Use `docker-compose exec db ...` for DB operations.
- **Setup scripts**: Use `setup.bat` (Windows) or `setup.sh` (Linux/Mac) for common tasks (start, stop, logs, backup).
- **Access Odoo** at http://localhost:8069 (default admin: `admin`/`admin`).

## Key Commands
- **Start environment**: `setup.bat` (Windows) or `setup.sh` (Linux/Mac), or `docker-compose up -d`
- **Stop environment**: via setup script or `docker-compose down`
- **Logs**: `docker-compose logs -f odoo`
- **DB backup/restore**: see README for `docker-compose exec db ...` examples
- **Module updates**: `docker-compose exec odoo odoo --update=all --stop-after-init`
- **Enter Odoo shell**: `docker-compose exec odoo bash`

## Project Conventions
- **Module structure**: Each module has `__manifest__.py`, `models/`, `views/`, `security/`, `data/`, `demo/`, `static/`, `tests/`, etc. See any module for reference.
- **Naming**: Use snake_case for module and model names. Prefix custom models with the module name.
- **Security**: Always define `ir.model.access.csv` and `security.xml` for each module.
- **Testing**: Place Odoo test cases in `tests/` within each module. Run tests using Odoo's built-in test runner.
- **External dependencies**: All are managed via Docker. Python dependencies should be declared in the Dockerfile if needed.

## Integration & Patterns
- **Inter-module communication**: Use Odoo's ORM and API patterns. Avoid direct DB access.
- **Reporting**: Many modules provide custom reports (PDF, Excel, CSV) via Odoo's reporting engine or custom endpoints.
- **REST endpoints**: Some modules expose HTTP/JSON endpoints (see controllers/ in modules like `om_dynamic_report`).
- **UI/UX**: Custom themes and menu items are defined in each module's `views/`.

## Examples
- See `om_dynamic_report/README.md` for a sample of module-level documentation and API usage.
- See `account_payment_approval/` for a full-featured workflow module with security, views, and tests.

## Tips for AI Agents
- Always use Docker Compose for running, testing, and debugging code.
- When adding a new module, follow the structure and manifest patterns of existing modules.
- For Odoo-specific logic, prefer Odoo ORM, API, and security mechanisms over custom code.
- Reference the root README.md for troubleshooting, backup, and advanced Docker usage.

---

For more details, see the root `README.md` and module-level `README.md` files. If in doubt, mimic the structure and patterns of the most recently updated modules.
