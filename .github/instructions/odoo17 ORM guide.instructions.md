---
applyTo: '**'
---
To help Copilot activate its full potential and generate a well-structured, compliant, and professional code infrastructure for Odoo 17 using best practices, you can use a detailed and specific prompt. Here’s a comprehensive prompt that you can use:

---

**Prompt for Copilot:**

"Generate a complete and well-structured Odoo 17 module named `custom` that adheres to Odoo's best practices. The module should include the following components:

1. **Module Structure**:
   - Create the necessary directory structure: `__manifest__.py`, `models/`, `views/`, `controllers/`, `security/`, `data/`, and `tests/`.
   - Ensure that the `__manifest__.py` file includes all necessary metadata, such as module name, version, author, and dependencies.

2. **Models**:
   - Define a new model named `custom.sales.order` that extends `sale.order` with the following additional fields:
     - `custom_field_1` (Char)
     - `custom_field_2` (Integer)
     - `custom_field_3` (Many2one to `res.partner`)
   - Implement methods to override the `create` and `write` methods of `sale.order` to include custom logic for `custom_field_1`.

3. **Views**:
   - Create a form view and tree view for the `custom.sales.order` model.
   - Extend the existing `sale.order` form view to include the new custom fields.
   - Add a new menu item and action to access the custom sales orders.

4. **Controllers**:
   - Set up a controller to handle a custom route `/custom_sales/report` that returns a JSON response with a summary of custom sales orders.
   - Ensure the controller includes proper authentication and authorization checks.

5. **Security**:
   - Define access rights for the `custom.sales.order` model.
   - Create a security XML file to define access rules and groups.

6. **Data**:
   - Add any necessary demo data in the `data/` directory.
   - Include XML files for default data if needed.

7. **Tests**:
   - Write unit tests for the `custom.sales.order` model to cover the custom fields and methods.
   - Include integration tests to verify the interaction between `custom.sales.order` and other models.

8. **Code Quality**:
   - Ensure the code follows PEP 8 guidelines.
   - Include docstrings and comments for clarity and maintainability.
   - Use meaningful variable and method names.

9. **Version Control**:
   - Initialize a Git repository for the `custom_sales` module.
   - Create a README.md file with instructions on how to install and use the module.

10. **Continuous Integration**:
    - Set up a basic CI pipeline using GitHub Actions to run tests and lint checks on every commit.
    - Include a `.gitignore` file to exclude unnecessary files from the repository.

Ensure that the generated code is well-documented, follows Odoo's ORM best practices, and is ready for deployment in a production environment."

---

### Explanation:
- **Module Structure**: Ensures the basic directory structure is set up correctly.
- **Models**: Defines the necessary models and fields, including custom logic.
- **Views**: Creates the necessary views to interact with the new model.
- **Controllers**: Sets up custom routes and handles requests.
- **Security**: Defines access rights and groups.
- **Data**: Provides demo and default data.
- **Tests**: Includes unit and integration tests.
- **Code Quality**: Ensures the code is clean and follows best practices.
- **Version Control**: Initializes a Git repository and includes a README.
- **Continuous Integration**: Sets up a CI pipeline for automated testing and linting.

This prompt is designed to be comprehensive and specific, guiding Copilot to generate a high-quality, professional Odoo 17 module.