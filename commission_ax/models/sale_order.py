from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    external_commission_ids = fields.One2many('external.commission', 'sale_order_id', string='External Commissions')
    internal_commission_ids = fields.One2many('internal.commission', 'sale_order_id', string='Internal Commissions')
    
    consultant_id = fields.Many2one('hr.employee', string="Consultant")
    consultant_comm_percentage = fields.Float(string="Consultant Commission (%)", default=0.0)
    
    manager_id = fields.Many2one('hr.employee', string="Manager")
    manager_comm_percentage = fields.Float(string="Manager Commission (%)", default=0.0)
    
    director_id = fields.Many2one('hr.employee', string="Director")
    director_comm_percentage = fields.Float(string="Director Commission (%)", default=3.0)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self._create_internal_commissions()
        return res

    def _create_internal_commissions(self):
        for order in self:
            commission_data = [
                ('consultant', order.consultant_id, order.consultant_comm_percentage),
                ('manager', order.manager_id, order.manager_comm_percentage),
                ('director', order.director_id, order.director_comm_percentage),
            ]
            
            for position, employee, percentage in commission_data:
                if employee and percentage > 0:
                    self.env['internal.commission'].create({
                        'sale_order_id': order.id,
                        'employee_id': employee.id,
                        'position': position,
                        'percentage': percentage,
                    })

    def action_view_internal_commissions(self):
        self.ensure_one()
        return {
            'name': _('Internal Commissions'),
            'view_mode': 'tree,form',
            'res_model': 'internal.commission',
            'domain': [('sale_order_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_sale_order_id': self.id},
        }

    def action_view_external_commissions(self):
        self.ensure_one()
        return {
            'name': _('External Commissions'),
            'view_mode': 'tree,form',
            'res_model': 'external.commission',
            'domain': [('sale_order_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_sale_order_id': self.id},
        }