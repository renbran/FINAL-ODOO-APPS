# Comprehensive Odoo 17 Module Development Prompt for Copilot

## Core Instructions for Copilot

You are an expert Odoo 17 developer. Generate a complete, production-ready, and installable Odoo 17 module that strictly follows Odoo's architectural patterns, coding standards, and best practices. The module must be immediately deployable and fully functional.

---

## 1. Module Foundation & Architecture

### Directory Structure (MANDATORY)
Create the following exact directory structure:
```
[module_name]/
├── __init__.py
├── __manifest__.py
├── models/
│   └── __init__.py
├── views/
├── controllers/
│   └── __init__.py
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
├── demo/
├── static/
│   ├── src/
│   │   ├── css/
│   │   ├── js/
│   │   └── xml/
│   └── description/
│       ├── icon.png
│       └── index.html
├── tests/
│   └── __init__.py
├── wizard/
│   └── __init__.py
├── report/
└── README.md
```

### __manifest__.py Requirements
```python
{
    'name': '[Module Display Name]',
    'version': '17.0.1.0.0',
    'category': '[Appropriate Category]',
    'summary': '[Brief Summary]',
    'description': """
[Detailed Description]
    """,
    'author': '[Author Name]',
    'website': '[Website URL]',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],  # Minimal dependencies
    'external_dependencies': {
        'python': [],  # Python packages if needed
        'bin': [],     # Binary dependencies if needed
    },
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/menu.xml',
        'views/[model_name]_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '[module_name]/static/src/css/*.css',
            '[module_name]/static/src/js/*.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,  # Set to True if it's a standalone application
    'sequence': 100,
}
```

---

## 2. Model Development Standards

### Model Class Structure
```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class ModelName(models.Model):
    _name = 'module.model'
    _description = 'Model Description'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # If needed
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Name must be unique'),
    ]
    
    # Fields definition with proper types and attributes
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        help="Help text for the field"
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)
    
    # Computed fields
    @api.depends('field1', 'field2')
    def _compute_computed_field(self):
        for record in self:
            record.computed_field = record.field1 + record.field2
    
    # Constraints
    @api.constrains('field_name')
    def _check_field_name(self):
        for record in self:
            if not record.field_name:
                raise ValidationError("Field name cannot be empty")
    
    # CRUD overrides
    @api.model
    def create(self, vals):
        # Custom logic before creation
        return super().create(vals)
    
    def write(self, vals):
        # Custom logic before write
        return super().write(vals)
    
    def unlink(self):
        # Custom logic before deletion
        return super().unlink()
    
    # Custom methods
    def custom_method(self):
        """Custom method with proper docstring"""
        self.ensure_one()
        # Implementation
        return True
```

### Field Types and Best Practices
- Use appropriate field types: `Char`, `Text`, `Integer`, `Float`, `Boolean`, `Date`, `Datetime`, `Selection`, `Many2one`, `One2many`, `Many2many`
- Always include `string`, `help`, and `required` parameters where appropriate
- Use `index=True` for frequently searched fields
- Implement proper `_sql_constraints` for data integrity
- Use `tracking=True` for fields that should be tracked in chatter

---

## 3. View Development Standards

### Form View Structure
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_model_form" model="ir.ui.view">
        <field name="name">model.form</field>
        <field name="model">module.model</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <button name="action_confirm" type="object" string="Confirm" 
                            class="oe_highlight" states="draft"/>
                    <field name="state" widget="statusbar" statusbar_visible="draft,confirmed,done"/>
                </header>
                <sheet>
                    <div class="oe_title">
                        <label for="name" class="oe_edit_only"/>
                        <h1><field name="name" placeholder="Name..."/></h1>
                    </div>
                    <group>
                        <group>
                            <field name="field1"/>
                            <field name="field2"/>
                        </group>
                        <group>
                            <field name="field3"/>
                            <field name="field4"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="General Information">
                            <field name="description"/>
                        </page>
                        <page string="Additional Info">
                            <!-- Additional fields -->
                        </page>
                    </notebook>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>
</odoo>
```

### Tree View Structure
```xml
<record id="view_model_tree" model="ir.ui.view">
    <field name="name">model.tree</field>
    <field name="model">module.model</field>
    <field name="arch" type="xml">
        <tree>
            <field name="name"/>
            <field name="state" widget="badge" 
                   decoration-success="state == 'done'"
                   decoration-warning="state == 'confirmed'"
                   decoration-muted="state == 'draft'"/>
            <field name="create_date"/>
        </tree>
    </field>
</record>
```

---

## 4. Security Implementation

### Access Rights (ir.model.access.csv)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_module_model_user,module.model user,model_module_model,base.group_user,1,1,1,1
access_module_model_manager,module.model manager,model_module_model,base.group_system,1,1,1,1
```

