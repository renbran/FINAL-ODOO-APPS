from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # The field names in the model must match the view exactly
    booking_date = fields.Date(
        string='Booking Date',
        tracking=True,
    )
    
    developer_commission = fields.Float(
        string='Broker Commission',
        tracking=True,
        digits=(16, 2),
    )
    
    buyer_id = fields.Many2one(
        'res.partner',
        string='Buyer',
        tracking=True,
    )
    
    deal_id = fields.Integer(
        string='Deal ID',
        tracking=True,
        copy=False,
    )
    
    project_template_id = fields.Many2one(
        'product.template',
        string='Project Name',
        tracking=True,
        domain=[('detailed_type', '=', 'service')],
        help="Select a product template that represents the project"
    )
    
    sale_value = fields.Monetary(
        string='Sale Value',
        tracking=True,
        currency_field='currency_id',
    )
    
    unit_id = fields.Many2one(
        'product.product',
        string='Unit',
        tracking=True,
    )

    @api.onchange('project_template_id')
    def _onchange_project_template(self):
        """Update unit domain when project template changes"""
        if self.project_template_id:
            domain = [('product_tmpl_id', '=', self.project_template_id.id)]
            return {'domain': {'unit_id': domain}}
        else:
            return {'domain': {'unit_id': []}}