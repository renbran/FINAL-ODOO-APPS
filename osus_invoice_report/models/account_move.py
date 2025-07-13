from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_print_custom_invoice(self):
        """
        Print the PDF copy of the invoice using the custom report action.
        """
        return self.env.ref('osus_invoice_report.action_report_custom_invoice_modern').report_action(self)
