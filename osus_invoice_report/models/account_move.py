from odoo import models, api

class AccountMove(models.Model):
    def action_print_custom_bill(self):
        """
        Print the PDF copy of the bill using the custom report action.
        """
        return self.env.ref('osus_invoice_report.action_report_custom_bill').report_action(self)

    def action_print_custom_receipt(self):
        """
        Print the PDF copy of the receipt using the custom report action.
        """
        return self.env.ref('osus_invoice_report.action_report_custom_receipt').report_action(self)
    _inherit = 'account.move'

    def action_print_custom_invoice(self):
        """
        Print the PDF copy of the invoice using the custom report action.
        """
        return self.env.ref('osus_invoice_report.action_report_custom_invoice_modern').report_action(self)
