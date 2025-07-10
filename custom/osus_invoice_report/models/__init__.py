from . import sale_order

from odoo import models, api

class AccountMoveCustomPrint(models.Model):
    _inherit = 'account.move'

    def action_print_custom_invoice(self):
        # Implement your custom invoice print logic here
        return self.env.ref('osus_invoice_report.action_report_custom_invoice').report_action(self)

    def action_print_custom_bill(self):
        # Implement your custom bill print logic here
        return self.env.ref('osus_invoice_report.action_report_custom_bill').report_action(self)

    def action_print_custom_receipt(self):
        # Implement your custom receipt print logic here
        return self.env.ref('osus_invoice_report.action_report_custom_receipt').report_action(self)
