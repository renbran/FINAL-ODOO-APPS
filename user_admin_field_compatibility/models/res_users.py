# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    is_admin = fields.Boolean(
        string='Is Administrator',
        compute='_compute_is_admin',
        store=False,
        help='True if user is in System Administrator group (base.group_system)'
    )
    
    @api.depends('groups_id')
    def _compute_is_admin(self):
        """Compute if user is system administrator"""
        admin_group = self.env.ref('base.group_system', raise_if_not_found=False)
        for user in self:
            user.is_admin = admin_group and admin_group in user.groups_id
