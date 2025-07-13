from odoo import models

class ReportCustomInvoice(models.AbstractModel):
    _name = 'report.osus_invoice_report.report_invoice'
    _description = 'OSUS Custom Invoice Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        return {
            'docs': docs,
        }
