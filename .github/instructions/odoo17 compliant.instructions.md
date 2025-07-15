---
applyTo: '**/*.ts'
---
# Copilot AI – Odoo 17 Strict Instruction

You are an Odoo 17 expert. Every time you generate code, follow the rules below **exactly and completely**. Do not deviate, do not use deprecated syntax, and do not invent non-standard patterns.

---

## 1. Target & Environment
- **Branch / Version** = `17.0`  
- **Python** ≥ 3.8, PEP-8 compliant (ignore E501/E301/E302)  
- **JS** = ES-6 modules only; no minified bundles  
- **CSS / SCSS** = prefix every custom class with `o_<module_name>_`  

---

## 2. Module File Tree (always reproduce)
```
<module_name>/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   └── <model>.py
├── views/
│   ├── <model>_views.xml
│   └── <model>_templates.xml
├── security/
│   ├── ir.model.access.csv
│   └── <model>_security.xml
├── data/
│   └── <model>_demo.xml
├── static/
│   ├── src/
│   │   ├── js/<module>.esm.js
│   │   ├── scss/<module>.scss
│   │   └── xml/<module>.xml
│   └── description/
│       └── img/
├── tests/
│   ├── __init__.py
│   └── test_<something>.py
└── README.md
```

---

## 3. Python Rules
1. **Header** always present  
   ```
   # -*- coding: utf-8 -*-
   # Copyright <YEAR> <AUTHOR>
   # License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
   ```

2. **Import order**  
   ```
   # 1. stdlib
   import logging
   # 2. odoo core
   from odoo import api, fields, models, _
   # 3. odoo addons (only if needed)
   ```

3. **Model template**  
   ```
   class MyModel(models.Model):
       _name = 'my.model'
       _inherit = ['mail.thread', 'mail.activity.mixin']
       _description = 'My Model'
       _order = 'create_date desc'
       _check_company_auto = True

       name = fields.Char(required=True)
       state = fields.Selection([
           ('draft', 'Draft'),
           ('done', 'Done'),
       ], default='draft')
   ```

4. **Field suffixes**  
   - Boolean: `is_`, `has_`, `allow_`  
   - Many2one → `_id`  
   - One2many / Many2many → `_ids` or `_line_ids`

5. **CRUD overrides**  
   - Use `@api.model_create_multi` for `create`.  
   - Use `super().<method>` **first** for `write`, `unlink`, `create`.

---

## 4. XML Rules
1. **Naming patterns**  
   - Menu root: `<model>_menu`  
   - Tree view: `<model>_view_tree`  
   - Form view: `<model>_view_form`  
   - Search view: `<model>_view_search`  
   - Window action: `<model>_action`  
   - Record rule: `<model>_rule_<group>`  

2. **View skeleton**  
   ```
   <record id="my_model_view_form" model="ir.ui.view">
       <field name="name">my.model.form</field>
       <field name="model">my.model</field>
       <field name="arch" type="xml">
           <form string="My Model">
               <sheet>
                   <group>
                       <field name="name"/>
                   </group>
               </sheet>
           </form>
       </field>
   </record>
   ```

3. **Security CSV**  
   ```
   id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
   access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
   ```

4. **No inline domain strings** – always use `<field name="domain">[('field','=',value)]</field>`.

---

## 5. JavaScript Rules
1. **File path** = `static/src/js/<module>.esm.js`  
   ```
   /** @odoo-module **/
   import { registry } from "@web/core/registry";
   import { Component } from "@odoo/owl";

   class MyComponent extends Component {
       static template = "my_module.MyComponent";
   }
   registry.category("actions").add("my_module.action", MyComponent);
   ```

2. **No jQuery** – use Odoo OWL 2 and `@web/core/*` utilities only.

---

## 6. CSS / SCSS Rules
- **File path** = `static/src/scss/<module>.scss`  
- **Selector prefix** = `o_<module_name>_`  
  ```
  .o_my_module_card {
      border: 1px solid $o-brand-primary;
  }
  ```

---

## 7. Security & Access Rights
- Always create `ir.model.access.csv` for every new model.  
- Add record rules in `<model>_security.xml` when multi-company or multi-department.  
- Default group for users: `base.group_user`; for managers: create `<module>_group_manager`.

---

## 8. Testing
- **Path** = `tests/test_<something>.py`  
- **Template**  
  ```
  from odoo.tests import TransactionCase

  class TestMyModel(TransactionCase):
      def test_create(self):
          rec = self.env['my.model'].create({'name': 'Test'})
          self.assertEqual(rec.state, 'draft')
  ```

---

## 9. Prohibited Patterns
- No SQL in controllers or models; use ORM only.  
- No `env.cr.execute()` unless absolutely unavoidable (comment the reason).  
- No direct calls to `http.request.session` in models.  
- No monkey-patches outside `register_hook()`.  
- No `api.one`, no `api.multi`, no `api.returns`.  
- No old-style `fields_view_get` overrides; use `view_init` or arch xpath.

---

## 10. Manifest Keys (minimum)
```
'version': '17.0.1.0.0',
'category': 'Sales',
'depends': ['base', 'mail'],
'data': [
    'security/ir.model.access.csv',
    'views/my_model_views.xml',
],
'assets': {
    'web.assets_backend': [
        'my_module/static/src/js/my_module.esm.js',
        'my_module/static/src/scss/my_module.scss',
    ],
},
'installable': True,
'application': True,
'license': 'LGPL-3',
```

---

## 11. Final Checklist Before Output
- [ ] Module installs on a fresh `17.0` runbot without errors.  
- [ ] No warnings in log (`odoo.tools.convert: No such field`, etc.).  
- [ ] All XML-IDs are unique across the module.  
- [ ] All demo data loads and can be deleted (`--test-tags` passes).  
- [ ] All tests pass (`odoo-bin -i my_module --test-enable`).  

Print only code that satisfies every point above.