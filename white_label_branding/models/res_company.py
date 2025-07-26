# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    white_label_name = fields.Char(
        string='White Label Name',
        help='Name to replace Odoo branding with',
        compute='_compute_white_label_name',
        store=True,
        readonly=False
    )
    
    replace_odoo_branding = fields.Boolean(
        string='Replace Odoo Branding',
        default=True,
        help='Replace all Odoo references with company branding'
    )
    
    @api.depends('name')
    def _compute_white_label_name(self):
        for company in self:
            if not company.white_label_name:
                company.white_label_name = company.name
    
    @api.model
    def get_white_label_name(self):
        """Get the white label name for the current company"""
        company = self.env.company
        return company.white_label_name or company.name or _('Your Company')
    
    def write(self, vals):
        """Override write to update branding when company name changes"""
        result = super().write(vals)
        if 'name' in vals and not vals.get('white_label_name'):
            for company in self:
                if not company.white_label_name:
                    company.white_label_name = company.name
        return result
