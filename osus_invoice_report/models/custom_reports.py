from odoo import models, fields, api, _
from odoo.exceptions import UserError
from num2words import num2words
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Use correct custom field names from custom_fields module
    # booking_date, developer_commission, buyer, deal_id, project, sale_value, unit are already defined in custom_fields
    amount_total_words = fields.Char(string='Amount in Words', compute='_compute_amount_total_words', store=True)

    @api.depends('amount_total', 'currency_id')
    def _compute_amount_total_words(self):
        """Convert amount to words in English"""
        for record in self:
            if record.amount_total:
                try:
                    # Convert to words using num2words library
                    amount_words = num2words(record.amount_total, lang='en').title()
                    currency_name = record.currency_id.name or 'Dirhams'
                    record.amount_total_words = f"{amount_words} {currency_name} Only"
                except Exception as e:
                    _logger.warning(f"Error converting amount to words: {e}")
                    record.amount_total_words = f"{record.amount_total:.2f} {record.currency_id.name or 'AED'} Only"
            else:
                record.amount_total_words = ""

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

    def _get_formatted_date_uk(self, date_field):
        """Format date in UK format (DD/MM/YYYY)"""
        if date_field:
            return date_field.strftime('%d/%m/%Y')
        return ''

    def _get_commission_rate_percentage(self):
        """Get commission rate as percentage from first invoice line"""
        if self.invoice_line_ids:
            # Assuming quantity represents the commission rate (e.g., 0.05 for 5%)
            return self.invoice_line_ids[0].quantity * 100
        return 0.0

    def _get_vat_percentage(self):
        """Get VAT percentage from taxes"""
        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                for tax in line.tax_ids:
                    if tax.amount > 0:
                        return f"{tax.amount}%"
        return "5%"  # Default UAE VAT rate


class CustomInvoiceReport(models.AbstractModel):
    _name = 'report.osus_invoice_report.report_custom_invoice'
    _description = 'OSUS Custom Invoice Report'

    def _get_report_values(self, docids, data=None):
        """Get report values with enhanced data"""
        if not docids:
            raise UserError(_('No documents to print.'))
        
        docs = self.env['account.move'].browse(docids)
        
        # Validate documents
        for doc in docs:
            if doc.move_type not in ('out_invoice', 'out_refund'):
                raise UserError(_('Document %s is not a customer invoice or credit note.') % doc.name)
        
        # Helper functions for template
        def format_uk_date(date_obj):
            """Format date in UK format"""
            return date_obj.strftime('%d/%m/%Y') if date_obj else ''
        
        def get_commission_rate(invoice_lines):
            """Get commission rate percentage"""
            if invoice_lines:
                return invoice_lines[0].quantity * 100
            return 0.0
        
        def get_vat_rate(invoice_lines):
            """Get VAT rate from taxes"""
            for line in invoice_lines:
                for tax in line.tax_ids:
                    if tax.amount > 0:
                        return f"{tax.amount}%"
            return "5%"
        
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'data': data,
            'format_uk_date': format_uk_date,
            'get_commission_rate': get_commission_rate,
            'get_vat_rate': get_vat_rate,
            'company': self.env.company,
        }


class CustomBillReport(models.AbstractModel):
    _name = 'report.osus_invoice_report.report_custom_bill'
    _description = 'OSUS Custom Bill Report'

    def _get_report_values(self, docids, data=None):
        """Get report values for bills"""
        if not docids:
            raise UserError(_('No documents to print.'))
        
        docs = self.env['account.move'].browse(docids)
        
        # Validate documents
        for doc in docs:
            if doc.move_type not in ('in_invoice', 'in_refund'):
                raise UserError(_('Document %s is not a vendor bill or credit note.') % doc.name)
        
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'data': data,
            'company': self.env.company,
        }


class CustomReceiptReport(models.AbstractModel):
    _name = 'report.osus_invoice_report.report_custom_receipt'
    _description = 'OSUS Custom Receipt Report'

    def _get_report_values(self, docids, data=None):
        """Get report values for receipts"""
        if not docids:
            raise UserError(_('No documents to print.'))
        
        docs = self.env['account.move'].browse(docids)
        
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'data': data,
            'company': self.env.company,
        }