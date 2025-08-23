# odoo-lsp

Cloned from https://github.com/Desdaemon/odoo-lsp.git

## Activation Instructions

1. Ensure you have Node.js installed.
2. In this directory, run:
   ```bash
   npm install
   npm run build
   ```
3. For VS Code integration, install the [Odoo LSP extension](https://marketplace.visualstudio.com/items?itemName=Desdaemon.odoo-lsp).
4. Configure the extension to point to this local binary if needed.

## Environment Setup

- Recommended Node.js version: 18.x or higher.
- If using Python virtual environments for Odoo, ensure your VS Code Python interpreter matches your Odoo environment.
- For CloudPepper deployment, validate with:
  ```bash
  python cloudpepper_deployment_final_validation.py
  python comprehensive_module_analyzer.py odoo-lsp
  ```

## Troubleshooting

- If the extension fails to start, check for missing dependencies or build errors.
- For Windows: Run VS Code as administrator if you encounter permission issues.
- If you see "Failed to download odoo-lsp binary", manually build as above and set `"odoo-lsp.serverPath"` in `.vscode/settings.json`.

## Integration Notes

- For Odoo 17/CloudPepper, ensure all modules and custom scripts are referenced in your workspace.
- Use the extension for real-time error detection, code completion, and validation in all Odoo modules.
- Always run validation scripts before deployment.

Refer to the official [odoo-lsp documentation](https://github.com/Desdaemon/odoo-lsp) for advanced usage.
