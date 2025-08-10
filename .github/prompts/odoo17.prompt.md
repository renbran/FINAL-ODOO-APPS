---
mode: ask
---
Create a professional, Odoo 17 compliant module that adheres to best practices for control, simplicity, functionality, and logic system handling. The module should be built with proper sequence and architecture to minimize casual time and unnecessary production errors.
Instructions:
Define the Module Purpose and Scope:
Clearly outline the purpose of the module.
Specify the features and functionalities the module should include.
Identify the target audience and use cases.
Set Up the Development Environment:
Ensure Odoo 17 is installed and running on your development machine.
Set up a virtual environment to isolate dependencies.
Install any necessary dependencies or libraries.
Create the Module Structure:
Follow the standard Odoo module structure:
Copy
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   ├── my_model_views.xml
│   └── my_module_menu.xml
├── controllers/
│   ├── __init__.py
│   └── my_controller.py
├── static/
│   ├── src/
│   │   ├── js/
│   │   │   └── my_script.js
│   │   └── css/
│   │       └── my_style.css
│   └── img/
│       └── my_image.png
└── security/
    ├── ir.model.access.csv
    └── my_security.xml
Define the Module Manifest:
Create the __manifest__.py file with the following content:
Python
Copy
{
    'name': 'My Module',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'A brief summary of the module',
    'description': """
    A detailed description of the module.
    """,
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
        'views/my_module_menu.xml',
        'security/my_security.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
    'application': True,
}
Develop the Models:
Create the models/__init__.py file to import your models.
Define your models in models/my_model.py:
Python
Copy
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.module.model'
    _description = 'My Module Model'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
Create Views and Templates:
Define XML views in views/my_model_views.xml:
xml
Copy
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my.module.model.form</field>
        <field name="model">my.module.model</field>
        <field name="arch" type="xml">
            <form string="My Model">
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="description"/>
                        <field name="active"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>
    <record id="view_my_model_tree" model="ir.ui.view">
        <field name="name">my.module.model.tree</field>
        <field name="model">my.module.model</field>
        <field name="arch" type="xml">
            <tree string="My Model">
                <field name="name"/>
                <field name="description"/>
                <field name="active"/>
            </tree>
        </field>
    </record>
</odoo>
Create the menu in views/my_module_menu.xml:
xml
Copy
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <menuitem id="my_module_menu" name="My Module" />
    <menuitem id="my_model_menu" name="My Model" parent="my_module_menu" action="my_model_action"/>
    <record id="my_model_action" model="ir.actions.act_window">
        <field name="name">My Model</field>
        <field name="res_model">my.module.model</field>
        <field name="view_mode">tree,form</field>
    </record>
</odoo>
Implement Security:
Define access rights in security/ir.model.access.csv:
Copy
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_module_model,access.my.module.model,model_my_module_model,,1,1,1,1
Create security rules in security/my_security.xml if needed.
Develop Controllers (if applicable):
Create the controllers/__init__.py file to import your controllers.
Define your controllers in controllers/my_controller.py:
Python
Copy
from odoo import http
from odoo.http import request

class MyController(http.Controller):
    @http.route('/my_module/my_route', auth='public')
    def my_method(self):
        return "Hello, World!"
Static Assets (if applicable):
Place any static assets (JS, CSS, images) in the static directory.
Ensure they are properly referenced in your views or templates.
Testing and Validation:
Test the module thoroughly to ensure all functionalities work as expected.
Validate the module using Odoo’s built-in tools and best practices.
Documentation:
Provide clear documentation for the module, including installation instructions, usage, and any configuration details.
Review and Refine:
Review the code for adherence to Odoo’s best practices.
Refine the module based on feedback and testing results.
Additional Notes:
If any part of the instructions is unclear, please ask for clarification.
Always review the instructions provided to ensure they are followed accurately.
Aim to eliminate casual time and unnecessary production errors by following best practices for control, simplicity, functionality, and logic system handling.