### Security Groups (security.xml)
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="group_module_user" model="res.groups">
        <field name="name">Module User</field>
        <field name="category_id" ref="base.module_category_operations"/>
        <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    </record>
    
    <record id="group_module_manager" model="res.groups">
        <field name="name">Module Manager</field>
        <field name="category_id" ref="base.module_category_operations"/>
        <field name="implied_ids" eval="[(4, ref('group_module_user'))]"/>
    </record>
</odoo>
```

---

## 5. Controller Development

### Controller Structure
```python
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class ModuleController(http.Controller):
    
    @http.route('/module/api/data', type='json', auth='user', methods=['POST'])
    def get_data(self, **kwargs):
        """API endpoint to retrieve data"""
        try:
            # Validate input
            if not kwargs.get('required_param'):
                return {'error': 'Required parameter missing'}
            
            # Process request
            data = request.env['module.model'].search_read(
                [('active', '=', True)],
                ['name', 'state']
            )
            
            return {
                'success': True,
                'data': data
            }
        except Exception as e:
            _logger.error(f"Error in get_data: {str(e)}")
            return {'error': str(e)}
    
    @http.route('/module/report/<int:record_id>', type='http', auth='user')
    def generate_report(self, record_id, **kwargs):
        """Generate and return report"""
        try:
            record = request.env['module.model'].browse(record_id)
            if not record.exists():
                return request.not_found()
            
            # Generate report logic
            return request.make_response(
                data,
                headers=[
                    ('Content-Type', 'application/pdf'),
                    ('Content-Disposition', f'attachment; filename=report_{record_id}.pdf')
                ]
            )
        except Exception as e:
            _logger.error(f"Error generating report: {str(e)}")
            return request.render('http_routing.http_error', {
                'status_code': 500,
                'status_message': 'Internal Server Error'
            })
```

---

## 6. Testing Framework

### Unit Tests
```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestModuleModel(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.Model = self.env['module.model']
        self.test_data = {
            'name': 'Test Record',
            'field1': 'Value 1',
            'field2': 100,
        }
    
    def test_create_record(self):
        """Test record creation"""
        record = self.Model.create(self.test_data)
        self.assertTrue(record.exists())
        self.assertEqual(record.name, self.test_data['name'])
    
    def test_constraint_validation(self):
        """Test field constraints"""
        with self.assertRaises(ValidationError):
            self.Model.create({
                'name': '',  # This should fail validation
                'field1': 'Value 1',
            })
    
    def test_computed_field(self):
        """Test computed field calculation"""
        record = self.Model.create(self.test_data)
        # Test computed field logic
        self.assertEqual(record.computed_field, expected_value)
```

---

## 7. Code Quality Standards

### Python Code Standards
- Follow PEP 8 guidelines strictly
- Use meaningful variable names: `sale_order` instead of `so`
- Include comprehensive docstrings for all methods
- Use type hints where appropriate
- Implement proper error handling with try/except blocks
- Use logging instead of print statements
- Follow Odoo's ORM patterns and avoid raw SQL queries

### XML Code Standards
- Use proper indentation (4 spaces)
- Include `<?xml version="1.0" encoding="utf-8"?>` header
- Use meaningful record IDs with module prefix
- Include proper field labels and help text
- Use appropriate widget types for fields

---

## 8. Performance Optimization

### Database Optimization
- Add database indexes for frequently searched fields
- Use `search_read()` instead of `search()` + `read()` when possible
- Implement proper domain filters to reduce query load
- Use `exists()` method for existence checks
- Batch operations when processing multiple records

### Memory Optimization
- Use `ensure_one()` for single record operations
- Implement proper caching for computed fields
- Use lazy loading for large datasets
- Avoid loading unnecessary fields in searches

---

## 9. Deployment Considerations

### Installation Requirements
- Ensure all dependencies are properly declared
- Include migration scripts if needed
- Test installation on fresh Odoo instance
- Verify all menu items and actions work correctly

### Configuration
- Include demo data for testing
- Provide clear installation instructions
- Document any required system configurations
- Include troubleshooting guide

---

## 10. Documentation Requirements

### README.md Structure
```markdown
# Module Name

## Description
Brief description of the module functionality.

## Installation
1. Copy the module to your Odoo addons directory
2. Restart Odoo server
3. Update app list and install the module

## Configuration
Step-by-step configuration instructions.

## Usage
How to use the module features.

## Dependencies
List of required modules and external dependencies.

## Known Issues
Any known limitations or issues.

## Changelog
Version history and changes.
```

---

## Copilot Execution Instructions

1. **Always start with the manifest file** and ensure all dependencies are correctly declared
2. **Create models first** with proper inheritance and field definitions
3. **Generate views** that follow Odoo's UX patterns
4. **Implement security** with appropriate access rights
5. **Add controllers** only if web APIs are needed
6. **Include comprehensive tests** for all functionality
7. **Generate demo data** for testing purposes
8. **Create proper documentation** including README and code comments
9. **Ensure the module is installable** by testing the manifest structure
10. **Follow Odoo's naming conventions** throughout the codebase

Remember: The generated module must be immediately installable and fully functional in Odoo 17 without any modifications.