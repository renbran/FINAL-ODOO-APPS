from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    property_order_id = fields.Many2one('property.sale', string="Property Sale Order")
    property_rental_id = fields.Many2one('property.rental', string="Rental Order")
    broker_commission_id = fields.Many2one('broker.commission.invoice', string="Broker Commission")
    property_offer_id = fields.Many2one('property.sale.offer', string="Property Offer", 
                                       related='broker_commission_id.property_offer_id', store=True, readonly=True)
    
    @api.model
    def create(self, vals):
        """Override create to set property_offer_id if broker_commission_id is set"""
        res = super(AccountMove, self).create(vals)
        
        # If this is a broker commission invoice, update related fields
        if res.broker_commission_id:
            # Update the broker commission state if needed
            if res.broker_commission_id.state == 'confirmed':
                res.broker_commission_id.state = 'invoiced'
                
        return res
    
    def action_post(self):
        """Override post action to update broker commission payment status"""
        res = super(AccountMove, self).action_post()
        
        # Update broker commission payment info when posting the invoice
        for move in self:
            if move.broker_commission_id:
                move.broker_commission_id._compute_payment_info()
                
        return res
    
    def button_draft(self):
        """Override reset to draft to check broker commission status"""
        for move in self:
            if move.broker_commission_id and move.broker_commission_id.state == 'invoiced':
                # Reset broker commission to confirmed state when invoice is reset to draft
                move.broker_commission_id.state = 'confirmed'
                
        return super(AccountMove, self).button_draft()
    
    def button_cancel(self):
        """Override cancel to check broker commission status"""
        for move in self:
            if move.broker_commission_id and move.broker_commission_id.state == 'invoiced':
                # Reset broker commission to confirmed state when invoice is cancelled
                move.broker_commission_id.state = 'confirmed'
                
        return super(AccountMove, self).button_cancel()
    
    def action_view_property_sale(self):
        """Smart button to view related property sale"""
        self.ensure_one()
        if self.property_order_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Property Sale'),
                'res_model': 'property.sale',
                'res_id': self.property_order_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return {}
    
    def action_view_broker_commission(self):
        """Smart button to view related broker commission"""
        self.ensure_one()
        if self.broker_commission_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Broker Commission'),
                'res_model': 'broker.commission.invoice',
                'res_id': self.broker_commission_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        return {}
