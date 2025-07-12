from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    """A class that inherits the already existing model account move to add
    the related property sale and rental records"""
    _inherit = 'account.move'

    property_order_id = fields.Many2one('property.sale',
                                      string="Property Sale",
                                      help='The corresponding property sale order')
    property_rental_id = fields.Many2one('property.rental',
                                       string='Property Rental',
                                       help='The corresponding property rental order')
    
    def write(self, vals):
        result = super(AccountMove, self).write(vals)
        
        # If the invoice is being paid
        if 'payment_state' in vals and vals.get('payment_state') == 'paid':
            for record in self:
                if record.property_order_id:
                    # Find the related sale lines for this invoice
                    sale_lines = self.env['property.sale.line'].search([
                        ('invoice_id', '=', record.id)
                    ])
                    
                    if sale_lines:
                        # Update collection status for related sale lines
                        sale_lines.write({
                            'collection_status': 'paid',
                            'payment_date': fields.Date.today()
                        })
                        
                        # Update the property payment progress
                        if record.property_order_id.property_id:
                            record.property_order_id.property_id._compute_payment_progress()
                            record.property_order_id.property_id._compute_payment_details()
        
        # If the invoice is being cancelled and it's related to a property sale
        if 'state' in vals and vals['state'] == 'cancel':
            for record in self:
                if record.property_order_id:
                    # Find the related sale lines for this invoice
                    sale_lines = self.env['property.sale.line'].search([
                        ('invoice_id', '=', record.id)
                    ])
                    
                    if sale_lines:
                        # Reset collection status for related sale lines
                        sale_lines.write({
                            'collection_status': 'unpaid',
                            'invoice_id': False,
                            'payment_date': False
                        })
                        
                        # Update the sale state if needed
                        if record.property_order_id.state == 'invoiced':
                            # Only revert to confirm if not all lines have invoices
                            remaining_invoiced_lines = record.property_order_id.property_sale_line_ids.filtered(
                                lambda l: l.invoice_id and l.invoice_id.state != 'cancel'
                            )
                            
                            if not remaining_invoiced_lines:
                                record.property_order_id.write({'state': 'confirm'})
                        
                        # Force recompute progress on property
                        if record.property_order_id.property_id:
                            record.property_order_id.property_id._compute_payment_progress()
                            record.property_order_id.property_id._compute_payment_details()
        
        return result
    
    def action_post(self):
        """Override to update property sale line status on invoice posting"""
        res = super(AccountMove, self).action_post()
        
        # Update property sale lines associated with this invoice
        for record in self:
            if record.property_order_id:
                property_sale_lines = self.env['property.sale.line'].search([
                    ('invoice_id', '=', record.id)
                ])
                
                if property_sale_lines:
                    # Update the status if the invoice is being posted
                    if record.state == 'posted':
                        # If invoice is paid already, mark lines as paid
                        if record.payment_state == 'paid':
                            property_sale_lines.write({
                                'collection_status': 'paid',
                                'payment_date': fields.Date.today()
                            })
                        
                        # Update property payment details
                        if record.property_order_id.property_id:
                            record.property_order_id.property_id._compute_payment_progress()
                            record.property_order_id.property_id._compute_payment_details()
        
        return res
    
    def button_cancel(self):
        """Override to update property sale line status on invoice cancellation"""
        # Check if any associated property sale lines exist
        for record in self:
            if record.property_order_id:
                sale_lines = self.env['property.sale.line'].search([
                    ('invoice_id', '=', record.id),
                    ('collection_status', '=', 'paid')
                ])
                
                if sale_lines:
                    raise UserError(_("Cannot cancel this invoice because it's linked to paid property installments. "
                                     "Please create a credit note instead."))
        
        res = super(AccountMove, self).button_cancel()
        return res
