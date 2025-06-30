from odoo import models, fields, api, _
from odoo.exceptions import UserError
from num2words import num2words
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Real Estate Commission Fields - matching sale.order fields
    buyer_id = fields.Many2one('res.partner', string='Buyer', 
                              help='The buyer of the property (from sale order)')
    project_id = fields.Many2one('product.template', string='Project',
                                help='The real estate project (product template)')
    unit_id = fields.Many2one('product.product', string='Unit',
                             help='The specific unit in the project (product variant)')
    booking_date = fields.Date(string='Booking Date',
                              help='Date when the property was booked')
    developer_commission = fields.Float(string='Developer Commission (%)',
                                       help='Commission percentage from developer')
    sale_value = fields.Monetary(string='Sale Value',
                                help='Total sale value of the property')
    deal_id = fields.Char(string='Deal ID',
                         help='Reference number for the deal')
    
    # Amount in words
    amount_total_words = fields.Char(
        string='Amount in Words', 
        compute='_compute_amount_total_words', 
        store=True
    )

    @api.depends('amount_total', 'currency_id')
    def _compute_amount_total_words(self):
        """Convert amount to words in English"""
        for record in self:
            if record.amount_total:
                try:
                    amount_words = num2words(record.amount_total, lang='en').title()
                    currency_name = record.currency_id.name or 'Dirhams'
                    record.amount_total_words = f"{amount_words} {currency_name} Only"
                except Exception as e:
                    _logger.warning(f"Error converting amount to words: {e}")
                    record.amount_total_words = f"{record.amount_total:.2f} {record.currency_id.name or 'AED'} Only"
            else:
                record.amount_total_words = ""

    @api.model
    def create(self, vals):
        """Inherit create to copy deal information from sale order"""
        result = super().create(vals)
        
        # If invoice is created from sale order, copy deal information
        if result.invoice_origin and result.move_type in ['out_invoice', 'out_refund']:
            sale_order = self.env['sale.order'].search([
                ('name', '=', result.invoice_origin)
            ], limit=1)
            
            if sale_order:
                result.write({
                    'buyer_id': sale_order.buyer_id.id,
                    'project_id': sale_order.project_id.id,
                    'unit_id': sale_order.unit_id.id,
                    'booking_date': sale_order.booking_date,
                    'developer_commission': sale_order.developer_commission,
                    'sale_value': sale_order.sale_value,
                    'deal_id': sale_order.deal_id,
                })
        
        return result

    def action_print_custom_invoice(self):
        """Print custom invoice report"""
        self.ensure_one()
        if self.move_type not in ('out_invoice', 'out_refund'):
            raise UserError(_('This report can only be printed for customer invoices and credit notes.'))
        
        return self.env.ref('osus_invoice_report.action_report_custom_invoice').report_action(self)

    def action_print_custom_bill(self):
        """Print custom bill report"""
        self.ensure_one()
        if self.move_type not in ('in_invoice', 'in_refund'):
            raise UserError(_('This report can only be printed for vendor bills and credit notes.'))
        
        return self.env.ref('osus_invoice_report.action_report_custom_bill').report_action(self)

    def action_print_custom_receipt(self):
        """Print custom receipt report"""
        self.ensure_one()
        return self.env.ref('osus_invoice_report.action_report_custom_receipt').report_action(self)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        """Override to include deal information in invoice"""
        invoice_vals = super()._prepare_invoice()
        
        # Add deal tracking fields to invoice
        invoice_vals.update({
            'buyer_id': self.buyer_id.id,
            'project_id': self.project_id.id,
            'unit_id': self.unit_id.id,
            'booking_date': self.booking_date,
            'developer_commission': self.developer_commission,
            'sale_value': self.sale_value,
            'deal_id': self.deal_id,
        })
        
        return invoice_vals