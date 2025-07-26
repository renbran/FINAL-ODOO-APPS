# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    white_label_name = fields.Char(
        related='company_id.white_label_name',
        readonly=False,
        string='White Label Name'
    )
    
    replace_odoo_branding = fields.Boolean(
        related='company_id.replace_odoo_branding',
        readonly=False,
        string='Replace Odoo Branding'
    )
    
    @api.onchange('replace_odoo_branding')
    def _onchange_replace_odoo_branding(self):
        """Set default white label name when enabling branding replacement"""
        if self.replace_odoo_branding and not self.white_label_name:
            self.white_label_name = self.company_id.name or _('Your Company')
