# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_status = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('custom_review', 'Custom Review'),
        ('custom_approved', 'Custom Approved'),
    ], string='Custom Status', default='draft', tracking=True)

    def action_set_custom_review(self):
        self.write({'custom_status': 'custom_review'})

    def action_set_custom_approved(self):
        self.write({'custom_status': 'custom_approved'})

    @api.constrains('custom_status')
    def _check_custom_status(self):
        for order in self:
            if order.custom_status not in dict(self.fields_get('custom_status')['selection']):
                raise ValidationError(_('Invalid custom status!'))
