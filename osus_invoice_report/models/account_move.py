from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_print_custom_invoice(self):
        """
        Print the PDF copy of the invoice using the custom report action.
        """
        return self.env.ref('osus_invoice_report.action_report_osus_invoice').report_action(self)

    def action_print_custom_bill(self):
        """
        Print the PDF copy of the bill using the custom report action.
        """
        return self.env.ref('osus_invoice_report.action_report_osus_bill').report_action(self)

    def action_print_custom_receipt(self):
        """
        Print the PDF copy of the receipt using the custom report action.
        """
        return self.env.ref('osus_invoice_report.action_report_osus_invoice').report_action(self)
