from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_print_custom_invoice(self):
        return self.env.ref('osus_invoice_report.action_report_custom_invoice').report_action(self)

    def action_print_custom_bill(self):
        return self.env.ref('osus_invoice_report.action_report_custom_bill').report_action(self)

    def action_print_custom_receipt(self):
        return self.env.ref('osus_invoice_report.action_report_custom_receipt').report_action(self)


class CustomInvoiceReport(models.AbstractModel):
    _name = 'report.osus_invoice_report.report_custom_invoice'
    _description = 'Custom Invoice Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'data': data,
        }