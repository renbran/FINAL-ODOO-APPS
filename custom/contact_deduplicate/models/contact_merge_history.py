# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ContactMergeHistory(models.Model):
    _name = 'contact.merge.history'
    _description = 'Contact Merge History'
    _order = 'merge_date desc'

    master_partner_id = fields.Many2one(
        'res.partner', string='Master Contact',
        required=True, ondelete='cascade'
    )
    merged_partner_ids = fields.Text(
        string='Merged Contact IDs',
        help="JSON list of merged partner IDs and names"
    )
    merge_date = fields.Datetime(
        string='Merge Date',
        default=fields.Datetime.now
    )
    merge_user_id = fields.Many2one(
        'res.users', string='Merged By',
        default=lambda self: self.env.user
    )
    field_changes = fields.Text(
        string='Field Changes',
        help="JSON representation of field changes during merge"
    )
    notes = fields.Text(string='Merge Notes')

    def name_get(self):
        """Custom name_get to show meaningful names"""
        result = []
        for record in self:
            name = f"Merge into {record.master_partner_id.name} on {record.merge_date.strftime('%Y-%m-%d')}"
            result.append((record.id, name))
        return result
