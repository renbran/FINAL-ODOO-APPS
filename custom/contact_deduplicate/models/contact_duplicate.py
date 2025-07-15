# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ContactDuplicate(models.Model):
    _name = 'contact.duplicate'
    _description = 'Contact Duplicate'
    _order = 'similarity_score desc'

    partner_id = fields.Many2one(
        'res.partner', string='Contact',
        required=True, ondelete='cascade'
    )
    duplicate_partner_id = fields.Many2one(
        'res.partner', string='Potential Duplicate',
        required=True, ondelete='cascade'
    )
    similarity_score = fields.Float(
        string='Similarity Score',
        digits=(5, 2),
        help="Similarity score between 0 and 1"
    )
    matching_fields = fields.Text(
        string='Matching Fields',
        help="Fields that match between the contacts"
    )
    state = fields.Selection([
        ('new', 'New'),
        ('reviewed', 'Reviewed'),
        ('merged', 'Merged'),
        ('ignored', 'Ignored'),
    ], string='Status', default='new')
    review_date = fields.Datetime(string='Review Date')
    review_user_id = fields.Many2one('res.users', string='Reviewed By')
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to avoid creating reverse duplicates"""
        filtered_vals = []
        
        for vals in vals_list:
            partner_id = vals.get('partner_id')
            duplicate_partner_id = vals.get('duplicate_partner_id')
            
            # Check if reverse duplicate already exists
            existing = self.search([
                ('partner_id', '=', duplicate_partner_id),
                ('duplicate_partner_id', '=', partner_id)
            ])
            
            if not existing:
                filtered_vals.append(vals)
        
        return super().create(filtered_vals)

    def action_mark_as_duplicate(self):
        """Mark this as a confirmed duplicate and open merge wizard"""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Merge Contacts',
            'res_model': 'contact.merge.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_ids': [(6, 0, [self.partner_id.id, self.duplicate_partner_id.id])],
                'default_master_partner_id': self.partner_id.id,
                'default_duplicate_record_id': self.id,
            }
        }

    def action_ignore_duplicate(self):
        """Mark this duplicate as ignored"""
        self.write({
            'state': 'ignored',
            'review_date': fields.Datetime.now(),
            'review_user_id': self.env.user.id,
        })

    def action_review_duplicate(self):
        """Mark this duplicate as reviewed"""
        self.write({
            'state': 'reviewed',
            'review_date': fields.Datetime.now(),
            'review_user_id': self.env.user.id,
        })

    def name_get(self):
        """Custom name_get to show meaningful names"""
        result = []
        for record in self:
            name = f"{record.partner_id.name} ↔ {record.duplicate_partner_id.name} ({record.similarity_score:.0%})"
            result.append((record.id, name))
        return result
