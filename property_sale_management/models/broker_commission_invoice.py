from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BrokerCommissionInvoice(models.Model):
    _name = 'broker.commission.invoice'
    _description = 'Broker Commission Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    property_sale_id = fields.Many2one('property.sale', string='Property Sale', required=True, ondelete='cascade')
    seller_id = fields.Many2one('res.partner', string='Broker/Seller', required=True)
    commission_percentage = fields.Float(string='Commission Percentage')
    commission_amount = fields.Monetary(string='Commission Amount', currency_field='currency_id')
    currency_id = fields.Many2one(related='property_sale_id.currency_id', store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    invoice_ids = fields.Many2many('account.move', string='Invoices')
    total_invoiced = fields.Monetary(string='Total Invoiced', compute='_compute_payment_details', store=True, currency_field='currency_id')
    total_paid = fields.Monetary(string='Total Paid', compute='_compute_payment_details', store=True, currency_field='currency_id')
    payment_progress = fields.Float(string='Payment Progress %', compute='_compute_payment_details', store=True)
    
    @api.depends('invoice_ids', 'invoice_ids.payment_state', 'invoice_ids.amount_total', 'invoice_ids.amount_residual')
    def _compute_payment_details(self):
        for record in self:
            total_invoiced = sum(record.invoice_ids.mapped('amount_total'))
            total_paid = sum(record.invoice_ids.filtered(lambda i: i.payment_state == 'paid').mapped('amount_total'))
            
            record.total_invoiced = total_invoiced
            record.total_paid = total_paid
            
            if total_invoiced > 0:
                record.payment_progress = (total_paid / total_invoiced) * 100
            else:
                record.payment_progress = 0.0
                
            # Update state based on payment status
            if record.invoice_ids and all(inv.payment_state == 'paid' for inv in record.invoice_ids):
                record.state = 'invoiced'
                
    def action_generate_invoice(self):
        """Generate invoice for broker commission"""
        self.ensure_one()
        
        # Check if broker account is set
        if not self.seller_id.property_account_receivable_id:
            raise UserError(_('Please set a receivable account for the broker %s') % self.seller_id.name)
            
        # Create invoice
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.seller_id.id,
            'invoice_date': fields.Date.context_today(self),
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.env.ref('property_sale_management.product_broker_commission').id,
                    'name': _('Broker Commission - %s - %s%%') % (self.property_sale_id.name, self.commission_percentage),
                    'quantity': 1,
                    'price_unit': self.commission_amount,
                    'tax_ids': [(6, 0, [])],  # No taxes
                })
            ],
        }
        
        invoice = self.env['account.move'].create(invoice_vals)
        self.write({
            'invoice_ids': [(4, invoice.id)],
            'state': 'confirmed',
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Broker Commission Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }
        
    def action_cancel(self):
        """Cancel the broker commission invoice"""
        self.ensure_one()
        
        if self.state == 'cancelled':
            raise UserError(_('This commission is already cancelled'))
            
        if self.invoice_ids.filtered(lambda i: i.state != 'draft'):
            raise UserError(_('Cannot cancel a commission with confirmed invoices'))
            
        # Cancel any draft invoices
        draft_invoices = self.invoice_ids.filtered(lambda i: i.state == 'draft')
        draft_invoices.button_cancel()
        
        self.state = 'cancelled'
        
    def action_reset_to_draft(self):
        """Reset commission to draft state"""
        self.ensure_one()
        
        if self.state != 'cancelled':
            raise UserError(_('Only cancelled commissions can be reset to draft'))
            
        self.state = 'draft'