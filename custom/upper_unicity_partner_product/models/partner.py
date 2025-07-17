from odoo import models, fields, api, exceptions, _


class UniquePartner(models.Model):
    _inherit = 'res.partner'

    _sql_constraints = [
        ('res_partner_name_uniqu', 'unique(name)', 'Name of partner already exists!')
    ]

    @api.model
    def create(self, vals):
        """Ensure partner names are uppercase on creation and handle duplicates gracefully."""
        if 'name' in vals and vals['name']:
            original_name = vals['name']
            vals['name'] = vals['name'].upper()
            
            # Check if partner with this name already exists
            existing_partner = self.search([('name', '=', vals['name'])], limit=1)
            if existing_partner:
                # If we have email, append it to make name unique
                if vals.get('email') and vals['email'] not in vals['name']:
                    vals['name'] = f"{vals['name']} ({vals['email']})"
                else:
                    # Append a counter to make it unique
                    counter = 1
                    base_name = vals['name']
                    while self.search([('name', '=', vals['name'])], limit=1):
                        vals['name'] = f"{base_name} ({counter})"
                        counter += 1
        
        return super(UniquePartner, self).create(vals)

    def write(self, vals):
        """Ensure partner names are uppercase on update."""
        if 'name' in vals and vals['name']:
            vals['name'] = vals['name'].upper()
        return super(UniquePartner, self).write(vals)

    @api.onchange('name')
    def _onchange_name(self):
        """Convert the partner name to uppercase during form changes."""
        if self.name:
            self.name = self.name.upper()
