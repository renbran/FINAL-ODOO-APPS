from odoo import models

class ReportCustomBill(models.AbstractModel):
    _name = 'report.osus_invoice_report.report_bills'
    _description = 'OSUS Custom Bill Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        return {
            'docs': docs,
        }
