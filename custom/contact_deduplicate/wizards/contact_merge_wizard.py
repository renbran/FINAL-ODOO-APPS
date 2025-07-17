# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json


class ContactMergeWizard(models.TransientModel):
    _name = 'contact.merge.wizard'
    _description = 'Contact Merge Wizard'

    partner_ids = fields.Many2many(
        'res.partner', string='Contacts to Merge',
        required=True
    )
    master_partner_id = fields.Many2one(
        'res.partner', string='Master Contact',
        required=True,
        help="The contact that will remain after merge"
    )
    duplicate_record_id = fields.Many2one(
        'contact.duplicate', string='Duplicate Record'
    )
    merge_strategy = fields.Selection([
        ('keep_master', 'Keep Master Contact Data'),
        ('merge_all', 'Merge All Data'),
        ('manual', 'Manual Selection'),
    ], string='Merge Strategy', default='merge_all', required=True)
    
    # Field merge options
    name = fields.Char(string='Name')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City')
    zip = fields.Char(string='ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one('res.country.state', string='State')
    vat = fields.Char(string='VAT')
    website = fields.Char(string='Website')
    comment = fields.Text(string='Internal Notes')
    
    preview_html = fields.Html(string='Merge Preview', compute='_compute_preview_html')

    @api.onchange('partner_ids', 'master_partner_id', 'merge_strategy')
    def _onchange_merge_data(self):
        """Update merge fields based on strategy"""
        if not self.partner_ids or not self.master_partner_id:
            return
        
        if self.merge_strategy == 'keep_master':
            master = self.master_partner_id
            self.name = master.name
            self.email = master.email
            self.phone = master.phone
            self.mobile = master.mobile
            self.street = master.street
            self.street2 = master.street2
            self.city = master.city
            self.zip = master.zip
            self.country_id = master.country_id
            self.state_id = master.state_id
            self.vat = master.vat
            self.website = master.website
            self.comment = master.comment
            
        elif self.merge_strategy == 'merge_all':
            # Merge data from all contacts
            self._merge_all_data()

    def _merge_all_data(self):
        """Merge data from all selected contacts"""
        partners = self.partner_ids
        
        # Name: prefer non-empty, longest name
        names = [p.name for p in partners if p.name]
        self.name = max(names, key=len) if names else ''
        
        # Email: prefer master's email, then first non-empty
        emails = [p.email for p in partners if p.email]
        self.email = self.master_partner_id.email or (emails[0] if emails else '')
        
        # Phone: prefer master's phone, then first non-empty
        phones = [p.phone for p in partners if p.phone]
        self.phone = self.master_partner_id.phone or (phones[0] if phones else '')
        
        # Mobile: prefer master's mobile, then first non-empty
        mobiles = [p.mobile for p in partners if p.mobile]
        self.mobile = self.master_partner_id.mobile or (mobiles[0] if mobiles else '')
        
        # Address: prefer most complete address
        best_address = self._find_best_address(partners)
        if best_address:
            self.street = best_address.street
            self.street2 = best_address.street2
            self.city = best_address.city
            self.zip = best_address.zip
            self.country_id = best_address.country_id
            self.state_id = best_address.state_id
        
        # VAT: prefer non-empty VAT
        vats = [p.vat for p in partners if p.vat]
        self.vat = vats[0] if vats else ''
        
        # Website: prefer non-empty website
        websites = [p.website for p in partners if p.website]
        self.website = websites[0] if websites else ''
        
        # Comments: merge all comments
        comments = [p.comment for p in partners if p.comment]
        self.comment = '\n---\n'.join(comments) if comments else ''

    def _find_best_address(self, partners):
        """Find the most complete address among partners"""
        best_partner = None
        best_score = 0
        
        for partner in partners:
            score = 0
            if partner.street:
                score += 1
            if partner.city:
                score += 1
            if partner.zip:
                score += 1
            if partner.country_id:
                score += 1
            if partner.state_id:
                score += 1
            
            if score > best_score:
                best_score = score
                best_partner = partner
        
        return best_partner

    @api.depends('partner_ids', 'master_partner_id')
    def _compute_preview_html(self):
        """Generate HTML preview of the merge"""
        for wizard in self:
            if not wizard.partner_ids:
                wizard.preview_html = ''
                continue
            
            html = '<div class="merge-preview">'
            html += '<h4>Contacts to Merge:</h4>'
            html += '<ul>'
            
            for partner in wizard.partner_ids:
                is_master = partner == wizard.master_partner_id
                html += f'<li><strong>{partner.name}</strong>'
                if is_master:
                    html += ' (Master)'
                html += f'<br/>Email: {partner.email or "N/A"}'
                html += f'<br/>Phone: {partner.phone or "N/A"}'
                html += '</li>'
            
            html += '</ul>'
            html += '</div>'
            
            wizard.preview_html = html

    def action_merge(self):
        """Perform the actual merge"""
        self.ensure_one()
        
        if len(self.partner_ids) < 2:
            raise UserError(_("Please select at least 2 contacts to merge."))
        
        if self.master_partner_id not in self.partner_ids:
            raise UserError(_("Master contact must be one of the selected contacts."))
        
        # Prepare merge data
        merge_data = {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'street': self.street,
            'street2': self.street2,
            'city': self.city,
            'zip': self.zip,
            'country_id': self.country_id.id if self.country_id else False,
            'state_id': self.state_id.id if self.state_id else False,
            'vat': self.vat,
            'website': self.website,
            'comment': self.comment,
        }
        
        # Get contacts to merge (excluding master)
        contacts_to_merge = self.partner_ids - self.master_partner_id
        
        # Store original data for history
        original_data = {}
        for field in merge_data:
            original_data[field] = getattr(self.master_partner_id, field)
        
        # Update master contact
        self.master_partner_id.write(merge_data)
        
        # Handle related records (move them to master contact)
        self._merge_related_records(contacts_to_merge)
        
        # Create merge history
        self._create_merge_history(contacts_to_merge, original_data, merge_data)
        
        # Update duplicate record status if exists
        if self.duplicate_record_id:
            self.duplicate_record_id.write({
                'state': 'merged',
                'review_date': fields.Datetime.now(),
                'review_user_id': self.env.user.id,
            })
        
        # Deactivate merged contacts
        contacts_to_merge.write({'active': False})
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Merged Contact',
            'res_model': 'res.partner',
            'res_id': self.master_partner_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _merge_related_records(self, contacts_to_merge):
        """Merge related records to master contact"""
        master_id = self.master_partner_id.id
        merge_ids = contacts_to_merge.ids
        
        # Define models and fields to update
        models_to_update = [
            ('sale.order', 'partner_id'),
            ('purchase.order', 'partner_id'),
            ('account.move', 'partner_id'),
            ('crm.lead', 'partner_id'),
            ('project.project', 'partner_id'),
            ('helpdesk.ticket', 'partner_id'),
            ('mail.message', 'author_id'),
            ('mail.followers', 'partner_id'),
        ]
        
        for model_name, field_name in models_to_update:
            if model_name in self.env:
                model = self.env[model_name]
                records = model.search([(field_name, 'in', merge_ids)])
                if records:
                    try:
                        records.write({field_name: master_id})
                    except Exception:
                        # Some models might have constraints, skip silently
                        pass

    def _create_merge_history(self, merged_contacts, original_data, new_data):
        """Create merge history record"""
        merged_data = []
        for contact in merged_contacts:
            merged_data.append({
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
            })
        
        field_changes = {}
        for field, new_value in new_data.items():
            old_value = original_data.get(field)
            if old_value != new_value:
                field_changes[field] = {
                    'old': old_value,
                    'new': new_value
                }
        
        self.env['contact.merge.history'].create({
            'master_partner_id': self.master_partner_id.id,
            'merged_partner_ids': json.dumps(merged_data),
            'field_changes': json.dumps(field_changes),
            'notes': f"Merged {len(merged_contacts)} contacts using strategy: {self.merge_strategy}"
        })
